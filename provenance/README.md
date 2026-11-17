# 文獻快取說明

存取日：2026-11-17。

這裡保存本次真正下載或從下載檔切出來的文字，用來支撐來源包裡的逐字句。`manifest.json` 有每個入庫檔的 SHA-256。

沒有入庫、只記錄雜湊的下載：

- τ-bench 的 ICLR 2025 PDF 全文。入庫的是首頁文字擷取 `extracts/taubench-p1.txt`。
- ReAct 的 ar5iv HTML 全文。入庫的是兩個短視窗 `extracts/react-ar5iv-windows.txt`。

這樣做是為了不把整篇論文再放進作業壓縮檔。短摘錄仍可對回這些擷取檔。

本次沒有拿到的頁面：OpenReview 回傳驗證挑戰，DBLP 回傳機器人檢查，Semantic Scholar 回傳 429。這些失敗沒有用別的網頁冒充。
