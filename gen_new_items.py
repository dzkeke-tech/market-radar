#!/usr/bin/env python3
"""Generate new_items.json from researched candidates, deduped against seen.json."""
import json, hashlib

def make_id(url, title=""):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

with open('seen.json') as f:
    seen = json.load(f)
seen_ids = set(seen.get('ids', []))

candidates = [
    # ────────── 大盘头条 ──────────
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "07:00",
        "group": "大盘头条",
        "title": "SK Hynix Launches Record $28B Nasdaq Listing as HBM Shortage Locks In AI Memory Lead",
        "summary": (
            "SK Hynix officially kicked off its ~$28.13B Nasdaq IPO (ticker: SKHY), targeting July 10 "
            "trading start. 177.9M ADS priced at ~$158.14 each. If completed, this would be the largest "
            "US listing ever by a foreign company; proceeds earmarked for expanding HBM manufacturing capacity."
        ),
        "why": "HBM全球市占率约60%的SK海力士纳斯达克挂牌，募资规模创外资企业美股IPO历史纪录；直接改变DRAM/HBM板块竞争格局，需关注美光与SK海力士相对估值变化。",
        "source": "Fortune",
        "verified": True,
        "keywords": ["SK海力士", "SK Hynix", "HBM", "Nasdaq", "HBM4", "存储芯片"],
        "translated": False,
        "url": "https://fortune.com/2026/07/06/sk-hynix-ipo-stock-offer-nasdaq-29-billion-ai/",
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "12:30",
        "group": "大盘头条",
        "title": "港股午评：恒指涨2.38% 科指涨4.34% 科网股普涨 阿里巴巴涨超8%",
        "summary": (
            "7月8日午间，港股科技股全线走强，恒生科技指数涨4.34%，恒生指数涨2.38%。"
            "阿里巴巴涨超8%，联想集团涨超9%，腾讯、美团、小米等均录得明显涨幅。"
            "分析师指超跌、AI重估、资金回流、政策托底四重因素共振推动。恒生科技PE约20倍，处历史分位23.6%低位。"
        ),
        "why": "港股科技午间迎年内最强单日表现之一，持仓腾讯/阿里/美团/小米短期均显著正收益，隐含波动率或随之上升，可适时布局covered call落袋。",
        "source": "新浪财经",
        "verified": False,
        "keywords": ["港股", "恒生科技", "阿里巴巴", "腾讯", "美团", "小米", "联想"],
        "translated": False,
        "url": "https://finance.sina.com.cn/stock/hkstock/marketalerts/2026-07-08/doc-inihaicz1474533.shtml",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US", "HK"],
        "time": "09:00",
        "group": "大盘头条",
        "title": "Samsung Electronics shares fall as capex concerns outweigh strong Q2",
        "summary": (
            "Samsung preliminary Q2 2026 operating profit surged ~19-fold to KRW 89.4 trillion (~$58.4B), "
            "beating consensus of KRW 87.3T. The result exceeds Samsung's cumulative 2023-2025 profits in a "
            "single quarter. Yet the stock fell 6.9% in Seoul on concerns about capex commitments and demand "
            "sustainability, triggering a global memory chip selloff."
        ),
        "why": "三星创历史最佳业绩却大跌6.9%，市场担忧AI内存需求见顶与资本开支过剩；连锁触发美光、闪迪同日大跌约7%，存储板块整体波动率飙升，期权保护成本上升。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["三星", "Samsung", "HBM", "存储芯片", "DRAM", "半导体"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/07/samsung-electronics-preliminary-second-quarter-profit-hits-fresh-high.html",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK"],
        "time": "18:00",
        "group": "大盘头条",
        "title": "Beijing bolsters Hong Kong bond, gold trading in global yuan push",
        "summary": (
            "Beijing and Hong Kong jointly announced measures: Southbound Bond Connect quota raised from "
            "CNY 500B to CNY 800B; RMB Business Facility doubled to CNY 500B; HK launched gold central "
            "clearing system and revived gold futures trading; national FX reserves to increase HK asset "
            "allocation proportion going forward."
        ),
        "why": "人民币国际化提速，南向债券通扩额60%、双倍RMB融资工具利好港股整体流动性；黄金结算枢纽建设直接利好老铺黄金等相关资产，亦强化港股作为离岸金融中心的长期吸引力。",
        "source": "Reuters / MarketScreener",
        "verified": True,
        "keywords": ["港股", "离岸人民币", "黄金", "债券通", "老铺黄金", "南向"],
        "translated": False,
        "url": "https://www.marketscreener.com/news/beijing-bolsters-hong-kong-bond-gold-trading-in-global-yuan-push-ce7f5edbdf88f42c",
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["A", "HK"],
        "time": "09:00",
        "group": "大盘头条",
        "title": "6月末我国外汇储备规模34163亿美元",
        "summary": (
            "国家外汇管理局7月7日公布：截至2026年6月末，中国外汇储备规模为34163亿美元，"
            "较5月末减少260亿美元（-0.75%）。主因美元指数上升及全球主要金融资产价格涨跌互现，"
            "汇率折算和资产价格变化综合导致规模小幅下降。"
        ),
        "why": "外储小幅回落但仍处历史高位，美元强势阶段对南向资金流动影响有限；宏观整体稳健，对港股汇率风险影响中性。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["外汇储备", "宏观", "人民币", "美元"],
        "translated": False,
        "url": "https://finance.sina.com.cn/tech/roll/2026-07-08/doc-inihaawh8034720.shtml",
    },
    # ────────── 个股 ──────────
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK", "US"],
        "time": "05:00",
        "group": "个股",
        "title": "Alibaba wins court reprieve from Pentagon lobbying ban tied to DoD blacklist",
        "summary": (
            "A US federal judge granted Alibaba a 60-day reprieve from a lobbying ban after the Pentagon "
            "added Alibaba to the 1260H Chinese military companies list in June 2026, causing all 25+ "
            "registered lobbyists to drop the firm. The court will rule on constitutionality. Alibaba "
            "argues the restriction violates the First Amendment."
        ),
        "why": "阿里巴巴军事黑名单诉讼获临时缓冲，但60天内须等待最终裁决；若维持，将严重限制美国业务拓展，BABA/9988存在重大监管风险尾部，持仓须密切跟踪。",
        "source": "Bloomberg",
        "verified": True,
        "keywords": ["阿里巴巴", "Alibaba", "BABA", "9988.HK", "五角大楼", "监管"],
        "translated": False,
        "url": "https://www.bloomberg.com/news/articles/2026-07-05/alibaba-gets-reprieve-from-lobbying-ban-tied-to-pentagon-s-curbs",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "00:30",
        "group": "个股",
        "title": "Tesla (TSLA) Q2 2026 vehicle delivery production",
        "summary": (
            "Tesla reported 480,126 global deliveries in Q2 2026, +25% YoY, exceeding internal consensus "
            "of ~406K by 18% and growing 34% sequentially from Q1. Miami Robotaxi launched July 3 "
            "(city #4 after Dallas, Houston, Austin), operating without in-car safety monitors. "
            "Musk targets Robotaxi in ~12 states by year-end."
        ),
        "why": "交付量大超预期叠加Robotaxi全国扩张加速，TSLA正催化因素充分，隐含波动率高企；持仓可考虑Covered Call收割溢价，同时关注即将到来的季报指引。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["特斯拉", "Tesla", "TSLA", "Robotaxi", "FSD", "自动驾驶"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/02/tesla-tsla-q2-2026-vehicle-delivery-production.html",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "09:30",
        "group": "个股",
        "title": "Micron, SanDisk, and Western Digital Sink 7% as Samsung Earnings Spark a Memory Selloff",
        "summary": (
            "Micron (MU), SanDisk (SNDK) and Western Digital each fell ~7% on July 7 as Samsung's record "
            "Q2 profit paradoxically triggered a memory selloff on demand sustainability fears. Micron, "
            "Samsung and SK Hynix are all now down 20%+ from recent highs. Micron's own Q3 FY2026 "
            "revenue was $41.46B (+346% YoY) with Q4 guidance of $50B."
        ),
        "why": "美光和闪迪基本面极强但短期超卖（Q3营收$41.5B，Q4指引$50B）；大跌或为sell put入场时机，但须先确认存储周期是否见顶，行业资本开支风险不可忽视。",
        "source": "24/7 Wall St.",
        "verified": True,
        "keywords": ["美光", "Micron", "MU", "闪迪", "SanDisk", "SNDK", "存储", "内存", "HBM"],
        "translated": False,
        "url": "https://247wallst.com/investing/2026/07/07/micron-sandisk-and-western-digital-sink-7-as-samsung-earnings-spark-a-memory-selloff/",
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["HK"],
        "time": "08:00",
        "group": "个股",
        "title": "Tencent Bought Back 465,000 Shares For HK$204.8 Million On July 6, HKEX Filing Shows",
        "summary": (
            "Tencent repurchased 465,000 shares for HK$204.8M on July 6, per HKEX filing, marking the "
            "32nd consecutive trading day of buybacks with 34.5151M shares accumulated total. "
            "Shareholders approved a mandate for up to ~912M shares (10% of total) at the May 2026 AGM."
        ),
        "why": "腾讯连续32日回购创历史持续纪录，累计逾3400万股；管理层高置信度支撑股价下行保护，对sell put策略极为有利。",
        "source": "Reuters (via TradingView)",
        "verified": True,
        "keywords": ["腾讯", "Tencent", "0700.HK", "回购"],
        "translated": False,
        "url": "https://www.tradingview.com/news/reuters.com,2026:newsml_FWN43801M:0-tencent-bought-back-465-000-shares-for-hk-204-8-million-on-july-6-hkex-filing-shows/",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "18:00",
        "group": "个股",
        "title": "Google Loses EU Court Appeal Over 4.1 Billion Euro Android Antitrust Fine",
        "summary": (
            "The EU Court of Justice dismissed Google's final appeal against the 4.1B euro ($4.7B) "
            "Android antitrust fine on July 2, 2026, ending an 8-year legal battle. The court confirmed "
            "Google abused market dominance by requiring device makers to pre-install Search and Chrome "
            "to license the Play Store. The fine is now permanent; further third-party damages claims may follow."
        ),
        "why": "谷歌欧盟罚款最终落定（约$47亿现金出血），更大尾部风险是引发第三方竞争损害追偿；GOOGL监管风险溢价叠加美国DOJ反垄断诉讼，持仓须关注法律不确定性。",
        "source": "Bloomberg",
        "verified": True,
        "keywords": ["谷歌", "Google", "Alphabet", "GOOGL", "Android", "反垄断", "欧盟"],
        "translated": False,
        "url": "https://www.bloomberg.com/news/articles/2026-07-02/google-loses-eu-court-fight-over-4-1-billion-android-fine",
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "19:00",
        "group": "个股",
        "title": "快手可灵AI完成30亿美元融资，腾讯、阿里、百度罕见同台联投",
        "summary": (
            "快手旗下视频生成AI公司可灵AI（北京可灵智能）完成30亿美元外部融资，融前估值150亿美元、"
            "融后180亿美元，为全球视频生成AI领域有史以来最大单笔融资。腾讯、阿里巴巴、百度（BAT）"
            "史上首次共同参投同一项目。快手持股稀释至约68.33%，可灵继续并入快手报表。"
            "预计12个月内启动港股IPO。"
        ),
        "why": "腾讯和阿里同时参投可灵AI证明中国头部互联网对视频AI赛道极高确信度；港股IPO计划有望带动科技板块AI估值重估，腾讯/阿里的战略收益将体现于未来财报。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["快手", "可灵AI", "Kling", "腾讯", "阿里巴巴", "AI", "港股IPO"],
        "translated": False,
        "url": "https://finance.sina.com.cn/roll/2026-07-03/doc-inifqrwk3443647.shtml",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Intel to lay off up to 20% of Intel Foundry workers",
        "summary": (
            "Intel plans to cut up to 20% (10,000+) of Intel Foundry employees starting mid-July "
            "under CEO Lip-Bu Tan's refocus on engineering talent. Broader 2025-2026 restructuring "
            "has eliminated 25,000+ positions (from ~125K to under 100K). Ohio fab delayed to 2030; "
            "18A process running in Arizona for Google AI workloads."
        ),
        "why": "英特尔Foundry大幅收缩，代工战略短期难追台积电；对英伟达/台积电构成相对利好，INTC仓位不宜积极加仓，需等待代工业务真正企稳信号。",
        "source": "Yahoo Finance",
        "verified": True,
        "keywords": ["英特尔", "Intel", "INTC", "代工", "foundry", "晶圆代工", "18A"],
        "translated": False,
        "url": "https://finance.yahoo.com/news/intel-lay-off-20-intel-175032169.html",
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US", "HK"],
        "time": "08:00",
        "group": "个股",
        "title": "EU Package Fee from 1 July 2026: New Customs Rules Hit Temu, Shein and European E-Commerce",
        "summary": (
            "From July 1, 2026, the EU levies a flat 3-euro fee per tariff classification on all packages "
            "imported from non-EU countries and abolishes the previous 150-euro customs exemption. "
            "This directly hits Temu, Shein and AliExpress which relied on direct-from-China shipping. "
            "Temu also faces a separate 200M-euro EU fine from May 2026 for illegal products."
        ),
        "why": "欧盟跨境包裹税正式生效，直接压缩Temu欧洲业务盈利空间；叠加5月违规罚款2亿欧元，PDD出海战略面临双重合规压力，期权策略宜保持谨慎。",
        "source": "E-Commerce Institute Cologne",
        "verified": True,
        "keywords": ["拼多多", "PDD", "Temu", "阿里巴巴", "跨境电商", "出海"],
        "translated": False,
        "url": "https://ecommerceinstitut.de/eu-package-fee-from-1-july-2026-what-the-new-customs-rules-mean-for-temu-shein-and-european-e-commerce/",
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Standard Chartered and Circle launch first G-SIB-led integrated access to USDC minting and redemption",
        "summary": (
            "Standard Chartered became the first Global Systemically Important Bank (G-SIB) to offer "
            "institutional clients integrated USDC minting and redemption via partnership with Circle "
            "(announced July 2). Available via Standard Chartered's DIFC operations; institutions access "
            "USDC without needing direct Circle accounts."
        ),
        "why": "全球系统重要性银行首次接入USDC是里程碑，大幅提升Circle机构合规形象；GENIUS Act框架下稳定币业务护城河加深，CRCL是稳定币机构化加速的最直接受益者。",
        "source": "Circle (official press release)",
        "verified": True,
        "keywords": ["Circle", "CRCL", "USDC", "稳定币", "stablecoin", "GENIUS Act"],
        "translated": False,
        "url": "https://www.circle.com/pressroom/standard-chartered-and-circle-launch-launch-first-g-sib-led-integrated-access-to-usdc-minting-and-redemption",
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["HK"],
        "time": "10:00",
        "group": "个股",
        "title": "Tencent Hunyuan Officially Releases Hy3, Advancing Agent Capabilities and Deeper Product Integration",
        "summary": (
            "Tencent officially launched Hunyuan Hy3 with significantly enhanced Agent capabilities, "
            "completing the full model-development loop from infrastructure rebuild in January 2026 "
            "to Hy3 preview in April to full release. Deeply integrated into Yuanbao app for "
            "complex multi-step autonomous tasks and file generation (PPT, Word, Excel, PDF, HTML)."
        ),
        "why": "腾讯元宝AI Agent能力大幅升级，提升用户粘性和商业化潜力；混元Hy3是今日港股科技涨势的重要催化之一，腾讯AI生态竞争地位进一步巩固。",
        "source": "Tencent (official)",
        "verified": True,
        "keywords": ["腾讯", "Tencent", "0700.HK", "混元", "Hunyuan", "AI", "元宝"],
        "translated": False,
        "url": "https://www.tencent.com/en-us/articles/2202386.html",
    },
]

# Assign IDs
for it in candidates:
    it["id"] = make_id(it["url"], it["title"])

# Deduplicate against seen.json
fresh = [it for it in candidates if it["id"] not in seen_ids]
dupes = len(candidates) - len(fresh)

print(f"Candidates: {len(candidates)}, already-seen (pre-filtered): {dupes}, fresh: {len(fresh)}")
for it in fresh:
    status = "[NEW]"
    print(f"  {status} [{it['tier']}] {it['id']} | {it['title'][:65]}")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(fresh, f, ensure_ascii=False, indent=2)
print(f"\nnew_items.json written with {len(fresh)} items.")
