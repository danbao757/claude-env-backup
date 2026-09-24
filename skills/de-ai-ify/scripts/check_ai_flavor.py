#!/usr/bin/env python3
"""扫描中文文本里的AI味痕迹，输出命中清单供人工复核。

用法:
    python check_ai_flavor.py <文件路径> [--strict]

说明:
- 这是复查清单，不是硬门槛。正式文档里的冒号、行话等命中可能是合理的，
  每个命中处逐个人工决定"改"还是"留"。
- --strict 时若存在任何命中，退出码为 1，可用于自动化把关；默认始终退出 0。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 每组: (组名, [(条目名, 正则), ...])
PATTERNS: list[tuple[str, list[tuple[str, re.Pattern]]]] = [
    (
        "翻案句（句式表演深刻）",
        [
            ("不是…而是…", re.compile(r"不是[^。；！？\n]{0,30}，?而是")),
            ("并非…而是…", re.compile(r"并非[^。；！？\n]{0,30}，?而是")),
            ("与其说…不如说…", re.compile(r"与其说[^，。\n]{0,25}不如说")),
            ("表面…实际…", re.compile(r"表面(?:上看|上)?[^，。\n]{0,20}(?:实际|实则|实则上|实际上)")),
            ("不只是…更…", re.compile(r"不(?:只是|仅是?|但)[^。；！？\n]{0,20}，?(?:更|还)(?:是|能|会|在|有)")),
            ("看似…实则…", re.compile(r"看似[^，。\n]{0,20}实则")),
        ],
    ),
    (
        "顿悟路标（替读者惊讶）",
        [
            ("值得注意的是", re.compile(r"(?:值得|需要|特别)注意的是")),
            ("更有意思的是", re.compile(r"(?:更|相当|十分|颇为)(?:有意思|有趣|耐人寻味)的是")),
            ("某种意义上", re.compile(r"在?某种意义上(?:说|来讲)?")),
            ("这里的关键在于", re.compile(r"(?:这里的)?关键(?:在于|就是)")),
            ("说白了/说穿了", re.compile(r"说(?:白了|穿了)")),
            ("更微妙的是", re.compile(r"更(?:微妙|深层)的是")),
        ],
    ),
    (
        "总分口号（表演总结）",
        [
            ("总而言之", re.compile(r"总而言之|总的说来")),
            ("综上所述", re.compile(r"综上(?:所述|来看)")),
            ("由此可见", re.compile(r"由此可[见见]")),
            ("归根结底", re.compile(r"归根(?:结底|到底)")),
            ("一言以蔽之", re.compile(r"一言以蔽之")),
        ],
    ),
    (
        "升华腔（结尾拔高）",
        [
            ("不仅仅是…更是…", re.compile(r"不仅(?:仅|只)是[^。；！？\n]{0,20}，?(?:更|也)是")),
            ("让我们拭目以待", re.compile(r"拭目以待")),
            ("这正是…的意义", re.compile(r"这(?:正)?是[^，。\n]{0,25}(?:意义|魅力|价值)(?:所在)?")),
            ("未来…可期", re.compile(r"未来可期|前景可期|未来.{0,10}值得期待")),
            ("时代开头", re.compile(r"在?(?:当今|这个|如今)[^，。\n]{0,15}(?:时代|浪潮|背景下)")),
            ("随着…的发展", re.compile(r"随着[^，。\n]{2,25}(?:的)?(?:不断)?(?:发展|深入|推进|普及)")),
        ],
    ),
    (
        "商业黑话",
        [
            ("赋能", re.compile(r"赋能")),
            ("抓手", re.compile(r"(?:有力)?抓手")),
            ("闭环", re.compile(r"闭环")),
            ("颗粒度", re.compile(r"颗粒度")),
            ("底层逻辑/顶层设计", re.compile(r"(?:底层逻辑|顶层设计)")),
            ("组合拳", re.compile(r"组合拳")),
            ("打法", re.compile(r"打法")),
            ("对齐/拉通", re.compile(r"(?:对齐|拉通)(?:了|一下)?(?:颗粒度|进度|认知|目标)?")),
            ("生态/心智/护城河", re.compile(r"(?:生态(?:位|圈|圈)?|用户心智|护城河)")),
        ],
    ),
    (
        "抬价副词与空洞形容",
        [
            ("抬价副词", re.compile(r"(?:极大地|显著地?|充分地?|深入地?|有效地?地)(?:提升|提高|改善|优化|促进|推动|降低|减少)")),
            ("丰富多彩类", re.compile(r"(?:丰富多彩|形式多样|卓有成效|行稳致远|焕然一新|有声有色)")),
            ("全面提升类", re.compile(r"(?:全面|全方位|多维度|多层次)(?:提升|赋能|覆盖|发力)")),
        ],
    ),
    (
        "翻译腔",
        [
            ("进行了X", re.compile(r"进行了(?:一[次番场个])?[^，。；\n]{0,6}?(?:讨论|分析|研究|交流|部署|优化|调整|汇报|总结|梳理|重构)")),
            ("作出了X", re.compile(r"作出了?(?:重要)?(?:贡献|决定|部署|指示|表态)")),
            ("扮演着角色", re.compile(r"扮演(?:着|了)(?:重要|关键|不可或缺)?的?角色")),
            ("发挥着作用", re.compile(r"发挥(?:着|了)(?:重要|关键|巨大|积极)?作用")),
            ("对于X而言", re.compile(r"对于[^，。\n]{1,20}而言")),
        ],
    ),
    (
        "AI高频词",
        [
            ("堪称/可谓/无疑", re.compile(r"(?:堪称|可谓|无疑|毋庸置疑|无可置疑)")),
            ("旨在/致力于", re.compile(r"(?:旨在|致力于)")),
            ("聚焦/深耕/擘画", re.compile(r"(?:聚焦|深耕|擘画)")),
            ("助力/打造", re.compile(r"(?:助力|着力?打造)")),
            ("深入探讨", re.compile(r"深入(?:探讨|剖析|解读)")),
        ],
    ),
    (
        "客服腔与教师腔",
        [
            ("希望对您有帮助", re.compile(r"希望[^，。\n]{0,8}对(?:您|你)(?:有所)?帮助")),
            ("欢迎随时", re.compile(r"欢迎?随时(?:咨询|告诉我|联系|提问)")),
            ("很荣幸", re.compile(r"很(?:荣幸|高兴)(?:能)?(?:为您|为你|帮您|帮你)")),
            ("记住，X是关键", re.compile(r"记住[，,][^，。\n]{0,20}(?:很关键|是关键|最重要)")),
            ("让我们", re.compile(r"让我们(?:一起)?(?:来看|来看看|回到|继续|想象)")),
            ("这是一个好问题", re.compile(r"这是(?:一[个条])?(?:非常|很)?(?:好|棒|优秀)的?(?:问题|想法|提问)")),
        ],
    ),
    (
        "工整枚举（短文里的首先其次最后）",
        [
            ("首先…其次…", re.compile(r"首先[^，。\n]{0,60}其次")),
            ("再次/最后（枚举链）", re.compile(r"其次[^，。\n]{0,60}(?:再次|最后)")),
        ],
    ),
]

# 标点类命中。冒号在技术文档（键值/时间/比例）里是正常的，报告但不加重。
PUNCT_CHECKS: list[tuple[str, re.Pattern, str]] = [
    ("破折号（中文最强AI信号之一）", re.compile(r"—|──|–(?![0-9])|(?<![0-9])–"), "改句号断开或普通逗号"),
    ("感叹号连用", re.compile(r"！{2,}|!{2,}"), "保留一个或全部去掉"),
    ("句号省略号堆叠", re.compile(r"。{4,}|\.{6,}"), "用标准省略号……"),
    ("分号工整串联", re.compile(r"[^；\n]{4,30}；[^；\n]{4,30}；"), "拆成短句"),
]

EMOJI_DECOR = re.compile(
    "[\U0001F389\U0001F31F\U0001F680\U0001F4A1\U0001F525\U0001F4CC\U0001F3AF"
    "\U0001F4AA\U0001F44D\U00002764\U00002705\U0000274C\U0001F4C8\U0001F4C6"
    "▍■●★☆✨✔✖]"
)

# 这些位置的冒号/破折号不算命中：URL、时间、代码
URL_RE = re.compile(r"https?://\S+|[\w.-]+\.(?:com|cn|io|org|net|py|ts|js|md)\b\S*")
TIME_RE = re.compile(r"[0-2]?\d:[0-5]\d(:[0-5]\d)?")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def strip_quiet_zones(text: str) -> tuple[str, list[tuple[int, int]]]:
    """返回(清洗后的文本, 被抹掉区间的列表)，把代码块/行内代码/URL/时间替换为等长的空白。"""
    spans: list[tuple[int, int]] = []

    def _blank(m: re.Match) -> str:
        spans.append((m.start(), m.end()))
        return " " * (m.end() - m.start())

    cleaned = CODE_FENCE_RE.sub(_blank, text)
    cleaned = INLINE_CODE_RE.sub(_blank, cleaned)
    cleaned = URL_RE.sub(_blank, cleaned)
    cleaned = TIME_RE.sub(_blank, cleaned)
    return cleaned, spans


def line_of_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan(path: Path, strict: bool) -> int:
    raw = path.read_text(encoding="utf-8", errors="replace")
    cleaned, _ = strip_quiet_zones(raw)

    hits: list[tuple[str, str, int, str]] = []  # (组, 条目, 行号, 样本)

    for group, entries in PATTERNS:
        for name, pat in entries:
            for m in pat.finditer(cleaned):
                hits.append((group, name, line_of_offset(cleaned, m.start()), m.group(0)[:40]))

    # 标点：只扫清洗后的文本
    for name, pat, advice in PUNCT_CHECKS:
        for m in pat.finditer(cleaned):
            hits.append((f"标点·{name}", "标点", line_of_offset(cleaned, m.start()), m.group(0)[:40]))

    # 冒号：中文冒号与行中英文冒号（键值/时间已被抹掉，剩下的多是引出金句）
    for m in re.finditer(r"：", cleaned):
        hits.append(("标点·中文冒号（确认不是键值/时间）", "标点", line_of_offset(cleaned, m.start()), "："))

    # 装饰符号出现在小标题行
    for i, line in enumerate(cleaned.splitlines(), start=1):
        if line.lstrip().startswith("#") and EMOJI_DECOR.search(line):
            hits.append(("结构·emoji小标题", "结构", i, line.strip()[:40]))

    # 加粗密度：**xx** 出现次数 / 正文字符数
    prose_len = len(re.sub(r"\s", "", cleaned))
    bold_count = len(re.findall(r"\*\*[^*\n]{1,40}\*\*", cleaned))
    bold_warn = ""
    if prose_len > 300 and bold_count > max(3, prose_len // 300):
        bold_warn = f"加粗 {bold_count} 处 / {prose_len} 字，密度偏高，全文都是重点等于没有重点"

    # 输出
    out = sys.stdout
    if not hits and not bold_warn:
        out.write("未发现明显AI味命中。注意这是模式扫描，句子的机器感仍需人工通读判断。\n")
        return 0

    by_group: dict[str, list] = {}
    for h in hits:
        by_group.setdefault(h[0], []).append(h)

    out.write(f"AI味扫描报告：{path.name}，共 {len(hits)} 处命中\n")
    out.write("=" * 60 + "\n")
    for group in by_group:
        items = by_group[group]
        out.write(f"\n[{group}] {len(items)} 处\n")
        shown: set[str] = set()
        for _, name, lineno, sample in items:
            key = f"{name}|{sample}"
            mark = "" if key not in shown else "（重复模式）"
            shown.add(key)
            out.write(f"  L{lineno:<4} {name}  {sample}{mark}\n")
    if bold_warn:
        out.write(f"\n[结构·加粗密度]\n  {bold_warn}\n")
    out.write("\n" + "=" * 60 + "\n")
    out.write("这是复查清单不是判决书：逐个命中处人工判断要改还是合理保留（如技术文档键值冒号、确属行话的黑话）。\n")
    return 1 if strict else 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="扫描中文文本里的AI味痕迹")
    ap.add_argument("path", type=Path)
    ap.add_argument("--strict", action="store_true", help="存在命中时以退出码 1 结束")
    args = ap.parse_args()
    if not args.path.exists():
        sys.stderr.write(f"文件不存在：{args.path}\n")
        sys.exit(2)
    sys.exit(scan(args.path, args.strict))


if __name__ == "__main__":
    main()
