#!/usr/bin/env python3
"""
merge_radar.py — Market Radar 数据合并 & 发布脚本

职责：读取 Claude 本次生成的 new_items.json，与 GitHub 上的历史 data.json 合并，
     剪枝后通过 GitHub Contents API 写回 main 分支。

Claude 的上下文里永远不需要载入历史条目。
用法：python3 merge_radar.py

v4 改动（2026-07-25 上午）：新增发布日期硬性过滤，防止把过期新闻（原文发布已数周/数月）
当作"新增"收录进雷达。触发原因：2026-07-25 发现"阿里巴巴全年收入首破1万亿元"
（原文发布于 2026-05-13）、"小米汽车6月销量"（原文 2026-07-08）、"腾讯混元Hy3"
（原文 2026-07-07）三条新闻被当作当日新增收录，实际都是旧闻。
详见 routine-prompt.md 2.6/2.7 节。

v6 改动（2026-08-11）：新增 schema 校验闸门 validate_item_schema()。触发原因：
2026-08-11 08:11 那轮 Routine 输出用了另一套字段名（type/entry/tags），漏掉了
why/markets/keywords/group，脚本原样发布、前端又是 `${it.why ? ... : ""}` 这种
写法——缺字段不报错、只安静地少渲染一块，结果当天 7 条新闻全都没有"为何相关"，
市场标签和关键词筛选也一并失效，直到用户自己打开 App 才发现。根因是 Routine 的
prompt 与 routine-prompt.md §6 脱节，而脚本这层完全没有把关。修复：
  (a) 发布前逐条校验前端必需字段，缺失即拒绝该条；
  (b) type→group、tags→keywords 做别名兼容，能救的先救；
  (c) 全部候选都不合格 → 判定为系统性漂移，联网写入前直接 exit(1)，不推降级数据；
      仅部分不合格 → 好的照常发布，末尾以非 0 退出码告警，当天就能发现。

v5 改动（2026-07-25 下午）：把发布目标分支从 claude/radar-data 改回 main，并新增
"陈旧分支保护"。触发原因：v4 上线后 Routine 当天首次真正跑通 merge_radar.py，
写入的是 claude/radar-data 分支——但这个分支自 2026-07-06 起就没人碰过（此前
main 分支一直由另一条"radar: HH:MM batch"命名的旧管线持续更新，直到今天
2026-07-25 08:18 才停）。claude/radar-data 里躺了 19 天的旧数据一夜之间被
prune() 的 KEEP_DAYS=7 逻辑几乎清空，只剩当天新增的 8 条，而这个分支的
updated_at 又比 main 新，于是页面改成展示这个几乎清空的分支——用户看到"之前
推送全没了"。核心问题：两个分支各自独立累积历史，一旦其中一个长期没人写，
下次一写就会被自己的"7天保留期"规则误杀。修复：
  (a) 把 BRANCH 改回 main，与过去19天实际在用、持续更新的分支保持一致，
      不再维护一个可能被遗忘的第二分支；
  (b) prune() 增加陈旧分支保护：如果现有条目里最新的 first_seen 本身已经
      超过 KEEP_DAYS，说明这个数据源已经很久没更新，这次直接跳过按日期
      剪枝（只按 MAX_ITEMS 数量上限裁剪），避免"长期没跑 + 一朝跑通"的
      组合再次清空历史。

v8 改动（2026-08-17）：两个问题一起修。

问题 A ——「Routine 显示跑了，App 却没更新」：2026-08-17 08:07 那轮 Routine
实际跑通、搜到 3 条合规新闻，但发布到 GitHub main 分支这一步没有成功——main
最后一次更新停在 2026-08-16 21:07，而这轮的产出（data.json/seen.json/
new_items.json 三个文件，内容和字段结构都和 merge_radar.py 会产出的一模一样）
最终是以一次普通 git commit 的形式，落在了这次运行自己的一次性分支
claude/modest-goldberg-o8ovg4 上，没有人再看这个分支，App 读的是 main，于是
永远看不到这轮更新。翻了一下仓库历史，这不是孤例：几十个 claude/<随机名> 分支
里躺着历史上其他几轮的产出（本质是运行环境每轮都会把工作目录的改动提交到自己
的一次性分支——这一步和 merge_radar.py 通过 GitHub API 直接发布到 main 是两条
独立的路径）。真正的问题是：一旦 API 发布失败/被跳过，Routine 侧目前的应对是
"退回去手动把 data.json/seen.json 攒出来、本地 git commit 兜底"，这恰恰重新
制造了 v3 架构想消灭的东西（Claude 在自己上下文里手搓合并结果），而且没有任何
显式报错，用户只能靠自己发现 App 没更新。真正的修复在 routine-prompt.md 里加了
一条硬规则：merge_radar.py 非 0 退出 = 停止并报错，禁止手动写 data.json/
seen.json 或本地 git commit 兜底；脚本这层无法强制这一点，只能靠 prompt 说清楚
后果。

问题 B ——「重复/过去好几天的旧闻反复出现」：`id` 去重只按 url（或标题）算哈希，
挡得住"同一篇文章被重复提交"，挡不住"同一个事件被不同来源、不同天的文章各写
一篇"。2026-08-17 抽查 main 分支发现腾讯Q2业绩、美国7月CPI、零售销售等好几个
事件，在 data.json 里以不同 id、不同来源、跨 4~5 天分别出现了 4~6 次——每次
都满足 2.5 节的 published_date/still_developing 规则（技术上没违规），但对
用户来说就是同一条新闻被推了好几遍。新增 `dedupe_topics()`：在 id 去重之后，
再按标题/摘要的文本相似度 + keywords 重合度做一次"事件级"去重，与已发布历史
（existing_items）和同批次候选互相比对，命中则丢弃并计入 seen，防止同一事件
被反复收录。
"""

