# Claude Code 环境备份

我的 Claude Code 全部插件与技能的完整备份，用于跨设备同步。

> 🔑 **Token 已脱敏**：`settings.json` 中 `ANTHROPIC_AUTH_TOKEN` 已替换为 `<YOUR_TOKEN_HERE>` 占位符。恢复后请手动填入你自己的 Token（bigmodel.cn 控制台获取）。其余配置（模型、API 地址、插件开关）完整保留。

## 仓库结构
哈哈哈
| 路径 | 内容 |
|---|---|
| `skills/` | 全部个人技能（60+ 个），含 **ecc**(everything-claude-code) 与 **mattpocock-skills** 两个目录插件的完整源码 |
| `settings.json` | 全局设置：模型、API 地址、Token、插件启用状态、hooks 开关 |
| `settings.local.json` | 权限白名单 |
| `plugins/installed_plugins.json` | 已安装插件清单（版本号） |
| `plugins/known_marketplaces.json` | 插件市场源地址 |
| `restore.sh` | 一键恢复脚本（Git Bash 运行） |

## 在新电脑上恢复

### 前置条件
- 安装 [git](https://git-scm.com)（Windows 版自带 Git Bash）
- 安装 [Claude Code](https://claude.com/product/claude-code)

### 方式一：一键脚本（推荐）

```bash
git clone https://github.com/danbao757/claude-env-backup.git
cd claude-env-backup
bash restore.sh
```

完成后重启 Claude Code 即可。

### 方式二：手动恢复

1. 把 `skills/` 下所有文件夹复制到 `~/.claude/skills/`
2. 把 `settings.json`、`settings.local.json` 复制到 `~/.claude/`，并把其中 `<YOUR_TOKEN_HERE>` 替换为你的真实 API Token
3. 安装市场插件：

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add thedotmack/claude-mem
claude plugin marketplace add tanweai/pua
claude plugin marketplace add https://github.com/eze-is/web-access.git
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill

claude plugin install skill-creator@claude-plugins-official
claude plugin install claude-mem@thedotmack
claude plugin install pua@pua-skills
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
claude plugin install web-access@web-access
```

> ecc 与 mattpocock-skills 是**目录插件**（`@skills-dir`），随 `skills/` 文件夹自动加载，无需安装命令。

## 插件清单（备份于 2026-09-24）

| 插件 | 版本 | 来源 | 恢复方式 |
|---|---|---|---|
| ecc (everything-claude-code) | — | 本地目录 | `skills/everything-claude-code-main` 自动加载 |
| mattpocock-skills | — | 本地目录 | `skills/skills-main` 自动加载 |
| claude-mem | 13.9.2 | thedotmack/claude-mem | 市场安装 |
| pua | 3.5.0 | tanweai/pua | 市场安装 |
| web-access | 2.5.2 | eze-is/web-access | 市场安装 |
| ui-ux-pro-max | 2.6.2 | nextlevelbuilder/ui-ux-pro-max-skill | 市场安装 |
| skill-creator | — | anthropics/claude-plugins-official | 市场安装 |

## 日常更新备份

技能/配置有变动后，在本机重新同步并推送：

```bash
cd ~/claude-env-backup
cp -rf ~/.claude/skills/* skills/
cp ~/.claude/settings.json ~/.claude/settings.local.json .
# 重新脱敏 Token，避免真实凭据入库
sed -i 's/"ANTHROPIC_AUTH_TOKEN": "[^"]*"/"ANTHROPIC_AUTH_TOKEN": "<YOUR_TOKEN_HERE>"/' settings.json
git add -A
git commit -m "update backup $(date +%F)"
git push
```
