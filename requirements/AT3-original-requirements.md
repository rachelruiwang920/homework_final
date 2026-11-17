# AT3 作業要求快照

這份文字依 2026-11-17 校正時提供的作業實質內容記入。第一版環境沒有讀到原始 Markdown 檔，所以這不是那個檔的位元組複本。沒有另加封面、學號或其他未出現的欄位。

累積式大作業 AT3。三部分合計 30%。遲交每天扣 10%，超過 7 天以 0 分計。本次提供的文本沒有截止日期，也沒有封面或學號規定。

## ① 文獻綜述，8%，對應 AT4 Related Work

標題寫的是選定前沿方向、3 至 5 篇核心論文的結構化調研。正文要求是：從教師選題池（含 AI Agents 框架與應用）選一個前沿方向，閱讀至少 5 篇論文，其中至少 2 篇是 2024 年以後的頂會，產出結構化知識圖譜（腦圖或表格）加 1 頁摘要。

該部分評分權重：

- 前沿性 20%
- 覆蓋度 30%
- 結構組織 30%
- 批判分析 20%

## ② 技術復現，12%，對應 AT4 Method

從第一部分選定的論文裡選 1 篇，復現核心方法。可以簡化，例如小資料、少 epoch。產出可運行程式碼（GitHub）、結果截圖和簡要說明。

該部分評分權重：

- 可運行性 30%
- 與原論文結果復現度 30%
- 規範、註釋、結構、README 20%
- 過程文檔 20%

## ③ Agent 工作任務，10%，對應 AT4 Experiments

使用 Agent，或教師認可的 Agent 工具，完成離線來源整理：搜尋指定來源包、讀三個相關來源、生成一頁含 citation 的研究簡報，並通過 final-state validator。

核心 fixture 不需要 API、模型、GPU、網路或大型套件。付費模型框架不加分。

小受控比較只選一個：max_steps 3 對 6；含糊對清晰的 tool description；單 prompt 對 Agent tool loop。任務、來源包、validator 與 rubric 保持不變。

提交檔：

- `final-brief.md`（1 頁）
- `task-contract.json`
- `tool-schema.json`
- `trajectory.jsonl`
- `tool-results.jsonl`
- `evaluation.csv`
- `error-note.md`
- `provenance.json`

分析不超過 2 頁，要含完成狀態、tool calls、最容易出錯的步驟、小比較、限制與下一步測試。

該部分評分權重：

- 完成與 validator 30%
- tool calls、observations、citation evidence 25%
- 比較與失敗分析 25%
- provenance、可重跑、安全邊界的表達 20%

只有截圖、卻沒有 trajectory，或把教師 fixture 說成真模型，視為不完整。

## 來源與仍然未完成的部分

使用者於 2026-11-17 指示以自行選定的相關來源代替教師來源包。缺少教師來源包因此不是阻斷項。教師的 final-state validator 程式仍然沒有附上，本作業的驗證器是自建的。教師是否認可這份作業，尚未發生。
