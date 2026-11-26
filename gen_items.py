import json, hashlib

def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

items = [
    {
        "id": make_id("https://finance.sina.com.cn/roll/2026-11-26/doc-inizzftt3828986.shtml", ""),
        "tier": 1,
        "lang": "zh",
        "markets": ["US"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "美股感恩节前夕大幅震荡：纳指100一度跌破历史高位20%逼近技术性熊市，英伟达重挫近4%",
        "summary": "11月25日（感恩节前夕）美股大幅震荡，纳斯达克100指数盘中一度较历史收盘高点下跌逾20%，逼近技术性熊市门槛，随后低位买盘入场回升。三大指数收盘分化：道指涨0.33%，标普500跌0.25%，纳指跌0.62%。费城半导体指数大幅承压，英伟达收跌约4%（盘中一度跌近9%）；亚马逊跌3.14%。11月26日（感恩节）美股全日休市，27日提前至下午1点收盘，流动性偏低。",
        "why": "纳指100技术性熊市确认将压制科技股估值；感恩节前后低流动性放大波动，卖出期权的时间价值消耗在此期间加速，但Gamma风险也同步上升，须警惕隐波跳升侵蚀权利金收益。",
        "source": "新浪财经",
        "verified": True,
        "keywords": ["纳斯达克100", "英伟达", "芯片股", "美股", "感恩节"],
        "translated": False,
        "url": "https://finance.sina.com.cn/roll/2026-11-26/doc-inizzftt3828986.shtml",
        "published_date": "2026-11-26",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "id": make_id("https://bea.gov/news/2026/personal-income-and-outlays-october-2026", ""),
        "tier": 1,
        "lang": "zh",
        "markets": ["US"],
        "time": "09:30",
        "group": "大盘头条",
        "title": "美国10月核心PCE同比升3.3%创近3年新高，强化12月美联储加息预期",
        "summary": "美国商务部经济分析局（BEA）11月25日公布数据，10月核心PCE价格指数同比上涨3.3%（市场预期3.2%），创近3年来最高；整体PCE同比升3.8%（高于9月的3.6%），第三个月连续环比上涨0.3%。市场对美联储12月9–10日FOMC会议加息25个基点的预期显著升温。美联储主席Kevin Warsh在10月会议以10比2多数票维持利率在3.75%–4%不变（有两票主张立即加息）。",
        "why": "通胀持续高企确认了美联储年内再加息的基准情形，将压制科技股估值并可能拉高隐含波动率；对持有高估值科技股的投资者，12月加息前可考虑降低整体仓位风险。",
        "source": "BEA（美国经济分析局）",
        "verified": True,
        "keywords": ["PCE", "通胀", "美联储", "加息", "Kevin Warsh"],
        "translated": False,
        "url": "https://bea.gov/news/2026/personal-income-and-outlays-october-2026",
        "published_date": "2026-11-25",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "id": make_id("https://www.bloomberg.com/news/articles/2026-11-25/s-p-says-it-may-downgrade-nvidia-s-ratings-on-governance-worries", ""),
        "tier": 1,
        "lang": "zh",
        "markets": ["US"],
        "time": "10:00",
        "group": "大盘头条",
        "title": "S&P将英伟达AA评级列入负面信用观察，管治风险与出口管控隐患引发降级警告",
        "summary": "标普全球评级11月25日将英伟达AA级发行人评级及高级无担保债务评级列入负面信用观察，观察期约90天。理由包括：董事会独立性薄弱、长期任职董事多、缺乏正式继任计划，以及中国出口管控合规存在潜在不确定性。若下调最多一档至AA-，仍属投资级。英伟达5年期信用违约互换（CDS）利差升至历史高点147个基点。",
        "why": "信用降级警告将压制机构资金流入，同时治理争议拉高隐含波动率（NVDA盘中波动近9%印证）；卖出NVDA Put的投资者须评估隐波跳升是否需要调整行权价或平仓。",
        "source": "Bloomberg / S&P Global",
        "verified": False,
        "keywords": ["英伟达", "NVDA", "S&P", "信用评级", "管治"],
        "translated": False,
        "url": "https://www.bloomberg.com/news/articles/2026-11-25/s-p-says-it-may-downgrade-nvidia-s-ratings-on-governance-worries",
        "published_date": "2026-11-25",
        "still_developing": False,
        "cross_ref": "https://uk.finance.yahoo.com/news/p-global-warns-nvidia-credit-205320758.html"
    },
    {
        "id": make_id("https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000090/nov23pressrelease.htm", ""),
        "tier": 2,
        "lang": "zh",
        "markets": ["US"],
        "time": "11:00",
        "group": "大盘头条",
        "title": "英伟达SEC 8-K正式确认：董事会恢复黄仁勋CEO职务，同步成立国家安全与出口管控监督委员会",
        "summary": "英伟达11月23日在SEC提交8-K文件，官方宣布董事会已恢复黄仁勋担任总裁、CEO及董事职务，称已获美国政府高层背书、确认复职不构成国家安全风险；董事会主席Harvey Jones留任，Colette Kress重回CFO职位。公司同日宣布成立国家安全与出口管控监督委员会，由独立董事Suzanne Nora Johnson主持；针对黄仁勋的调查将继续进行至完成。",
        "why": "延续报道：黄仁勋11月12日辞职，11月23日SEC 8-K正式确认复职，11月25日标普已因此事采取信用评级行动，事件仍在发酵；公司治理不确定性短期内将持续压制股价估值。",
        "source": "英伟达（SEC 8-K 2026-11-23）",
        "verified": True,
        "keywords": ["英伟达", "NVDA", "黄仁勋", "CEO", "国家安全"],
        "translated": False,
        "url": "https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000090/nov23pressrelease.htm",
        "published_date": "2026-11-23",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "id": make_id("https://longbridge.com/en/news/306832692", ""),
        "tier": 2,
        "lang": "zh",
        "markets": ["US", "HK"],
        "time": "08:30",
        "group": "大盘头条",
        "title": "中概股金龙指数涨1.87%，BOSS直聘大涨逾12%、理想汽车涨11%，中国资产逆势走强",
        "summary": "11月25日美股盘中，尽管整体市场受科技股重创，纳斯达克中国金龙指数逆市上涨1.87%。BOSS直聘（Kanzhun）大涨逾12%，理想汽车涨约11%（同日公布Q3业绩），中国资产整体表现稳健，形成与美股主板的明显分化。",
        "why": "港股美股中概股在美股整体下行背景下逆势走强，说明机构资金对中国资产有独立信心；持有港股消费与科技标的的投资者无需过度担忧本轮美国芯片股调整的传染效应。",
        "source": "Longbridge",
        "verified": False,
        "keywords": ["中概股", "金龙指数", "BOSS直聘", "理想汽车", "中国资产"],
        "translated": False,
        "url": "https://longbridge.com/en/news/306832692",
        "published_date": "2026-11-26",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "id": make_id("https://www.sec.gov/Archives/edgar/data/0001791706/000110465926131768/tm2630657d1_ex99-1.htm", ""),
        "tier": 1,
        "lang": "zh",
        "markets": ["US", "HK"],
        "time": "09:00",
        "group": "个股",
        "title": "理想汽车Q3 2026业绩超预期：收入288亿元人民币高于指引上限，非GAAP亏损收窄68.6%，股价涨约11%",
        "summary": "理想汽车（LI/2015.HK）2026年11月25日公布Q3业绩：总收入约288亿元人民币（约43亿美元），超出公司指引266–280亿元上限；Q3交付99,964辆汽车，接近指引上限；GAAP净亏损3.097亿元人民币，非GAAP净亏损1.129亿元人民币，同比大幅收窄68.6%，优于此前市场预期。业绩推动美股ADS盘后上涨约11%。",
        "why": "亏损持续快速收窄，收入超预期——若Q4毛利率进一步改善或交付量提速，可能触发估值重估；股价大涨11%意味着持有或卖出Put的投资者均需重新评估行权价合理性。",
        "source": "理想汽车（SEC 6-K 2026-11-25）",
        "verified": True,
        "keywords": ["理想汽车", "LI", "2015.HK", "电动车", "Q3业绩"],
        "translated": False,
        "url": "https://www.sec.gov/Archives/edgar/data/0001791706/000110465926131768/tm2630657d1_ex99-1.htm",
        "published_date": "2026-11-25",
        "still_developing": False,
        "cross_ref": ""
    }
]

# Print for review
for item in items:
    print(f"ID: {item['id']} | Tier: {item['tier']} | {item['title'][:60]}")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nWrote {len(items)} items to new_items.json")
