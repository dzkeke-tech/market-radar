import json, hashlib

def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

with open('/tmp/seen.json') as f:
    seen_ids = set(json.load(f)['ids'])

candidates = [
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US", "HK", "A"],
        "time": "14:00",
        "group": "大盘头条",
        "title": "Fed keeps rates at 3.75%-4.00%; two members dissented for a hike; Warsh says politics played no role",
        "summary": "美联储10月28日维持联邦基金利率目标区间3.75%-4.00%不变，符合市场预期。两名委员持异议倾向立即加息。美联储主席Kevin Warsh表示9月加息效果与经济数据支持暂停，并否认与中期选举相关。",
        "why": "美联储动向直接影响全球风险资产定价；9月已加息25bp。CME FedWatch显示12月再加息概率约84.5%（Babypips 2026-10-30援引CME FedWatch数据）。Sell Put策略需关注12月会议前隐含波动率走势及行权价选择。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["美联储", "利率", "Kevin Warsh", "加息"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/10/28/fed-meeting-today-live-updates.html",
        "published_date": "2026-10-28",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "08:30",
        "group": "大盘头条",
        "title": "U.S. Q3 GDP advance estimate: 3.4% annualized beats consensus 3.2%; Sept core PCE 3.1% YoY fuels December hike bets",
        "summary": "美国BEA发布Q3 GDP初值：实际GDP年化增速3.4%（高于Q2的2.2%及市场预期3.2%）。9月核心PCE同比3.1%（8月3.0%），整体PCE同比3.6%（8月3.4%），能源价格为主要驱动，均符合市场预期。",
        "why": "GDP超预期+PCE加速共同强化12月加息预期（CME FedWatch约84.5%，Babypips 2026-10-30援引）。加息预期升温将压制高估值科技股；Sell Put持仓需注意尾部风险，关注12月FOMC前隐含波动率动态。",
        "source": "美国经济分析局(BEA)",
        "verified": True,
        "keywords": ["GDP", "PCE", "通胀", "美联储", "加息", "宏观"],
        "translated": False,
        "url": "https://www.bea.gov/data/gdp/gross-domestic-product",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "16:00",
        "group": "大盘头条",
        "title": "Alphabet (GOOGL) Shares Drop 12.5% After Q3 Earnings Miss, Dragging Tech Sector Lower",
        "summary": "谷歌母公司Alphabet Q3业绩双双不及预期：调整后EPS $2.67（预期$3.02），营收$127.58B（预期$128.22B），为近四年来首次顶底线同时未达预期。自由现金流转负，系20余年上市以来首次。股价应声跌12.5%。",
        "why": "谷歌暴跌拖累整个科技板块，纳指当日收跌1.38%；自由现金流转负反映AI资本开支急剧扩张带来的盈利压力，波及AI供应链估值预期。短期内持有科技相关Sell Put仓位需防范板块联动下行风险。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["谷歌", "Alphabet", "GOOGL", "财报", "科技股"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/10/28/alphabet-googl-earnings-q3-2026.html",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "16:30",
        "group": "大盘头条",
        "title": "Intel stock plunges 21% as Q4 guidance misses consensus; chipmaker blames PC slowdown",
        "summary": "英特尔Q3营收$16.5B超预期，但Q4指引极度令人失望：营收指引$15-16B远低于分析师预期$17.1B，Non-GAAP EPS指引$0.25远低于预期$0.43，公司归因于PC需求放缓。股价盘后暴跌21%。",
        "why": "英特尔Q4指引大幅低于预期，显示PC市场需求超预期疲弱。数据中心AI业务(+78% YoY)强劲但难以抵消客户端拖累；英伟达/AMD相对受益于份额转移逻辑。INTC持仓需重新评估行权价合理性。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["英特尔", "Intel", "INTC", "财报", "PC", "半导体", "晶圆代工"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/10/29/intel-intc-q3-earnings-report-2026-.html",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "17:00",
        "group": "大盘头条",
        "title": "Amazon Q3 2026: EPS misses at $1.89 vs $1.97 est; AWS revenue surges 39% YoY to $45.98B",
        "summary": "亚马逊Q3营收$201.9B（同比+12%，低于预期）；EPS $1.89（预期$1.97，未达预期）。亮点：AWS营收$45.98B同比增速39%，约五年来最快；运营利润$28.1B创历史新高，运营利润率13.9%。Q4营收指引$240-247B。",
        "why": "AWS增速加速（39%超预期）确认AI云需求强劲，长期利好英伟达/SK海力士等AI供应链；但广告收入$19.6B低于预期约$20.8B预期，自由现金流转负（资本开支$75.9B/季），股价盘后仍承压。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["亚马逊", "Amazon", "AMZN", "AWS", "财报", "云计算"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/10/29/amazon-amzn-q3-earnings-report-2026.html",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "20:00",
        "group": "大盘头条",
        "title": "Binance suffers ~$6.3B security breach, largest crypto hack to date; Tether and Circle freeze over $1.8B in stablecoins",
        "summary": "Binance遭遇迄今最大规模加密货币安全事故，约63亿美元资产受影响，近30亿美元被冻结，疑因DevOps工程师笔记本电脑遭入侵。Tether冻结逾9.71亿美元USDT，Circle冻结约8亿至8.23亿美元USDC，Binance暂停充提款。",
        "why": "全球最大加密交易所Binance遭史上最大规模黑客攻击，加密市场系统性风险事件。Circle(CRCL)盘后大幅走低，USDC稳定性受短期冲击关注（Q3业绩将于11月4日公布）；持有相关加密资产或CRCL仓位需密切跟踪事态进展。",
        "source": "CoinDesk",
        "verified": True,
        "keywords": ["Binance", "加密货币", "黑客", "USDC", "USDT", "稳定币", "Circle"],
        "translated": False,
        "url": "https://www.coindesk.com/business/2026/10/29/binance-loses-over-6-billion-in-the-largest-crypto-hack-to-date",
        "published_date": "2026-10-29",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["HK"],
        "time": "09:00",
        "group": "个股",
        "title": "泡泡玛特Q3营收同比下滑45%-50%，LABUBU热潮退去；摩根大通降级至减持",
        "summary": "泡泡玛特(9992.HK)2026年三季度业务公告：整体收益同比下降45%-50%，亚太/美洲/欧洲海外市场跌幅均超50%（美洲跌70-75%最大）；中国内地线上渠道跌45-50%，线下跌5-10%。摩根大通随即将评级下调至减持。",
        "why": "Labubu出圈爆发后首次季度大幅负增长，IP潮玩生意模型的脆弱性暴露；股价持续走低，隐含波动率或扩大。已有Sell Put仓位须检视行权价，此时更适合以Covered Call锁定收益而非继续裸卖Put，防范进一步下行。",
        "source": "21世纪经济报道",
        "verified": True,
        "keywords": ["泡泡玛特", "Pop Mart", "9992.HK", "Labubu", "财报", "摩根大通"],
        "translated": False,
        "url": "https://m.21jingji.com/article/20261029/herald/942094b1a2f222bf0f7c592883ded1f7.html",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK", "US"],
        "time": "10:00",
        "group": "个股",
        "title": "SK hynix Q3 2026: Record KRW 104.6T revenue, 80% operating margin as HBM4 mass production begins",
        "summary": "SK海力士Q3营收达KRW 104.6万亿（同比+328%，环比+32%），历史首次突破百万亿韩元大关；营业利润率80%创历史纪录。HBM4于Q3开始量产并出货，DRAM价格季内上涨约20%+。公司表示供应约束将持续至2030年。",
        "why": "SK海力士HBM4量产启动、利润率创纪录，确认AI存储芯片超级周期延续，直接利好南方两倍做多SK海力士ETF(7709.HK)及美光/闪迪等存储仓位；供需格局长期偏紧，支持中期持有逻辑。",
        "source": "SK海力士 SEC 6-K",
        "verified": True,
        "keywords": ["SK海力士", "SK Hynix", "HBM4", "HBM", "存储芯片", "财报", "DRAM"],
        "translated": False,
        "url": "https://www.sec.gov/Archives/edgar/data/0002120882/000119312526420934/d413172d6k.htm",
        "published_date": "2026-10-28",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["A"],
        "time": "10:00",
        "group": "大盘头条",
        "title": "A股三季报：3490家公司净利润同比增11.5%，AI算力产业链领跑",
        "summary": "截至10月28日，Wind数据统计3490家A股公司前三季度业绩：营收合计25.37万亿元同比+8.55%，归母净利润1.96万亿元同比+11.53%。AI算力链（存储芯片、覆铜板、服务器、PCB等）、生物医药、基础化工景气度领先；176家公司净利润翻倍。",
        "why": "A股三季报整体超预期，AI算力产业链高增长验证AI资本开支周期延续。半导体/算力相关A股基本面走强，值得关注其H股对应标的估值重估机会。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["A股", "三季报", "AI算力", "净利润", "半导体"],
        "translated": False,
        "url": "https://finance.sina.com.cn/roll/2026-10-29/doc-iniwwifc5336352.shtml",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "18:00",
        "group": "个股",
        "title": "Nvidia responds to report Jensen Huang was targeted by Chinese intelligence, says allegations investigated and debunked",
        "summary": "针对媒体报道称黄仁勋曾是中国情报目标一事，英伟达(NVDA)公开回应称相关转移指控已经调查并被驳斥。同期有报道称ByteDance/阿里/腾讯合计订购逾350亿美元英伟达RTX PRO 5500芯片，但英伟达警告因产能及出口规则限制可能无法完全交付。",
        "why": "英伟达否认间谍指控有助消除短期声誉风险；中国科技巨头350亿美元订单显示AI算力需求极旺，但出口管制仍是核心不确定因素。当前NVDA期权隐含波动率较高，Sell Put需关注地缘政治尾部风险。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["英伟达", "Nvidia", "NVDA", "黄仁勋", "Jensen Huang", "AI芯片", "出口管制"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/10/29/nvidia-jensen-huang-chinese-intelligence-asset.html",
        "published_date": "2026-10-29",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "11:00",
        "group": "个股",
        "title": "腾讯正式成为APEC 2026峰会战略合作伙伴；花旗重申买入，目标价755港元",
        "summary": "腾讯(00700.HK)已正式成为2026年APEC峰会（11月18-19日，深圳）战略合作伙伴，将提供AI翻译、媒体服务及移动支付支持。花旗10月26日研报认为此事件是腾讯AI与云能力的重要外部验证，维持买入评级，目标价755港元，认为近期股价回调提供更好入场机会。",
        "why": "延续报道：腾讯10月23日宣布APEC合作伙伴关系，花旗于10月26日发布研报跟进（距今4天，still_developing）。花旗目标价755港元较当前约385港元存在较大上行空间，对中长期Sell Put仓位（看涨腾讯）策略逻辑具有参考价值。",
        "source": "富途牛牛",
        "verified": False,
        "keywords": ["腾讯", "Tencent", "00700", "APEC", "花旗", "买入", "AI"],
        "translated": False,
        "url": "https://news.futunn.com/hk/post/1002253976/citi-tencent-s-00700-selection-as-a-strategic-partner-for",
        "published_date": "2026-10-26",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "tier": 3,
        "lang": "zh",
        "markets": ["A"],
        "time": "09:30",
        "group": "大盘头条",
        "title": "A股三大指数集体大幅低开，科技成长股受海外财报拖累承压",
        "summary": "2026年10月30日早盘，A股三大指数集体大幅低开，创业板指跌幅居前，CPO、覆铜板、激光雷达等科技成长板块领跌；受前一日美股英特尔暴跌21%、谷歌跌12%等科技股巨震拖累，市场情绪偏谨慎。",
        "why": "海外科技龙头财报不及预期引发A股科技成长板块开盘大幅走低；短期波动对A股科技ETF和持仓有影响，中期来看若三季报数据持续向好基本面逻辑未变，可关注超跌机会。",
        "source": "新浪财经",
        "verified": False,
        "keywords": ["A股", "科技股", "低开", "创业板", "覆铜板", "CPO"],
        "translated": False,
        "url": "https://k.sina.com.cn/article_7857201856_1d45362c001908szqs.html",
        "published_date": "2026-10-30",
        "still_developing": False,
        "cross_ref": ""
    },
]

new_items = []
batch_ids = set()
for item in candidates:
    item_id = make_id(item['url'], item['title'])
    item['id'] = item_id
    if item_id in seen_ids:
        print(f"SKIP (seen): {item_id} - {item['title'][:60]}")
    elif item_id in batch_ids:
        print(f"SKIP (dup url): {item_id} - {item['title'][:60]}")
    else:
        batch_ids.add(item_id)
        new_items.append(item)
        print(f"ADD: {item_id} - {item['title'][:60]}")

with open('new_items.json', 'w', encoding='utf-8') as f:
    json.dump(new_items, f, ensure_ascii=False, indent=2)

print(f"\nTotal new items: {len(new_items)}")
