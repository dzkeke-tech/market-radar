import json, hashlib

def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

candidates = [
    # ===== 大盘头条 =====
    {
        "tier": 1, "lang": "zh", "markets": ["A"], "time": "07:00", "group": "大盘头条",
        "title": "A股交易新规7月6日正式施行：主板ST股涨跌幅上限由5%提至10%，盘后固定价格交易扩至全A",
        "summary": "沪深北交易所修订版交易规则今日正式落地，三大变化：主板ST/*ST股涨跌幅扩至10%、盘后固定价格交易（15:05–15:30）由科创板扩展至全部A股及ETF、基金收盘交易改为收盘集合竞价。超150只股票受影响。证监会同步拟建立储架发行制度，优化小额快速融资机制。",
        "why": "ST股弹性加大、盘后交易便利性提升，短期增加相关个股波动率；期权卖方需注意新规下结算价变化机制对持仓的影响。",
        "source": "证券时报",
        "verified": True,
        "keywords": ["A股", "交易规则", "ST股", "盘后交易", "监管", "再融资"],
        "translated": False,
        "url": "https://www.stcn.com/article/detail/3998955.html"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US", "HK"], "time": "02:00", "group": "大盘头条",
        "title": "Fed holds rates at 3.5-3.75% for 4th straight meeting; flags persistent inflation and Middle East supply risks",
        "summary": "The FOMC voted unanimously on June 17 to keep the fed funds target at 3.5-3.75%, its fourth consecutive hold. The statement flagged inflation still elevated partly due to Middle East-driven energy shocks, with productivity growth strong and the labour market in balance. Policy commentary explicitly pushes back on near-term rate-cut expectations.",
        "why": "Higher-for-longer延续，Sell Put期权premium维持高位；港股HKD挂钩美元，美国利率预期直接左右资金流向。",
        "source": "Federal Reserve",
        "verified": True,
        "keywords": ["Fed", "利率", "宏观", "通胀", "Higher for longer", "FOMC"],
        "translated": False,
        "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "12:00", "group": "大盘头条",
        "title": "Tesla Q2 2026: 480,126 deliveries crushed estimates by 74K (+25% YoY), yet stock fell ~6.5%",
        "summary": "Tesla produced 451,758 and delivered 480,126 vehicles in Q2 2026, smashing Wall Street consensus of ~406K units. Model 3/Y accounted for 467,762 deliveries; energy storage hit 13.5 GWh. Despite the beat, stock dropped ~6.5% — prior 11% rally, US demand concerns, and margin questions weighed.",
        "why": "交付大幅超预期但股价反跌，典型买预期卖事实；Robotaxi扩张带来高波动率，卖put需审慎选择行权价与到期日，等Q2财报（7月22日）后再评估。",
        "source": "Tesla Investor Relations",
        "verified": True,
        "keywords": ["Tesla", "TSLA", "交付", "Robotaxi", "自动驾驶", "特斯拉"],
        "translated": False,
        "url": "https://ir.tesla.com/press-release/tesla-second-quarter-2026-production-deliveries-and-deployments"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "09:00", "group": "大盘头条",
        "title": "Micron breaks ground on $9.3B Hiroshima HBM fab expansion backed by $4.8B Japanese government subsidy",
        "summary": "Micron held a July 4 groundbreaking ceremony in Higashi-Hiroshima for a major expansion targeting HBM and advanced memory production. Commercial shipments expected around summer 2028. Japan has committed roughly ¥775B (~$4.8B) in total subsidies to Micron to date.",
        "why": "美光HBM产能大幅扩充锁定长期AI存储需求，2028年投产后将强化HBM4竞争地位；对美光持仓估值有长期正面支撑，亦印证HBM供给仍是AI基础设施瓶颈。",
        "source": "Japan Times",
        "verified": True,
        "keywords": ["Micron", "美光", "HBM", "日本", "存储芯片", "AI芯片"],
        "translated": False,
        "url": "https://www.japantimes.co.jp/business/2026/07/04/tech/micron-hiroshima-chip-plant/"
    },
    {
        "tier": 2, "lang": "zh", "markets": ["A"], "time": "07:30", "group": "大盘头条",
        "title": "A股上半年首批业绩预告：69家披露，62家预喜（约90%），消费与科技领跑",
        "summary": "截至7月5日21时，A股69家上市公司披露2026年上半年业绩预告，其中62家预喜（预增/扭亏/续盈），预喜率约90%。四大证券报7月6日头条显示景气集中在消费升级和科技赛道。",
        "why": "开局预喜率高为A股消费+科技持仓提供基本面支撑，但总量尚少，8月中报密集披露期才是关键验证窗口。",
        "source": "新浪财经（四大证券报摘要）",
        "verified": False,
        "keywords": ["A股", "业绩预告", "半年报", "消费", "科技", "中报"],
        "translated": False,
        "url": "https://finance.sina.com.cn/stock/y/2026-07-06/doc-inifvkkf8791035.shtml"
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "08:00", "group": "大盘头条",
        "title": "Alphabet joins Dow Jones 30, replacing Verizon; Gemini paying subscribers hit 350M but compute-constrained",
        "summary": "Google's parent Alphabet has been added to the Dow Jones Industrial Average, joining Apple, Microsoft, Amazon and Nvidia. Q1 2026 cloud revenue hit $20B (+63% YoY), Gemini Enterprise paying MAUs grew 40% QoQ to 350M total paid subscriptions. CEO Sundar Pichai flagged compute constraints limiting cloud upside.",
        "why": "纳入道琼斯扩大被动资金买入规模；Gemini算力瓶颈意味着收入上行弹性受供给约束，关注$180-190B年度资本开支能否加速落地，是GOOGL卖put的隐含波动率定价依据。",
        "source": "MarketWise",
        "verified": False,
        "keywords": ["谷歌", "Alphabet", "GOOGL", "道琼斯", "Gemini", "Google Cloud", "AI"],
        "translated": False,
        "url": "https://marketwise.com/investing/alphabet-dow-gemini-capacity-constrained/"
    },

    # ===== 个股 =====
    {
        "tier": 1, "lang": "zh", "markets": ["HK"], "time": "08:30", "group": "个股",
        "title": "腾讯加速大规模回购（6月以来几乎每天），股东大会批准10%授权；微信AI助手内测启动",
        "summary": "腾讯5月13日股东大会批准回购约9.12亿股（约10%股本）。6月以来几乎每日回购，6月15日单日耗资51亿港元（108万股，价格458-475.6港元）。此外腾讯已开始在微信内测AI助手，目标追赶国内AI竞争对手，将AI融入10亿用户核心应用。",
        "why": "大规模持续回购是管理层对当前股价的看涨信号，减少流通股对EPS有正向作用；微信AI助手若顺利推出将打开新变现空间，是卖covered call时机的参考信号。",
        "source": "Yahoo Finance (Bloomberg报道)",
        "verified": False,
        "keywords": ["腾讯", "Tencent", "0700.HK", "回购", "WeChat", "微信", "AI"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/stocks/articles/tencent-ramps-buybacks-share-rout-002809157.html"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "10:00", "group": "个股",
        "title": "Nvidia launches RAISE: revenue-sharing model finances AI cloud startups, 210,000 Grace Blackwell GPUs deployed",
        "summary": "Nvidia announced July 1 the RAISE program, backstopping GPU infrastructure builds by capital-constrained cloud operators in exchange for a recurring share of future cloud revenue. First partners Sharon AI and Firmus plan up to 210,000 GB300 Grace Blackwell GPUs. CFO Colette Kress detailed the model on the Nvidia blog.",
        "why": "RAISE是Nvidia从硬件销售商向AI基础设施平台运营商的战略延伸，打开长期经常性收入；同时增加资产负债表风险，期权市场IV可能因商业模式拓展而重新定价，持仓基本面更稳健。",
        "source": "Nvidia Blog",
        "verified": True,
        "keywords": ["英伟达", "Nvidia", "NVDA", "GPU", "AI芯片", "Blackwell", "数据中心"],
        "translated": False,
        "url": "https://blogs.nvidia.com/blog/nvidia-unlocks-ai-compute-at-scale-capital-partners-to-power-ai-infrastructure-buildout/"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "06:30", "group": "个股",
        "title": "Tesla Robotaxi expands to Miami — first unsupervised commercial deployment outside Texas (July 3)",
        "summary": "Tesla launched driverless ride-hailing in a 10-14 sq-mile zone in western Miami-Dade on July 3, marking its first autonomous commercial deployment outside Texas. The expansion tests camera-only FSD in tropical heat, sudden downpours, and intense glare — conditions at the center of an active NHTSA investigation into failure in degraded visibility.",
        "why": "Robotaxi地域扩展是特斯拉FSD变现路径的关键里程碑；但NHTSA摄像头雨天失效调查悬而未决，短期事件风险较高；卖put应注意行权价与Robotaxi催化剂时间的匹配。",
        "source": "Not a Tesla App",
        "verified": True,
        "keywords": ["Tesla", "TSLA", "Robotaxi", "FSD", "自动驾驶", "特斯拉"],
        "translated": False,
        "url": "https://www.notateslaapp.com/news/4394/tesla-launches-unsupervised-robotaxi-rides-in-miami"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "08:00", "group": "个股",
        "title": "Micron Q3 FY2026 record results: ~$33.5B revenue guidance, 81% gross margin; $0.15 dividend record date TODAY (July 6)",
        "summary": "Micron reported record Q3 FY2026 on June 24: ~$33.5B revenue guidance, 81% gross margin, >$19 EPS. HBM4 for Nvidia Vera Rubin is ramping at 2x the pace of HBM3E with better-than-expected yields. Board declared $0.15 quarterly dividend; record date is close of business July 6 (today), payable July 21. Micron also signed a multi-year AI infrastructure partnership with Anthropic as primary memory supplier.",
        "why": "今日为美光分红登记日，持有者须在收盘前持股以获本期分红；$33.5B营收指引+HBM4良率超预期，Anthropic战略合作锁定长期需求，基本面强劲支撑MU卖put策略。",
        "source": "Micron Investor Relations",
        "verified": True,
        "keywords": ["美光", "Micron", "MU", "HBM", "HBM4", "DRAM", "存储", "分红"],
        "translated": False,
        "url": "https://investors.micron.com/news-releases/news-release-details/micron-technology-inc-reports-record-results-third-quarter"
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "09:00", "group": "个股",
        "title": "Palantir's Foundry selected as US Army NGC2 cloud data layer — Army's top modernization priority; Palantir-Nvidia Sovereign AI deal signed",
        "summary": "Palantir's Foundry platform was selected as the cloud data layer for the US Army's Next Generation Command and Control (NGC2), the Army's highest-priority modernization initiative. Within the architecture Palantir handles cloud data; Anduril's Lattice covers the tactical layer. Separately, Palantir and Nvidia announced a partnership deploying AI models in secure sovereign environments for US government and critical infrastructure. Q1 2026 revenue rose 85% YoY to $1.633B.",
        "why": "NGC2是美军最高优先级现代化项目，Foundry成数据骨干是Palantir政府业务护城河的最强体现；Nvidia Sovereign AI合作拓展商业边界；Q1 +85%增速强化卖put的基本面支撑。",
        "source": "Insider Monkey",
        "verified": False,
        "keywords": ["Palantir", "PLTR", "AIP", "Foundry", "国防AI", "政府合同"],
        "translated": False,
        "url": "https://www.insidermonkey.com/blog/the-us-army-just-made-palantir-pltr-foundry-the-data-backbone-of-its-biggest-tech-overhaul-1790836/"
    },
    {
        "tier": 1, "lang": "en", "markets": ["HK"], "time": "07:00", "group": "个股",
        "title": "SK hynix ships HBM4E samples to customers: 12-layer 48GB, 4 TB/s bandwidth, +17% heat resistance vs HBM4",
        "summary": "SK hynix announced June 18 it began shipping HBM4E samples to major customers. Using Advanced MR-MUF technology, the product achieves 48GB capacity in 12 layers, 16Gbps per-pin, 4 TB/s peak bandwidth, and >20% better power efficiency vs HBM4. SK hynix is projected to hold ~70% HBM4 market share for Nvidia's Rubin platform.",
        "why": "HBM4E样品领先出货确立SK海力士在Nvidia Rubin代供应链中的地位；对南方两倍做多SK海力士ETP（7709.HK）有直接基本面支撑，HBM4E下游客户验证节奏决定明年量产预期。",
        "source": "SK Hynix Newsroom",
        "verified": True,
        "keywords": ["SK海力士", "SK Hynix", "HBM", "HBM4E", "存储芯片", "高带宽内存"],
        "translated": False,
        "url": "https://news.skhynix.com/12-layer-hbm4e-sample/"
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "08:00", "group": "个股",
        "title": "Intel 18A-P enters risk production: +9% perf or -18% power vs 18A; 18A-PT adds Foveros Direct 3D hybrid bonding",
        "summary": "Intel announced at VLSI Symposium (June 16) that Intel 18A-P entered risk production on schedule. It delivers 9% higher performance at iso-power (or 18% lower power at iso-performance) vs 18A, with 20-40% improved thermal resistance. 18A-PT extends this with <5um hybrid bonding pitch. Fab 52 in Arizona has run its first wafer; volume production starts in Oregon then Arizona.",
        "why": "18A-P商业化是Intel代工业务扭亏的关键节点，若年底量产将显著改善对Intel Foundry的估值预期；18A-PT先进封装路径具有战略意义，是INTC中长期估值重估催化剂。",
        "source": "Intel Investor Relations",
        "verified": True,
        "keywords": ["英特尔", "Intel", "INTC", "18A", "foundry", "晶圆代工", "CPU"],
        "translated": False,
        "url": "https://www.intc.com/news-events/press-releases/detail/1772/intel-foundry-details-process-milestones-and-future"
    },
    {
        "tier": 2, "lang": "en", "markets": ["HK"], "time": "07:00", "group": "个股",
        "title": "Pop Mart 'The Monsters 10th Anniversary World Tour' opens in NYC July 17-Aug 31; Labubu's US debut",
        "summary": "Following stops in Shanghai, Taipei, Hong Kong, Paris and Tokyo, Pop Mart's immersive 10th-anniversary exhibition for The Monsters opens in New York City July 17 through August 31 — the first US appearance of character Lung. Nine themed galleries trace the origins of Labubu, Zimomo and Tycoco.",
        "why": "北美展览是泡泡玛特出海的里程碑，提升Labubu在全球最大消费市场的品牌认知；结合FIFA世界杯联名效应，支撑9992.HK海外收入估值，软新闻亦有助降低期权隐含波动率。",
        "source": "Las Vegas Sun News",
        "verified": True,
        "keywords": ["泡泡玛特", "Pop Mart", "Labubu", "The Monsters", "9992.HK", "潮玩", "出海"],
        "translated": False,
        "url": "https://lasvegassun.com/news/2026/jul/01/labubu-takes-over-nyc-pop-mart-celebrates-the-mons/"
    },
    {
        "tier": 2, "lang": "zh", "markets": ["HK"], "time": "06:00", "group": "个股",
        "title": "Labubu登场2026 FIFA世界杯开幕式（6月12日）——泡泡玛特品牌史上最大破圈事件",
        "summary": "6月12日，两只巨型Labubu（蓝色和棕色）现身2026 FIFA世界杯开幕式球场。这是泡泡玛特IP在全球最大体育赛事上的首次亮相，FIFA联名系列（含盲盒、挂件、球衣款毛绒玩偶）已全线上市并反复补货。",
        "why": "逾35亿观众的世界杯开幕式曝光大幅提升Labubu国际认知度；FIFA联名产品持续补货意味着Q2-Q3营收催化，直接利好9992.HK出海估值。",
        "source": "TechNode",
        "verified": True,
        "keywords": ["泡泡玛特", "Labubu", "FIFA", "世界杯", "Pop Mart", "9992.HK", "出海", "破圈"],
        "translated": False,
        "url": "https://technode.com/2026/06/12/pop-mart-labubu-makes-a-surprise-appearance-at-the-2026-fifa-world-cup-opening-ceremony/"
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "09:00", "group": "个股",
        "title": "Fed proposes stablecoin issuer rules; Circle (CRCL) USDC positioned as biggest potential beneficiary",
        "summary": "Following the GENIUS Act (signed July 2025), the Federal Reserve proposed a regulatory framework governing payment stablecoin issuers. USDC was already GENIUS-compliant in substance. Analysts note FRB rules combined with SEC broker-dealer alignment and FIS partnership give USDC institutional advantages that competitors are scrambling to match.",
        "why": "稳定币监管明确加固Circle/USDC合规护城河；GENIUS Act框架已奠定USDC先发优势，监管清晰化通常对隐含波动率有压缩效应，利于CRCL持仓的卖put策略。",
        "source": "Yahoo Finance",
        "verified": False,
        "keywords": ["Circle", "CRCL", "USDC", "稳定币", "stablecoin", "GENIUS Act", "稳定币法案"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/crypto/articles/circle-crcl-faces-fed-stablecoin-010923003.html"
    },
    {
        "tier": 2, "lang": "zh", "markets": ["HK", "US"], "time": "09:30", "group": "个股",
        "title": "阿里通义千问Qwen3.7-Max在Arena AI评分首超GPT-5.5（1284 vs 1215），开源下载量破7亿",
        "summary": "阿里云5月于云峰会发布Qwen3.7系列。Qwen3.7-Max-Preview（万亿参数MoE架构）在Arena AI评测中以1284分首次超越GPT-5.5（1215分）。Qwen系列全球累计下载量超7亿次，开发者采用量断层领先；阿里云同步推出多模态开发套件及夜间计划折扣定价，阿里巴巴-W 6月30-7月1日回购约1亿美元股票。",
        "why": "Qwen竞争力上升支撑阿里云AI变现预期；管理层连续回购体现对股价的信心，是9988.HK/BABA卖put策略基本面支撑信号，关注Q2云收入增速。",
        "source": "阿里云开发者社区",
        "verified": False,
        "keywords": ["阿里巴巴", "阿里云", "BABA", "通义千问", "Qwen", "9988.HK", "AI", "回购"],
        "translated": False,
        "url": "https://zhuanlan.zhihu.com/p/2048143817132486785"
    },
]

# Load seen IDs (use local seen.json — most up-to-date after 08:18 run)
with open("seen.json") as f:
    raw_ids = json.load(f)["ids"]

# Build full-length set AND a prefix set (12-char) to catch older shorter-hash IDs
seen_ids = set(raw_ids)
seen_prefixes = {i[:12] for i in seen_ids}

# Compute IDs and filter
new_items = []
skipped = []
for item in candidates:
    iid = make_id(item["url"], item["title"])
    item["id"] = iid
    if iid in seen_ids or iid[:12] in seen_prefixes:
        skipped.append((iid, item["title"][:50]))
    else:
        new_items.append(item)

print(f"Total candidates: {len(candidates)}")
print(f"New (not in seen): {len(new_items)}")
print(f"Skipped (already seen): {len(skipped)}")
for sid, stitle in skipped:
    print(f"  SKIP {sid}: {stitle}")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(new_items, f, ensure_ascii=False, indent=2)

print("\nnew_items.json written.")
