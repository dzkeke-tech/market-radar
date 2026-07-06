import json, hashlib

def make_id(url, title=""):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

with open("/tmp/seen.json") as f:
    seen_ids = set(json.load(f).get("ids", []))

candidates = [
    # ──────────── 大盘头条 ────────────
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["A"],
        "time": "00:00",
        "group": "大盘头条",
        "title": "A股七大交易新规今日（7月6日）正式施行：主板ST股涨跌幅上限升至10%，盘后固定价格交易扩至全A股",
        "summary": "沪深交易所新规今日起施行，主板风险警示股票（ST/*ST）涨跌幅限制由5%扩至10%；盘后固定价格交易适用范围由科创板扩展至全部A股和ETF；深交所同步在创业板引入做市商制度；上交所基金收盘阶段由连续竞价改为收盘集合竞价。",
        "why": "A股交易机制重大调整，ST股流动性和波动率将显著提升；做市商制度有利于创业板成交活跃度，直接影响持仓标的估值定价效率。",
        "source": "证券时报",
        "verified": True,
        "keywords": ["A股", "交易新规", "ST股", "盘后固定价格交易", "做市商"],
        "translated": False,
        "url": "https://www.stcn.com/article/detail/3998631.html"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US", "HK", "A"],
        "time": "07:00",
        "group": "大盘头条",
        "title": "Meta to sell excess AI compute capacity, triggering global chip selloff; Philadelphia Semiconductor Index plunges 10% over two sessions",
        "summary": "Meta announced plans to build a cloud business selling excess AI compute capacity, inking deals with Anthropic ($1.25B/month) and Google ($920M/month). The news triggered a sharp reversal in chip stocks — the Philadelphia Semiconductor Index fell 6.3% on July 1 and continued lower July 2, with Nvidia, AMD, Micron and Intel all suffering heavy losses. A-share semiconductors fell 6.7%, equipment sector -8.13%, and ChiNext 50 dropped 7%+ intraday.",
        "why": "全球最大AI算力买家之一开始对外出售富余计算力，市场担忧AI硬件采购增速见顶，半导体估值逻辑受到冲击；直接压制NVDA、MU等持仓标的，并波及A股科技链，相关covered call/sell put策略需重新审视期权隐含波动率。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["Meta", "AI compute", "oversupply", "semiconductor", "chip selloff", "Philadelphia Semiconductor Index", "费城半导体"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/01/meta-stock-cloud-ai-compute.html"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "08:30",
        "group": "大盘头条",
        "title": "U.S. June nonfarm payrolls rose just 57,000, far below 115,000 consensus; unemployment steady at 4.2%",
        "summary": "The Bureau of Labor Statistics reported June nonfarm payrolls of 57,000, well below the Dow Jones consensus of 115,000 and the prior month's downwardly-revised 129,000. Unemployment held at 4.2% as labor force participation dropped 0.3pp to 61.5%. Following the report, Fed rate-hike probability for October fell sharply, reinforcing a 'higher for longer but no more hikes' stance.",
        "why": "就业数据大幅低于预期，进一步打压美联储加息预期（期货已基本排除今年加息），美元走弱、美债收益率下降；对sell put策略而言，波动率偏高背景下时间价值收入仍佳，但需关注经济下行风险。",
        "source": "CNBC / BLS",
        "verified": True,
        "keywords": ["nonfarm payroll", "jobs report", "unemployment", "Federal Reserve", "rate hike", "非农就业"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/02/jobs-report-june-2026-.html"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["A"],
        "time": "09:00",
        "group": "大盘头条",
        "title": "宇树科技IPO注册获批，科创板人形机器人第一股将于7月下旬或8月初正式挂牌",
        "summary": "中国证监会正式批准宇树科技科创板IPO注册，全程仅用104天，创科创板预审机制落地以来最快纪录。公司拟募资42亿元，2025年营收17.08亿元（+335%）。预计7月下旬或8月初挂牌，成为科创板首只人形机器人股票。",
        "why": "具身智能概念A股重大催化剂；宇树上市将带动机器人整体板块估值重估，同时验证新经济IPO快速通道，关注相关机器人ETF和供应链标的联动效应。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["宇树科技", "Unitree", "科创板", "IPO", "人形机器人", "具身智能"],
        "translated": False,
        "url": "https://k.sina.com.cn/article_7879922977_1d5ae152106801giri.html"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["A"],
        "time": "21:00",
        "group": "大盘头条",
        "title": "证监会就完善上市公司再融资规则征求意见：锁价定增退出，全面改为市价定价，储架发行制度落地",
        "summary": "证监会7月3日晚发布征求意见稿，核心变化三点：1.竞价定增统一以发行期首日为定价基准日，彻底取消锁价套利；2.建立定向增发储架发行制度，合规公司可一次注册多次发行；3.小额快速再融资上限由3亿元提至6亿元，龙头企业放宽至10亿元。",
        "why": "再融资生态重大调整：锁价定增退出消除折价套利，定价机制市场化；储架发行提升融资灵活性。短期或引发定增预案重新定价，关注持仓中涉定增公司的股价影响。",
        "source": "北京商报 / 证监会",
        "verified": True,
        "keywords": ["证监会", "再融资", "定向增发", "储架发行", "市价定价", "CSRC"],
        "translated": False,
        "url": "https://www.bbtnews.com.cn/2026/0703/598217.shtml"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:30",
        "group": "大盘头条",
        "title": "Alphabet joins Dow Jones Industrial Average, replacing Verizon; Dow closes above 52,000 for the first time",
        "summary": "Alphabet (GOOGL) officially joined the DJIA on June 29, replacing Verizon. The Dow closed at 52,120, its first close above 52,000. Five of the Magnificent Seven — Nvidia, Amazon, Apple, Microsoft, and now Alphabet — are in the index. GOOGL shares rose ~4% on its Dow debut and are up more than 11% YTD.",
        "why": "Alphabet正式纳入道指是机构被动资金增量配置信号；GOOGL年内已涨逾11%，Q2财报7月22日公布将是近期核心催化剂，持有期间可考量covered call策略锁定部分收益。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["Alphabet", "Dow Jones", "DJIA", "GOOGL", "Google", "道琼斯"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/06/29/alphabet-googl-stock-dow-average.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US", "HK"],
        "time": "10:00",
        "group": "大盘头条",
        "title": "Gold mid-year outlook: Hit record $5,589/oz in January before pulling back; J.P. Morgan targets $6,000 by year-end",
        "summary": "World Gold Council's mid-year review shows gold hit an all-time intraday high of $5,589.38 on January 28, 2026, before retreating below $4,000 by late June on dollar strength and profit-taking. Central banks purchased 244 tonnes net in Q1 2026 (+3% YoY). A weak June U.S. jobs report has recently supported a recovery rally. J.P. Morgan targets $6,000/oz by year-end and sees $6,300/oz possible in 2027.",
        "why": "直接影响老铺黄金（6181.HK）估值逻辑：其固定价格销售模式在金价上涨周期中享受溢价，但从高点回落至4000美元以下已令其股价较高峰下跌超50%；若JPM预测6000美元兑现，是重要的再入场参考。",
        "source": "World Gold Council",
        "verified": True,
        "keywords": ["gold", "黄金", "central bank", "J.P. Morgan", "老铺黄金", "gold price", "Laopu"],
        "translated": False,
        "url": "https://www.gold.org/goldhub/research/gold-mid-year-outlook-2026"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "11:00",
        "group": "大盘头条",
        "title": "Bitcoin rebounds above $61,000 on softer inflation signals; June ETF outflows hit record $4.51B as BTC touched 21-month lows",
        "summary": "Bitcoin climbed back above $61,000 on July 2 after Fed Chair Warsh signaled lower inflation risks, reducing rate-hike fears. June had been brutal: BTC touched 21-month lows, and U.S. spot Bitcoin ETFs saw a record $4.51B monthly net outflow led by BlackRock's IBIT. On-chain data shows whales accumulated 270,000+ BTC in recent weeks, a potential contrarian signal.",
        "why": "比特币弱势格局影响加密整体情绪，Circle/USDC稳定币业务间接承压；同时这也是宏观流动性紧缩的信号，对高估值科技股（如持仓的NVDA、PLTR等）有连带压制作用。ETF流出创纪录说明机构正在减持，需警惕。",
        "source": "CoinDesk",
        "verified": True,
        "keywords": ["Bitcoin", "BTC", "crypto", "ETF outflow", "IBIT", "BlackRock", "stablecoin", "比特币"],
        "translated": False,
        "url": "https://www.coindesk.com/markets/2026/07/02/bitcoin-zooms-above-usd61-000-as-inflation-fears-soften"
    },
    # ──────────── 个股 ────────────
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "08:00",
        "group": "个股",
        "title": "Tesla Q2 2026 deliveries surge 25% YoY to 480,126 vehicles, crushing Wall Street consensus of 406,024 — best-ever Q2",
        "summary": "Tesla delivered 480,126 vehicles in Q2 2026 (+25% YoY, +34% QoQ), far exceeding the consensus of 406,024. Production reached 451,758 vehicles. Model 3/Y accounted for 467,762 of deliveries; energy storage deployments hit 13.5 GWh. A 28,000+ unit inventory draw signals robust end-demand. Citi's most bullish estimate had topped out at ~420,000.",
        "why": "交付量大超预期终结连续两年的下滑趋势，是对特斯拉基本面最强的季度证明；FSD/Robotaxi和Optimus的商业化故事维持吸引力；但股价年内仍下跌约7%，关注是否形成sell put抄底机会。",
        "source": "Electrek / Tesla SEC 8-K",
        "verified": True,
        "keywords": ["Tesla", "TSLA", "Q2 deliveries", "Model 3", "Model Y", "Robotaxi", "特斯拉"],
        "translated": False,
        "url": "https://electrek.co/2026/07/02/tesla-q2-2026-deliveries-480126/"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "08:30",
        "group": "个股",
        "title": "Tesla Robotaxi launches in Miami — third state; NHTSA escalates FSD rain-visibility probe to engineering analysis",
        "summary": "Tesla launched unsupervised Robotaxi rides in western Miami-Dade on July 3, marking expansion to its third state after Texas and California. Simultaneously, NHTSA escalated its investigation of Tesla FSD's performance in degraded visibility conditions to an engineering analysis — the final step before a potential recall. Future expansion includes Phoenix permits and Nevada (5,000 vehicles filed).",
        "why": "Robotaxi商业化加速是特斯拉估值重构的核心叙事，但NHTSA调查升级增加监管不确定性，可能压制短期股价；持仓TSLA的期权策略需留意隐含波动率因监管消息走高的对冲需求。",
        "source": "Teslarati / TechTimes",
        "verified": True,
        "keywords": ["Tesla", "TSLA", "Robotaxi", "FSD", "Miami", "NHTSA", "autonomous driving", "自动驾驶"],
        "translated": False,
        "url": "https://www.teslarati.com/tesla-expands-robotaxi-florida-third-state-autonomy/"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "07:30",
        "group": "个股",
        "title": "小米汽车6月交付超3万辆，H1累计近18万辆；港股单日涨约5%；YU9将于8月发布",
        "summary": "小米汽车6月交付量超过3万辆，实现连续第三个月破3万，上半年累计约18万辆（全年55万辆目标的约33%）。花旗预计YU9豪华SUV将于8月发布，或带动股价进一步反弹。港股7月2日受比亚迪及小米交付数据双重提振，小米（1810.HK）单日涨约5%。",
        "why": "小米汽车业务规模化验证加速，月均交付持续突破3万辆是关键里程碑；YU9进军高端细分市场具有品牌升级意义；港股涨势对sell put行权价设置有直接参考意义。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["小米", "Xiaomi", "1810.HK", "SU7", "YU7", "YU9", "电动车", "交付量"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/02/china-ev-stocks-xiaomi-byd-june-deliveries-production.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Palantir wins U.S. Army's top-priority NGC2 cloud contract; Nvidia partnership for sovereign AI in secure federal environments",
        "summary": "The U.S. Army selected Palantir's Foundry as the core cloud data layer for its Next Generation Command and Control (NGC2) program — the Army's highest modernization priority — moving from prototype to wide deployment. Separately, Palantir and Nvidia announced a joint initiative to deploy Nvidia AI and Nemotron models in secure, sovereign environments for federal agencies and critical infrastructure. PLTR stock rose ~3% on the contract news.",
        "why": "美国陆军最高优先级合同落地验证了Palantir政府AI平台的核心地位；与Nvidia的主权AI合作扩大生态护城河；PLTR年内已有显著涨幅，高估值下建议关注期权保护或covered call策略。",
        "source": "Yahoo Finance",
        "verified": False,
        "keywords": ["Palantir", "PLTR", "Army", "NGC2", "Nvidia", "sovereign AI", "Foundry", "government contract"],
        "translated": False,
        "url": "https://sg.finance.yahoo.com/news/palantir-doubles-down-national-security-150700513.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US", "HK"],
        "time": "09:00",
        "group": "个股",
        "title": "SK hynix ships HBM4E samples to major customers: 48GB 12-layer stack, 4 TB/s bandwidth, 20%+ power efficiency improvement",
        "summary": "SK hynix announced on June 18 it shipped HBM4E samples to major customers. The product uses Advanced MR-MUF technology to achieve 48GB in a 12-Hi stack, improving heat resistance by 17% vs. HBM4 and delivering 4 TB/s maximum bandwidth. Power efficiency improves by over 20% vs. the previous generation. HBM3E is expected to represent ~2/3 of total HBM shipments in 2026, with HBM4/4E gradually taking share.",
        "why": "SK Hynix主导HBM供应链（市占超50%），HBM4E验证其技术领先优势，维持对英伟达等主要客户的核心供应商地位；在Meta算力超卖冲击半导体板块的背景下，HBM结构性需求强势是重要反驳论据。",
        "source": "SK hynix Newsroom (official)",
        "verified": True,
        "keywords": ["SK Hynix", "HBM4E", "HBM4", "DRAM", "AI memory", "high bandwidth memory", "存储芯片"],
        "translated": False,
        "url": "https://news.skhynix.com/12-layer-hbm4e-sample/"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "10:00",
        "group": "个股",
        "title": "Circle (CRCL) faces new Federal Reserve stablecoin oversight rules; Arc blockchain ownership creates unresolved GENIUS Act conflict",
        "summary": "The Federal Reserve has proposed new rules for payment stablecoin issuers, directly targeting Circle and USDC. A structural conflict has also emerged: Circle raised $222M for 'Arc,' its own layer-1 blockchain (a16z leading), meaning Circle would own the settlement rail for USDC — a conflict the GENIUS Act never addressed. Analysts note USDC has become the default institutional stablecoin post-GENIUS Act, building operational lock-in.",
        "why": "Circle/USDC是持仓标的，新监管规则可能影响其盈利模式；自建区块链引发垂直整合争议，潜在监管风险需持续追踪；但GENIUS Act落地后USDC机构采用率上升是中期利好，两端拉扯估值。",
        "source": "Yahoo Finance / Forbes",
        "verified": False,
        "keywords": ["Circle", "CRCL", "USDC", "stablecoin", "GENIUS Act", "Federal Reserve", "Arc blockchain", "稳定币"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/crypto/articles/circle-crcl-faces-fed-stablecoin-010923003.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "10:30",
        "group": "个股",
        "title": "Alphabet Q2 2026 earnings set for July 22; Gemini reaches 900M monthly users; Cloud Q1 revenue up 63% to $20B",
        "summary": "Alphabet will report Q2 2026 earnings on July 22. Q1 highlights: Google Cloud revenue hit $20B (+63% YoY) with a $462B backlog and 32.9% operating margin; Gemini reached 900M monthly active users across 230 countries with paid subscriptions at 350M. Google told Meta it couldn't meet full Gemini capacity requests — a rare supply constraint signal. Stock is up ~11% YTD.",
        "why": "7月22日Q2财报是GOOGL下一个主要催化剂；Cloud加速增长和Gemini商业化验证是核心看点；Gemini容量受限是罕见的供不应求信号，维持高估值合理性；可考量财报前建立covered call以锁定时间价值。",
        "source": "Barchart / CNBC",
        "verified": False,
        "keywords": ["Google", "Alphabet", "GOOGL", "Gemini", "Google Cloud", "Q2 earnings", "AI", "谷歌"],
        "translated": False,
        "url": "https://www.barchart.com/story/news/3117520/dear-google-stock-fans-mark-your-calendars-for-july-22"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "11:00",
        "group": "个股",
        "title": "EU ending duty-free allowance for parcels under 150 euros in July; PDD shares down ~30% since Nov 2025 as Temu pivots to semi-managed model",
        "summary": "The EU is eliminating its 150-euro duty-free de minimis threshold for cross-border parcels in July 2026 — a major blow to Temu's direct-from-China model after Turkey also dropped its 30-euro threshold. This follows U.S. de minimis changes (effective May 2025) that effectively added 25-60% import charges on many items. Temu has pivoted to a 'semi-managed' local-merchant model with next-day delivery. PDD Holdings shares have fallen ~30% since November 2025.",
        "why": "欧盟取消150欧元免税门槛是Temu/拼多多最大的海外增长威胁之一，直接压制其低价跨境模式；PDD已从高增长切换至整合期，营收增速降至个位数，持仓需审视下行保护是否足够。",
        "source": "Yahoo Finance",
        "verified": False,
        "keywords": ["拼多多", "PDD", "Temu", "EU tariff", "de minimis", "cross-border", "e-commerce", "跨境电商"],
        "translated": False,
        "url": "https://finance.yahoo.com/news/temu-slashes-prices-60-pdd-173339664.html"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "16:30",
        "group": "个股",
        "title": "Micron Q3 FY2026 record: revenue ~$41.5B vs $35.8B estimate; Q4 guidance ~$50B crushes $43.6B consensus; HBM4 in high-volume production, full-year supply sold out",
        "summary": "Micron reported Q3 FY2026 record revenue of $41.46B vs. $35.84B estimate. Data center sales surged ~7x to $11.5B; cloud memory +300% to $13.77B. Q4 FY2026 guidance of ~$50B vs. analyst consensus of $43.58B. Management confirmed HBM4 entered high-volume production in Q2 2026 and the entire 2026 HBM supply is sold out with pricing agreed. Quarterly dividend of $0.15/share; record date is today, July 6, 2026.",
        "why": "美光Q3/Q4超预期业绩是AI存储需求强劲的最强佐证，有力对冲Meta算力过剩担忧的恐慌情绪；HBM4量产巩固AI存储三强格局；今日为股息记录日，持有者可获0.15美元/股季度股息。芯片股本周可能出现超跌买入机会。",
        "source": "CNBC / Micron Investor Relations",
        "verified": True,
        "keywords": ["Micron", "MU", "HBM4", "DRAM", "Q3 earnings", "Q4 guidance", "AI memory", "存储芯片", "美光"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/06/24/micron-mu-earnings-report-q3-2026.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Nvidia unveils Vera Rubin HPC supercomputer platform; AI compute partnership for cloud firms; market cap ~$4.7T, Blackwell sold out through mid-2026",
        "summary": "Nvidia announced the Vera Rubin platform for world-class AI HPC supercomputers, with 35 units in development across Europe. On July 4, Nvidia launched a strategic initiative supporting cloud firms acquiring expensive AI chips. The Blackwell architecture remains sold out through mid-2026 demonstrating extraordinary demand for next-gen AI accelerators. FY2026 annual revenue reached $15.94B (+65% YoY). Market cap ~$4.7T; stock up ~5% YTD.",
        "why": "英伟达在Meta出售富余算力冲击下，通过新平台和合作协议继续巩固AI算力生态主导权；Blackwell供不应求维持AI基础设施投资景气度；市值4.7万亿意味着估值仍处于高位，Meta消息引发的下跌可能是逢低介入的机会。",
        "source": "Guru Focus / NVIDIA Newsroom",
        "verified": False,
        "keywords": ["Nvidia", "NVDA", "Vera Rubin", "Blackwell", "AI chip", "GPU", "data center", "英伟达"],
        "translated": False,
        "url": "https://www.gurufocus.com/news/8944672/nvidias-ai-compute-partnership-boosts-cloud-firms-stock-ticker-nvda"
    },
]

items = []
skipped = 0
for c in candidates:
    item_id = make_id(c["url"], c.get("title", ""))
    if item_id in seen_ids:
        print(f"  [SKIP already seen] {c['title'][:60]}")
        skipped += 1
    else:
        c["id"] = item_id
        items.append(c)
        print(f"  [NEW] {item_id} | tier={c['tier']} | {c['title'][:60]}")

print(f"\nTotal candidates: {len(candidates)}")
print(f"Already seen (skipped): {skipped}")
print(f"New items to publish: {len(items)}")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nnew_items.json written with {len(items)} items.")
