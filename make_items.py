#!/usr/bin/env python3
import json, hashlib

def make_id(url, title=''):
    s = (url or title or '').strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]

items = [
  {
    "id": make_id("https://www.21jingji.com/article/20261024/herald/475a067b1a53256d60f7e7993a1430fb.html"),
    "tier": 1,
    "lang": "zh",
    "markets": ["US"],
    "time": "09:00",
    "group": "大盘头条",
    "title": "美联储10月27-28日议息会议在即：市场预期维持利率不变概率逾90%，12月加息押注升温",
    "summary": "CME联储观察10月24日数据显示，美联储10月28日维持3.75%-4.00%利率不变的概率约90.6%，加息25基点概率约9.4%；对12月加息押注更重，概率约67.5%。美联储主席沃什（Kevin Warsh）此前表示不预先透露决议方向，会议结果存在不确定性。10年期美债收益率近期升至约5.14%。",
    "why": "本周最大宏观事件，结果直接影响美股估值与波动率水平；FOMC前短期隐含波动率偏高，Sell Put策略宜在结果落地后操作，避免被spike消耗。",
    "source": "21世纪经济报道",
    "verified": True,
    "keywords": ["美联储", "宏观", "macro"],
    "translated": False,
    "url": "https://www.21jingji.com/article/20261024/herald/475a067b1a53256d60f7e7993a1430fb.html",
    "published_date": "2026-10-24",
    "still_developing": False,
    "cross_ref": ""
  },
  {
    "id": make_id("https://www.cnbc.com/2026/10/22/meta-stock-q3-earnings-free-cash-flow.html"),
    "tier": 1,
    "lang": "en",
    "markets": ["US"],
    "time": "07:30",
    "group": "大盘头条",
    "title": "Meta stock sinks nearly 7% as AI spend pushes free cash flow negative",
    "summary": "Meta Q3 2026: revenue $64.6B (+26% YoY), beat ~$63.3B estimates. Full-year capex guidance narrowed to $135-145B (raised low end from $130B). Q3 capex ~$34.9B pushed free cash flow negative for the first time since 2012. Q4 revenue guidance $73-76B above expectations. Stock fell ~7% to ~$648.85 as market focused on surging AI investment costs.",
    "why": "AI资本开支大幅扩张拖累自由现金流转负，引发市场对AI投资回报的质疑；触发本周科技股整体卖压，Nvidia、Alphabet等同步受压；对所有持仓科技股的AI capex预期需同步审视。",
    "source": "CNBC",
    "verified": True,
    "keywords": ["科技", "AI", "宏观"],
    "translated": False,
    "url": "https://www.cnbc.com/2026/10/22/meta-stock-q3-earnings-free-cash-flow.html",
    "published_date": "2026-10-22",
    "still_developing": False,
    "cross_ref": ""
  },
  {
    "id": make_id("https://www.scmp.com/tech/big-tech/article/3334162/nvidia-google-ai-chip-rivalry-escalates-report-meta-talks"),
    "tier": 1,
    "lang": "en",
    "markets": ["US"],
    "time": "08:00",
    "group": "大盘头条",
    "title": "Nvidia-Google AI chip rivalry escalates on report of Meta talks",
    "summary": "Reports emerged that Meta Platforms is in talks to spend billions on Google TPU chips for data centers in 2027, challenging Nvidia GPU dominance. Nvidia shares fell approximately 4-6% on the news (to ~$212). Meta already holds a multi-year TPU rental deal with Google and supply agreements with AMD. The development signals major hyperscalers diversifying AI chip sourcing.",
    "why": "英伟达（NVDA）个股利空：大客户Meta分流算力采购至谷歌TPU，压制英伟达数据中心收入增速预期；同时利好谷歌（GOOGL）云，正当Alphabet于10月28日发布Q3财报。",
    "source": "SCMP",
    "verified": False,
    "keywords": ["英伟达", "Nvidia", "NVDA", "谷歌", "Google", "GOOGL"],
    "translated": False,
    "url": "https://www.scmp.com/tech/big-tech/article/3334162/nvidia-google-ai-chip-rivalry-escalates-report-meta-talks",
    "published_date": "2026-10-22",
    "still_developing": False,
    "cross_ref": ""
  },
  {
    "id": make_id("https://www.21jingji.com/article/20261023/herald/0f49e084ebe2673776274d32118811b8.html"),
    "tier": 2,
    "lang": "zh",
    "markets": ["HK", "A"],
    "time": "16:30",
    "group": "大盘头条",
    "title": "反攻，港股飘红！A股多板块异动，创业板指涨4.16%两市成交额1.96万亿",
    "summary": "10月23日A股大幅反弹：沪指收涨0.89%，深证指数涨2.79%，创业板指涨4.16%，两市成交额约1.96万亿元人民币。港股同步走强，恒生科技指数收涨2.05%，恒生指数收涨0.69%重回23000点上方。人形机器人、半导体、光通信等成长板块领涨。",
    "why": "前日（10月22日）港科网股与A股因监管及美股AI卖压大幅下挫后技术性反弹；恒指重回23000点对持仓港股标的短期情绪有支撑，但FOMC前市场不稳定，反弹可持续性待观察。",
    "source": "21世纪经济报道",
    "verified": True,
    "keywords": ["宏观", "消费", "科技"],
    "translated": False,
    "url": "https://www.21jingji.com/article/20261023/herald/0f49e084ebe2673776274d32118811b8.html",
    "published_date": "2026-10-23",
    "still_developing": False,
    "cross_ref": ""
  },
  {
    "id": make_id("https://www.cls.cn/detail/2381190"),
    "tier": 2,
    "lang": "zh",
    "markets": ["A"],
    "time": "10:30",
    "group": "大盘头条",
    "title": "A股人形机器人板块持续爆发：多股批量涨停，宇树科技盘中涨超10%",
    "summary": "10月20日A股人形机器人概念板块持续大幅走高，多只相关股票触发涨停，长盈精密盘中20cm涨停，宇树科技总市值接近2200亿元。行业数据：2026年上半年全球人形机器人收入5.4亿美元、销量3.6万台，前五名均为中国企业；TrendForce预计中国人形机器人产量2026年同比增长94%。",
    "why": "延续报道：人形机器人板块在A股持续活跃，从概念炒作向量产业绩兑现转变；10月23日大盘反弹中该板块亦领涨，短期交易热度仍高；对供应链（电机/精密件/传感器）相关持仓有参考意义。",
    "source": "财联社",
    "verified": True,
    "keywords": ["科技", "technology", "人形机器人"],
    "translated": False,
    "url": "https://www.cls.cn/detail/2381190",
    "published_date": "2026-10-20",
    "still_developing": True,
    "cross_ref": ""
  },
  {
    "id": make_id("https://www.cnbc.com/2026/10/21/tesla-tsla-q3-2026-earnings-report.html"),
    "tier": 1,
    "lang": "en",
    "markets": ["US"],
    "time": "21:00",
    "group": "个股",
    "title": "Tesla Q3 2026 beats estimates; Musk says SpaceX merger is 'a good idea', deal committees formed",
    "summary": "Tesla Q3 2026: adjusted EPS $0.48 vs ~$0.43 estimated; revenue $28.05B. Auto gross margin ex-credits 18.1% (up from 16.3% prior quarter). Energy storage deployments 13.7 GWh (2nd-best quarter). Free cash flow fell 62% YoY to $1.53B. Separately, Musk said on SpaceX Oct 20 earnings call that a Tesla-SpaceX merger would be 'a good idea.' Both companies formed special committees of independent directors. SpaceX Q3: revenue $14.6B (+161%), first quarterly profit since IPO.",
    "why": "特斯拉（TSLA）业绩超预期，汽车毛利率持续修复；SpaceX合并消息是重大估值催化剂——若交易成形将大幅重估TSLA市值（合并至12月3日股东大会前）。Barclays预计年底前宣布合并，TSLA隐含波动率料持续偏高，Sell Put/Covered Call需审慎管理被赋值风险。",
    "source": "CNBC",
    "verified": True,
    "keywords": ["特斯拉", "Tesla", "TSLA", "马斯克", "Musk"],
    "translated": False,
    "url": "https://www.cnbc.com/2026/10/21/tesla-tsla-q3-2026-earnings-report.html",
    "published_date": "2026-10-21",
    "still_developing": True,
    "cross_ref": ""
  },
]

# Load seen IDs
with open('/tmp/seen.json') as f:
    seen_ids = set(json.load(f)['ids'])

print("=== Item Preview ===")
for item in items:
    status = "SEEN(skip)" if item["id"] in seen_ids else "NEW"
    print(f"{status} | {item['id']} | tier={item['tier']} | {item['title'][:55]}")

print(f"\nTotal: {len(items)} items")

with open("new_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("\nnew_items.json written successfully.")
