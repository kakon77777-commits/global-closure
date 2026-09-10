# Global Closure｜全域閉合

**可實際執行的離線研究稿整理 MVP，附 `global-first-completion` 與 `lspr` 開發技能。**

版本：**0.1.0**。本儲存庫保存兩個可執行工具、完整原始碼、範例、測試與技能。工具本身不呼叫 AI，不需要帳號、API Key 或第三方套件。

| 工具 | 功能 | 環境 |
| --- | --- | --- |
| 文件盤點 | 掃描真實資料夾、擷取標題與字元數、找出位元組相同的稿件、輸出 Markdown／JSON | Python 3.10+ |
| 紀錄合併 | 合併 JSON 批次、統一欄位與稿號、去重、保留衝突及來源、產生完整統計 | Node.js 18+ |
| 開發 SKILL | 引導 AI 完成整體範圍，或對單一疑點進行最小必要修復 | 支援 SKILL 的 AI 工具 |

兩個程式可獨立使用；只用文件盤點時不需要安裝 Node.js。所有範例資料均為虛構。

## Windows：立即執行文件盤點

下載並解壓本儲存庫，在專案資料夾開啟 PowerShell：

```powershell
py -3 .\run.py .\examples\papers --output .\demo-output
```

如果電腦使用 `python` 命令，將 `py -3` 改成 `python` 即可。

預期結果：**4 份文件、1 組完全相同的內容、1 份額外副本、0 個讀取問題**。

```powershell
notepad .\demo-output\inventory.md
notepad .\demo-output\inventory.json
```

附帶的 `Run-Demo.ps1` 會執行同一個 Python 主程式：

```powershell
.\Run-Demo.ps1
```

若本機腳本政策不允許執行 `.ps1`，使用上面的 Python 命令即可，不需要修改系統政策。

盤點自己的資料夾：

```powershell
py -3 .\run.py "C:\Research\Papers" --output "C:\Research\Inventory"
```

輸出資料夾必須在來源資料夾之外。以上例子中 `Papers` 與 `Inventory` 是並列資料夾。重跑會更新輸出資料夾中的 `inventory.json` 與 `inventory.md`；請使用專用的報表資料夾。

## 執行紀錄合併

```powershell
node .\record_merge.mjs .\examples\research-batches.json --output .\demo-output\merged.json
notepad .\demo-output\merged.json
```

範例有 12 筆原始紀錄：合併 2 筆重複紀錄、隔離 1 筆缺少稿號的紀錄，留下 **7 個已確定稿號與 1 個衝突稿號**。這份範例刻意包含衝突，因此程式寫出報表後回傳結束碼 `1`。

`P-004` 的「完成／進行中」兩個版本都會保留。只有衝突稿的「記憶」系列仍會顯示 **有效稿件 0、衝突稿號 1**。相同標題但不同稿號不會自動合併。

輸入是 JSON 陣列，每批須有不重複的 `source` 名稱及 `rows` 陣列。每筆紀錄接受以下欄位；同一欄有多種名稱時，依表格順序取第一個非 null 值：

| 內容 | 欄位名稱 |
| --- | --- |
| 稿號 | `id`、`paper_id`、`稿號` |
| 標題 | `title`、`name`、`標題` |
| 系列 | `series`、`category`、`系列` |
| 狀態 | `status`、`state`、`狀態` |

稿號格式為 `P-001`，可輸入大小寫與全形版本。狀態接受 `完成`／`done`、`草稿`／`draft`、`進行中`／`in_progress`。稿號與狀態會做 NFKC 正規化；標題、系列只去除首尾空白，不將數學或其他 Unicode 字元轉寫。

來源標記 `A:1` 表示 A 批次的第 1 筆。衝突依稿號分組，每個版本保留標題、系列、狀態及所有來源。未知狀態、缺欄位或無效稿號列入 `rejected`，不偷偷計入有效統計。跨系列衝突會在每個受影響系列各記一次，故各系列衝突數的總和可能大於全域衝突稿號數。

## 結束碼

| 結束碼 | 文件盤點 | 紀錄合併 |
| --- | --- | --- |
| `0` | 兩份報表已寫出，沒有讀取問題 | 報表已寫出，沒有衝突或隔離紀錄 |
| `1` | 報表已寫出，但部分檔案／資料夾無法讀取 | 報表已寫出，含衝突或隔離紀錄 |
| `2` | 參數、路徑或輸出失敗 | 參數、JSON、批次結構、路徑或輸出失敗 |