import json
import os
import re
import sys
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPO    = "dzkeke-tech/market-radar"
BRANCH  = "main"
API_URL = f"https://api.github.com/repos/{REPO}/contents"
TOKEN   = os.environ.get("GITHUB_TOKEN", "")

MAX_ITEMS = 150
KEEP_DAYS = 7
STALE_BRANCH_GRACE_DAYS = KEEP_DAYS  # 若现有数据的最新 first_seen 已超过这个天数，视为“陈旧分支”，本轮跳过按日期剪枝

# 发布日期硬性过滤（v4 新增）：
#   - MAX_AGE_SOFT_DAYS：默认时间窗。超过则要求 still_developing=true 才放行。
#   - MAX_AGE_HARD_DAYS：硬上限。无论是否 still_developing，超过一律丢弃。
#   - 缺失/无法解析 published_date 的候选：暂不硬性丢弃（避免 Claude 端 prompt
#     还没升级、字段缺失时把新流水线打断），只打印警告。等 routine 稳定产出
#     published_date 后，可把 REQUIRE_PUBLISHED_DATE 改成 True 转为硬性拦截。
MAX_AGE_SOFT_DAYS = 2
MAX_AGE_HARD_DAYS = 5
REQUIRE_PUBLISHED_DATE = False

TZ_BJ = timezone(timedelta(hours=8))


# ── GitHub API helpers ────────────────────────────────────────────────────────

