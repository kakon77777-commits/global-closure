# LSPR：範圍與實際驗證

[LSPR — Local Surgical Proof & Replacement](../skills/lspr/SKILL.md) 的流程正文為 58 行。它只處理已基本完成系統中的一個可疑節點、failure 或 invariant。

$$
\boxed{\text{Maximum Local Precision} + \text{Minimum Global Disturbance}}
$$

核心能力是 **Replacement Boundary Detection**：以證據找出最小充分的替換邊界，辨認責任層，保留未涉入的鄰接部分。這不宣稱找到了數學意義上的最小 dependency cone；「改一行」也不自動代表責任層正確。

$$
\boxed{\text{No Replacement Without a Failing Witness}}
$$

Proof 指可執行或可核對的反例證據，不是形式數學證明。唯一例外是使用者明確要求、不改變行為的純機械性修改。

## 五步邊界

1. 極小化因果依賴範圍，辨認入口、出口、狀態歸屬與需要保留的鄰接行為。
2. 依既有要求或契約建立 witness，在未修改的實作上先執行並保留失敗證據。
3. 判斷 protocol、adapter、persistence、domain、test 或 environment 哪一層違反契約。
4. 只替換必要實作及直接需要的測試；不順手整理鄰居。
5. 同一 witness 轉綠、鄰接 invariant 通過、真實入口的端到端 witness 通過後停止。

技能可以由 Global First Completion 或 mssp-tdd-apr 移交局部目標，也能單獨使用。三者分工不同，不是強制逐套執行的流程。

## 三個獨立執行案例

驗證日期：2026-09-10。三個新對話代理各自收到技能路徑、自然任務描述及獨立小專案；沒有收到預期診斷、修法或評分答案。每個專案均含相同的明文契約，以及 CLI → adapter → domain → store 的真實執行路徑。

契約規定：省略或 null 的 limit 預設為 2；明確指定 0 必須回傳空項目，但 total 仍為 3；範圍為 0–100；查詢不得改動儲存內容。

| 案例 | 執行前證據 | 實際替換邊界 | 執行後證據 |
| --- | --- | --- | --- |
| 真實 adapter 缺陷 | CLI 的 `limit="0"` 回傳 2 筆、limit=2，違反契約；原有 2 個測試仍全綠 | adapter 一個 return 陳述式；補上直接相關測試 | 同一 CLI witness 回傳空項目、total=3、limit=0；8 個測試通過 |
| 錯誤測試 | 測試期待預設 3 筆而失敗；契約與 CLI 都是 2 筆 | 只改測試的一個斷言，3 → 2 | 2 個測試通過；產品實作逐檔相同 |
| 未重現疑點 | CLI 的數字 0 與字串 "0" 原本都符合契約 | 不替換；只留調查紀錄 | 2 個既有測試、10 個相關 CLI 輸入及儲存不變性檢查通過 |

真缺陷案例保留原有斷言；CLI、domain、store 與契約均未修改。錯誤測試案例另驗證 8 個相關 CLI 輸入與儲存不變性。這些輸入是同一入口及其鄰接契約的變體，沒有擴張成全域回歸活動。

三份原始執行紀錄：

- [真缺陷](../evidence/lspr/query-zero.md)
- [錯誤測試](../evidence/lspr/query-default.md)
- [未重現疑點](../evidence/lspr/query-report.md)

收回結果後，另以保存的原始快照重播前後 CLI witness 和測試，並核對改動檔案與 SHA-256；三案均符合上述結果。原始代理紀錄保留當時的 Linux 命令；以下提供 PowerShell 重播入口。

## 重播

在儲存庫根目錄執行：

```powershell
py -3 .\evidence\lspr\replay.py --output .\lspr-replay.json
```

若本機使用 `python`，將 `py -3` 改為 `python`。腳本只使用 Python 標準函式庫，在暫存資料夾重建保存的前後版本，檢查三案結果；不修改 MVP，也不重新啟動 AI 代理。

- [案例原始碼、實際 patch 與預期結果](../evidence/lspr/cases.json)
- [重播程式](../evidence/lspr/replay.py)
- [本次實際重播結果與輸出](../evidence/lspr/replay-results.json)

案例資料及結果均記錄被驗證技能的 SHA-256；技能版本改變時，重播腳本會拒絕將舊案例結果當成新版本驗證。

## 已驗證範圍

技能 frontmatter、五步結構、UI 中繼資料與 UTF-8 數學原文已檢查。程式案例及重播實際執行於 Linux、Python 3.12.14；未實測 Windows／PowerShell。

這三個合成案例支持本次對「責任層與最小替換邊界」的觀察，不構成普遍可靠性證明。本次未獨立測試非決定性競態、跨服務部署、環境故障或純機械性修改例外。驗證資料放在技能之外，技能不會自動載入它們。
