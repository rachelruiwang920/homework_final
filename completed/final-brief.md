# 證據簡報

標示：這份簡報由確定性腳本控制器把工具觀察組裝而成，不是語言模型輸出。來源是依使用者指示自行選定的論文摘錄，屬於自建替代，不是教師夾具。未宣稱通過教師驗證器。

## 問題

交錯式工具迴圈、訓練期自學 API、以及多環境代理評測，分別把「行動」放在什麼位置？答案只能用來源包裡的逐字摘錄支撐。

## 自撰轉述

【自撰轉述】這條摘錄把推理痕跡和任務行動放在同一次生成裡交錯產生，並把行動說成接觸外部來源的介面。這描述的是論文中的語言模型做法，不是本作業這個離線腳本。
【自撰轉述】這條摘錄說的是一個經過訓練的模型，要自己決定呼叫哪一個 API、何時呼叫、傳什麼參數，以及如何把結果放進後續的 token 預測。摘錄把這個過程稱為自監督。它和上一槽把推理與行動留在同一條推論軌跡裡，不在同一層。
【自撰轉述】這條摘錄把評測對象寫成互動環境中的語言模型代理，並寫明規模是 8 個環境。它評的是代理能力，不是本作業這個確定性腳本。

【自撰轉述】三段摘錄把「行動」放在不同層：第一段在同一次生成裡與推理交錯，第二段由經過訓練的模型在預測後續 token 時決定 API 呼叫，第三段把代理在多個環境裡的行動當成評測對象。這三句是組裝時加上的對照，不是論文原句。

## 逐字引用

:::citation source=react_2023 start=797 end=1205 sha256=a2ee4b59b2756aebee077fad8e685eee556907e96150025d4b5cc3d1fc1532e7
In this paper, we explore the use of LLMs to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two: reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with external sources, such as knowledge bases or environments, to gather additional information.
:::

:::citation source=toolformer_2023 start=1112 end=1379 sha256=ebe5d08dc960dbf245ec21d406a82c0f98b2cc38c1ffea173423633122d28cb8
a model trained to decide which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results into future token prediction. This is done in a self-supervised way, requiring nothing more than a handful of demonstrations for each API.
:::

:::citation source=agentbench_2024 start=1054 end=1213 sha256=aa3d142c9cf9581a8300dbdeeb959d9fc1d1d4c6da28c959ffb51b9b01ef4458
We present AgentBench, a multi-dimensional benchmark that consists of 8 distinct environments to assess LLM-as-Agent's reasoning and decision-making abilities.
:::

## 區間約定

start 與 end 是來源檔 UTF-8 位元組偏移，半開區間。sha256 是該位元組區間的 SHA-256。
上面的【自撰轉述】不是引文，驗證器不把它當成證據。
