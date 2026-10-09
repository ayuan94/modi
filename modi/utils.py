# -*- coding: utf-8 -*-
import json
import os

from mcdreforged.api.rtext import *
from mcdreforged.api.types import *

from modi.resources import *


def tr(key, *args) -> str:
    return ServerInterface.get_instance().tr(f"{plugin}.{key}", *args)


def rtext_cmd(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.run_command, cmd)


def rtext_paste(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.suggest_command, cmd)


# ---------------- 配置读写 ----------------

def default_config():
    return {
        "command": default_command,
        "run_on_startup": default_run_on_startup,
        "cron": default_cron,
    }


def load_config():
    """读取配置，若文件不存在或字段缺失则补全默认值并保存"""
    cfg = default_config()
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg.update(data)
        except (json.JSONDecodeError, OSError):
            pass
    # 补全缺失字段
    changed = False
    for k, v in default_config().items():
        if k not in cfg:
            cfg[k] = v
            changed = True
    if changed or not os.path.isfile(config_path):
        save_config(cfg)
    return cfg


def save_config(cfg):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


# ---------------- 命令执行 ----------------

def execute_command(server: ServerInterface, raw_command: str):
    """执行一条 MC 命令，自动去掉开头的 / 前缀（server.execute 不需要 /）"""
    cmd = raw_command.strip()
    if cmd.startswith("/"):
        cmd = cmd[1:]
    server.execute(cmd)


# ---------------- cron 表达式解释 ----------------

def _describe_field(field: str, field_name_zh: str, field_name_en: str) -> str:
    """解释单个 cron 字段"""
    field = field.strip()
    if field == "*":
        return tr("cron_every", field_name_zh)
    if field.startswith("*/"):
        try:
            n = int(field[2:])
            return tr("cron_every_n", field_name_zh, n)
        except ValueError:
            return field
    # 列表
    if "," in field:
        parts = field.split(",")
        return field_name_zh + ": " + ", ".join(parts)
    # 范围
    if "-" in field:
        return field_name_zh + ": " + field
    # 单个数字
    return field_name_zh + ": " + field


def cron_describe(expression: str) -> str:
    """把 5 字段 cron 表达式翻译成通俗中文解释"""
    if not expression or not expression.strip():
        return tr("cron_disabled")
    parts = expression.strip().split()
    if len(parts) != 5:
        return tr("cron_invalid", expression)

    names_zh = cron_field_names_zh
    names_en = cron_field_names_en
    desc_parts = [_describe_field(parts[i], names_zh[i], names_en[i]) for i in range(5)]
    return tr("cron_format", *desc_parts)


def cron_is_valid(expression: str) -> bool:
    """校验 cron 表达式是否为合法的 5 字段格式（语法层面）"""
    if not expression or not expression.strip():
        return True  # 空表示禁用，合法
    parts = expression.strip().split()
    if len(parts) != 5:
        return False
    # 简单校验每个字段的字符合法性
    allowed = set("0123456789*/,-")
    for p in parts:
        if not p or any(ch not in allowed for ch in p):
            return False
    return True
