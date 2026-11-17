# 提交對照

2026-11-17 的校正已提供 AT3 原文的實質要求，記在 `requirements/AT3-original-requirements.md`。第一版清單寫過原始 Markdown 沒讀到；那是當時的傳檔問題，現行對照以這份快照為準。原文沒有封面或學號欄。

三部分合計 30%：文獻綜述 8%，技術復現 12%，Agent 工作任務 10%。遲交每天扣 10%，超過 7 天 0 分。文本沒有給截止日期，所以本包不宣稱準時或遲交。

來源是依使用者 2026-11-17 的指示自行選定的論文摘錄。缺少教師來源包不是阻斷項。下面凡寫「通過」，都只指自建規則 `self_built_rubric_v1`。驗證器不是教師的程式，控制器是確定性腳本，沒有模型輸出，也沒有教師認可或分數。

## ① 文獻綜述，課程比重 8%

方向取教師選題池中的 AI Agents。正文要求至少 5 篇，含 2 篇 2024 年以後的頂會。標題另寫 3 至 5 篇核心論文。本作業收 6 篇，以滿足至少 5 篇：ReAct（ICLR 2023）、Toolformer 與 Reflexion（NeurIPS 2023）、AgentBench 與 SWE-bench（ICLR 2024）、τ-bench（ICLR 2025）。

| 該部分權重 | 對到哪裡 | 狀態 |
| --- | --- | --- |
| 前沿性 20% | 2023 至 2025 的工具使用與代理評測，含三篇 ICLR 2024/2025 | 已按一次來源寫入書目表 |
| 覆蓋度 30% | 六篇的題名、場合、年份、作者與短摘錄 | 已完成。會議頁與 arXiv 不一致處並列，不合併 |
| 結構組織 30% | 表格、逐字摘錄、`reports/knowledge-graph.svg` | 已完成 |
| 批判分析 20% | `reports/01-critical-summary.md` 與其 1 頁 PDF | 已完成。行動所在層不同，不能拿論文百分率互減 |

## ② 技術復現，課程比重 12%

選的是 ReAct 的工具迴圈外形，不是它的模型實驗。可運行程式在 `react_min/`。結果截圖是 `evidence/screenshots/terminal-unittest-and-experiment.png`。說明在 `reports/02-scope.md` 與 `README.md`。

| 該部分權重 | 對到哪裡 | 狀態 |
| --- | --- | --- |
| 可運行性 30% | `python3 -m unittest discover -s tests -v` 與 `python3 scripts/run_experiment.py` | 已在本機跑過。解壓重跑的紀錄見 `evidence/extraction-rerun.txt` |
| 與原論文結果復現度 30% | 論文的 HotpotQA、FEVER、ALFWorld、WebShop 數字 | 未做，也不宣稱達標。只復現了 Thought、Action、Observation 的結構。34% 與 10% 沒有重測 |
| 規範、註釋、結構、README 20% | `README.md`、`react_min/` 的模組說明 | 已有。程式註釋說明腳本與路徑侷限 |
| 過程文檔 20% | `reports/04-execution-log.md`、`evidence/` | 已有實際命令與輸出 |

GitHub：套件可以上傳，但名稱與是否公開尚未決定。這一项仍待學生自己的倉庫。不要把開發環境的暫存遠端當成作業網址。

## ③ Agent 工作任務，課程比重 10%

小比較只做了 max_steps 3 對 6。沒有同時做含糊對清晰描述，也沒有做單 prompt 對工具迴圈。任務契約、來源包、自建驗證器在兩次之間不變。

使用的是標準庫腳本，不是付費框架，也不是教師點名的某個 Agent 產品。這符合免 API、免模型、免 GPU、免大型套件。不能把它寫成教師認可工具，也不能把軌跡寫成模型輸出。

| 該部分權重 | 對到哪裡 | 狀態 |
| --- | --- | --- |
| 完成與 validator 30% | 上限 6 通過自建規則；上限 3 為 `no_final_brief` | 自建驗證已跑。教師的 final-state validator 沒有附上，所以不能說通過了教師的檢查 |
| tool calls、observations、citation evidence 25% | 成功軌跡 5 次；三條引用有 UTF-8 區間與 SHA-256 | 已完成。錨點只寫在散文裡不能通過 |
| 比較與失敗分析 25% | `reports/03-analysis.md`，1 頁，未超過 2 頁 | 已寫完成狀態、工具次數、最容易出錯的第三次 read、比較、限制與下一步 |
| provenance、可重跑、安全邊界 20% | `provenance.json`、路徑拒絕、重跑位元組比對 | 已完成。重跑會改牆鐘時間，不改簡報與軌跡 |

只有截圖、沒有 trajectory，會算不完整。本包兩者都有。把教師 fixture 說成真模型也算不完整。這裡沒有教師 fixture，腳本也標成非模型。

規定檔案：

| 檔案 | 完成條件 | 上限 3 |
| --- | --- | --- |
| `final-brief.md` | 根目錄、`completed/`、`runs/max_steps_6/`。排版稿 `reports/final-brief.pdf` 為 1 頁 | 故意沒有 |
| `task-contract.json` | 有 | 有 |
| `tool-schema.json` | 有 | 有 |
| `trajectory.jsonl` | 有，5 步 | 有，3 步 |
| `tool-results.jsonl` | 有 | 有 |
| `evaluation.csv` | 有 | 有 |
| `error-note.md` | 有，寫明不是失敗 | 有，寫明未執行的下一步 |
| `provenance.json` | 有 | 有 |

## 實測

`provenance.json` 的時間是 2026-11-17T15:32:53Z，Python 3.12.3。來源欄位是 `self_selected_per_user_instruction`，`teacher_source_pack_blocking` 為 false。

- 上限 3：不通過。工具 3 次（search 1、read 2、write 0）。失敗代碼 `no_final_brief`。
- 上限 6：通過自建規則。工具 5 次（search 1、read 3、write 1）。未使用 1 步。簡報 SHA-256 `6c5327436ef0b68084171affee6052af85a2a2c3bfcba4aa7c31468077522e07`。

## 仍然未完成

1. 教師的 final-state validator 沒有附上。自建規則通過，不等於教師的檢查通過，也沒有教師認可。
2. 學生指定的 GitHub 倉庫是 https://github.com/rachelruiwang920/homework_final 。上傳前用 GitHub API 讀過，倉庫沒有任何提交，也沒有既有檔案。接著用一般 `git push` 推 `main`，沒有 force。結果是 `fatal: could not read Username for 'https://github.com': terminal prompts disabled`。`gh auth status` 顯示沒有登入任何 GitHub 主機。可讀的 GitHub 連線沒有提供寫入或推送工具。因此這個倉庫目前仍是空的，本機提交不能算成已上傳。
3. 原論文結果沒有復現。第二部分那 30% 的復現度不能記成完成。
4. OpenReview 被驗證頁擋住，DBLP 被機器人檢查擋住，Semantic Scholar 回 429。τ-bench 的引用鍵沒有對到參考文獻表。
5. Toolformer 與 Reflexion 的作者名單在會議頁和 arXiv 之間不一致，兩份都保留。
6. 全文 PDF 沒有再放進壓縮檔。入庫的是短摘錄與 SHA-256。
