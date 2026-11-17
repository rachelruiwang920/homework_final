# 離線 ReAct 結構作業

這是 AT3 的離線作業。方向是 AI agents 的工具使用。文獻、可執行的工具迴圈，以及 max_steps 3 對 6，都圍繞同一個問題：行動放在推論軌跡、訓練後的 token 預測，還是評測環境。

來源是依使用者 2026-11-17 的指示自行選定的論文摘錄，不把缺少教師來源包當成未完成。控制器仍是確定性腳本，不是語言模型，也不是 ReAct 論文實驗的復現。沒有重測論文裡的 34% 與 10%。驗證器是自建的，沒有宣稱教師認可。

## 怎麼跑

在這個目錄：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_excerpts.py
python3 scripts/run_experiment.py
```

前三項只用 Python 3 標準庫。實驗會重寫 `runs/`、`completed/`，以及根目錄上那一份完成條件的產物。

限頁 PDF 用本機的 Chrome 列印，不參與實驗：

```bash
python3 scripts/build_pdfs.py
```

批判摘要與 `final-brief.md` 的排版稿必須是 1 頁。分析不得超過 2 頁。超過頁數時腳本會失敗。

## 目錄

- `reports/01-literature.md`：六篇書目、逐字摘錄、自撰對照。
- `reports/01-critical-summary.md`：一頁批判摘要。
- `reports/02-scope.md`：論文中的 ReAct 與這次簡化差在哪。
- `reports/03-analysis.md`：上限 3 與上限 6 的對照。
- `reports/knowledge-graph.svg`：作者交集與自撰機制對照。
- `sourcepack/`：自建來源包。
- `provenance/`：2026-11-17 下載或切出的一次來源。
- `react_min/`：search、read、write 與驗證器。
- `runs/max_steps_3/`：真實失敗的那一次，沒有簡報。
- `runs/max_steps_6/` 與 `completed/` 與倉庫根目錄：真實通過的那一次。
- `requirements/AT3-original-requirements.md`：校正時記入的作業要求。
- `SUBMISSION_CHECKLIST.md`：配分、權重與仍未完成的項目。

## GitHub

套件可以直接推上你自己的倉庫。本次沒有新建公開倉庫，也沒有寫下一個不存在的網址。名稱和公開或私人要等你決定再上傳。
