# 财经雷达 Market Radar — 搭建说明

每天 08:00 / 13:00 / 18:00，云端自动抓取并整理港股·美股·A股新闻，推到一个你能加到 iPhone 主屏的网页。

## 仓库里的文件
- `index.html` — 仪表盘页面（已配好主屏图标/全屏）
- `manifest.webmanifest` + `icon-*.png` — 主屏 App 图标与启动配置
- `data.json` — 新闻数据（由云端 Routine 每次覆盖；现在是占位）
- `keywords.json` — **关键词库 / 筛选标准**，可随时改
- `sources.json` — **信源白名单**（官方披露优先，其次中英媒体）
- `seen.json` — **去重**存储（Routine 自动维护）
- `routine-prompt.md` — 粘贴进云端 Routine 的指令

---

## 一、建仓库并传文件（约 3 分钟）
1. 登录 GitHub → 右上「+」→ **New repository**。
2. 名字填 `market-radar`；选 **Public**（免费版的 GitHub Pages 只支持公开仓库；本阶段仓库里只有新闻，无敏感信息）。
3. 建好后点 **Add file → Upload files**，把本文件夹里**所有文件**拖进去 → **Commit changes**。

> 隐私提醒：等接 IBKR 持仓时，**持仓不会进这个公开仓库**——我们会用单独的私密渠道，你的仓位不会公开。

## 二、开启 GitHub Pages（约 1 分钟）
1. 仓库 **Settings → Pages**。
2. Source 选 **Deploy from a branch**；Branch 选 **main**，文件夹 **/(root)** → **Save**。
3. 等 1–2 分钟，页面顶部会出现你的网址：
   **https://dzkeke-tech.github.io/market-radar/**

## 三、加到 iPhone 主屏
1. 用 **Safari** 打开上面的网址。
2. 点底部分享图标 → **添加到主屏幕** → 完成。
3. 现在主屏多了「财经雷达」图标，点开就是最新一期。Mac 上把同一网址存书签即可。

> 现在打开会看到一条「等待首次运行」占位 —— 说明托管成功，等 Routine 第一次跑完就会变成真实新闻。

## 四、建云端 Routine（核心）
1. 打开 **claude.ai/code/routines**（或桌面 App → Code → New task → **New remote task**）。
2. 新建 routine：
   - **Repository**：挂载你刚建的 `market-radar`。
   - **Prompt**：把 `routine-prompt.md` 里「===」之间的全部内容粘进去。
   - **Model**：选 **Opus 4.8**。
   - **Schedule**：分别建三档 `08:00`、`13:00`、`18:00`。
   - **时区**：默认 **America/Los_Angeles**（你所在的太平洋时间）。若你更想按市场时间锚定，改成 **Asia/Hong_Kong** 即可——**这一点你确认一下想用哪个**。
   - **网络/工具**：确保环境**允许联网**并开启 web 搜索（否则抓不到新闻）。
3. **分支设置**：Routine 默认只允许推送到 `claude/` 前缀分支。因为 Pages 从 `main` 取数，需允许它把 **data.json / seen.json 推到 main**。它只改这两个数据文件，风险很低。

跑通后，每次运行结束它会覆盖 `data.json` 并 push，Pages 自动刷新，你主屏图标点开就是最新的。

## 五、日常调优
- 想加/减关键词：直接在 GitHub 上编辑 `keywords.json`（手机也能改）。
- 某来源不靠谱：把它加到 `sources.json` 的 `demote`。
- 都是下次运行即生效，无需改代码。

## 下一步（待办）
- **IBKR 持仓同步**：本地跑 IBKR Client Portal Web API（只读子集）导出持仓 → 作为动态关键词。登录认证由你本人完成；代码与步骤我另外给。
- **收藏跨设备同步**：当前收藏每台设备各存各的；需要同步时再加。
