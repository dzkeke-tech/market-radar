#!/usr/bin/env python3
import json, hashlib

def make_id(url, title=""):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

items = [
    # --- 大盘头条 Tier 1 ---
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK", "US", "A"],
        "time": "10:00",
        "group": "大盘头条",
        "title": "三星电子Q2 2026预披露：营业利润89.4万亿韩元（约$584亿），同比增约19倍，但股价收跌6.9%",
        "summary": "三星Q2营业利润89.4万亿韩元（约584亿美元），营收171万亿韩元，均大超预期，但股价因市场担忧AI资本支出可持续性而在首尔收跌约6.9%。此为三星有史以来最高单季度利润。",
        "why": "Samsung业绩爆发但股价跳水印证"业绩兑现获利了结"格局；AI存储需求峰值担忧蔓延至港股/A股半导体板块，SK海力士(HBM持仓)受牵连，需关注期权波动率抬升。",
        "source": "Samsung Newsroom / CNBC",
        "verified": True,
        "keywords": ["三星", "Samsung", "HBM", "存储芯片"],
        "translated": False,
        "url": "https://news.samsung.com/global/samsung-electronics-announces-earnings-guidance-for-second-quarter-2026"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["A"],
        "time": "16:00",
        "group": "大盘头条",
        "title": "A股7月8日：三大指数集体重挫，上证跌1.37%、深证跌3.17%、创业板跌3.84%，科技/存储板块领跌",
        "summary": "受三星业绩股价跳水及英伟达供应链担忧双重冲击，A股今日大幅下行，德明利、北京君正、江波龙等存储相关标的跌幅居前，半导体存储指数重创。",
        "why": "A股科技/消费赛道整体情绪受压，需评估持仓组合的beta风险；存储/半导体板块可观察是否有超跌反弹机会，结合sell put策略时机。",
        "source": "新浪财经（四大证券报）",
        "verified": True,
        "keywords": ["A股", "上证指数", "创业板", "存储器"],
        "translated": False,
        "url": "https://finance.sina.com.cn/stock/y/2026-07-08/doc-inifzwqf1428353.shtml"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["US", "HK"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "英伟达官方否认Kyber NVL144延迟至2028年：芯片路线图完好，供应链股恐慌性下跌后修复",
        "summary": "SemiAnalysis 7月5-6日报告称英伟达Kyber NVL144机架系统因PCB正交背板制造难题延至2028年，导致Ibiden等PCB供应商暴跌。英伟达随即声明路线图完好，股价回升约1%，Goldman维持买入评级。",
        "why": "Nvidia路线图若无恙则供应链股前期超跌属过度反应；HBM/GPU供给持续紧张逻辑不变，但事件揭示下游制造复杂性已成新风险点，英伟达相关期权波动率阶段性走高。",
        "source": "WccfTech / CNBC",
        "verified": True,
        "keywords": ["英伟达", "Nvidia", "NVDA", "Rubin", "GPU", "AI芯片"],
        "translated": False,
        "url": "https://wccftech.com/nvidia-quashes-rubin-kyber-rack-delay-rumors-says-chip-roadmap-is-intact/"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK", "A"],
        "time": "09:00",
        "group": "大盘头条",
        "title": "央行行长潘功胜：债券通南向通额度扩至8000亿元，将持续提高外汇储备在港资产配置比例",
        "summary": "潘功胜7月7日在香港货币与固定收益峰会宣布，南向通年度投资额度由5000亿元提至8000亿元，纳入回购支持并扩展至港元/人民币债券及澳门市场；同时明确支持更多优质国企民企赴港上市及发债，加大外汇储备在港配置。",
        "why": "央行政策性利好直接提升港股市场资金面和信心，对富途/盈透等港美股券商及赴港上市潜在受益公司估值均有正面推动；南向通扩容也拓宽内地资金配置港股通道。",
        "source": "21财经（21世纪经济报道）",
        "verified": True,
        "keywords": ["央行", "债券通", "南向通", "港股", "外汇储备"],
        "translated": False,
        "url": "https://m.21jingji.com/article/20260707/herald/12089137f41b2604577e6b45c35b5c06.html"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "16:30",
        "group": "大盘头条",
        "title": "港股7月7日收盘：恒生指数跌0.51%，恒生科技指数跌0.75%，半导体存储与医药板块领跌",
        "summary": "港股延续谨慎震荡格局，恒生指数早盘低开后震荡收跌，科技指数跌幅较大。半导体存储板块受三星预警拖累大幅下挫；荣昌生物、三生制药等医药股跌超6%。",
        "why": "港股整体情绪偏弱，持仓核心标的（腾讯、美团、泡泡玛特等）短期受市场情绪压制；建议关注恒生科技ETF隐含波动率，评估sell put入场时机。",
        "source": "证券时报",
        "verified": True,
        "keywords": ["恒生指数", "港股", "恒生科技"],
        "translated": False,
        "url": "https://www.stcn.com/article/detail/4002346.html"
    },
    # --- 个股 Tier 1 ---
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "07:30",
        "group": "个股",
        "title": "腾讯以港币约107亿元减持快手约15亿美元，股权降至9.37%，不再为大股东；快手股价跌10.4%",
        "summary": "腾讯旗下子公司以HK$43.25/股出售约2.73亿快手股份（今年港股最大宗交易），套现约15亿美元，持股比例从15.68%降至9.37%，触发失去主要股东地位门槛，剩余股份90天禁售。快手随即暴跌10.4%。",
        "why": "腾讯AI转型步伐加快（Q1资本支出319亿元同比+63%），套现成熟投资加速投入AI；此举对快手短期造成流动性冲击，腾讯本身战略聚焦度提升，90天禁售解除后仍有减持风险需关注。",
        "source": "Bloomberg / SCMP",
        "verified": True,
        "keywords": ["腾讯", "Tencent", "0700.HK", "快手", "AI"],
        "translated": False,
        "url": "https://www.scmp.com/tech/big-tech/article/3359664/kuaishou-shares-tumble-tencent-slashes-stake-after-us3b-kling-ai-deal"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "10:30",
        "group": "个股",
        "title": "SK Hynix to Debut on Nasdaq July 10 via $29.4B ADR—Largest Foreign ADR Ever; Reference Price Cut by ~$1B on HBM Oversupply Fears",
        "summary": "SK Hynix confirmed its Nasdaq ADR (ticker: SKHY) listing for July 10, targeting ~$29.4B (surpassing Alibaba's 2014 $21.8B record), with BoA/Citi/Goldman/JPMorgan as underwriters. The July 6 regulatory filing lowered the reference price and cut the fundraising target by ~$1B amid concerns over HBM oversupply and Samsung's massive capacity expansion.",
        "why": "SK海力士ADR上市提供美股存储标的配置路径，但参考价下调暗示机构对HBM供给预期趋保守；南方两倍做多SKHynix ETF持仓的隐含波动率料于7月10日前后大幅抬升，应审慎管理期权delta风险。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["SK海力士", "SK Hynix", "HBM", "HBM3E", "HBM4", "DRAM", "CSOP"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/06/24/sk-hynix-nasdaq-adr-listing-south-korea.html"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Tesla Q2 2026 Deliveries Jump 25% YoY to 480,126—Best Q2 Ever; Robotaxi Launches in Miami Without Safety Monitors",
        "summary": "Tesla delivered 480,126 vehicles in Q2 2026 (+25% YoY, best Q2 ever, beating consensus), with energy deployment of 13.5 GWh (+41% YoY). Tesla also expanded Robotaxi to Miami with no human safety monitor aboard—a first. Q2 financial results are scheduled for July 22 after market close.",
        "why": "交付超预期叠加Robotaxi无安全员城市扩张，FSD商业化里程碑有望推动TSLA估值重估；7月22日财报前隐含波动率持续抬升，是执行sell put/covered call策略的窗口期。",
        "source": "CNBC / Bloomberg",
        "verified": True,
        "keywords": ["特斯拉", "Tesla", "TSLA", "Robotaxi", "FSD", "自动驾驶"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/02/tesla-tsla-q2-2026-vehicle-delivery-production.html"
    },
    # --- 大盘头条 Tier 2 ---
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "Hyperscalers Raise 2026 AI Capex to ~$750B Combined; Meta Lifts Guidance to $125-145B, Spending Set to Top $1T in 2027",
        "summary": "Amazon (~$200B), Alphabet (~$175-185B), Meta ($125-145B) and Microsoft (~$120B) collectively commit ~$750B to AI infrastructure in 2026, up ~67% YoY. All hyperscalers report supply-constrained rather than demand-constrained markets; spending is forecast to exceed $1T in 2027.",
        "why": "AI资本支出超预期是英伟达/SK海力士/美光等AI芯片持仓最直接的逻辑支撑；谷歌、Meta中长期广告变现效率也将随AI投入增强，利好组合核心科技敞口。",
        "source": "Yahoo Finance / Futurum",
        "verified": False,
        "keywords": ["AI", "数据中心", "资本支出", "hyperscaler"],
        "translated": False,
        "url": "https://finance.yahoo.com/sectors/technology/articles/hyperscalers-hit-700-billion-2026-111243744.html"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK", "US", "A"],
        "time": "07:00",
        "group": "大盘头条",
        "title": "中东局势趋缓：布伦特原油从3月峰值逾$126大幅回落至约$72，霍尔木兹海峡恢复通航",
        "summary": "美以对伊朗军事行动曾使3月布伦特原油飙至逾126美元；随后随霍尔木兹海峡重开大幅回落，当前约$72。但特朗普最新表态维持对伊强硬立场，地缘尾部风险仍在。美联储因此维持利率于3.5-3.75%的高位。",
        "why": "油价大幅回落缓解全球通胀压力，有利美联储评估降息时机；同时降低消费类持仓（餐饮/旅游等）的能源成本端压力，对海底捞、携程等标的偏正面。",
        "source": "Gulf Times / IQI Global",
        "verified": False,
        "keywords": ["油价", "中东", "地缘风险", "布伦特"],
        "translated": False,
        "url": "https://www.gulf-times.com/article/728426/business/analysts-dial-down-oil-forecasts-as-hormuz-reopening-eases-supply-concerns/amp"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["A"],
        "time": "10:00",
        "group": "大盘头条",
        "title": "宇树科技科创板IPO注册生效，104天审核创科创板最快纪录，"人形机器人第一股"即将挂牌",
        "summary": "宇树科技（人形+四足机器人）于3月20日递交申请，7月2日获证监会批复，全程仅104天创科创板最快纪录。计划募资42.02亿元，对应估值约420亿元，预计7月中下旬正式挂牌，将成A股首只人形机器人纯标股。",
        "why": "具身智能/机器人板块重大催化，宇树上市将带动相关ETF和概念股炒作；A股科技赛道重要里程碑事件，留意上市首日行情对机器人板块整体情绪的提振效应。",
        "source": "21财经",
        "verified": True,
        "keywords": ["人形机器人", "具身智能", "科创板", "IPO"],
        "translated": False,
        "url": "https://m.21jingji.com/article/20260707/herald/54f500b88749975777d40c75bcec201a.html"
    },
    # --- 个股 Tier 2 ---
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["US"],
        "time": "08:00",
        "group": "个股",
        "title": "拼多多Temu遭欧盟开罚2亿欧元（不安全违禁产品），须提交整改方案；PDD年初至今股价跌逾33%",
        "summary": "欧盟委员会以Temu平台出售不安全和违禁产品为由对PDD开罚2亿欧元，并要求提交整改行动计划。叠加Q1营收增速降至11% YoY（低于预期）及百亿供应链升级投入，PDD股价年初至今累跌约33.9%。",
        "why": "欧盟监管处罚压制Temu出海增长逻辑，合规整改成本将进一步压缩盈利；配合Q1业绩低于预期，PDD估值修复路径不畅，暂不宜执行sell put策略。",
        "source": "South China Morning Post",
        "verified": True,
        "keywords": ["拼多多", "PDD", "Temu", "跨境电商"],
        "translated": False,
        "url": "https://www.scmp.com/tech/big-tech/article/3359060/pdd-embraces-chinas-city-future-after-bruising-regulatory-clash-and-record-fine"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "08:00",
        "group": "个股",
        "title": "EU Top Court Upholds EUR 4.1B Android Antitrust Fine Against Alphabet/Google; EU Opens New AI Competition Probe",
        "summary": "The ECJ issued a final ruling July 2 confirming the EUR 4.1B Android antitrust fine against Alphabet, pushing cumulative EU fines to nearly EUR 11B. Separately, the EU opened a new probe into Google's AI practices potentially distorting competition for publishers and content creators.",
        "why": "监管压力持续叠加（罚款+新调查），对Alphabet短期股价和广告收入构成压制；但GOOGL已从5月高点回调12%+，核心搜索+云业务护城河稳固，结合估值收缩后中长期仍具配置价值。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["谷歌", "Google", "Alphabet", "GOOGL", "Gemini", "反垄断"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/02/alphabet-google-android-eu-antitrust-fine-4-1-billion-euro-appeal.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Micron (MU) FY Q3 Revenue $41.46B (+346% YoY), NAND +361%—Stock Drops 5.7% From Record $1,255 High on Sell-the-News",
        "summary": "Micron's fiscal Q3 2026 revenue hit $41.46B (vs. $35.43B consensus), NAND revenue +361% YoY to $9.9B with ~1/3 of NAND volume under long-term agreements. Yet shares fell ~5.7% to ~$929 pre-market July 7 in a classic sell-the-news reversal from the all-time high of $1,255.",
        "why": "美光超预期业绩后股价仍大幅回调，与三星相似的兑现卖出格局，暗示市场对存储周期见顶担忧升温；持有两倍做多美光产品头寸需警惕短期回调，评估减仓或买保护的必要性。",
        "source": "The Motley Fool",
        "verified": False,
        "keywords": ["美光", "Micron", "MU", "NAND", "DRAM", "两倍做多美光"],
        "translated": False,
        "url": "https://www.fool.com/investing/2026/07/07/why-micron-stock-just-crashed/"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:30",
        "group": "个股",
        "title": "Palantir Wins US Army NGC2 Contract; Partners With Nvidia for Sovereign Government AI Platform; Q1 Revenue +85% YoY",
        "summary": "US Army selected Palantir Foundry as core cloud data layer for NGC2 modernization (moving to wide deployment). Palantir and Nvidia jointly launched a platform for secure government/critical-infrastructure AI workloads using Nvidia Nemotron models. Q1 2026 revenue was $1.63B (+85% YoY), with FY2026 guidance raised to +71% growth.",
        "why": "美国政府/国防AI合同持续落地，与英伟达战略绑定深化护城河；PLTR年初至今虽跌约27%，但Q1业绩超预期加上合同驱动逢低sell put可积累成本，等待Q2财报催化。",
        "source": "StocksToTrade / SEC EDGAR",
        "verified": False,
        "keywords": ["Palantir", "PLTR", "AIP", "Foundry", "国防AI", "政府合同"],
        "translated": False,
        "url": "https://stockstotrade.com/news/palantir-technologies-inc-pltr-news-2026_07_01/"
    },
]

# Assign IDs
for item in items:
    item["id"] = make_id(item["url"], item["title"])

# Verify uniqueness
ids = [it["id"] for it in items]
dupes = [id for id in set(ids) if ids.count(id) > 1]
if dupes:
    print(f"WARNING: Duplicate IDs found: {dupes}")
else:
    print("All IDs unique.")

# Write output
with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nWritten {len(items)} items to new_items.json")
tier_counts = {}
group_counts = {}
for it in items:
    tier_counts[it['tier']] = tier_counts.get(it['tier'], 0) + 1
    group_counts[it['group']] = group_counts.get(it['group'], 0) + 1
    print(f"  [T{it['tier']}] [{it['group']}] {it['id']} | {it['title'][:70]}")

print(f"\nTier distribution: {tier_counts}")
print(f"Group distribution: {group_counts}")
print(f"大盘头条 count: {group_counts.get('大盘头条', 0)} (min required: 5)")
