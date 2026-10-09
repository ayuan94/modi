# -*- coding: utf-8 -*-
from mcdreforged.api.command import *
from mcdreforged.api.types import *

from modi.resources import *
from modi.utils import *

# 全局调度器与 server 引用
scheduler = None
server_instance = None


# ---------------- 权限检查 ----------------

def permission_check(src: CommandSource, cmd: str) -> bool:
    return src.get_permission_level() >= permission.get(cmd, 1)


# ---------------- 帮助信息 ----------------

def get_help_msg():
    return p_start + """
""" + rtext_cmd(f'§b{PREFIX}§r', tr('click_show'), PREFIX) + " §a" + tr('help_show') + """
""" + rtext_cmd(f'§b{PREFIX} run§r', tr('click_run'), f'{PREFIX} run') + " §a" + tr('help_run') + """
""" + rtext_paste(f'§b{PREFIX} setcmd§r §d<command>§r', tr('click_paste'), f'{PREFIX} setcmd ') + " §a" + tr('help_setcmd') + """
""" + rtext_paste(f'§b{PREFIX} setcron§r §d<expr|off>§r', tr('click_paste'), f'{PREFIX} setcron ') + " §a" + tr('help_setcron') + """
""" + rtext_cmd(f'§b{PREFIX} startup§r', tr('click_toggle'), f'{PREFIX} startup') + " §a" + tr('help_startup') + """
""" + p_line


# ---------------- 状态展示 ----------------

def show_status(src: CommandSource):
    cfg = load_config()
    src.reply(p_start)
    src.reply(tr("status_command", cfg["command"]))
    startup_on = cfg.get("run_on_startup", True)
    src.reply(tr("status_startup", "§a" + tr("on") + "§r" if startup_on else "§c" + tr("off") + "§r"))

    cron_expr = (cfg.get("cron") or "").strip()
    if cron_expr:
        src.reply(tr("status_cron_on", "§a" + cron_expr + "§r"))
        src.reply(tr("status_cron_desc", cron_describe(cron_expr)))
        if scheduler is not None:
            job = scheduler.get_job("modi_cron")
            if job and job.next_run_time:
                nxt = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                src.reply(tr("status_next_run", nxt))
    else:
        src.reply(tr("status_cron_off", "§c" + tr("off") + "§r"))
    src.reply(p_line)


# ---------------- 命令操作 ----------------

def run_now(src: CommandSource):
    cfg = load_config()
    server = ServerInterface.get_instance()
    cmd = cfg["command"]
    if cmd.startswith("!!"):
        server.execute_command(cmd)
    else:
        execute_command(server, cmd)
    src.reply(system_return + tr("run_executed", cmd))


def set_cmd(src: CommandSource, command: str):
    cfg = load_config()
    cfg["command"] = command.strip()
    save_config(cfg)
    update_scheduler()
    src.reply(system_return + tr("cmd_set", command.strip()))


def set_cron(src: CommandSource, expression: str):
    expr = expression.strip()
    # 支持 off/disable/none 关闭 cron
    if expr.lower() in ("off", "disable", "none", "null", "0"):
        expr = ""
    if expr and not cron_is_valid(expr):
        src.reply(error + tr("cron_invalid", expr))
        return
    cfg = load_config()
    cfg["cron"] = expr
    save_config(cfg)
    update_scheduler()
    if expr:
        src.reply(system_return + tr("cron_set", expr, cron_describe(expr)))
    else:
        src.reply(system_return + tr("cron_disabled_msg"))


def toggle_startup(src: CommandSource):
    cfg = load_config()
    cfg["run_on_startup"] = not cfg.get("run_on_startup", True)
    save_config(cfg)
    state = "§a" + tr("on") + "§r" if cfg["run_on_startup"] else "§c" + tr("off") + "§r"
    src.reply(system_return + tr("startup_toggled", state))


# ---------------- 调度器 ----------------

def start_scheduler():
    global scheduler
    if scheduler is not None:
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        server_instance.logger.error(f"[{plugin}] APScheduler not installed, cron disabled. "
                                     f"Run: pip install apscheduler")
        return
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.start()
    update_scheduler()


def stop_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None


def update_scheduler():
    """根据当前配置重新注册 cron 任务"""
    if scheduler is None:
        return
    for job in scheduler.get_jobs():
        job.remove()
    cfg = load_config()
    cron_expr = (cfg.get("cron") or "").strip()
    if not cron_expr:
        return
    try:
        from apscheduler.triggers.cron import CronTrigger
        trigger = CronTrigger.from_crontab(cron_expr)
        scheduler.add_job(
            _cron_job,
            trigger,
            id="modi_cron",
            replace_existing=True,
        )
        server_instance.logger.info(f"[{plugin}] cron job registered: {cron_expr}")
    except Exception as e:
        server_instance.logger.error(f"[{plugin}] invalid cron expression '{cron_expr}': {e}")


def _cron_job():
    """cron 触发时执行的任务"""
    cfg = load_config()
    cmd = cfg["command"]
    if cmd.startswith("!!"):
        server_instance.execute_command(cmd)
    else:
        execute_command(server_instance, cmd)
    server_instance.logger.info(f"[{plugin}] cron executed: {cmd}")


# ---------------- 命令注册 ----------------

def register_command(server: PluginServerInterface):
    server.register_command(
        Literal(PREFIX).
            runs(lambda src: show_status(src)).
            on_error(UnknownArgument, lambda src: src.reply(get_help_msg()), handled=True).
            then(
            Literal("help").runs(lambda src: src.reply(get_help_msg()))
        ).then(
            Literal("run").
                requires(lambda src: permission_check(src, "run")).
                runs(lambda src: run_now(src)).
                on_error(RequirementNotMet, lambda src: src.reply(error + tr("err_permission")), handled=True)
        ).then(
            Literal("setcmd").
                requires(lambda src: permission_check(src, "setcmd")).
                on_error(RequirementNotMet, lambda src: src.reply(error + tr("err_permission")), handled=True).
                then(
                GreedyText("command").
                    runs(lambda src, ctx: set_cmd(src, ctx["command"])).
                    on_error(UnknownArgument, lambda src: src.reply(error + tr("err_syntax")), handled=True)
            )
        ).then(
            Literal("setcron").
                requires(lambda src: permission_check(src, "setcron")).
                on_error(RequirementNotMet, lambda src: src.reply(error + tr("err_permission")), handled=True).
                then(
                GreedyText("expression").
                    runs(lambda src, ctx: set_cron(src, ctx["expression"])).
                    on_error(UnknownArgument, lambda src: src.reply(error + tr("err_syntax")), handled=True)
            )
        ).then(
            Literal("startup").
                requires(lambda src: permission_check(src, "startup")).
                runs(lambda src: toggle_startup(src)).
                on_error(RequirementNotMet, lambda src: src.reply(error + tr("err_permission")), handled=True)
        )
    )


# ---------------- 事件 ----------------

def on_load(server: PluginServerInterface, old):
    global server_instance
    server_instance = server
    load_config()  # 确保配置文件存在
    register_command(server)
    start_scheduler()
    server.register_help_message(PREFIX, tr("main_msg"))


def on_unload(server: PluginServerInterface):
    stop_scheduler()


def on_server_startup(server: PluginServerInterface):
    cfg = load_config()
    if cfg.get("run_on_startup", True):
        server.logger.info(f"[{plugin}] running command on server startup")
        cmd = cfg["command"]
        if cmd.startswith("!!"):
            server.execute_command(cmd)
        else:
            execute_command(server, cmd)
