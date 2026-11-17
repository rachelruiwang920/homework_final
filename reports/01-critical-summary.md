# 批判摘要：行動放在哪一層

這六篇都在問語言模型怎樣使用工具，或怎樣被當成代理來評，但「行動」不在同一層。ReAct（Yao、Zhao、Yu、Du、Shafran、Narasimhan、Cao；ICLR 2023 口頭報告）把推理痕跡和任務行動交錯寫進同一條推論軌跡，行動用來向知識庫或環境取資訊。Toolformer 在 NeurIPS 2023 摘要頁列出九位作者，含 Eric Hambro；arXiv v1 少了這一位。那篇把「呼叫哪個 API、何時呼叫、傳什麼參數、如何寫進後續 token」說成訓練出來的能力，並稱為自監督。Reflexion 的會議摘要頁是 Shinn、Cassano、Gopinath、Narasimhan、Yao 五人；arXiv v4 多了 Edward Berman。它讓代理用語言反思任務回饋，把反思文字放進情節記憶，供下一輪使用。

2024 年以後的三篇都是 ICLR，而且把問題改成可執行的評測。AgentBench 用 8 個環境評 29 個模型，並把主要障礙寫成長期推理、決策與指令遵循。SWE-bench 收集 12 個 Python 程式庫的 2,294 個真實 issue；摘要頁寫 Claude 2 只解決 1.96%。τ-bench 的 PDF 首頁聲明為 ICLR 2025。它把模擬使用者、領域 API 與政策放在同一段對話，用結束時的資料庫狀態對答案，並提出 pass^k。arXiv 摘要寫 gpt-4o 的成功率小於 50%，retail 的 pass^8 小於 25%。

對照可以站住的有三點。第一，ReAct 的行動發生在當下這條軌跡裡，Reflexion 新增的語言發生在試次之間。第二，Toolformer 把「要不要呼叫工具」訓練成下一步預測，ReAct 把它留在提示與環境觀察的交替裡。任務不同，有沒有更新權重也不同，不能拿兩邊的分數比誰的代理更強。第三，後期評測改測測試是否通過、指令是否做完，或資料庫是否到達目標狀態，不再把一段看起來合理的推理句當成完成。τ-bench 還說明單次做成不夠，重複試驗會更不穩。

第二部分因此只再現 ReAct 的迴圈外形：檢索、讀取、依觀察決定還要不要讀、最後寫出帶有位元組區間與雜湊的簡報。不選 Toolformer，是因為它的核心在自監督訓練，不是一次推論裡的工具迴圈。不選 Reflexion，是因為它需要跨試次的語言記憶。這個選擇只支持一件事：用確定性腳本看步數預算夠不夠先搜尋、再讀三份、再寫。它不重跑 HotpotQA、ALFWorld 或 WebShop，也不測量任何模型。上文的百分率都是論文摘要裡的數字，和本作業自己數到的工具呼叫分開。

存取日 2026-11-17。這是自建筆記，不是教師評語。逐字句與作者差異見知識表。一次來源：

https://iclr.cc/virtual/2023/oral/12647

https://arxiv.org/abs/2210.03629

https://proceedings.neurips.cc/paper_files/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html

https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html

https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html

https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html

https://proceedings.iclr.cc/paper_files/paper/2025/file/1b126cc38b8638e07bef37e7b2bb72bf-Paper-Conference.pdf

https://arxiv.org/abs/2406.12045
