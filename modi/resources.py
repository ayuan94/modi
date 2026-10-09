# -*- coding: utf-8 -*-
plugin = 'modi'
PREFIX = '!!modi'

config_path = "config/" + plugin + ".json"

# 默认命令（不带 / 前缀，server.execute 不需要）
default_command = "player modi spawn at -358.86 60.00 -184.23 facing -358 -184 in minecraft:the_end"
default_run_on_startup = True
default_cron = ""  # 空字符串表示不启用 cron

system_return = f"""§b[§r{plugin}§b] §r"""
error = system_return + """§cError: §r"""

p_start = f"""§b============§f{plugin}§b============§r"""
p_line = "§b=====================================§r"

# 权限
permission = {
    "help": 1,
    "show": 1,
    "run": 1,
    "setcmd": 2,
    "setcron": 2,
    "startup": 2,
}

# cron 字段顺序（5 字段标准格式）
cron_fields = ["minute", "hour", "day_of_month", "month", "day_of_week"]
cron_field_names_zh = ["分钟", "小时", "日期", "月份", "星期"]
cron_field_names_en = ["minute", "hour", "day", "month", "weekday"]
