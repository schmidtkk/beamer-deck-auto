# 技术中文写作规范 — 用于 English→中文 翻译关 (Beamer decks)

This reference governs the **translation pass** that turns a finished, verified **English**
deck into a Chinese deck. You draft and reason in English (see the Language Policy in
`SKILL.md`); you do **not** think directly in Chinese. So the failure mode to guard against
is **翻译腔 / calque** — English sentence skeletons wearing Chinese words. Translate the
*meaning*, then rebuild the sentence in natural technical Chinese.

> Adapted from the Paper2Html `reference/zh-style.md` (native-authored). Keep its table intact;
> add deck-specific items here. When you find new translationese, append it to the table.

## 0. The one rule

**译意，不译词。** Read the English line, understand the relationship it asserts, then write
the Chinese a native technical writer would say. Keep standard ML/math terms in English inline
(token, latent, attention, pipeline, Hodge, Ricci flow, Laplacian…) — but the **sentence
skeleton must be natural Chinese**. If a line reads stiff aloud, it is almost always a calque.

## A. 翻译腔 / calque（直译造词，必须改）

| 生硬表达 | 问题 | 建议替换 |
|---|---|---|
| 根问题 | "root question" 直译 | 核心问题 / 真正要回答的问题 |
| 复现边界 | "reproduction boundary" 直译 | 复现门槛 / 复现条件 / 能复现到哪一步 |
| 把 X 放回 Y | "put X back into Y" 直译 | 把 X 拉回 Y / 还原到 Y |
| 把 X 表述为 Y | "formulate X as Y" 偏生硬 | 把 X 建模为 Y / 把 X 改写成 Y |
| 做一个 X / 进行 X | "perform/conduct X" 翻译腔 | 直接用动词：评测 / 求解 / 对齐 |
| 它被……所…… | 英文被动残留 | 改主动语序，或 "受……影响" |
| 基于……的事实 | "based on the fact that" | 因为…… / 鉴于…… |
| 这给了我们…… | "this gives us…" | 由此得到 / 这样就有 |
| 一个…的…的… | 多层定语堆叠（英文后置定语直译） | 拆成短句，或把定语后移 |

## B. 拟人化图表（中文里图表不会"想"，要改）

| 生硬表达 | 建议替换 |
|---|---|
| 这张表/图 想证明…… | 这张表/图要支撑的结论是…… / 这张图用来回答…… |
| 这张图在强调…… | 这张图要点出的是…… / 重点要看的是…… |
| 论文/作者 想证明…… | 论文要说明的是…… / 作者想验证的是…… |

## C. 填充口癖（高频出现就删或换）

`其实` · `本质上` · `某种意义上 / 某种程度上` · `值得注意的是` · `需要指出的是` ·
`我们可以看到 / 不难发现` · `总的来说` · `归根结底`

- 多数可直接删除，句子更干净（对应 en-style 的 "cut filler"）。
- `不是 A，而是 B` 是好结构，但一段里别用两次以上；换 `与其说 A，不如说 B` / `重点不在 A，而在 B`。

## D. 标点与排版（中文 deck 特有）

- 用**全角**标点：。，、；：「」（）—— 不要把英文 `,` `.` `()` 留在中文句里。
- 中英混排时，CJK 与英文/数字之间**不加空格**（LaTeX 的 xeCJK 会自动处理间距）；不要手敲空格。
- 行内英文术语保留半角；术语首次出现可用 `\TLterm{中文 (English)}` 给双语锚点。
- 数学一律保留在 math mode，**不翻译符号**。

## E. 可以保留（不是口癖，别误杀）

`兜底`、`凑出来的`、`抓手`、`落地`、`接到……上`、`跑在单块 GPU 上`、`做评测/做对齐`、`摊平`、
`抹匀` —— 自然的工程/口语中文，符合讲义语气，保留。

## F. Beamer 翻译关的机械清单（每次都做）

1. **只改自然语言串**：frame 标题、正文、bullet、`\TL*` 块内文字、TikZ node/label/caption。
   数学、`\TL*` 宏名、TikZ 结构与坐标**保持字节级不变**。
2. **本地化 `\TLtakeaway`**：默认 "Key Takeaway." → "要点。"
   ```latex
   \renewcommand{\TLtakeaway}[1]{...\textbf{要点。} #1...}
   ```
3. **双语 gate 词**：`validate_deck.py` 按英文关键词判定（notation / exercise / reference；
   苏格拉底式 question / attempt / hint / reflection）。中文标题保留双语，如「符号表 (Notation)」
   「习题 (Exercises)」「参考文献 (References)」，让静态校验仍然通过。
4. **`\TLtakeaway` = 一个新结论**（沿用 en-style）：翻译后仍不能变成"本页小结"。
5. **重排溢出**：中文通常**比英文短**，英文能排下的页中文一般也能排下；但仍要重跑 Quality Gate，
   若有 Overfull 就**拆页，不缩字**（见 `feedback-split-not-shrink`）。

## G. 自检（交付前念一遍）

1. 念出来卡不卡口？卡 → 多半是 calque 或名词堆叠，重排。
2. 这个词中文母语者平时会不会说？不会 → 换。
3. 主谓宾是不是中文语序？英文残留（被动、后置定语、"基于…的事实"）→ 重排。
4. 术语保留 OK，但一句里中英混插别超过让人读断的程度。
5. 对照 A–C 三表逐条扫一遍；命中即改。
