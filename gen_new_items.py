#!/usr/bin/env python3
import json, hashlib

def make_id(url, title=""):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

raw = [
    # ══════ 大盘头条 ══════
    {
        "tier": 1, "lang": "en", "markets": ["US","HK","A"], "time": "08:00", "group": "大盘头条",
        "title": "Brent Crude Tops $90 as US-Iran Conflict Escalates, Hormuz Shipping Disrupted",
        "summary": "Brent crude surged 3% to $90.79/barrel on July 20 as the US and Iran exchanged strikes for a ninth consecutive night. Shipping through the Strait of Hormuz fell to four vessels Sunday from eight the prior day, raising energy supply disruption fears.",
        "why": "布伦特破$90直接拉高通胀预期，加大美联储9月加息概率；对成长科技持仓Sell Put选手需关注隐含波动率上行风险，能源成本压力亦传导至消费赛道。",
        "source": "CNBC", "verified": True, "translated": False,
        "keywords": ["oil","Brent","Iran","Strait of Hormuz","geopolitical"],
        "url": "https://www.cnbc.com/2026/07/20/oil-prices-today-brent-wti-crude-us-iran-centcom-hormuz.html",
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "09:00", "group": "大盘头条",
        "title": "30-Year Treasury Yield at 5.06%; Bond Market Signals 64% Odds of September Fed Rate Hike",
        "summary": "The 30-year Treasury yield stood at 5.06% as of July 19, near pre-2008-crisis highs. The 6-month yield sits 30bp above the Fed Funds rate. Markets now price a 64% probability of a September rate hike as oil-driven inflation expectations rise following the Iran conflict escalation.",
        "why": "长端利率企稳5%以上压缩成长股估值倍数；美联储9月加息预期若进一步升温，将对Sell Put行权价安全边际形成系统性考验，适合在7月29日FOMC前降低delta敞口。",
        "source": "Wolf Street", "verified": False, "translated": False,
        "keywords": ["Treasury","yield","Fed","rate hike","inflation","5%"],
        "url": "https://wolfstreet.com/2026/07/19/30-year-treasury-yield-still-5-06-30-year-tips-yield-highest-since-2010-reintroduction-yield-curve-prepped-for-rate-hike-this-year/",
    },
    {
        "tier": 1, "lang": "en", "markets": ["A","HK"], "time": "16:00", "group": "大盘头条",
        "title": "China Stocks Tumble: Shanghai -3%, Shenzhen -5.4% as CXMT's $8.6B IPO Stirs Liquidity Panic",
        "summary": "Shanghai Composite plunged 3.05% to near 11-month low of 3,764 on July 17; Shenzhen Component fell 5.4%. Investors fear CXMT's 57.9bn-yuan ($8.6B) STAR Market IPO will drain market liquidity, compounded by upcoming mega-IPOs from Unitree and Yangtze Memory Technologies.",
        "why": "A股流动性恐慌直接拖累港股情绪，本周港股互联网板块（腾讯、阿里、美团等）可能承压；CXMT 7月27日挂牌前后是关键观察窗口。",
        "source": "Business Recorder", "verified": True, "translated": False,
        "keywords": ["A股","上证","深成指","CXMT","IPO","流动性","科创板"],
        "url": "https://www.brecorder.com/news/40430501/china-stocks-tumble-as-cxmts-86-billion-ipo-stirs-liquidity-concerns",
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "22:00", "group": "大盘头条",
        "title": "US Stocks Post Worst Week in Three Months: Nasdaq -2.9%, S&P 500 -1.6% on AI Capex Slowdown Fears",
        "summary": "The Nasdaq lost 2.9% and the S&P 500 fell 1.6% for the week ending July 17 — the worst weekly performance in three months. Chip stocks led declines (Nvidia -2.2%, AMD -1%, Intel -2%) on concerns AI hyperscalers may cut infrastructure spending.",
        "why": "AI基建投入收缩传闻触发芯片板块系统性下跌，直接影响英伟达、英特尔、美光等持仓；本周Q2财报季（特斯拉、谷歌、英特尔）是情绪能否修复的关键观察窗口。",
        "source": "Washington Post", "verified": True, "translated": False,
        "keywords": ["Nasdaq","S&P 500","chip stocks","AI","semiconductor","weekly decline"],
        "url": "https://www.washingtonpost.com/business/2026/07/17/wall-street-stocks-dow-nasdaq/64463f38-821d-11f1-8a16-393bd03340b0_story.html",
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "09:30", "group": "大盘头条",
        "title": "Fed Seen on Hold at July 29 FOMC but September Hike Odds Climb; Core PCE Stays at 3.3%",
        "summary": "The FOMC meets July 28-29 and is expected to leave rates at 3.5%-3.75%. However, persistent inflation (PCE 3.6%, core PCE 3.3%) and hawkish signals from Chair Kevin Warsh have pushed CME FedWatch September hike odds to 46.5%, with broader market estimates reaching 64-65%.",
        "why": "7月底FOMC结果与9月加息预期演变是近期最重要宏观变量，直接决定成长股和债市估值中枢；建议在7月29日前关注通胀数据与官员讲话以动态调整仓位。",
        "source": "CNBC", "verified": False, "translated": False,
        "keywords": ["Fed","FOMC","rate hike","PCE","inflation","Kevin Warsh","July 29"],
        "url": "https://www.cnbc.com/2026/07/13/-a-july-rate-hike-from-the-fed-the-odds-are-rising.html",
    },
    {
        "tier": 1, "lang": "en", "markets": ["A"], "time": "10:00", "group": "大盘头条",
        "title": "CXMT Prices $8.6B Shanghai IPO — Asia's Largest of 2026; STAR Market Listing Set for July 27",
        "summary": "ChangXin Memory Technologies (CXMT) priced its Shanghai IPO at 8.66 yuan/share, raising 57.9 billion yuan ($8.6B) — the largest A-share semiconductor offering ever and Asia's biggest IPO of 2026. Subscription was oversubscribed 200x+ though at a lower pace than typical Chinese IPOs. Listing date: July 27.",
        "why": "CXMT上市是中国DRAM国产化战略标志性事件，对美光、SK海力士构成中长期竞争威胁；抽血A股流动性短期拖累科技板块，7月27日挂牌后存储芯片股波动可能加剧。",
        "source": "Bloomberg", "verified": True, "translated": False,
        "keywords": ["CXMT","DRAM","A股","科创板","IPO","ChangXin","存储芯片","中国半导体"],
        "url": "https://www.bloomberg.com/news/articles/2026-07-14/cxmt-prices-shanghai-star-board-ipo-at-8-66-yuan-per-share",
    },
    # ══════ 个股 ══════
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "21:00", "group": "个股",
        "title": "Tesla Q2 2026: Record 480,126 EV Deliveries (+25% YoY, Beat by 74K); Q2 Earnings Call July 22",
        "summary": "Tesla delivered 480,126 vehicles in Q2 2026 — its best quarter ever — beating Wall Street's ~406,000 forecast by ~74,000. Energy storage deployments reached 13.5 GWh (+53% QoQ). Full Q2 earnings release and Musk call scheduled July 22 after market close; analysts expect revenue of ~$26.1B and focus on gross margins and Cybercab progress.",
        "why": "创纪录交付提振基本面；但连续四季利润率未达预期，7月22日财报带来方向性大波动。Sell Put选手需在发布前重新评估行权价安全边际，关注毛利率与FSD收入兑现情况。",
        "source": "Tesla Investor Relations", "verified": True, "translated": False,
        "keywords": ["Tesla","TSLA","deliveries","Q2","earnings","Cybercab","FSD","energy storage"],
        "url": "https://ir.tesla.com/press-release/tesla-second-quarter-2026-production-deliveries-and-deployments",
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "10:00", "group": "个股",
        "title": "Nvidia Implements 'Whitelist' for Asian AI Chip Buyers; Over Half of Customers Cut Under BIS Compliance",
        "summary": "Nvidia deployed a new customer whitelist system for Asian AI chip sales on July 14, sending field staff to inspect data centers and interview end-users. Over half of previous Asian buyers have failed the enhanced BIS-aligned compliance checks. The system targets Singapore, Malaysia, and Japan to prevent chip diversion to China.",
        "why": "英伟达主动缩减亚洲合规客户相当于自我限量，短期影响亚洲订单；但Blackwell/Rubin产能被顶级云客户吃满，长期减少监管风险。持有NVDA需关注下季度亚洲渠道订单变化。",
        "source": "Yahoo Finance", "verified": True, "translated": False,
        "keywords": ["Nvidia","NVDA","whitelist","export controls","AI chip","BIS","compliance","Asia"],
        "url": "https://finance.yahoo.com/technology/ai/articles/nvidia-tightens-asian-customer-approvals-105148051.html",
    },
    {
        "tier": 1, "lang": "en", "markets": ["US"], "time": "09:30", "group": "个股",
        "title": "Alphabet Q2 Earnings July 22: $117B Revenue Forecast; Google Cloud at Record $20B Run Rate",
        "summary": "Alphabet reports Q2 2026 on July 22 after market close. Consensus: revenue $117B (+21% YoY), EPS $2.88. Key focus: Google Cloud (Q1: +63% YoY to $20B, record 32.9% op margin), $462B cloud backlog, Gemini 3.5 Pro delays, and EU Android antitrust headwinds.",
        "why": "谷歌是本周最重量级财报之一（与特斯拉同日），Cloud增速若维持60%+将强化AI投资回报叙事；Gemini延迟是下行风险。结果可能引发科技板块整体重新定价。",
        "source": "IG", "verified": False, "translated": False,
        "keywords": ["Alphabet","GOOGL","Google Cloud","Gemini","earnings","Q2 2026","TPU","DeepMind"],
        "url": "https://www.ig.com/en/news-and-trade-ideas/alphabet-q2-2026-earnings-preview-260716",
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "22:30", "group": "个股",
        "title": "Micron Falls 8%+ as CXMT's $8.6B DRAM IPO and Potential HBM Export Controls Create Twin Headwinds",
        "summary": "Micron dropped over 8% on July 15-16 as China's CXMT priced its $8.6B DRAM-focused IPO, signaling China's DRAM ambitions, while rumors emerged of potential US HBM export restrictions. However, Micron's HBM supply is sold out through 2026 under non-cancelable agreements booked into 2027-28.",
        "why": "美光遭双重利空冲击，但HBM至2026年末均已售罄——当前股价下跌可能是情绪性非基本面杀跌；HBM出口管制若落地将是实质风险，需跟踪政策进展；高波动期适合评估Sell Put建底仓机会。",
        "source": "TradingKey", "verified": False, "translated": False,
        "keywords": ["Micron","MU","CXMT","HBM","DRAM","export controls","IPO","存储芯片"],
        "url": "https://www.tradingkey.com/analysis/stocks/us-stocks/262033102-micron-mu-stock-falls-cxmt-ipo-hbm-export-restriction-2026-tradingkey",
    },
    {
        "tier": 2, "lang": "en", "markets": ["HK"], "time": "09:00", "group": "个股",
        "title": "SK hynix Ships 12-Layer HBM4E Samples; Record 4 TB/s Bandwidth, 37% Faster Than HBM4",
        "summary": "SK hynix shipped 12-layer HBM4E samples to major customers in early July, achieving 48GB capacity, 16 Gbps per-pin speed (+37% vs HBM4 at 12 Gbps), 4 TB/s total bandwidth, and 20%+ power efficiency improvement. Heat resistance improved 17% for stable operation in high-performance AI computing.",
        "why": "SK海力士HBM4E样品出货稳固其AI内存市场技术领先地位（全球约50-55%份额），强化英伟达Rubin GPU的独供关系；港股南方两倍做多SK海力士ETF（7709.HK）持有者可关注技术护城河带来的溢价支撑。",
        "source": "SK hynix Newsroom", "verified": True, "translated": False,
        "keywords": ["SK Hynix","HBM4E","HBM4","AI memory","DRAM","7709.HK","带宽","高带宽内存"],
        "url": "https://news.skhynix.com/en/12-layer-hbm4e-sample-1/",
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "22:00", "group": "个股",
        "title": "Circle Wins OCC National Trust Bank Charter; Shares Jump 14% as GENIUS Act Deadline Passes",
        "summary": "Circle Internet Group received final OCC approval on July 10 to establish First National Digital Currency Bank, N.A., making it the first stablecoin issuer with a US federal trust bank charter. The milestone preceded the GENIUS Act implementing-rules deadline of July 18, strengthening USDC's regulatory foundation.",
        "why": "获得联邦信托银行资质是Circle从支付公司向受监管金融机构转型的关键里程碑，有助于USDC储备管理透明化；稳定币正规化利好CRCL长期估值重构，但CLARITY法案与银行业竞争仍存变数。",
        "source": "CNBC", "verified": True, "translated": False,
        "keywords": ["Circle","CRCL","USDC","OCC","national bank","GENIUS Act","stablecoin","稳定币"],
        "url": "https://www.cnbc.com/2026/07/10/circle-gets-an-occ-bank-charter-as-stablecoin-competition-heats-up-shares-surge-14percent.html",
    },
    {
        "tier": 2, "lang": "en", "markets": ["HK"], "time": "09:00", "group": "个股",
        "title": "Pop Mart LABUBU Makes Historic FIFA World Cup Opening Ceremony Debut — First Chinese IP Since 1930",
        "summary": "LABUBU appeared as two giant mascots at the 2026 FIFA World Cup opening ceremony on June 12 — the first Chinese original IP to perform at a World Cup since the tournament began in 1930. The LABUBU x FIFA collection drove sustained restock demand through the tournament, which concluded July 19.",
        "why": "Labubu登上FIFA世界杯开幕式是泡泡玛特IP出海史上最大级别的全球曝光里程碑；世界杯刚于7月19日落幕，后续销量与联名复购数据将验证品牌破圈转化效果，是9992.HK估值重估的重要催化剂。",
        "source": "TechNode", "verified": True, "translated": False,
        "keywords": ["泡泡玛特","Pop Mart","LABUBU","Labubu","FIFA","World Cup","9992.HK","IP","潮玩","出海"],
        "url": "https://technode.com/2026/06/12/pop-marts-labubu-makes-a-surprise-appearance-at-the-2026-fifa-world-cup-opening-ceremony/",
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "08:00", "group": "个股",
        "title": "Futu moomoo Singapore: Private Wealth AUM +158% YoY; MooFest 2026 Held July 18 at Marina Bay Sands",
        "summary": "Moomoo Singapore reported private wealth AUM growth of 158% YoY with 40 External Asset Managers, per its July 20 announcement. Global IBKR-comparison: 5.185M client accounts (+34% YoY) and client equity of $930.3B (+40% YoY). MooFest 2026 was held July 18 at Marina Bay Sands. Caveat: Futu also faces securities fraud lawsuits filed in early July following regulatory penalties.",
        "why": "富途私人财富AUM增速亮眼；但7月初遭遇证券欺诈诉讼（监管罚款引发股价跌27%）是显著法律风险。业务增长与尾部法律风险并存，Sell Put策略需留意判决时点带来的波动。",
        "source": "Caproasia", "verified": False, "translated": False,
        "keywords": ["富途","Futu","moomoo","FUTU","AUM","MooFest","Singapore","私人财富"],
        "url": "https://www.caproasia.com/2026/07/20/futu-online-investment-trading-platform-moomoo-singapore-reports-1-growth-in-retail-private-wealth-institutional-business-with-private-wealth-aum-158-yoy-40-external-asset-managers-eams-o/",
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "09:00", "group": "个股",
        "title": "Intel Q2 Earnings July 23; Stock Swings 10%+ Down Then +4.5% on AI Demand Recovery",
        "summary": "Intel will report Q2 2026 results on July 23 after market close. The stock dropped more than 10% when Samsung's weak Q2 prelim sparked a broad chip selloff, then rebounded 4.5% to $107.76 on July 15 amid AI chip demand optimism. Key watch: 18A technology yield progress and Intel Foundry Services trajectory.",
        "why": "英特尔7月23日财报是本周第三只科技巨头业绩，18A良率披露是代工业务重估故事核心观测点；代工若有实质突破可能触发大幅重估，否则股价下行压力持续；与谷歌、特斯拉共同构成本周Q2财报季情绪试金石。",
        "source": "Intel Newsroom", "verified": True, "translated": False,
        "keywords": ["Intel","INTC","earnings","Q2 2026","18A","foundry","CPU","AI chip"],
        "url": "https://newsroom.intel.com/corporate/intel-to-report-second-quarter-2026-financial-results",
    },
    {
        "tier": 2, "lang": "en", "markets": ["US"], "time": "09:30", "group": "个股",
        "title": "Interactive Brokers Q2 Earnings Due Today (July 21); Client Accounts +34% YoY to 5.185M",
        "summary": "Interactive Brokers reports Q2 2026 earnings after market close today. June client accounts reached 5.185 million (+34% YoY) with client equity of $930.3 billion (+40% YoY). Consensus EPS: $0.61/share; the broker has a 4-quarter average earnings surprise of +11.7%. Higher Q2 market volatility is expected to boost trading commissions.",
        "why": "盈透今日发布Q2财报，高市场波动率（中东冲突+AI板块动荡）对券商交易收入是正催化；可与富途对比观察互联网券商竞争格局；期权交易量上升对IBKR收入贡献值得重点关注。",
        "source": "The Motley Fool", "verified": False, "translated": False,
        "keywords": ["Interactive Brokers","IBKR","earnings","Q2 2026","broker","accounts","盈透"],
        "url": "https://www.fool.com/investing/2026/07/19/interactive-brokers-grew-its-customer-accounts-34/",
    },
    {
        "tier": 2, "lang": "zh", "markets": ["HK"], "time": "09:00", "group": "个股",
        "title": "蜜雪冰城美国首店落地洛杉矶好莱坞，全球化出海再下一城",
        "summary": "蜜雪冰城（2097.HK）首家美国门店在洛杉矶好莱坞正式开业，成为首个进入美国市场的中国连锁茶饮品牌。蜜雪冰城目前全球门店数近6万家，已布局东南亚、澳大利亚等市场，美国门店是其国际化战略的重要里程碑。",
        "why": "蜜雪冰城进入全球最大消费市场是关键出海里程碑，对港股2097.HK有正向情绪提振；美国门店运营成本与客流量将成为检验品牌出海能力的重要样本，投资者可期待后续营运数据披露。",
        "source": "Yahoo Finance HK", "verified": True, "translated": False,
        "keywords": ["蜜雪冰城","Mixue","2097.HK","出海","洛杉矶","好莱坞","新茶饮","全球化"],
        "url": "https://hk.finance.yahoo.com/news/%E8%9C%9C%E9%9B%AA%E5%86%B0%E5%9F%8E%E5%9C%A8%E7%BE%8E%E9%A6%96%E5%BA%97%E8%90%BD%E8%85%B3%E6%B4%9B%E6%9D%89%E7%A3%AF%E5%A5%BD%E8%90%8A%E5%A1%A2-%E4%B8%AD%E5%9C%8B%E8%8C%B6%E9%A6%AE%E5%85%A8%E7%90%83%E5%8C%96%E5%86%8D%E4%B8%8B-%E5%9F%8E-075003171.html",
    },
    {
        "tier": 3, "lang": "zh", "markets": ["HK"], "time": "10:00", "group": "个股",
        "title": "小米宣布推出澎程增程SUV新系列，延展电动汽车产品矩阵",
        "summary": "小米汽车宣布推出全新澎程（SkyNomad）智能可变空间SUV系列，不属于子品牌，而是与SU7、YU7并列的独立产品线，规划五座和七座增程车型。同期公布7月YU7购车权益，含6,500元科技舒享套装限时优惠及3,000元车漆优惠券。",
        "why": "澎程系列进入增程赛道扩大小米汽车的细分市场覆盖，或助力拓展家庭用户与下沉市场；但竞争激烈（理想、华为问界），定价与销量爬坡周期是关键变量，对1810.HK短期估值边际影响有限。",
        "source": "IT之家", "verified": True, "translated": False,
        "keywords": ["小米","Xiaomi","1810.HK","澎程","SkyNomad","增程","SUV","YU7","雷军"],
        "url": "https://www.ithome.com/0/971/053.htm",
    },
    {
        "tier": 3, "lang": "en", "markets": ["US","HK"], "time": "09:00", "group": "个股",
        "title": "Trip.com Partners with Seat Unique to Add 500,000+ VIP Sports & Event Packages for APAC Travelers",
        "summary": "Trip.com Group and UK's Seat Unique announced a global partnership listing 500,000+ official hospitality and VIP live-event packages on Trip.com's platform, targeting Asia-Pacific travelers seeking curated sports and entertainment experiences. The deal broadens Trip.com's premium offerings beyond transport and hotels.",
        "why": "携程VIP赛事套餐合作丰富高毛利产品矩阵，有助提升ARPU；在出境游加速复苏背景下，差异化高端产品有利于用户留存。但China Renaissance近期下调至持有评级，整体估值压力需关注。",
        "source": "Sahm Capital", "verified": False, "translated": False,
        "keywords": ["携程","Trip.com","TCOM","9961.HK","VIP","Seat Unique","OTA","出境游"],
        "url": "https://www.sahmcapital.com/news/content/how-investors-are-reacting-to-tripcom-group-tcom-adding-500000-vip-event-packages-through-seat-unique-2026-07-15",
    },
    {
        "tier": 3, "lang": "en", "markets": ["US"], "time": "09:00", "group": "个股",
        "title": "SanDisk (SNDK) Q3 Revenue +251% YoY to $6.0B; Stock +4,885% Since 2025 IPO as NAND Supercycle Peaks",
        "summary": "SanDisk Q3 FY2026 revenue surged 251% YoY to $6.0 billion with gross margins of 78.4%, driven by AI-fueled NAND contract price increases and tight global supply. The stock has risen approximately 4,885% from its February 2025 IPO price of ~$38.50 to ~$1,745/share.",
        "why": "闪迪NAND超级周期验证AI对存储需求的强劲拉动，与美光DRAM周期互为参照；4885%涨幅后估值风险较高，在芯片板块本周系统性调整背景下，高位期权策略需谨慎。",
        "source": "The Motley Fool", "verified": False, "translated": False,
        "keywords": ["SanDisk","SNDK","NAND","flash","存储","闪存","Q3 2026"],
        "url": "https://www.fool.com/investing/2026/07/06/after-surging-4885-is-sandisk-stock-still-a-buy-he/",
    },
]

# Assign IDs
for item in raw:
    item["id"] = make_id(item["url"], item.get("title",""))

# Print summary
for item in raw:
    print(f"{item['id']}  T{item['tier']}  {item['group'][:4]}  {item['title'][:65]}")

print(f"\nTotal: {len(raw)} items")

with open("/home/user/market-radar/new_items.json", "w", encoding="utf-8") as f:
    json.dump(raw, f, ensure_ascii=False, indent=2)

print("Written: new_items.json")
