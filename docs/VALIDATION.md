# Validation — v0.1.0

驗證日期：2026-09-10。執行環境：Linux、Python 3.12.14、Node.js v24.19.0。

## 實際結果

| 檢查 | 結果 |
| --- | --- |
| Python 行為與真實 CLI 測試 | 17 通過，0 失敗 |
| Node.js 合併、來源保留與真實 CLI 測試 | 16 通過，0 失敗 |
| Python 語法編譯 | 通過 |
| 文件盤點範例 | 4 文件、1 重複群組、0 讀取問題；exit 0 |
| 紀錄合併範例 | 7 已確定稿號、1 衝突稿號、1 隔離紀錄；預期 exit 1 |
| 範例來源位元組 | 執行前後相同 |
| 技能原文 | 與已安裝的 global-first-completion 原文逐位元組相同 |

首輪實際輸出保留在 [first-validation.json](../evidence/first-validation.json)。

最終交付會從乾淨解壓的原始碼重跑這些檢查，核對報表與範例來源；結果保留在 [final-validation.json](../evidence/final-validation.json)。

## 驗證邊界

- Windows／PowerShell 啟動腳本已提供，未在 Windows 或 PowerShell 實機執行。
- Python 3.10／3.11 與 Node.js 18 的最低版本相容性未逐版本實測；程式使用這些版本提供的標準功能。
- UTF-8、YAML/frontmatter 與相對文件連結會在交付前檢查。
- 沒有將資料衝突解決、跨模型優勢、效能或 Token 節省列為已驗證結論。
