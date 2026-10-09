# modi

一个 [MCDReforged](https://github.com/MCDReforged/MCDReforged) 插件，用于在**服务器启动完成后**及/或按 **cron 定时**执行一条可配置的 Minecraft 命令。

## 功能特性

- **启动执行**：监听 MCDR 的 `on_server_startup` 事件，服务器启动完成后自动执行命令（可开关）
- **定时执行**：基于 APScheduler，支持标准 5 字段 cron 表达式
- **命令可配置**：游戏内命令即可修改，修改后立即生效，无需重载
- **状态查看**：`!!modi` 可查看当前命令、启动开关、cron 状态、cron 通俗解释及下次执行时间
- **手动执行**：随时可手动触发一次
- **中英文双语**

## 安装

1. 将本插件放入 MCDR 的 `plugins/` 目录（或将 `.mcdr` 包放入该目录）
2. 启动服务器，插件会自动生成配置文件 `config/modi.json`

## 依赖

| 依赖 | 版本 | 说明 |
| ---- | ---- | ---- |
| MCDReforged | >=2.0.0 | 核心框架 |
| APScheduler | - | 必要，cron 定时功能需要 |

> 插件加载时，MCDR 会自动安装 `requirements.txt` 中的 Python 依赖，通常无需手动安装。
> 若服务器处于离线环境或自动安装失败，请手动执行 `pip install apscheduler`。
> 即使未安装 APScheduler，插件也不会崩溃，仅禁用 cron 定时功能，状态查看与手动执行仍可正常使用。

## 配置文件

`config/modi.json`：

```json
{
    "command": "player modi spawn at -358.86 60.00 -184.23 facing -358 -184 in minecraft:the_end",
    "run_on_startup": true,
    "cron": ""
}
```

| 字段 | 说明 |
| ---- | ---- |
| `command` | 要执行的 MC 命令，带不带开头的 `/` 都可以（插件会自动处理） |
| `run_on_startup` | 是否在服务器启动完成后自动执行 |
| `cron` | cron 表达式（5 字段：分 时 日 月 周），留空或 `off` 表示不启用 |

## 命令一览

| 命令 | 说明 | 所需权限 |
| ---- | ---- | -------- |
| `!!modi` | 查看当前命令、启动开关、cron 状态与通俗解释、下次执行时间 | 1 |
| `!!modi help` | 显示帮助 | 1 |
| `!!modi run` | 立即手动执行一次当前命令 | 1 |
| `!!modi setcmd <command>` | 设置要执行的 MC 命令 | 2 |
| `!!modi setcron <expr\|off>` | 设置 cron 表达式，`off` 关闭 | 2 |
| `!!modi startup` | 切换启动时执行开关 | 2 |

## Cron 表达式说明

标准 5 字段格式，顺序为：**分　时　日　月　星期**

```
┌──────────── 分钟 (0 - 59)
│ ┌────────── 小时 (0 - 23)
│ │ ┌──────── 日期 (1 - 31)
│ │ │ ┌────── 月份 (1 - 12)
│ │ │ │ ┌──── 星期 (0 - 6，0=周日)
│ │ │ │ │
* * * * *
```

### 常用示例

| 表达式 | 含义 |
| ------ | ---- |
| `0 12 * * *` | 每天 12:00 |
| `0 */6 * * *` | 每 6 小时 |
| `30 8 * * 1-5` | 周一至周五每天 08:30 |
| `0 20 * * 0,6` | 每周六、周日 20:00 |
| `0 0 1 * *` | 每月 1 号 00:00 |
| `*/30 * * * *` | 每 30 分钟 |

### 符号说明

- `*`：任意值（每个单位都触发）
- `*/n`：每隔 n 个单位
- `,`：列举多个值，如 `1,15,30`
- `-`：范围，如 `1-5`（周一到周五）

> 定时调度器时区为 `Asia/Shanghai`。

## 使用示例

设置每天 12 点执行：

```
!!modi setcron 0 12 * * *
```

更换要执行的命令：

```
!!modi setcmd player modi spawn at -358.86 60.00 -184.23 facing -358 -184 in minecraft:the_end
```

关闭启动时自动执行：

```
!!modi startup
```

## 权限说明

MCDReforged 权限等级：`0` guest < `1` user < `2` admin < `3` helper < `4` owner。
玩家权限在 MCDR 的 `config/permission.yml` 中配置。本插件默认：查看与手动执行类命令需等级 1，配置类命令（setcmd / setcron / startup）需等级 2。

## 许可证

本项目基于 [GNU General Public License v3.0](LICENSE) 许可证开源。
