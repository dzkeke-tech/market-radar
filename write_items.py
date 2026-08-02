import json, hashlib

def make_id(url, title=""):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

items = [
    # ===== 大盘头条 =====
    {
        "id": make_id("https://www.cnbc.com/2026/07/30/amazon-amzn-q2-earnings-report-2026.html"),
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "08:30",
        "group": "大盘头条",
        "title": "Amazon Q2 2026: Revenue $200.6B (+20% YoY), AWS surges 36.7% to $42.2B—fastest in 18 quarters; stock jumps 9% after hours",
        "summary": "亚马逊Q2营收$2006亿（+20%）大幅超预期$1961亿；AWS云业务营收$422亿（+36.7%），为18个季度最快增速；EPS $5.75远超$1.81预期；全年资本开支上调至$2200亿。盘后股价涨逾9%。",
        "why": "AWS加速增长确认AI基础设施需求拐点；$2200亿资本开支上调利好英伟达GPU及SK海力士HBM供应链；延续报道：财报后市场持续消化大云厂商AI投资周期对半导体供应商的拉动效应。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["Amazon", "AMZN", "AWS", "cloud", "AI"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/30/amazon-amzn-q2-earnings-report-2026.html",
        "published_date": "2026-07-30",
        "still_developing": True
    },
    {
        "id": make_id("https://www.cnbc.com/2026/07/30/apple-earnings-live-updates.html"),
        "tier": 1,
        "lang": "zh",
        "markets": ["US"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "苹果Q3财报：营收$1094亿超预期，但Q4供应约束警告致股价盘后暴跌8-10%；摩根大通/摩根士丹利下调目标价",
        "summary": "苹果Q3营收$1094亿（+16%）、EPS $2.02均超预期；Services营收$307亿略低于预估$312亿；CEO库克警告Q4 DRAM/NAND供应约束将显著恶化，Q4指引9-11%增长低于市场12%预期。摩根大通目标价从$345降至$340，摩根士丹利降至$360，股价7月31日盘初跌约10%，蒸发市值逾$4300亿。",
        "why": "供应链DRAM/NAND紧缺将压缩Q4毛利；隐含波动率扩大，sell put策略行权价需重新评估；延续报道：7月31日分析师集体下调、股价继续消化，市场对内存通胀叠加高利率的滞胀担忧升温。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["AAPL", "Apple", "苹果", "iPhone", "supply constraint", "services"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/30/apple-earnings-live-updates.html",
        "published_date": "2026-07-30",
        "still_developing": True
    },
    {
        "id": make_id("https://www.cnbc.com/2026/07/29/fed-rate-decision-july-2026.html"),
        "tier": 1,
        "lang": "zh",
        "markets": ["US", "HK", "A"],
        "time": "03:00",
        "group": "大盘头条",
        "title": "美联储FOMC 7月29日连续第五次维持利率3.5-3.75%不变，3票反对创近年新高，内部分歧扩大",
        "summary": "美联储FOMC以9票赞成、3票反对，连续第五次维持联邦基金利率目标区间在3.5%-3.75%不变；反对票数为近年最高，显示部分委员倾向加息，内部对通胀路径存在明显分歧。",
        "why": "延续报道：高利率路径持续压制成长股估值；结合苹果供应约束引发的内存通胀担忧，市场对滞胀情景定价概率上升；本周科技/消费股隐波偏高，sell put需关注利率端扰动风险。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["美联储", "FOMC", "利率", "Fed", "interest rate", "货币政策"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/07/29/fed-rate-decision-july-2026.html",
        "published_date": "2026-07-29",
        "still_developing": True
    },
    {
        "id": make_id("https://finance.sina.com.cn/tech/roll/2026-08-01/doc-inikuwea8911645.shtml"),
        "tier": 2,
        "lang": "zh",
        "markets": ["US"],
        "time": "10:00",
        "group": "大盘头条",
        "title": "美股一周大戏：苹果短暂超越英伟达后，因财报暴跌被反超逾3500亿美元",
        "summary": "苹果于7月27-28日短暂超越英伟达成为全球最高市值公司，结束英伟达272个交易日连续第一；但7月31日因Q3供应约束警告，AAPL单日跌约7.35%，英伟达涨2.93%重夺第一，两者市值差距扩大至约3500亿美元。",
        "why": "科技板块估值逻辑领头羊从消费硬件（苹果）回归AI算力（英伟达）；苹果暴跌引发内存/NAND价格连锁担忧，对英伟达、SK海力士、美光等持仓有直接参考意义。",
        "source": "新浪财经",
        "verified": False,
        "keywords": ["Apple", "Nvidia", "AAPL", "NVDA", "市值", "苹果", "英伟达"],
        "translated": False,
        "url": "https://finance.sina.com.cn/tech/roll/2026-08-01/doc-inikuwea8911645.shtml",
        "published_date": "2026-08-01",
        "still_developing": False
    },
    {
        "id": make_id("https://www.cls.cn/detail/2441856"),
        "tier": 1,
        "lang": "zh",
        "markets": ["US"],
        "time": "05:30",
        "group": "大盘头条",
        "title": "费城半导体指数暴涨超8%：泛林+20%、美光+14%、AMD+13%，纳斯达克突破25000点",
        "summary": "7月30日美股，费城半导体指数大涨逾8%；泛林半导体涨超20%，应用材料涨超15%，美光科技+14%，AMD+13%，英特尔+12%，ASML及台积电各涨超7%；纳斯达克综合指数触及25000点（日内+2.48%）。",
        "why": "延续报道：7月30日半导体板块爆发后，苹果财报披露DRAM/NAND供应紧缺担忧，美光次日跌5.9%，板块内部出现分化；持有美光、SK海力士及半导体相关衍生品仓位需密切追踪HBM/NAND供需动态。",
        "source": "财联社",
        "verified": True,
        "keywords": ["费城半导体", "SOX", "AMD", "美光", "Micron", "半导体", "芯片", "LRCX"],
        "translated": False,
        "url": "https://www.cls.cn/detail/2441856",
        "published_date": "2026-07-30",
        "still_developing": True
    },
    # ===== 个股 =====
    {
        "id": make_id("https://news.skhynix.com/en/q2-2026-business-results/"),
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "SK Hynix Q2 2026: Record revenue KRW 79.32T (+257% YoY), 76% operating margin, but missed estimates; shares plunge ~9% to near 52-week low",
        "summary": "SK海力士Q2营收79.32万亿韩元（+257% YoY，+51% QoQ），创历史新高；营业利润60.54万亿韩元（76%利润率）。但实际营收低于分析师预期，股价单日跌近9%至约$130，接近52周低位$128.38。公司宣布下半年大幅扩充HBM4产能，已与10大客户签长期供货协议。",
        "why": "延续报道：历史性营收却跌至年低，市场正在对HBM单价下行及下半年供应过剩前景重新定价；持有南方两倍做多SK海力士ETF（CSOP，7709.HK）需高度警惕；HBM4产能扩大将压制HBM3E单价，但AI算力需求2027-28年可见度仍强。",
        "source": "SK Hynix Newsroom",
        "verified": True,
        "keywords": ["SK海力士", "SK Hynix", "HBM", "HBM4", "DRAM", "存储", "memory"],
        "translated": False,
        "url": "https://news.skhynix.com/en/q2-2026-business-results/",
        "published_date": "2026-07-29",
        "still_developing": True
    },
    {
        "id": make_id("https://finance.yahoo.com/markets/stocks/articles/expect-palantir-q2-2026-earnings-124258336.html"),
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "09:00",
        "group": "个股",
        "title": "Palantir Q2 2026 earnings on August 3 after close: analysts expect $1.8B revenue (+80% YoY); options imply 12% post-earnings swing",
        "summary": "Palantir明日（8月3日）盘后公布Q2 2026财报；华尔街预期营收约$18亿（同比+80%），调整后EPS $0.35；期权市场隐含双向约12%波幅，高于历史平均盈后摆幅7.4%。股价现报约$122，年初至今累计下跌约30%；Q1曾实现+85% YoY营收增长。",
        "why": "Palantir是AI平台商业化落地的旗舰标的；盈后12%隐含摆幅为做多波动率策略提供窗口，同时也是sell put需规避的高风险节点；若Q2延续强劲增速将是股价重要催化剂。",
        "source": "Yahoo Finance",
        "verified": False,
        "keywords": ["Palantir", "PLTR", "AIP", "AI平台", "政府合同", "earnings"],
        "translated": False,
        "url": "https://finance.yahoo.com/markets/stocks/articles/expect-palantir-q2-2026-earnings-124258336.html",
        "published_date": "2026-08-01",
        "still_developing": False
    },
    {
        "id": make_id("https://finance.sina.com.cn/tech/digi/2026-07-30/doc-inikqupy9660465.shtml"),
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "14:00",
        "group": "个股",
        "title": "小米澎程技术发布会：雷军宣布SU7/YU7累计交付突破70万辆，同步发布昆仑全新技术架构",
        "summary": "7月30日小米澎程技术发布会，雷军宣布小米SU7和YU7累计交付量突破70万辆；并发布昆仑技术架构（昆仑平台、昆仑超级增程、昆仑全域安全），为下一代澎程增程车型（兼具SUV通过性与近似房车内部空间）奠定技术基础。",
        "why": "延续报道：70万辆里程碑+昆仑架构是小米汽车阶段性技术叙事转折；增程路线覆盖更大市场，有助于中期维持1810.HK多头情绪；关注本周港股交投是否跟进雷军媒体效应。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["小米", "Xiaomi", "SU7", "YU7", "小米汽车", "雷军", "澎程"],
        "translated": False,
        "url": "https://finance.sina.com.cn/tech/digi/2026-07-30/doc-inikqupy9660465.shtml",
        "published_date": "2026-07-30",
        "still_developing": True
    }
]

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Written {len(items)} items to new_items.json")
for item in items:
    print(f"  [{item['tier']}] {item['group']} | {item['published_date']} | id={item['id']}")
    print(f"       verified={item['verified']} still={item.get('still_developing',False)}")
    print(f"       {item['title'][:70]}")
