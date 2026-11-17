# 實際執行紀錄

工作目錄是這個套件的根目錄。下面兩段輸出是命令寫進 `evidence/` 的原文，不是事後編的分數。

單元測試與摘錄核對：

```
python3 -m unittest discover -s tests -v
python3 scripts/check_excerpts.py
```

實驗：

```
python3 scripts/run_experiment.py
```

`evidence/experiment.txt` 的內容是：

```
max_steps_3 pass=False tools=3 search=1 read=2 write=0 observed=2 cited=0 unused=0 reasons=no_final_brief
max_steps_6 pass=True tools=5 search=1 read=3 write=1 observed=3 cited=3 unused=1 reasons=
已寫入 runs/max_steps_3/evaluation.csv 與 runs/max_steps_6/evaluation.csv
完成條件已複製到 completed/ 與倉庫根目錄。這不是教師驗證器的結果。
```

目前 `provenance.json` 的 `executed_at_utc` 是 `2026-11-17T15:32:53Z`，Python 3.12.3。上限 3 的 `stop_reason` 是 `budget_exhausted`，上限 6 是 `complete`。這次執行把來源改記成依使用者指示自行選定。14:35:54Z 是上一份標示句的執行。

單元測試的完整輸出在 `evidence/unittest.txt`。若測試檔後來有增減，以該檔最後一次為準，不在這裡另造一個次數。

沒有呼叫模型 API，沒有 GPU，沒有連上教師的驗證器。

乾淨解壓後再跑的紀錄在 `evidence/extraction-rerun.txt`。19 項測試通過。簡報與軌跡的位元組和打包時相同。

推送到 https://github.com/rachelruiwang920/homework_final 的 `main` 沒有成功。命令是 `GIT_TERMINAL_PROMPT=0 git push https://github.com/rachelruiwang920/homework_final.git HEAD:main`。Git 回應 `fatal: could not read Username for 'https://github.com': terminal prompts disabled`。沒有使用 force push。

`evidence/screenshots/terminal-unittest-and-experiment.png` 是 XFCE 終端的實拍。拍攝時是 18 項測試，約 0.034 秒，並用 `cat` 印出已存的實驗日誌。其後才加上配分對照那一項，所以現在是 19 項。截圖沒有重拍。
