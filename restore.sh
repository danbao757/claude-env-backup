#!/usr/bin/env bash
# Claude Code 环境一键恢复脚本 — 在本仓库根目录用 Git Bash 运行
set -e

CLAUDE_DIR="$HOME/.claude"

echo "[1/4] 恢复个人技能与目录插件 (ecc / mattpocock-skills)..."
mkdir -p "$CLAUDE_DIR/skills"
cp -rf skills/* "$CLAUDE_DIR/skills/"

echo "[2/4] 恢复全局设置..."
cp -f settings.json settings.local.json "$CLAUDE_DIR/"
if grep -q "<YOUR_TOKEN_HERE>" "$CLAUDE_DIR/settings.json"; then
  echo "    ⚠️  Token 为占位符：请编辑 ~/.claude/settings.json，把 <YOUR_TOKEN_HERE>"
  echo "       替换为你的真实 API Token（bigmodel.cn 控制台获取）"
fi

echo "[3/4] 添加插件市场..."
claude plugin marketplace add anthropics/claude-plugins-official 2>/dev/null || true
claude plugin marketplace add thedotmack/claude-mem 2>/dev/null || true
claude plugin marketplace add tanweai/pua 2>/dev/null || true
claude plugin marketplace add https://github.com/eze-is/web-access.git 2>/dev/null || true
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill 2>/dev/null || true

echo "[4/4] 安装市场插件..."
claude plugin install skill-creator@claude-plugins-official 2>/dev/null || true
claude plugin install claude-mem@thedotmack 2>/dev/null || true
claude plugin install pua@pua-skills 2>/dev/null || true
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill 2>/dev/null || true
claude plugin install web-access@web-access 2>/dev/null || true

echo ""
echo "✅ 恢复完成！重启 Claude Code 后所有插件与技能即可使用。"
echo "   说明：ecc / mattpocock-skills 为目录插件(@skills-dir)，已随 skills/ 自动加载；"
echo "        市场插件版本以各上游仓库最新版为准。"
