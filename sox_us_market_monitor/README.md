# SOX / 美国股市市值监控网页

## 指标

分子：费城半导体指数（SOX）30只成分股的完整公司市值合计。  
分母：所有美国交易所上市公司的总市值。

网页通过 GitHub Pages 免费托管，并由 GitHub Actions 在每个工作日美股收盘后自动更新。

## 上线步骤

1. 在 GitHub 新建一个公开仓库，例如 `sox-market-monitor`。
2. 上传本项目内的所有文件和文件夹，注意 `.github` 也必须上传。
3. 打开仓库 `Settings → Pages`。
4. `Build and deployment` 中选择：
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)`
5. 点击 Save。几分钟后，Pages 页面会显示公开网址。
6. 打开 `Actions`，点击 `Daily market refresh`，选择 `Run workflow`，先手动运行一次。
7. 在 `Settings → Secrets and variables → Actions → Variables` 新增：
   - `US_MARKET_CAP_ANCHOR_DATE` = `2026-06-18`
   - `US_MARKET_CAP_ANCHOR_USD` = `74000000000000`

## 自动更新时间

工作日 22:30 UTC。美国夏令时约为美东18:30，冬令时约为美东17:30，均在常规交易收盘后。

## 更新SOX成分股

SOX固定30只，但成分会调整。发生调整时，编辑 `constituents.py`，保持30个Ticker。

## 估算限制

- 分子使用当前完整公司市值，并按复权股价回推历史市值。
- 分母使用全美上市公司总市值锚点，并按VTI变化估算。
- 海外ADR按完整公司市值计算。
- 免费数据源不能提供官方精确的逐日全市场总市值，因此本网页用于趋势监控，不是官方或审计数据。