def gh_get(filename):
    """Fetch a file from BRANCH. Returns (parsed_json, sha) or (None, None) on 404."""
    url = f"{API_URL}/{filename}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept":        "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            meta = json.loads(r.read())
        data = json.loads(base64.b64decode(meta["content"]).decode("utf-8"))
        return data, meta["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise


def gh_put(filename, obj, sha, message):
    """PUT a JSON object to BRANCH. Exits with code 1 on failure."""
    content_b64 = base64.b64encode(
        json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode()
    body = {"message": message, "content": content_b64, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(
        f"{API_URL}/{filename}",
        data=json.dumps(body).encode(),
        method="PUT",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept":        "application/vnd.github+json",
            "Content-Type":  "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            code = r.status
        print(f"  PUT {filename} → HTTP {code}")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"  PUT {filename} FAILED HTTP {e.code}: {err}", file=sys.stderr)
        sys.exit(1)


def gh_put_local(filename, obj, out_dir):
    """Write JSON object to a local file for manual publishing via MCP tools."""
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  LOCAL {filename} → {out_path}")


# ── Item helpers ──────────────────────────────────────────────────────────────

def validate_new_items(items, today_str):
    """发布日期硬性过滤（v4 新增）。

    Claude 在 new_items.json 里应为每条候选填 published_date（原文发布日期，
    YYYY-MM-DD，从原文页面的时间戳/作者栏读取，而不是"今天发现它"的日期）。

    规则：
      - published_date 距今 > MAX_AGE_HARD_DAYS：无条件丢弃（防"1-3个月前旧闻"复发）。
      - published_date 距今 > MAX_AGE_SOFT_DAYS 且未标 still_developing=true：丢弃。
      - published_date 格式无法解析：丢弃并警告。
      - published_date 缺失：REQUIRE_PUBLISHED_DATE=False 时仅警告放行（过渡期，
        避免 routine 侧 prompt 还没升级导致整条流水线被打断）；改成 True 后转硬性丢弃。

    返回 (valid_items, dropped)，dropped 为 [(item, reason), ...] 供日志打印。
    """
    today = datetime.strptime(today_str, "%Y-%m-%d")
    valid, dropped = [], []

    for it in items:
        pub = it.get("published_date")

        if not pub:
            if REQUIRE_PUBLISHED_DATE:
                dropped.append((it, "缺少 published_date（硬性要求已开启）"))
                continue
            print(f"  ⚠ [{it.get('id','?')}] 缺少 published_date，暂按放行处理（过渡期）：{it.get('title','')[:40]}")
            valid.append(it)
            continue

        try:
            pub_dt = datetime.strptime(str(pub)[:10], "%Y-%m-%d")
        except ValueError:
            dropped.append((it, f"published_date 格式无法解析: {pub!r}"))
            continue

        age_days = (today - pub_dt).days
        if age_days < 0:
            age_days = 0  # 允许时区/剪辑误差

        if age_days > MAX_AGE_HARD_DAYS:
            dropped.append((it, f"原文发布于 {pub}，距今 {age_days} 天，超过硬上限 {MAX_AGE_HARD_DAYS} 天"))
            continue

        if age_days > MAX_AGE_SOFT_DAYS and not it.get("still_developing"):
            dropped.append((it, f"原文发布于 {pub}，距今 {age_days} 天，超过默认时间窗 {MAX_AGE_SOFT_DAYS} 天且未标 still_developing"))
            continue

        valid.append(it)

    return valid, dropped


# ── Schema 校验闸门（v6 新增）────────────────────────────────────────────────

# 前端 index.html 渲染每张卡片时依赖的字段。缺任何一个都会导致该条静默降级
# （最典型的是 why 缺失 → "为何相关"整块不渲染，markets 缺失 → 市场标签消失、
# 港股/美股/A股筛选页漏掉这条）。因为前端是 `${it.why ? ... : ""}` 这种写法，
# 缺字段不会报错、只会安静地少一块，所以必须在发布前拦住。
REQUIRED_FIELDS = ["id", "tier", "title", "summary", "why", "source", "url", "markets", "keywords"]

# 机械可推导的字段：缺了不算错，自动补上并打印提示，不阻断发布。
AUTOFILL_DEFAULTS = {"group": "个股", "translated": False, "verified": False}

# 历史别名 → 规范字段名。2026-08-11 那次 Routine 漂移写的是 type/tags，
# 这里做一次兼容映射，能救回来的就救，救不回来的（why/markets）交给下面拦截。
FIELD_ALIASES = {"type": "group", "tags": "keywords"}

VALID_MARKETS = {"HK", "US", "A"}
MIN_WHY_LEN = 8  # 挡住 why 为 ""、"-"、"n/a" 这种敷衍值


def _has_cjk(s):
    return any("\u4e00" <= ch <= "\u9fff" for ch in str(s))


def validate_item_schema(items, now_bj):
    """校验每条候选是否具备前端渲染所需的全部字段。

    返回 (items, degraded)，items 含全部条目（合格的 + 已修复标注的），
    degraded 为 [(item, [问题描述, ...]), ...]。

    设计取舍（v7 修正，很重要）：**这一层永远不阻断发布**。

    v6 的做法是「全部条目不合格就在发布前 exit(1)」，理由是"降级数据不如不发"。
    实践证明这个判断是错的：2026-08-11 上线后，Routine 的 prompt 依然是漂移的，
    于是每一轮都走"全部不合格"分支直接中止，连续两天六轮一条都没发出去，而用户
    完全不知情——因为 Routine 的退出码只在运行日志里，用户看的是 App。结果是
    「静默降级」被我换成了「静默停摆」，反而更糟。

    现在的原则：
      - 缺字段的条目照常发布，但打 `_schema_issues` 标记、并把 why 换成醒目提示，
        让问题直接显示在用户真正会看的页面上；
      - 退出码仍置非 0，但只作为事后信号，且一定在写入成功之后；
      - 任何情况下都不在发布前中止。
    """
    out, degraded = [], []

    for it in items:
        # 1) 别名兼容：canonical 字段缺失时，从旧字段名搬过来
        for old, new in FIELD_ALIASES.items():
            if old in it and not it.get(new):
                it[new] = it.pop(old)
                print(f"  ⚠ [{it.get('id','?')}] 字段别名 {old} → {new}（Routine prompt 可能已漂移，请核对 routine-prompt.md §6）")

        problems = []

        # 2) 必填字段检查
        for f in REQUIRED_FIELDS:
            v = it.get(f)
            if v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and not v):
                problems.append(f"缺少必填字段 {f}")

        # 3) 关键字段的取值合法性
        if it.get("tier") not in (1, 2, 3, "1", "2", "3"):
            problems.append(f"tier 非法: {it.get('tier')!r}（应为 1/2/3）")

        why = it.get("why")
        if isinstance(why, str) and 0 < len(why.strip()) < MIN_WHY_LEN:
            problems.append(f"why 过短（{len(why.strip())} 字符），疑似占位值: {why!r}")

        mk = it.get("markets")
        if isinstance(mk, list) and mk:
            bad = [m for m in mk if m not in VALID_MARKETS]
            if bad:
                problems.append(f"markets 含非法值 {bad}（只允许 HK/US/A）")

        url = it.get("url")
        if isinstance(url, str) and url.strip() and not url.strip().startswith("http"):
            problems.append(f"url 不是可点击链接: {url!r}")

        if problems:
            # v7：不再剔除。缺字段的条目照常发布，但打上标记让前端显示"字段缺失"，
            # 并给 why 补一个明确的占位——降级展示远好过整轮不发。
            it["_schema_issues"] = problems
            if not (isinstance(it.get("why"), str) and it["why"].strip()):
                it["why"] = "⚠ 本条缺少「为何相关」——Routine 输出字段异常，请核对 routine-prompt.md §6。"
            if not it.get("markets"):
                it["markets"] = []
            if not it.get("keywords"):
                it["keywords"] = []
            if it.get("tier") not in (1, 2, 3, "1", "2", "3"):
                it["tier"] = 3
            degraded.append((it, problems))
            # 注意：这里不能 continue —— 下面的可推导字段补齐（lang/time/group）
            # 对降级条目同样要跑，否则前端拿到的仍是残缺结构。补完统一进 out。

        # 4) 可推导字段自动补齐（不阻断）
        for f, default in AUTOFILL_DEFAULTS.items():
            if f not in it:
                it[f] = default
                print(f"  · [{it.get('id','?')}] 自动补 {f}={default!r}")
        if not it.get("lang"):
            it["lang"] = "zh" if _has_cjk(it.get("title", "")) else "en"
            print(f"  · [{it.get('id','?')}] 自动补 lang={it['lang']!r}")
        if not it.get("time"):
            it["time"] = now_bj.strftime("%H:%M")
            print(f"  · [{it.get('id','?')}] 自动补 time={it['time']!r}")

        out.append(it)

    # out 含全部条目（合格的 + 已修复标注的）；degraded 只是其中问题条目的索引
    return out, degraded

def is_stale_branch(existing_items, today_str):
    """陈旧分支保护（v5 新增）。

    如果现有历史里"最新"的 first_seen 本身已经比 KEEP_DAYS 还早，说明这批数据
    已经很久没有被追加更新过（分支/流水线曾经断更）。这种情况下如果照常按
    "first_seen < today - KEEP_DAYS 就丢弃"来剪枝，会把全部旧历史一次性清空
    ——这正是 2026-07-25 claude/radar-data 分支history被误删的原因。

    检测到这种情况时，本轮跳过按日期剪枝，只保留按 MAX_ITEMS 的数量上限裁剪，
    避免"断更很久 + 突然又跑通"的组合再次清空历史。
    """
    non_new = [i for i in existing_items if not i.get("is_new") and i.get("first_seen")]
    if not non_new:
        return False
    newest_first_seen = max(i["first_seen"] for i in non_new)
    try:
        gap_days = (datetime.strptime(today_str, "%Y-%m-%d")
                    - datetime.strptime(newest_first_seen, "%Y-%m-%d")).days
    except ValueError:
        return False
    return gap_days > STALE_BRANCH_GRACE_DAYS


# ── 事件级去重（v8 新增）────────────────────────────────────────────────────
#
# id 去重只挡"同一篇文章"；这里再挡"同一个事件被不同来源/不同天的文章反复报道"。
# 纯文本相似度，机械可判断，不依赖 Claude 主观标注，跑在脚本侧，不占用 Claude 的
# 上下文/token。
#
# 调参说明：单独用"标题相似度"或"keywords 重合"任何一个信号阈值放低都会大量
# 误伤——同一公司/同一板块的不同新闻常常共享 2-3 个 keyword（比如两条都带
# "英伟达/Nvidia/AI chip"，但其实一条是 CoreWeave 财报、一条是三星 HBM4），
# 单纯标题 Jaccard 在中文短标题上噪音也很大；单纯的百分比数字（"+2%""+3%"这种
# 常见涨跌幅）在几乎每条盘面新闻里都会出现，拿百分比重合当强信号会把"今天"和
# "另一天"的两篇大盘收评互相误判成同一事件。用真实数据（2026-08-17 从 main
# 分支的 84 条历史里挑出的已知重复 + 已知不重复样本）反复调出以下组合规则：
#   (a) 标题+摘要里能抽出的**金额类**数字（"2048亿""4990万""20亿美元"这类，
#       百分比不算）重合 >= 1 个——具体金额是很强的指纹，同一笔钱/同一个营收
#       数字不太可能巧合出现在两条无关新闻里。
#   (b) keywords 重合 >= 3 个，且标题+摘要 token/字符bigram Jaccard >= 0.12
#       ——既要标签像，也要正文用词有一定重叠，单独任一条件都不够。
#   (c) 标题+摘要 Jaccard >= 0.30 ——文本本身已经高度相似（改写幅度很小）。
# 满足以上任一条即判定为同一事件。

_STOPWORDS_EN = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are",
    "at", "by", "with", "from", "its", "as", "after", "before", "this", "that",
    "be", "will", "has", "have", "had", "was", "were", "it", "than", "into",
}

# keywords 字段里过于宽泛、几乎所有同板块新闻都会挂的标签，不计入 (b) 的重合计数
# ——否则"美国PPI报告"和"美国CPI报告"这种不同数据但都带"美联储/通胀/货币政策"
# 的新闻会被误判成同一事件；同理"港股收评"这种每天都发的模板标题也会靠"港股/
# 恒生指数"这类标签互相误判。
_GENERIC_KEYWORDS = {
    "宏观", "macro", "美联储", "fed", "通胀", "货币政策", "美股", "港股", "a股",
    "大盘", "市场", "股市", "涨跌", "收评", "午盘", "盘中",
}

TOPIC_NUMERIC_MIN_OVERLAP = 1   # 判据(a)：共享的金额类数字个数
TOPIC_KEYWORD_MIN_OVERLAP = 3   # 判据(b)：keywords 重合个数
TOPIC_KEYWORD_TITLE_MIN_JACCARD = 0.12  # 判据(b)：同时要求的最低标题相似度
TOPIC_TITLE_ONLY_THRESHOLD = 0.30       # 判据(c)：标题本身已高度相似

# 只抓金额类单位，不含 % ——百分比涨跌幅太常见，单独拿来比对噪音太大，
# 只在 (b) 的标题相似度里间接起作用。"亿元"/"万元" 归一化成 "亿"/"万"，
# 避免 "2048亿" 和 "2048亿元" 这种同一个数字、有无"元"字的写法被判成不同。
_NUM_RE = re.compile(
    r"(\d+\.?\d*)\s*(亿元|亿港元|亿美元|亿|万股|万港元|万美元|万元|万|美元|港元|倍)"
)
_NUM_UNIT_NORMALIZE = {"亿元": "亿", "万元": "万"}


def _tokenize(text):
    """把中英混合文本切成一个 token 集合，用于粗略的相似度比较。

    英文按单词切（过滤停用词、长度<=1的），中文按字符 bigram 切（没有分词器，
    但 bigram 对"腾讯Q2业绩" vs "腾讯二季度财报"这类同事件不同措辞有一定鲁棒性）。
    """
    text = (text or "").lower()
    words = re.findall(r"[a-z0-9]+", text)
    words = {w for w in words if len(w) > 1 and w not in _STOPWORDS_EN}
    cjk_segs = re.findall(r"[一-鿿]+", text)
    bigrams = set()
    for seg in cjk_segs:
        for i in range(len(seg) - 1):
            bigrams.add(seg[i:i + 2])
        if len(seg) == 1:
            bigrams.add(seg)
    return words | bigrams


def _numeric_signature(text):
    """抽取文本里"具体金额数字+单位"的集合（如 {'2048亿','4990万'}），
    单位做归一化（"2048亿元" 和 "2048亿" 视为同一个数字）。"""
    out = set()
    for m in _NUM_RE.finditer(text or ""):
        unit = _NUM_UNIT_NORMALIZE.get(m.group(2), m.group(2))
        out.add(m.group(1) + unit)
    return out


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _topic_signature(item):
    title = item.get("title", "")
    summary = item.get("summary", "")
    tokens = _tokenize(title) | _tokenize(summary)
    numbers = _numeric_signature(title) | _numeric_signature(summary)
    keywords = {
        str(k).strip().lower() for k in (item.get("keywords") or [])
        if str(k).strip() and str(k).strip().lower() not in _GENERIC_KEYWORDS
    }
    return tokens, numbers, keywords


def find_topic_duplicate(candidate, pool):
    """在 pool（已有条目）里找和 candidate 属于同一事件的条目；没有就返回 None。"""
    c_tokens, c_nums, c_kws = _topic_signature(candidate)
    for other in pool:
        if other is candidate:
            continue
        o_tokens, o_nums, o_kws = _topic_signature(other)
        title_jaccard = _jaccard(c_tokens, o_tokens)
        if len(c_nums & o_nums) >= TOPIC_NUMERIC_MIN_OVERLAP:
            return other
        if (len(c_kws & o_kws) >= TOPIC_KEYWORD_MIN_OVERLAP
                and title_jaccard >= TOPIC_KEYWORD_TITLE_MIN_JACCARD):
            return other
        if title_jaccard >= TOPIC_TITLE_ONLY_THRESHOLD:
            return other
    return None


def dedupe_topics(candidates, existing_items):
    """对 id 去重后仍待发布的候选，再做一次事件级去重。

    依次处理每条候选：先跟"已发布历史"比，再跟"本批次里已经通过的候选"比
    （防止同一批里搜到同一事件的两篇不同文章）。命中即丢弃。

    返回 (kept, dropped)，dropped 为 [(item, matched_item), ...]。
    """
    kept = []
    dropped = []
    pool = list(existing_items)
    for cand in candidates:
        match = find_topic_duplicate(cand, pool)
        if match:
            dropped.append((cand, match))
            continue
        kept.append(cand)
        pool.append(cand)
    return kept, dropped


def prune(items, today_str, skip_date_prune=False):
    """Drop items older than KEEP_DAYS (never drop is_new=True); trim to MAX_ITEMS.

    skip_date_prune=True（陈旧分支保护触发时）会跳过按日期丢弃这一步，只按
    MAX_ITEMS 数量上限裁剪，防止长期断更的分支一朝更新就被清空历史。
    """
    if not skip_date_prune:
        cutoff = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")
        # 1. Drop stale items (keep all is_new=True regardless)
        items = [i for i in items if i.get("is_new") or i.get("first_seen", "9999") >= cutoff]

    # 2. If still over limit, trim oldest low-tier items first
    for tier in [3, 2]:
        if len(items) <= MAX_ITEMS:
            break
        candidates = sorted(
            [i for i in items if not i.get("is_new") and i.get("tier") == tier],
            key=lambda x: x.get("first_seen", ""),
        )
        to_remove = {i["id"] for i in candidates[:len(items) - MAX_ITEMS]}
        items = [i for i in items if i["id"] not in to_remove]

    return items


def sort_items(items):
    tier_rank = {1: 0, 2: 1, 3: 2, "1": 0, "2": 1, "3": 2}
    return sorted(items, key=lambda x: (
        0 if x.get("is_new") else 1,
        tier_rank.get(x.get("tier", 3), 2),
        x.get("first_seen", ""),
    ))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        print("Error: GITHUB_TOKEN not set.", file=sys.stderr)
        sys.exit(1)

    # new_items.json lives next to this script
    here = os.path.dirname(os.path.abspath(__file__))
    new_items_path = os.path.join(here, "new_items.json")
    missing_input = False
    if not os.path.exists(new_items_path):
        # v7：不再 exit(1)。这里中止过一次就意味着整轮不发布，而这个文件是否存在
        # 取决于 Routine 当轮有没有写成功——不该由它决定用户能不能看到雷达。
        print(f"⚠ {new_items_path} 不存在，本轮按「0 条新增」处理并继续发布。", file=sys.stderr)
        new_items, missing_input = [], True
    else:
        try:
            with open(new_items_path, encoding="utf-8") as f:
                new_items = json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠ new_items.json 解析失败（{e}），本轮按「0 条新增」处理并继续发布。", file=sys.stderr)
            new_items, missing_input = [], True
    print(f"Loaded {len(new_items)} candidate new items from new_items.json")

    now_bj    = datetime.now(TZ_BJ)
    today_str = now_bj.strftime("%Y-%m-%d")
    updated_at = now_bj.strftime("%Y-%m-%d %H:%M") + " (北京时间)"

    # Schema 闸门（v7）：只修复与标注，绝不阻断发布。见 validate_item_schema 说明。
    candidate_count = len(new_items)
    new_items, degraded = validate_item_schema(new_items, now_bj)
    if degraded:
        print(f"\n⚠ Schema 降级 {len(degraded)}/{candidate_count} 条（仍会照常发布，并在页面上标记）：")
        for it, problems in degraded:
            print(f"  ! [{it.get('id','?')}] {str(it.get('title',''))[:40]}")
            for p in problems:
                print(f"      → {p}")

    # 发布日期硬性过滤（v4 新增）——见 validate_new_items 说明
    new_items, dropped = validate_new_items(new_items, today_str)
    if dropped:
        print(f"Validation dropped {len(dropped)} candidate(s):")
        for it, reason in dropped:
            print(f"  ✗ [{it.get('id','?')}] {it.get('title','')[:40]} → {reason}")

    # Fetch history from branch
    print("Fetching data.json …")
    data_json, data_sha = gh_get("data.json")
    print("Fetching seen.json …")
    seen_json, seen_sha = gh_get("seen.json")

    existing_items = (data_json or {}).get("items", [])
    seen_ids       = set((seen_json or {}).get("ids", []))

    # Deduplicate（id 级：同一篇文章）
    existing_ids = {i["id"] for i in existing_items}
    truly_new = [i for i in new_items if i.get("id") not in seen_ids and i.get("id") not in existing_ids]
    skipped = len(new_items) - len(truly_new)
    print(f"After id-dedup: {len(truly_new)} new, {skipped} skipped")

    # 事件级去重（v8 新增）：同一事件被不同来源/不同天的文章反复报道
    truly_new, topic_dupes = dedupe_topics(truly_new, existing_items)
    if topic_dupes:
        print(f"Topic-level dedup dropped {len(topic_dupes)} candidate(s) (same event already covered):")
        for it, matched in topic_dupes:
            print(f"  ⚠ [{it.get('id','?')}] {str(it.get('title',''))[:40]} "
                  f"≈ existing [{matched.get('id','?')}] {str(matched.get('title',''))[:40]}")
    print(f"After topic-dedup: {len(truly_new)} new, {len(topic_dupes)} dropped as duplicate events")

    # Stamp new items
    for item in truly_new:
        item.setdefault("first_seen", today_str)
        item["is_new"] = True

    # Mark existing items as old
    for item in existing_items:
        item["is_new"] = False

    # 陈旧分支保护（v5 新增）：现有历史很久没更新过时，本轮跳过按日期剪枝
    skip_date_prune = is_stale_branch(existing_items, today_str)
    if skip_date_prune:
        print(f"⚠ 检测到陈旧分支（现有历史最新 first_seen 距今超过 {STALE_BRANCH_GRACE_DAYS} 天），"
              f"本轮跳过按日期剪枝，只按 MAX_ITEMS={MAX_ITEMS} 裁剪，避免清空历史。")

    # Merge → prune → sort
    merged = prune(truly_new + existing_items, today_str, skip_date_prune=skip_date_prune)
    merged = sort_items(merged)

    # Update seen IDs（校验环节丢弃的候选也一并计入 seen，避免下一轮重复抓取/重复丢弃同一条）
    all_candidate_ids = ({i["id"] for i in new_items if i.get("id")}
                         | {i["id"] for i, _ in dropped if i.get("id")}
                         | {i["id"] for i, _ in degraded if i.get("id")}
                         | {i["id"] for i, _ in topic_dupes if i.get("id")})
    new_seen_ids = list(seen_ids | all_candidate_ids)
    if len(new_seen_ids) > 1000:
        new_seen_ids = new_seen_ids[-1000:]

    # Build output objects (preserve meta from existing data.json)
    meta = data_json or {}
    new_data = {
        "is_sample":  False,
        "updated_at": updated_at,
        "next_runs":  meta.get("next_runs", ["08:00", "13:00", "18:00"]),
        "watchlist":  meta.get("watchlist", []),
        "positions":  [],
        # 本轮运行元信息：让前端能区分「没新闻」和「管线坏了」——只看 updated_at
        # 是看不出来的，因为即使 0 新增 updated_at 也会前进。
        "last_run": {
            "at":          updated_at,
            "new_count":   len(truly_new),
            "degraded":    len(degraded),
            "input_missing": missing_input,
        },
        "items":      merged,
    }
    new_seen = {
        "updated_at": updated_at,
        "ids":        new_seen_ids,
    }

    # Publish
    date_tag = now_bj.strftime("%Y-%m-%d")
    local_output = "--local-output" in sys.argv
    if local_output:
        out_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"LOCAL OUTPUT mode — writing files to {out_dir}")
        gh_put_local("data.json", new_data, out_dir)
        gh_put_local("seen.json", new_seen, out_dir)
        gh_put_local("new_items.json",
                     [i for i in merged if i.get("is_new")],
                     out_dir)
    else:
        print("Publishing …")
        gh_put("data.json", new_data, data_sha,
               f"chore(radar): update market radar {date_tag} (+{len(truly_new)} items)")
        gh_put("seen.json", new_seen, seen_sha,
               f"chore(radar): update seen {date_tag}")

    print(f"\n✓ +{len(truly_new)} new | {len(existing_items)} existing | {len(merged)} total in data.json"
          + (f" | {len(dropped)} dropped by date-validation" if dropped else "")
          + (f" | {len(topic_dupes)} dropped as duplicate events" if topic_dupes else "")
          + (f" | {len(degraded)} degraded by schema-gate" if degraded else ""))

    # 注意退出码语义：非 0 只表示"有条目字段不全"，**数据已经成功发布**。
    # 绝不能因为这个提前 return / 跳过发布——v6 就是栽在这里，连停两天。
    if degraded:
        print(
            "\n" + "=" * 68
            + f"\n⚠ 本轮有 {len(degraded)} 条字段不全，已降级发布并在页面上标记。"
              "\n  请照 routine-prompt.md §6 核对 Routine prompt 的输出字段。"
              "\n  data.json 已成功写入；退出码 1 仅作告警。\n"
            + "=" * 68,
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
