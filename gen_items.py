import json, hashlib

seen = json.load(open('/tmp/seen.json'))
seen_ids = set(seen['ids'])

def make_id(url, title):
    s = (url or title or "").strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

items = [
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["A", "HK"],
        "time": "09:30",
        "group": "大盘头条",
        "title": "国家统计局：10月CPI同比上涨0.7%，PPI同比上涨5.7%",
        "summary": "2026年10月全国居民消费价格同比上涨0.7%，涨幅较上月回落0.2个百分点；工业生产者出厂价格同比上涨5.7%，涨幅较上月扩大0.7个百分点，PPI环比回落0.5个百分点。核心CPI同比+0.8%。",
        "why": "通胀数据直接影响货币政策预期：CPI涨幅收窄、PPI同比扩张，显示工业需求仍强但终端消费偏温，A股与港股顺周期板块及消费标的值得关注；sell put布局需防通胀数据超预期引发市场波动。",
        "source": "新华网",
        "verified": True,
        "keywords": ["CPI", "PPI", "宏观", "通胀", "货币政策"],
        "translated": False,
        "url": "https://www.news.cn/fortune/20261109/decb1630fe0f4b03b1eedaed46676cc1/c.html",
        "published_date": "2026-11-09",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "zh",
        "markets": ["A", "HK"],
        "time": "09:00",
        "group": "大盘头条",
        "title": "国常会首提完善资本市场稳市机制，央行配合推互换便利工具",
        "summary": "11月6日国务院常务会议提出完善资本市场稳市机制，要求增强股市内在稳定性。央行随后开展1000亿元互换便利操作，证监会优化护盘式回购规则，政策组合拳持续加码，市场对制度化稳市安排预期升温。",
        "why": "制度化的稳市安排将长期降低A/H股尾部风险，对以sell put为主的期权策略构成隐含波动率压缩因素；短期市场支撑增强，但需观察增量资金落地节奏，关注11月9日A股开盘后的量能承接。",
        "source": "21世纪经济报道",
        "verified": True,
        "keywords": ["资本市场", "稳市机制", "宏观", "政策", "监管", "央行"],
        "translated": False,
        "url": "https://www.21jingji.com/article/20261109/herald/7359458aaeb2899c01366af1c6616394.html",
        "published_date": "2026-11-09",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "08:00",
        "group": "大盘头条",
        "title": "Nvidia board launches independent probe into CEO Jensen Huang amid Chinese spy allegations",
        "summary": "Nvidia's board announced on November 8 it would open an independent investigation into CEO Jensen Huang following press reports that he was allegedly targeted by a Chinese intelligence effort. Huang acknowledged an extramarital affair in a staff email and said he would cooperate fully; a committee of independent directors has engaged outside counsel.",
        "why": "英伟达CEO涉嫌被中国情报策反事件是当前AI板块最大尾部风险：若调查升级导致Huang离任，可能触发NVDA大幅杀跌并带动整个AI供应链连锁波动；持有NVDA相关期权头寸须关注隐含波动率急升风险，建议暂缓新建卖put仓位并审视现有行权价安全边际。",
        "source": "CNBC",
        "verified": True,
        "keywords": ["英伟达", "Nvidia", "NVDA", "黄仁勋", "AI芯片", "地缘", "监管"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/11/08/nvidia-jensen-huang-investigation-china-spy.html",
        "published_date": "2026-11-08",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "09:30",
        "group": "大盘头条",
        "title": "港股11月9日：恒指高开0.59%，科技股领涨，远信储能IPO首日涨逾120%",
        "summary": "11月9日港股开盘恒生指数涨0.59%报24626点，恒生科技指数涨1.02%，科网股与汽车股高开，PCB、光通信及存储半导体板块活跃；远信储能首日高开逾114%，午间涨幅超120%。午间收盘恒指涨0.2%，市场分歧扩大。",
        "why": "港股今日反弹主要由科技板块驱动，配合国常会稳市政策信号释放正面情绪；关注持仓的腾讯、美团、小米等盘中走势，科指上涨有利于已卖出put的浮盈保护。",
        "source": "新浪财经",
        "verified": False,
        "keywords": ["恒指", "港股", "科技股", "市场行情", "宏观"],
        "translated": False,
        "url": "https://finance.sina.com.cn/stock/hkstock/marketalerts/2026-11-09/doc-iniycfna6563730.shtml",
        "published_date": "2026-11-09",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["US"],
        "time": "16:00",
        "group": "大盘头条",
        "title": "Wall Street's worst week in 18 months: Nasdaq -5.5%, VIX surges 70% on Nov 5 as AI spending fears mount",
        "summary": "On November 5, the Nasdaq Composite fell 5.52%, its biggest one-day drop in a year and its first correction since April 2025. The VIX surged approximately 70%, its largest single-session spike in nearly two years. Stocks partially rebounded on November 6, with the Nasdaq recovering 1.09%, but the index logged a weekly loss of roughly 5.5%.",
        "why": "AI板块系统性抛售引发隐含波动率急升——对持有以科技股为标的sell put仓位构成直接冲击；本轮调整同时带出英伟达CEO调查等尾部风险，建议审视技术股名单的Delta敞口和行权价安全边际；关注周内能否企稳。",
        "source": "CNBC",
        "verified": False,
        "keywords": ["美股", "纳斯达克", "AI", "宏观", "market", "VIX", "波动率"],
        "translated": False,
        "url": "https://www.cnbc.com/2026/11/08/stock-market-today-live-updates.html",
        "published_date": "2026-11-08",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "tier": 1,
        "lang": "en",
        "markets": ["HK", "US"],
        "time": "10:00",
        "group": "个股",
        "title": "Oracle scraps $7 billion AI chip leasing deal with Tencent after U.S. government pressure",
        "summary": "Oracle canceled a roughly $7 billion, five-year agreement under which it would have leased about 100,000 AI chips to Tencent via Southeast Asian data centers, the Financial Times reported on November 4. U.S. officials raised concerns about the deal with Oracle; Guangdong provincial officials separately urged Tencent to use domestic chips. No official statement has been issued by Oracle, Tencent, or the White House.",
        "why": "此事件直接压缩腾讯AI基础设施海外算力获取路径，是腾讯中期AI竞争力的重要负面信号；结合11月18日Q3财报前瞻（析出AI投入幅度），建议关注事件对腾讯期权隐含波动率的潜在推升效应，待核实后酌情调整covered call行权价设置。",
        "source": "Bloomberg",
        "verified": False,
        "keywords": ["腾讯", "Tencent", "0700.HK", "AI芯片", "地缘", "美国出口管制", "Oracle"],
        "translated": False,
        "url": "https://www.bloomberg.com/news/articles/2026-11-04/oracle-scraps-7-billion-deal-to-lease-chips-to-tencent-ft-says",
        "published_date": "2026-11-04",
        "still_developing": True,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "zh",
        "markets": ["HK"],
        "time": "13:18",
        "group": "个股",
        "title": "腾讯混元Hy4正式版发布：770B参数，首次支持视觉理解与Computer Use",
        "summary": "腾讯于11月4日发布混元Hy4正式版，参数量770B，首次引入视觉理解能力并支持Computer Use，定价与preview版持平（输入6元/百万tokens）。腾讯表示将近期开源模型权重，低成本版Hy4 Flash即将发布，Hy5预计年底至明年初推出。",
        "why": "混元AI能力持续迭代有助腾讯企业服务变现潜力，但里昂等券商预警AI投入加速将拖累Q3利润（预测净利同比-9%）；11月18日Q3业绩将验证AI支出与盈利节奏，对sell put仓位而言，业绩前需控制Delta敞口。",
        "source": "财联社",
        "verified": True,
        "keywords": ["腾讯", "混元", "AI", "大模型", "Tencent"],
        "translated": False,
        "url": "https://www.cls.cn/detail/2525324",
        "published_date": "2026-11-04",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "11:00",
        "group": "个股",
        "title": "Musk: Tesla to wind down Cybertruck production at Giga Texas by mid-2027 to make room for Cybercab",
        "summary": "Elon Musk announced on X on November 6 that Tesla will wind down Cybertruck production at its Texas gigafactory around mid-2027 to free capacity for the Cybercab robotaxi. U.S. Cybertruck sales fell approximately 48% in 2025. The Cybercab has been providing autonomous rides in Austin since September 2026 and is set to expand to Dallas.",
        "why": "特斯拉放弃低销量高成本的Cybertruck、押注Cybercab Robotaxi转型，是正面估值重构信号；2027年中产能释放时间节点及Cybercab商业化速度将成为TSLA期权行权价设置的关键参考变量，建议关注Q4业绩对Cybercab发展路线的更新指引。",
        "source": "SCMP",
        "verified": True,
        "keywords": ["特斯拉", "Tesla", "TSLA", "Cybertruck", "Cybercab", "Robotaxi", "马斯克"],
        "translated": False,
        "url": "https://www.scmp.com/news/world/united-states-canada/article/3373598/teslas-musk-pulls-plug-cybertruck-robotaxi-push-after-years-poor-sales",
        "published_date": "2026-11-06",
        "still_developing": False,
        "cross_ref": ""
    },
    {
        "tier": 2,
        "lang": "en",
        "markets": ["US"],
        "time": "08:00",
        "group": "个股",
        "title": "Circle beats Q3 2026 earnings estimates on soaring USDC transaction volume",
        "summary": "Circle reported Q3 2026 revenue of $865 million, up 17% year-over-year and ahead of estimates, with net income from continuing operations of $226 million. USDC on-chain transaction volume surged 49% to $13.9 trillion in the quarter; average USDC in circulation was $73.3 billion, up 18% year-over-year. Circle also cut approximately 5% of staff.",
        "why": "USDC交易量+49%、环流量+18%，稳定币基础设施需求持续强劲；裁员5%体现利润率优化意图，有助提升EPS质量；对持有CRCL的投资者，业绩超预期支撑当前估值，但需关注裁员重组后的中期增长指引及稳定币监管立法进展（GENIUS Act）。",
        "source": "CoinDesk",
        "verified": True,
        "keywords": ["Circle", "CRCL", "USDC", "稳定币", "stablecoin", "GENIUS Act"],
        "translated": False,
        "url": "https://www.coindesk.com/business/2026/11/04/circle-beats-earnings-and-revenue-estimates-on-soaring-usdc-transaction-volume",
        "published_date": "2026-11-04",
        "still_developing": False,
        "cross_ref": ""
    }
]

# Add IDs
for item in items:
    item['id'] = make_id(item['url'], item['title'])

# Check for seen duplicates
new_items = []
skipped = []
for item in items:
    if item['id'] in seen_ids:
        skipped.append(item['id'] + ' | ' + item['title'][:50])
    else:
        new_items.append(item)

print(f"Total candidates: {len(items)}")
print(f"Already seen (skipped): {len(skipped)}")
for s in skipped:
    print(f"  SKIP: {s}")
print(f"New items to publish: {len(new_items)}")
for item in new_items:
    print(f"  [{item['tier']}] {item['group']} | {item['id']} | {item['title'][:60]}")

# Write
with open('new_items.json', 'w', encoding='utf-8') as f:
    json.dump(new_items, f, ensure_ascii=False, indent=2)
print("\nnew_items.json written.")
