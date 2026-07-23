import json, hashlib

def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

with open("/tmp/seen.json") as f:
    seen_data = json.load(f)
seen_ids = set(seen_data.get("ids", []))
print(f"Loaded {len(seen_ids)} seen IDs")

candidates = [
    # ── 大盘头条 ──
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "22:00",
        "group": "大盘头条",
        "title": "Alphabet earnings takeaways: Q2 revenue beats, GOOGL stock sinks on 2026 capex hike",
        "summary": "Alphabet Q2营收$119.8B同比+24%超预期，谷歌云$200亿+63%创历史纪录增速；但全年资本支出指引上调至创纪录$195-205B（季内capex同比翻倍至$449亿），历史首次出现负自由现金流（-$59亿）。GOOGL盘后跌约5%。",
        "why": "谷歌云63%增速为全球最快大型云，AI算力需求超强；但capex激增与负FCF引发市场担忧，隐含波动率上升，sell put需上调行权价或收窄规模。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["谷歌", "Google", "Alphabet", "GOOGL", "谷歌云", "Google Cloud"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/22/google-earnings-q2-goog-live-updates.html"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "21:00",
        "group": "大盘头条",
        "title": "Tesla (TSLA) releases Q2 2026 financial results: record revenue, big profit miss",
        "summary": "特斯拉Q2营收$28.24B同比+25.5%超预期，但GAAP EPS仅$0.33大幅低于预期$0.55；营业利润同比跌57%，主因监管积分收入缩减。FSD订阅用户达148万(+56%)。TSLA盘后跌至$362.80。",
        "why": "营收创纪录但利润率压缩严重，积分收入波动持续拖累EPS；Robotaxi战略是唯一叙事支撑，高波动率环境下sell put需谨慎评估行权价。",
        "source": "Electrek",
        "verified": True,
        "keywords": ["特斯拉", "Tesla", "TSLA", "FSD", "Robotaxi", "马斯克"],
        "translated": False,
        "url": "https://electrek.co/2026/07/22/tesla-tsla-q2-2026-financial-results/"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK", "A"],
        "time": "09:00",
        "group": "大盘头条",
        "title": "Citi upgrades China to overweight amid AI volatility, geopolitical friction",
        "summary": "花旗7月20日将中国股票由战术中性上调至超配，下调韩国至中性；恒指年末目标29,600、H1目标30,500；预计央行7月降息10bp；H2偏好A股（科技权重更高）。摩根士丹利同步建议增配港股。",
        "why": "国际资金回流中国港股/A股信号；持仓腾讯/美团/泡泡玛特等HK标的可能受益于估值重估；降息预期改善sell put安全边际。",
        "source": "South China Morning Post",
        "verified": True,
        "keywords": ["宏观", "macro", "HK"],
        "translated": False,
        "url": "https://www.scmp.com/business/markets/article/3361150/citi-upgrades-china-overweight-amid-ai-volatility-geopolitical-friction"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["A", "HK"],
        "time": "17:00",
        "group": "大盘头条",
        "title": "操盘必读：影响股市利好或利空消息_2026年7月23日",
        "summary": "7月23日A股三大指数小幅收红（沪指+0.25%），二季度GDP同比增长4.3%弱于目标区间4.5-5%（为2022Q4以来最弱）；证监会召开系列座谈会稳市，北京国资累计投入近百亿元布局股市；渣打、高盛维持A股超配。",
        "why": "GDP不及预期增加政策宽松预期，利好港股/A股后市；多方维稳降低系统性风险，持仓稳定性提升；可关注政策预期差带来的sell put机会。",
        "source": "新浪财经",
        "verified": False,
        "keywords": ["宏观", "A股"],
        "translated": False,
        "url": "https://finance.sina.com.cn/stock/cpbd/2026-07-23/doc-iniitvfn7776784.shtml"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "中际旭创启动港股公开发售，拟于7月30日在香港联交所主板挂牌交易",
        "summary": "光模块龙头中际旭创（3308.HK）7月22日启动港股IPO招股，拟募资约545亿港元（约70亿美元），为2026年港股年内最大IPO；最高发行价1010港元/股；7月30日上市；高盛、中金、摩根士丹利联席保荐。",
        "why": "港股年内最大科技/AI基础设施IPO，AI光互联龙头全球市占21%；新股上市可能带动算力基础设施赛道港股估值重估，可关注腾讯云/阿里云受益方向联动。",
        "source": "新浪科技",
        "verified": True,
        "keywords": ["科技", "internet", "HK"],
        "translated": False,
        "url": "https://finance.sina.com.cn/tech/roll/2026-07-22/doc-iniirwqh8847735.shtml"
    },
    # ── 个股 ──
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "22:30",
        "group": "个股",
        "title": "Tesla launches Robotaxi Service in two more Florida cities",
        "summary": "特斯拉7月22日将Robotaxi服务扩展至佛罗里达州奥兰多和坦帕，全美运营城市增至6个（奥斯汀、达拉斯、休斯顿、迈阿密、奥兰多、坦帕）；FSD v14 Lite同步准备广泛推送。",
        "why": "Robotaxi里程碑扩张，有助对冲Q2利润下滑叙事；商业化仍处早期，建议等待更多运营数据后再调整仓位策略。",
        "source": "Tesla Oracle",
        "verified": False,
        "keywords": ["特斯拉", "Tesla", "TSLA", "Robotaxi", "FSD", "自动驾驶"],
        "translated": False,
        "url": "https://www.teslaoracle.com/2026/07/22/tesla-launches-robotaxi-service-in-two-more-florida-cities/"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Intel to Report Second-Quarter 2026 Financial Results on July 23",
        "summary": "英特尔今日（7月23日）盘后公布Q2 2026业绩，电话会议太平洋时间2pm；分析师预期营收$14.42B、Non-GAAP EPS $0.21；股价年初涨163%；期权市场隐含摆动幅度约13.6%。",
        "why": "高隐含波动率（13.6%）提供期权卖方窗口但风险同步放大；18A良率与AI服务器CPU需求指引是多空关键变量，业绩前后均需谨慎定仓。",
        "source": "Intel Investor Relations",
        "verified": True,
        "keywords": ["英特尔", "Intel", "INTC", "CPU", "foundry", "晶圆代工", "18A"],
        "translated": False,
        "url": "https://www.intc.com/news-events/press-releases/detail/1774/intel-to-report-second-quarter-2026-financial-results"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK"],
        "time": "09:00",
        "group": "个股",
        "title": "SK Hynix Rockets 14% Ahead of July 29 Earnings as Chip Stocks Rebound",
        "summary": "SK海力士7月21日单日飙涨14%，为即将于7月29日公布Q2业绩提前定价；韩国券商预测Q2营业利润率74-77%，有望创历史新高；7709.HK（南方两倍做多SK海力士ETF）同步大涨。",
        "why": "HBM/存储赛道业绩确认期，7709.HK持仓beta显著放大；须警惕'buy the rumor sell the news'风险，卖出put时行权价应留充足安全垫。",
        "source": "24/7 Wall St.",
        "verified": False,
        "keywords": ["SK海力士", "SK Hynix", "HBM", "存储芯片", "内存", "南方两倍做多", "CSOP"],
        "translated": False,
        "url": "https://247wallst.com/investing/2026/07/21/sk-hynix-rockets-14-ahead-of-july-29-earnings-as-chip-stocks-rebound/"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK"],
        "time": "10:00",
        "group": "个股",
        "title": "SK hynix Set to Post Record Operating Margin in Q2, as HBM Mix Weighs on ASP Growth and LTAs Gain Focus",
        "summary": "TrendForce预测SK海力士Q2营业利润率将达74-77%（历史新高）；HBM销售比重提升同时压低DRAM均价增速；长期合约（LTA）定价成为分析师关注焦点；HBM4预计2027年带来40-50%产品溢价。",
        "why": "存储超级周期高点确认性信号；HBM4产品路线清晰，中期持仓逻辑强；LTA价格锁定需追踪以判断ASP增速拐点是否提前出现。",
        "source": "TrendForce",
        "verified": False,
        "keywords": ["SK海力士", "SK Hynix", "HBM", "HBM4", "DRAM", "存储芯片", "高带宽内存"],
        "translated": False,
        "url": "https://www.trendforce.com/news/2026/07/22/news-sk-hynix-set-to-post-record-operating-margin-in-q2-as-hbm-mix-weighs-on-asp-growth-and-ltas-gain-focus/"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "10:00",
        "group": "个股",
        "title": "腾讯市值4万亿港元徘徊：游戏收入产分歧，AI回报待考",
        "summary": "腾讯（00700）7月22日盘中一度跌逾7%，市值逼近4万亿港元支撑位；7月23日反弹至4.08万亿。Q2财报定于8月12日，市场分歧聚焦游戏收入增速及AI产品（元宝/混元）货币化；微信AI助手小微已启动灰度测试。",
        "why": "8月12日业绩是近期核心催化剂，业绩前隐含波动率将上升；4万亿港元是关键支撑，AI货币化若超预期将触发估值重估；sell put行权价建议参考该支撑位。",
        "source": "新浪科技",
        "verified": False,
        "keywords": ["腾讯", "Tencent", "0700.HK", "微信", "WeChat", "腾讯游戏", "元宝", "混元"],
        "translated": False,
        "url": "https://finance.sina.com.cn/tech/roll/2026-07-23/doc-iniiufvh7774531.shtml"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["HK"],
        "time": "09:00",
        "group": "个股",
        "title": "Pop Mart's stock price rises six percent on World Cup edition LABUBU launch",
        "summary": "泡泡玛特（9992.HK）推出FIFA世界杯2026 Labubu限定版（MEGA 400%），售价HK$1,625/个，限购一件；9992.HK盘中涨约6%。大股东段永平将持股从6.85%增至7.65%（增持约1059万股，最高HK$150/股）。",
        "why": "世界杯IP联名强化Labubu全球曝光，短期催化力强；段永平持续增持显示大股东信心；Monsters IP占总营收约40%，IP热度持续是长线核心变量。",
        "source": "The Standard HK",
        "verified": False,
        "keywords": ["泡泡玛特", "Pop Mart", "Labubu", "拉布布", "9992.HK", "The Monsters", "潮玩"],
        "translated": False,
        "url": "https://www.thestandard.com.hk/property/article/337435/Pop-Marts-stock-price-rises-six-percent-on-World-Cup-edition-LABUBU-launch"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Palantir Just Secured the U.S. Army's Biggest Data Overhaul",
        "summary": "Palantir中标美国陆军最大现代化项目NGC2核心云数据层；同步与英伟达推出在主权/安全环境部署AI的合作方案；Q1营收$16.33亿同比+85%，美国政府收入+84%至$6.87亿，合同余额RPO同比+134%。",
        "why": "政府AI合同长期锁定高能见度收入；英伟达合作验证AIP平台生态价值；RPO高增长对sell put方向性有利，可维持或小幅增仓。",
        "source": "Yahoo Finance",
        "verified": False,
        "keywords": ["Palantir", "PLTR", "AIP", "Foundry", "国防AI", "政府合同", "AI平台"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/stocks/articles/palantir-just-secured-u-army-180024842.html"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "EU Package Fee from 1 July 2026: What the New Customs Rules Mean for Temu, Shein and European E-Commerce",
        "summary": "欧盟自2026年7月1日起废除150欧元小额进口免税门槛，每票进口增收3欧元手续费，直击Temu、Shein等跨境电商模式；美国已于2026年5月对中国商品终止de minimis豁免。Temu加速扩大半管理模式和海外仓以应对。",
        "why": "中美欧三地同步收紧跨境免税，Temu全球扩张成本骤升，PDD跨境业务增速面临下调压力；持仓需重估未来季度海外营收影响及利润弹性。",
        "source": "E-Commerce Institute Cologne",
        "verified": True,
        "keywords": ["拼多多", "PDD", "Temu", "跨境电商", "Temu出海"],
        "translated": False,
        "url": "https://ecommerceinstitut.de/eu-package-fee-from-1-july-2026-what-the-new-customs-rules-mean-for-temu-shein-and-european-e-commerce/"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Circle (CRCL) Faces New Fed Stablecoin Rules As USDC Oversight Tightens",
        "summary": "GENIUS Act监管过渡期已于7月18日到期，美联储随即提出支付稳定币发行人新监管框架，对Circle USDC储备管理、资本要求及信息披露标准将收严；CRCL股价承压。",
        "why": "监管明确化短期增加Circle合规成本，但长期或强化机构对USDC信任；需关注Circle是否满足新标准，稳定币赛道整体估值逻辑将被重新定价。",
        "source": "Yahoo Finance",
        "verified": False,
        "keywords": ["Circle", "CRCL", "USDC", "稳定币", "stablecoin", "GENIUS Act", "稳定币法案"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/crypto/articles/circle-crcl-faces-fed-stablecoin-010923003.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "NVIDIA Corporation (NVDA) to Launch Rubin CPX by the End of 2026",
        "summary": "英伟达宣布将于2026年底推出Rubin CPX芯片，专攻视频生成和AI辅助编码等复杂任务（继Blackwell之后的下一代产品）；同步推出AI算力合作伙伴计划支持云服务商融资采购GPU；DeepSeek据报正自研AI芯片以削减对英伟达依赖。",
        "why": "Rubin路线图清晰强化护城河；DeepSeek自研是潜在中期竞争风险信号，但短期不改变Blackwell供需紧张格局；持仓NVDA逻辑仍强，可维持sell put。",
        "source": "Finviz",
        "verified": False,
        "keywords": ["英伟达", "Nvidia", "NVDA", "GPU", "AI芯片", "Blackwell", "黄仁勋", "Rubin"],
        "translated": False,
        "url": "https://finviz.com/news/168814/nvidia-corporation-nvda-to-launch-rubin-cpx-by-the-end-of-2026"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["HK"],
        "time": "09:00",
        "group": "个股",
        "title": "Meituan Keeta Accelerates Overseas Expansion: Plans to Enter the UAE, Kuwait, Qatar, Bahrain",
        "summary": "美团Keeta7月在沙特新增11城覆盖，累计已覆盖20城市、市场份额约10%（排名第三）；计划进一步拓展阿联酋、科威特、卡塔尔、巴林等海湾国家。摩根士丹利预测2028年Keeta中东市占达20%、GMV 60亿美元。",
        "why": "海外扩张验证美团非国内存量成长逻辑，出海里程碑提升估值弹性；适合中长线持仓，可搭配sell put在波动中增仓。",
        "source": "富途牛牛",
        "verified": False,
        "keywords": ["美团", "Meituan", "3690.HK", "Keeta", "外卖", "即时零售"],
        "translated": False,
        "url": "https://news.futunn.com/en/post/60458148/meituan-keeta-accelerates-overseas-expansion-plans-to-enter-the-uae"
    },
    {
        "tier": 3,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Micron (NASDAQ: MU) Stock News: AI Memory Demand Keeps Micron's Growth Story Intact",
        "summary": "美光MU股价约$1,090，Q3 FY2026营收$108.5亿同比+37%，GAAP EPS $2.52，Non-GAAP毛利率41.3%；Q4指引营收$112亿、EPS约$3.50；7月21日宣派息$0.15/股。AI驱动HBM及企业DRAM需求持续强劲。",
        "why": "存储超级周期受益方；Q4指引乐观支撑中线持仓；高位持有可辅以covered call收取权利金，降低持仓成本。",
        "source": "FX Leaders",
        "verified": False,
        "keywords": ["美光", "Micron", "MU", "HBM", "DRAM", "NAND", "存储", "内存"],
        "translated": False,
        "url": "https://www.fxleaders.com/news/2026/07/21/micron-mu-stock-news-ai-memory-demand-july-21-2026/"
    },
]

# Deduplicate against seen IDs
items = []
skipped = []
for c in candidates:
    item_id = make_id(c.get("url", ""), c.get("title", ""))
    if item_id not in seen_ids:
        c["id"] = item_id
        items.append(c)
    else:
        skipped.append(c.get("title", "")[:60])

print(f"\nNew items: {len(items)}")
print(f"Skipped (already seen): {len(skipped)}")
for s in skipped:
    print(f"  SKIP: {s}")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nWritten {len(items)} items to new_items.json")
for item in items:
    print(f"  [{item['tier']}] [{item['group']}] {item['title'][:70]}")
