import json, hashlib

def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

with open("/tmp/seen.json") as f:
    seen_data = json.load(f)
seen_ids = set(seen_data.get("ids", []))

candidates = [
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "20:30",
        "group": "大盘头条",
        "title": "June jobs report: US payrolls rose by 57,000, missing expectations",
        "summary": "美国6月非农就业仅新增5.7万人，远低于市场预期的11.5万，失业率降至4.2%但因劳动参与率滑至61.5%（2021年以来最低）而非真实改善。就业数据意外走弱大幅压低美联储7月加息概率。",
        "why": "非农弱势数据缓解加息担忧，推动港美股情绪回升，sell put整体安全边际改善；同日利好贵金属和科技股估值。",
        "source": "Yahoo Finance / BLS",
        "verified": True,
        "keywords": ["非农", "就业", "美联储", "macro"],
        "translated": False,
        "url": "https://finance.yahoo.com/economy/article/june-jobs-report-us-payrolls-rose-by-57000-missing-expectations-190000748.html"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "16:30",
        "group": "大盘头条",
        "title": "港股收评：恒指涨1.28% 科指涨1% 黄金股大涨 半导体板块调整",
        "summary": "7月3日港股收涨，恒生指数报23350.03点（涨1.28%），恒生科技指数涨1%，黄金股强势反弹；半导体板块受美股传导走弱。全市场逾3200只个股上涨。非农数据弱势提振市场情绪。",
        "why": "持仓港股科技股（腾讯、阿里、美团等）今日整体受益；黄金股大涨利好老铺黄金短线情绪。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["恒生指数", "港股", "大盘"],
        "translated": False,
        "url": "https://finance.sina.com.cn/stock/hkstock/marketalerts/2026-07-03/doc-inifpkay3629866.shtml"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "04:00",
        "group": "大盘头条",
        "title": "SanDisk Sinks 11%, Seagate Falls 7%, Micron Slides 4% on Memory Supply-Glut Fears",
        "summary": "7月1-2日美股存储芯片两日重挫：闪迪(SNDK)累计下跌24%进入技术性熊市，美光(MU)累跌逾15%，英特尔(INTC)跌超9%，费城半导体指数暴跌6%。触发因素：Meta有意出租过剩算力暗示AI资本开支见顶，叠加三星/SK海力士供给增加以及DRAM价格操纵集体诉讼。",
        "why": "持仓美光(MU)和闪迪(SNDK)直接受损；存储周期拐点担忧若坐实，须重新评估sell put行权价安全边际。",
        "source": "24/7 Wall St.",
        "verified": True,
        "keywords": ["SNDK", "MU", "INTC", "半导体", "存储芯片"],
        "translated": False,
        "url": "https://247wallst.com/investing/2026/07/02/sandisk-sinks-11-seagate-falls-7-micron-slides-4-on-memory-supply-glut-fears/"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "02:00",
        "group": "大盘头条",
        "title": "Fed Chief Kevin Warsh declines to hint at July rate decision, but says inflation 'too high'",
        "summary": "美联储主席Warsh在葡萄牙辛特拉央行论坛称通胀仍过高，维持3.5%-3.75%利率区间不变，拒绝给出7月前瞻指引。FOMC最新点阵图显示2026年PCE预期升至3.6%，市场约37.4%概率押注7月加息。",
        "why": "加息预期是隐含波动率核心驱动；非农走弱使加息概率下降，整体有利sell put策略；但通胀仍过高的措辞保留了鹰派尾险。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["美联储", "Fed", "利率", "通胀", "macro"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/01/kevin-warsh-ecb-forum-live-updates.html"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["US"],
        "time": "06:00",
        "group": "大盘头条",
        "title": "国际油价三连跌逼近$67，伊朗和谈推进、中东地缘溢价消退",
        "summary": "国际原油连续三日下跌逼近$67/桶，回吐战前水平。驱动因素：UAE霍尔木兹海峡出口恢复至390万桶/日，伊朗和谈在卡塔尔推进，EIA及IMF全年供过于求预期强化。",
        "why": "油价下跌降低通胀预期，间接有利于美联储维持宽松；同时利好下游消费与出行类持仓（携程、海底捞等）。",
        "source": "证券时报",
        "verified": True,
        "keywords": ["油价", "原油", "中东", "macro"],
        "translated": False,
        "url": "https://www.stcn.com/article/detail/3993734.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US", "HK", "A"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "China and US Target Tariff Reductions on Agricultural Products",
        "summary": "中美双方就农产品关税互降达成原则共识，中国商务部7月2日就此发表声明。同时美国贸易代表拟对中国加征12.5%强迫劳动附加关税（公众评论截至7月6日），贸易停战框架复杂性加剧。",
        "why": "农产品关税松动是贸易关系改善信号，利好中国出口相关和消费股；强迫劳动关税威胁仍存，跨境电商（拼多多Temu）风险未完全消除。",
        "source": "Bloomberg",
        "verified": True,
        "keywords": ["中美贸易", "关税", "macro"],
        "translated": False,
        "url": "https://www.bloomberg.com/news/articles/2026-07-02/china-and-us-target-tariff-reductions-on-agricultural-products"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "20:00",
        "group": "个股",
        "title": "Tesla (TSLA) Q2 2026 deliveries jump 25% to 480,126, beating estimates",
        "summary": "特斯拉Q2交付480,126辆（Model 3/Y占467,762辆），同比+25%，超华尔街预期约74,000辆，创公司单季最佳。Q2储能部署13.5 GWh（+40% YoY）。尽管交付超预期，股价盘后走弱。Q2财报电话会定于7月22日。",
        "why": "交付量大幅超预期增加Q2财报超预期概率；7月22日财报前期权IV通常上升，可考虑近月sell put捕获高权利金，但盘后走弱需注意情绪。",
        "source": "CNBC / Electrek / Bloomberg",
        "verified": True,
        "keywords": ["特斯拉", "Tesla", "TSLA", "交付量"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/02/tesla-tsla-q2-2026-vehicle-delivery-production.html"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["US", "HK"],
        "time": "01:00",
        "group": "个股",
        "title": "阿里巴巴与美国司法部签署6亿美元和解协议，解决违规化学品销售指控",
        "summary": "阿里巴巴与美国司法部达成6亿美元和解，终结2016-2024年平台违规销售处方药及化学品案件。与此同时，Rosen律所宣布就证券欺诈展开集体诉讼调查（源于Anthropic指控阿里蒸馏Claude事件）。BABA股价YTD已跌37%，年度股息约定于7月13日向ADS持有人派发。",
        "why": "6亿和解消除一项尾部法律风险；但证券欺诈调查与Claude蒸馏事件叠加，BABA/9988.HK短期多重利空，sell put须留足行权价安全垫。",
        "source": "美国司法部官网",
        "verified": True,
        "keywords": ["阿里巴巴", "Alibaba", "BABA", "司法部", "和解"],
        "translated": False,
        "url": "https://www.justice.gov/opa/pr/alibaba-group-and-aus-merchant-services-agree-pay-600-million-resolve-allegations-they"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["US", "HK"],
        "time": "09:00",
        "group": "个股",
        "title": "阿里巴巴7月10日起全面禁用Claude；Anthropic指控其通过2.5万账号发起2880万次AI蒸馏攻击",
        "summary": "Anthropic向美国参议员和白宫官员发函，指控阿里云旗下通义千问实验室利用近25,000个欺诈账号向Claude发起2880万次查询，以对抗蒸馏方式窃取软件工程和代理推理能力。阿里随即内部令全员于7月10日前卸载Claude全产品线（含Sonnet/Opus/Fable/Claude Code）。",
        "why": "涉嫌蒸馏攻击规模空前，叠加DOJ和解和证券调查，多重利空集中爆发；若监管跟进，对阿里AI战略和Qwen研发路径产生实质影响。",
        "source": "Bloomberg / Pandaily",
        "verified": True,
        "keywords": ["阿里巴巴", "Alibaba", "Anthropic", "Claude", "通义千问"],
        "translated": False,
        "url": "https://www.bloomberg.com/news/articles/2026-06-24/anthropic-accuses-alibaba-of-illicitly-accessing-its-ai-models"
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "22:00",
        "group": "个股",
        "title": "Circle (CRCL) Drops 15% After Open USD Stablecoin Launch by Stripe, Coinbase, Visa, BlackRock",
        "summary": "Stripe、Coinbase、Visa、Mastercard与BlackRock联合推出Open USD稳定币，向USDC发起正面竞争；Circle(CRCL)股价单日暴跌逾17%。Open USD核心差异：向合作伙伴分享储备金利息，直接冲击Circle依赖USDC利息（占营收96%）的盈利模式。美联储同步出台稳定币监管新框架。",
        "why": "竞争对手阵容极强（Visa/BlackRock/Coinbase/Stripe），USDC市场份额面临实质性侵蚀；Circle商业模式受根本性挑战，持仓需重新评估，sell put须大幅提高安全边际。",
        "source": "CoinDesk / Bitcoin Magazine",
        "verified": True,
        "keywords": ["Circle", "CRCL", "USDC", "稳定币", "stablecoin"],
        "translated": False,
        "url": "https://www.coindesk.com/business/2026/06/30/circle-slides-8-as-stripe-coinbase-and-blackrock-back-rival-stablecoin-network"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "10:00",
        "group": "个股",
        "title": "上半年金价跌去近三成，老铺黄金股价较峰值暴跌65%，存货危机加剧",
        "summary": "国际黄金从1月5598美元/盎司高点跌至6月底3962美元（跌幅近30%）。老铺黄金(6181.HK)股价从高点1065港元跌至约346港元（跌65%），市值蒸发逾1200亿港元。2025年底存货余额约160亿元（同比增近三倍），经营性现金流净流出68亿元。7月3日金价回升至约4200美元，港股黄金股盘中大涨。",
        "why": "金价大幅回撤与消费者买涨不买跌心理逆转双重压制，老铺黄金基本面压力持续；7月3日金价反弹带来短期缓解，可考虑高位布局covered call。",
        "source": "财新",
        "verified": True,
        "keywords": ["老铺黄金", "6181.HK", "黄金", "金价"],
        "translated": False,
        "url": "https://finance.caixin.com/2026-07-01/102459821.html"
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["A", "HK"],
        "time": "09:00",
        "group": "个股",
        "title": "工行、建行、交行等六大行宣布7月24日起关闭上金所个人贵金属交易业务",
        "summary": "工商银行、建设银行、交通银行、招商银行、广发银行等多家大型商业银行相继公告，将于2026年7月24日起关闭代理上海黄金交易所个人贵金属竞价交易及T+D业务（涉及Au99.99、Au(T+D)、Ag(T+D)等主要品种），建议存量持仓客户及时平仓出金。",
        "why": "银行通道关闭将压缩散户黄金投资渠道，7月24日前或有集中平仓抛售压力，不利于老铺黄金消费端需求；反映监管层对贵金属散户交易的系统性收紧。",
        "source": "工商银行官网 / 新浪财经",
        "verified": True,
        "keywords": ["老铺黄金", "黄金", "银行", "贵金属"],
        "translated": False,
        "url": "https://www.icbc.com.cn/page/1243135845339447296.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "21:00",
        "group": "个股",
        "title": "NVIDIA (NVDA) Leverages Balance Sheet to Support AI Chip Purchases; Vera Rubin Enters Full Production",
        "summary": "英伟达发布AI Compute Partner计划，通过财务支持帮助新兴云服务商购买GPU并分享营收。Vera Rubin平台进入全面量产，AWS/谷歌云/微软/Oracle将于下半年首批部署。Q1营收81.6亿美元（+85% YoY），80亿美元回购授权。",
        "why": "英伟达AI基础设施主导地位强化；AI Compute Partner可能创造新复购生态；Blackwell/Rubin周期持续利好NVDA长期估值，期权高IV适合sell put。",
        "source": "GuruFocus / NVIDIA Newsroom",
        "verified": True,
        "keywords": ["英伟达", "Nvidia", "NVDA", "GPU", "Rubin"],
        "translated": False,
        "url": "https://www.gurufocus.com/news/8942200/nvidia-nvda-leverages-balance-sheet-to-support-ai-chip-purchases"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "22:00",
        "group": "个股",
        "title": "Alphabet (GOOGL) Is Limiting Gemini AI Access As Cloud Capacity Tightens; Joins Dow Jones",
        "summary": "Alphabet正式加入道琼斯工业平均指数，股价当日涨约4%。因算力受限，Google Cloud已向Meta拒绝提供完整Gemini供货，Sundar Pichai称2026年基础设施支出将达1800-1900亿美元。Gemini月活跨越9亿用户，Google Cloud Q1营收200亿美元（+63% YoY）。",
        "why": "加入道指触发被动基金强制增持；算力受限反证需求旺盛，云业务高增速验证AI变现路径；建议继续持有，反弹后可酌情卖出covered call。",
        "source": "Yahoo Finance / MarketWise",
        "verified": True,
        "keywords": ["谷歌", "Google", "Alphabet", "GOOGL", "Gemini"],
        "translated": False,
        "url": "https://finance.yahoo.com/technology/ai/articles/alphabet-googl-limiting-gemini-ai-020811179.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["HK"],
        "time": "08:00",
        "group": "个股",
        "title": "SK Hynix reportedly eases HBM4 push as commodity DRAM margins surge; Nasdaq ADR set for July 10",
        "summary": "据Digitimes，SK海力士正放缓HBM4产能转换节奏，将更多资源转向普通DRAM（DDR5等），因DRAM价格飙升带来更高边际利润；2026年HBM供货已全部售罄，HBM全球市占率58%。SK海力士Nasdaq ADR将于7月10日上市，为国际投资者提供直投渠道。",
        "why": "HBM产能策略转向影响AI芯片供应预期；普通DRAM获利能力回升是整体存储板块正面信号；Nasdaq ADR上市为国际资金提供配置机会，关注南方两倍做多SKH ETF(7709.HK)。",
        "source": "Digitimes",
        "verified": False,
        "keywords": ["SK海力士", "SK Hynix", "HBM4", "DRAM"],
        "translated": False,
        "url": "https://www.digitimes.com/news/a20260624VL204/sk-hynix-hbm4-dram-hbm-samsung.html"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "20:00",
        "group": "个股",
        "title": "HSBC raises Intel stock price target to $200 on foundry upside; Intel 18A-P enters risk production",
        "summary": "英特尔18A-P制程（较18A性能提升9%、功耗降18%）进入风险量产阶段。HSBC将目标价从100美元翻倍升至200美元（维持买入），理由是将Foundry代工估值纳入模型。英伟达与软银已取得英特尔股权。7月23日Q2财报将是关键催化剂，届时预期披露正式代工合同和产能承诺。",
        "why": "英特尔代工基本面持续改善，股价年内涨幅已超250%；7月23日财报前IV可能上升，可考虑短期sell put，但需注意高涨幅后的获利回吐风险。",
        "source": "Investing.com",
        "verified": True,
        "keywords": ["英特尔", "Intel", "INTC", "代工", "foundry"],
        "translated": False,
        "url": "https://www.investing.com/news/analyst-ratings/hsbc-raises-intel-stock-price-target-to-200-on-foundry-upside-93CH-4773494"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "23:00",
        "group": "个股",
        "title": "PLTR Stock Jumps As AI And Defense Deals Pile Up",
        "summary": "Palantir Foundry成为美国陆军最高优先级现代化项目NGC2（下一代指挥控制）的云数据层，从原型转向大规模部署。同时与英伟达达成主权AI合作，将Nemotron模型集成至Palantir AIP平台，服务美国政府和关键基础设施。PLTR Q1营收16.33亿美元（+85% YoY），股价7月2日涨3%。",
        "why": "政府AI支出快速扩张是PLTR核心增长驱动；NGC2合同标志从销售期进入大规模部署，营收可见度提升；高IV下sell put策略可捕获可观权利金。",
        "source": "Timothy Sykes / Yahoo Finance",
        "verified": True,
        "keywords": ["Palantir", "PLTR", "政府合同", "国防AI"],
        "translated": False,
        "url": "https://www.timothysykes.com/news/palantir-technologies-inc-pltr-news-2026_07_02/"
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "16:00",
        "group": "个股",
        "title": "Interactive Brokers Group Reports Brokerage Metrics for June 2026",
        "summary": "Interactive Brokers 6月每日平均收入交易量(DARTs)达527万次（同比+53%，环比+6%），期末客户资产9303亿美元（同比+40%），保证金贷款余额1085亿美元（同比+67%）。Goldman Sachs和BMO Capital均上调IBKR目标价至109/105美元。Q2财报即将发布。",
        "why": "创纪录DARTs和客户资产直接推动佣金营收，加之期权/杠杆业务持续增长，Q2业绩超预期可能性高；持仓IBKR验证逻辑健康。",
        "source": "Yahoo Finance (IBKR官方公告)",
        "verified": True,
        "keywords": ["盈透证券", "Interactive Brokers", "IBKR"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/stocks/articles/interactive-brokers-group-reports-brokerage-160100580.html"
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "09:00",
        "group": "个股",
        "title": "蜜雪冰城在美首店落腳洛杉磯好萊塢 中國茶飲全球化再下一城",
        "summary": "蜜雪冰城(2097.HK)美国首店于6月20日在洛杉矶好莱坞开业，冰淇淋1.19美元、奶茶3.99美元起，延续极致性价比策略。公司同步推出H股激励计划，H1 2026营收同比+39.3%、净利+44.1%，积极推进美洲市场布局。",
        "why": "美国首店是蜜雪冰城进入高线国际市场的里程碑事件；若低价策略在美国成立，未来开店规模将支撑估值重估；关注下一步加盟/展店节奏。",
        "source": "Yahoo Finance HK / HKEXnews",
        "verified": True,
        "keywords": ["蜜雪冰城", "Mixue", "2097.HK", "出海"],
        "translated": False,
        "url": "https://hk.finance.yahoo.com/news/%E8%9C%9C%E9%9B%AA%E5%86%B0%E5%9F%8E%E5%9C%A8%E7%BE%8E%E9%A6%96%E5%BA%97%E8%90%BD%E8%85%B3%E6%B4%9B%E6%9D%89%E7%A3%AF%E5%A5%BD%E8%90%8A%E5%A1%A2-%E4%B8%AD%E5%9C%8B%E8%8C%B6%E9%A3%B2%E5%85%A8%E7%90%83%E5%8C%96%E5%86%8D%E4%B8%8B-%E5%9F%8E-075003171.html"
    },
    {
        "tier": 3,
        "lang": "en",
        "markets": ["US"],
        "time": "14:00",
        "group": "个股",
        "title": "Moomoo Launches Moomoo Engine, Unifying the Platform's Full Trading Workflow",
        "summary": "富途(FUTU)旗下moomoo平台推出付费产品Moomoo Engine，月费3.99美元（1000美元以上资产降至0.99美元/月），整合基本面引擎（AI简报+机构研报）、期权引擎（Level 2数据+策略实验室+Gamma敞口追踪+异常活动预警）及技术引擎（Level 3盘口+AI指标回测）。",
        "why": "期权工具专业化升级，对sell put/covered call策略者实用性高；付费产品推出有助于提升FUTU收入质量和ARPU；moomoo生态粘性增强。",
        "source": "Stocktitan / Yahoo Finance",
        "verified": True,
        "keywords": ["富途", "Futu", "FUTU", "moomoo", "期权"],
        "translated": False,
        "url": "https://www.stocktitan.net/news/FUTU/moomoo-launches-moomoo-engine-unifying-the-platform-s-full-trading-wskdcrzi63ys.html"
    },
]

# Compute IDs and filter seen
new_items = []
skipped = []
for item in candidates:
    iid = make_id(item["url"], item["title"])
    item["id"] = iid
    if iid in seen_ids:
        skipped.append((iid, item["title"][:40]))
    else:
        new_items.append(item)

print(f"Total candidates: {len(candidates)}")
print(f"Already seen (skipped): {len(skipped)}")
for s in skipped:
    print(f"  SKIP {s[0]} | {s[1]}")
print(f"New items to write: {len(new_items)}")
for it in new_items:
    print(f"  [{it['tier']}][{it['group']}] {it['id']} | {it['title'][:60]}")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(new_items, f, ensure_ascii=False, indent=2)
print(f"\nnew_items.json written with {len(new_items)} items.")
