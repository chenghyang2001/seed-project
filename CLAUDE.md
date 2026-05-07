# seed-project — 圖片簡報瀏覽器模板

## 概述

本 repo 是所有圖片簡報 Viewer 的母模板。每個新 Viewer 專案（如 aihcr-diagrams、openclaw-slides）都從這裡的模板 + gen.py 生成，不需手動調整 HTML/CSS/JS。

## 目錄結構

```
seed-project/
├── templates/
│   ├── simple.html    # Mode A：純平面 IMAGES 陣列（無分組）
│   └── grouped.html   # Mode B：GROUPS 陣列 + 左側邊欄分組
├── gen.py             # 產生器：掃描圖片 → 注入模板 → 輸出 index.html
├── example/           # （選用）本地示範用的小張圖片
└── CLAUDE.md          # 本文件
```

## 快速開始

### Mode A（平面清單，如 aihcr-diagrams）

```bash
# 在目標 repo 目錄執行（圖片放在 images/ 子目錄）
python path/to/seed-project/gen.py \
  --mode simple \
  --title "AIHCR 診斷圖" \
  --dir ./images \
  --accent cyan
```

### Mode B（分組，如 openclaw-slides）

```bash
# 每個子目錄代表一個章節/分組，底下放 PNG 檔
python path/to/seed-project/gen.py \
  --mode grouped \
  --title "OpenClaw 教學簡報" \
  --dir ./chapters \
  --accent blue
```

## 參數說明

| 參數 | 必填 | 說明 |
|------|------|------|
| `--mode` | ✅ | `simple` 或 `grouped` |
| `--title` | ✅ | 瀏覽器標題（顯示在 header）|
| `--dir` | ✅ | 圖片目錄（simple）或分組父目錄（grouped）|
| `--accent` | 選填 | 主題色：`cyan`（預設）/ `blue` / `green` / `amber` / `purple` |
| `--output` | 選填 | 輸出路徑，預設 `<dir>/../index.html`（即 `<dir>` 的父目錄）|

## 主題色對照

| 名稱 | 主色 | 適合場景 |
|------|------|---------|
| cyan | #38bdf8 | 科技、AI、監控 Dashboard |
| blue | #60a5fa | 教學、軟體、一般用途 |
| green | #4ade80 | 環境、生態、完成狀態 |
| amber | #fbbf24 | 警告、工業、醒目提示 |
| purple | #a78bfa | 創意、設計、AI 研究 |

## 兩種模板的選擇依據

| 判斷依據 | 選 Mode A (simple) | 選 Mode B (grouped) |
|---------|-------------------|-------------------|
| 圖片數量 | < 200 張 | ≥ 200 張或明確有章節 |
| 結構 | 無分類，線性瀏覽 | 有章節 / 分組 / 課程結構 |
| 導航 | 縮圖列即可 | 需要側邊欄快速跳章節 |
| 現有範例 | aihcr-diagrams, 書籍範例 | openclaw-slides, agent-teams（多場景）|

## 鐵律：永遠用 gen.py，不要複製貼上

> **複製既有 index.html 再改 = 繼承所有 bug。**
> gen.py 注入的是最新模板，功能永遠完整。

| 情境 | ✅ 正確 | ❌ 錯誤 |
|------|--------|--------|
| 建新 Viewer | `python gen.py ...` | 複製既有 index.html |
| 加新功能（如觸控） | 改 `templates/*.html` → 重跑 gen.py | 直接改部署的 index.html |
| 發現某 Viewer 缺功能 | 確認模板有後重跑 gen.py | 單獨 patch 那個 Viewer |

## 新建 Viewer Repo 的完整 SOP

1. **建立 GitHub Repo**
   ```bash
   gh repo create chenghyang2001/<repo-name> --public --clone
   cd <repo-name>
   ```

2. **放入圖片**
   - Simple：圖片放 `images/`（或任意子目錄，gen.py 會遞迴掃描）
   - Grouped：每組圖片放各自子目錄，例如 `ch01/`、`ch02/`

3. **執行 gen.py 產生 index.html**
   ```bash
   python ~/workspace/seed-project/gen.py --mode simple --title "..." --dir ./images
   ```

4. **三行 Smoke Test（必做，30 秒）**
   ```bash
   grep -c "自動播放"    index.html   # 必須 ≥ 1
   grep -c "dd-toggle"   index.html   # 必須 ≥ 1
   grep -c "progress-bar" index.html  # 必須 ≥ 1
   ```
   任何一行輸出 `0` → 停手，修 `templates/` 再重跑，**不要手補 index.html**。

5. **確認本地預覽正常**（選用）
   ```bash
   python -m http.server 8080
   # 開瀏覽器 http://localhost:8080
   ```

6. **推送並啟用 GitHub Pages**
   ```bash
   git add .
   git commit -m "新增 index.html（由 seed-project gen.py 產生）"
   git push
   # GitHub Settings → Pages → Source: main / (root)
   ```

7. **將 iframe 加入 mermaid-viewer**
   - 在 `mermaid-viewer/index.html` 新增 tab 按鈕和 pane
   - 參考現有 tab 格式，`data-src` 填入 `https://chenghyang2001.github.io/<repo-name>/`
   - 更新 `ACTIVE_CLASS` 陣列（長度必須與 tab 數量一致）

## 常見錯誤排查

| 症狀 | 原因 | 修法 |
|------|------|------|
| 圖片不顯示 | `img.src` 路徑錯誤 | 檢查 gen.py 輸出的 JSON，路徑是否相對於 index.html |
| 縮圖顯示但主圖空白 | JS syntax error | 開瀏覽器 DevTools → Console 看紅色錯誤 |
| Auto-play 按鈕不見 | CSS 被覆蓋或 HTML 結構問題 | 確認 `#play-btn` 在 `#header` 內 |
| mermaid-viewer tab 顯示空白 | `ACTIVE_CLASS` 陣列長度不足 | 確認陣列長度 == tab 數量 |
| GitHub Pages 404 | 尚未啟用 Pages | Settings → Pages → Source: main |

## 維護規則

- 修改 simple.html / grouped.html 後，現有 Viewer 不受影響（已生成的 index.html 獨立）
- gen.py 的 THEMES 顏色如需新增，同時更新本文件的主題色對照表
- 新 Viewer 加入 mermaid-viewer 後，記得更新 mermaid-viewer/index.html 的 ACTIVE_CLASS
