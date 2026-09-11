# AI Game Studio：三架構師、專用工具與跨對話協作

[技能正文](../skills/ai-game-studio/SKILL.md) 把傳統遊戲程式、美術、企劃三種職能，改成能設計方法、打造工具並負責實際交付的 AI 架構師。三者都能寫程式、使用演算法，也能把有明確邊界的工作交給其他 AI。

| 架構師 | 負責的結果 | 可按專案打造的工具 |
| --- | --- | --- |
| 遊戲程式 | 可執行的遊戲系統、資料與素材整合 | 匯入器、重播器、模擬器、建置工具、除錯介面 |
| 遊戲美術 | 一致、可使用、在遊戲中看得清楚的視覺系統 | 參數化素材產生器、生成工具串接、預覽器、動畫與圖集工具 |
| 遊戲企劃 | 玩家循環、機制、關卡、數值與內容 | 關卡生成器、平衡模擬器、規則驗證器、調參與內容編輯工具 |

每個角色都必須把「工具或演算法 → 實際產物 → 遊戲使用該產物」接起來。美術可以自己寫美術工具，企劃可以自己寫規則模擬器；程式架構師協調執行系統的相容性。工具規模由當前製作需求決定，不先打造萬用引擎或全能編輯器。

## 方法如何組合

Global First Completion 負責整體先接通、集中驗證、批次修復與完成判定。mssp-tdd-apr 負責共同專案狀態、可否證證據與 Lead/Twin 互查。

原有 MSSP 技能的標準版本是雙情境。這個 Skill 是使用者指定的三架構師擴充：每個需要跨職能判斷的議題，由三人中的一位主導、一位相關同儕核對；第三位可以繼續自己的工作或閒置。無須多設永久總管，也不會替每位架構師再加一個永久 Twin。

局部已證實的缺陷可以交給 LSPR 修復。這些方法分擔不同責任，共用必要證據，不累加成每一步都要跑完的完整流程。

## 跨對話的實際做法

三個對話指向同一份持久化專案，使用同一份契約與基準版本。每個角色讀自己需要的資料、寫自己負責的檔案，以新交接包記錄產物、證據、未知項目和下一個動作。

技能附有 `studio_handoff.py`：產生交接 JSON，並核對專案、收件角色、基準版本、契約及產物雜湊。它不會覆寫舊交接包，也不會把「檔案存在」當作「對方已讀／已批准」。版本或素材變動時，接手者會看到明確的過期結果。

如果執行環境有真正的對話訊息工具，就用它傳遞交接位置；否則經共享 GitHub 專案或檔案交換。**共享檔案可以跨對話接續，Skill 本身不會自動喚醒關閉的對話。** 收件者只有在實際檢查後，才能留下自己的回覆。只有單一對話時，應標示為依序執行三種職能，不能宣稱有三份獨立審查。

交接工具的格式與 PowerShell 用法見 [跨對話參考](../skills/ai-game-studio/references/handoff.md)。現有專案已有合適的狀態與訊息機制時可以沿用，不必搬到新的管理系統。

## 三個對話的起始提示

將「同一個專案位置」替換為實際的共享儲存庫或可讀取的專案位置。後續回到任何一個對話時，以最新專案版本及未處理交接包恢復工作。

```text
使用 $ai-game-studio。你是遊戲程式架構師。
專案：同一個專案位置。
先讀共同狀態、契約與給 programming 的交接，再完成執行系統、必要工具與整合驗證。
```

```text
使用 $ai-game-studio。你是遊戲美術架構師。
專案：同一個專案位置。
先讀共同狀態、契約與給 art 的交接，再打造並使用當前需要的美術工具，交付實際素材與可核對的視覺結果。
```

```text
使用 $ai-game-studio。你是遊戲企劃架構師。
專案：同一個專案位置。
先讀共同狀態、契約與給 design 的交接，再打造並使用規則、關卡或數值工具，交付遊戲可直接使用的資料與證據。
```

工具與程式成功執行、畫面品質、遊戲好玩，以及跨對話獨立確認，是不同的主張；各自需要相應的證據。

## 實際執行的三角色範例

本次以三個新的角色情境製作「Key & Door」小範例。企劃與美術先各自產出；程式情境從共享狀態、實際檔案與交接包接手整合，沒有取得前兩個對話的完整歷史。

| 職能 | 實際工具與產物 | 已觀察的證據 |
| --- | --- | --- |
| 企劃 | `design/level_tool.py` 把關卡來源編譯成 `level.json` | 13 個正反案例；鑰匙前不可穿門、可達性、邊界及 16 步路徑 |
| 美術 | `art/generate_assets.py` 依參數產生五種 SVG、manifest 與場景預覽 | 精確重建、參數效果及錯誤素材拒絕；已檢視原生尺寸與實際關卡的預覽 |
| 程式 | `programming/build.py` 消費真正的關卡資料及五種素材，產生單檔 HTML | 對 HTML 中實際 JavaScript 執行 7 個檢查，含移動、取鑰匙、通關、重開與失效門鎖反例 |

交接工具另有 [9 個可重播測試](../evidence/game-studio/test_handoff.py)，結果記錄於 [handoff-test-result.json](../evidence/game-studio/handoff-test-result.json)。它驗證版本與檔案完整性、角色路由、舊交接保留及失敗條件，不宣稱提供身分認證或自動審查。

程式情境實際驗證了兩份 DELIVER，並留下 [企劃 ACK](../examples/game-studio/handoffs/programming-ack-design-r1.md) 與 [美術 ACK](../examples/game-studio/handoffs/programming-ack-art-r1.md)。原企劃情境之後讀回整合產物，進行一次小範圍的原始碼／雜湊核對，留下 [限定範圍的 CONCUR](../examples/game-studio/design/runtime-peer-review-r1.md)，並確認收到程式端 ACK。

另在新暫存副本執行三個產生工具及 JavaScript 檢查；重建的 HTML 與原檔逐位元組相同，7 個 runtime 檢查通過。[實際重建紀錄](../evidence/game-studio/integration-replay.json) 保留命令、結果及證據範圍。這是一次小型三角色協作與檔案接續實測，不是一般化效能比較或背景自動調度測試。

範例保存在 [examples/game-studio](../examples/game-studio)，包含全部原始碼、參數、素材、生成結果、角色證據及交接包。下載儲存庫並解壓後，在根目錄的 PowerShell 開啟：

```powershell
Start-Process .\examples\game-studio\index.html
```

用方向鍵或 WASD 移動，拿到鑰匙後進入門；畫面提供重新開始。單檔 HTML 已內嵌資料與 SVG，不需伺服器或線上服務。重新生成工具產物：

```powershell
Set-Location .\examples\game-studio
py -3 .\design\level_tool.py build
py -3 .\art\generate_assets.py
py -3 .\programming\build.py
node .\programming\verify_runtime.cjs
```

生成工具只用 Python 標準函式庫；Node.js 用於執行 JavaScript 證據。PNG 是檢視用預覽，不是執行遊戲所需；重新產生 PNG 的渲染工具也不是遊戲相依項目。

**驗證範圍：**工具與 JavaScript 檢查在 Linux 執行。JavaScript 檢查使用 Node 與 DOM 替身，未啟動真正瀏覽器，因此沒有證明 Windows 瀏覽器的排版、焦點、圖像解碼或互動體驗；也沒有宣稱人類遊玩樂趣已測量。已檢視的美術預覽另存於 [preview.png](../examples/game-studio/art/generated/preview.png)。