找到重複內容本身不是錯誤。程式成功完成整理，也不代表來源資料已沒有衝突。

## 範圍與限制

- 文件盤點接受 `.md`、`.markdown`，副檔名不分大小寫；支援 UTF-8／UTF-8 BOM、中文與含空白的路徑。
- 第一個程式碼圍欄外的 ATX 一級標題（`# 標題`）作為標題，沒有時使用檔名。這不是完整 Markdown 解析器；不解析 YAML title 或 Setext 標題。
- 字元數採 Unicode code point 數，含 Markdown 標記、空白及換行，不含 BOM；不是詞數或視覺字形數。
- 文件重複判定依原始位元組的 SHA-256。BOM、空白、CRLF／LF 不正規化；這不是語義去重，也不另外複核雜湊碰撞。
- 預設略過 `.git`、`node_modules`、`__pycache__` 與巢狀符號連結，並在報表列出。非 Markdown 檔案不納入盤點。
- 原稿僅讀取。盤點期間應保持來源穩定；此版本不提供一致性快照、資料夾監控或 GUI。
- 每份盤點報表各自替換，不保證兩份檔案跨中斷時同步更新。輸出失敗時以結束碼及實際檔案為準。

## 整合開發 SKILL

名稱 **Global Closure（全域閉合）** 表達「整個任務的交付義務都有交代」；技能的穩定識別名稱保留為 **`global-first-completion`**。

技能以不同責任分工組成；軟體開發入口 [`AGENTS.md`](AGENTS.md) 會依任務選用，程式執行不依賴技能。

| 技能 | 主要責任 |
| --- | --- |
| [Global First Completion](skills/global-first-completion/SKILL.md) | 先接通完整系統，再集中驗證及收尾 |
| [mssp-tdd-apr](https://github.com/kakon77777-commits/mssp-tdd-apr) | 可否證閉環與證據控制；由獨立儲存庫提供 |
| [LSPR — Local Surgical Proof & Replacement](skills/lspr/SKILL.md) | 對已可運作系統的單一疑點，先建立 failing witness，再作最小必要替換 |

LSPR 的核心是 **Replacement Boundary Detection**：判斷真正錯誤、必要替換及不可碰觸的鄰接部分。沒有 failing witness，就不替換；僅明確要求的純機械性修改例外。Proof 指可重現的反例證據，不等於形式數學證明。

三者可以銜接，也可各自使用，不強制逐套執行。LSPR 的流程正文為 58 行；[獨立驗證紀錄](docs/LSPR-VALIDATION.md) 放在技能以外，不會被技能自動載入。

手動安裝至本機 Codex（PowerShell；若要安裝 LSPR，將此段路徑中的 `global-first-completion` 換為 `lspr`）：

```powershell
$skillDestination = if ($env:CODEX_HOME) {
    Join-Path $env:CODEX_HOME 'skills\global-first-completion'
} else {
    Join-Path $env:USERPROFILE '.codex\skills\global-first-completion'
}
if (Test-Path -LiteralPath $skillDestination) {
    throw '此技能已存在；請先比較內容再更新。'
}
New-Item -ItemType Directory -Path (Split-Path -Parent $skillDestination) -Force | Out-Null
Copy-Item -LiteralPath '.\skills\global-first-completion' -Destination $skillDestination -Recurse
```

可以要求 AI：

```text
使用 $global-first-completion 完成這個儲存庫內已授權的功能需求，接通主要流程、集中驗證、修復後交付。
```

對局部疑點可使用：

```text
使用 $lspr 檢查這個已可運作系統中的 limit=0 疑點。依既有契約建立反例，找出責任層，只替換必要實作，完成局部與邊界驗證後停止。
```

## 驗證

```powershell
py -3 -m unittest discover -s tests -v
py -3 -m compileall -q research_inventory run.py
node --test .\tests\test_merge_records.mjs
```

可直接閱讀預先產生的 [`sample-output/inventory.md`](sample-output/inventory.md) 與 [`sample-output/merged.json`](sample-output/merged.json)。實際驗證結果與平台限制記錄於 [`docs/VALIDATION.md`](docs/VALIDATION.md)，執行方式示範見 [`docs/WORKFLOW.md`](docs/WORKFLOW.md)。
