# 来源与证据

本 Skill 把写作规则分成四类证据。来源支持某个原则，不等于该原则在所有语言和文体中都已验证。

| 等级 | 含义 |
|---|---|
| A | 标准、同行评审研究或原始实验材料 |
| B | 有明确维护者的官方写作指南 |
| C | 经典写作论述、专业书籍或长期实践总结 |
| D | 项目工作流约定，需要靠实际使用检验 |

## 核心来源

| 来源 | 支持的内容 | 等级 | 适用范围和限制 |
|---|---|---|---|
| [ISO 24495-1:2023](https://www.iso.org/standard/78907.html), *Plain language — Part 1: Governing principles and guidelines* | 读者获得所需信息、容易找到、容易理解、容易使用；先识别读者、目的和场景；相关信息成组；重要信息前置；操作按时间顺序；危险警告放在动作前；把读者能否使用作为核心原则，并单列评估原则 | A | 本地只核对预览页，能确认前言、四项原则和部分条款；未读取完整标准，也未读到完整的评估指南。不能把具体读者测试方法都归到该标准名下。Plain language 不等于“简单语言”，也不等于只看可读性公式 |
| [Gopen & Swan, “The Science of Scientific Writing”](https://georgegopen.com/scientific-writing-articles/), *American Scientist*, 1990 | topic position 放旧信息，stress position 放新信息；主语靠近动词；动作由动词承担；先给语境；结构强调与内容重要性一致 | C | 作者明确说这些是读者期待，不是固定算法；高水平写作可以有意违反。文章以英文科学写作为例，不能直接推出所有中文句式规则 |
| [Reinhart et al., “Do LLMs write like humans? Variation in grammatical and rhetorical styles”](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/), *PNAS* 122(8):e2422455122, 2025, DOI 10.1073/pnas.2422455122 | instruction-tuned LLM 呈现名词密集、信息密集的风格；present participial clauses、nominalizations 等特征高于人类文本；装饰性词汇在多种文体中异常集中 | A | 英文语料研究，不是中文 AI 检测器。它支持“名词化、堆叠分词、装饰性词汇值得检查”，不能证明某个中文句子一定是 AI 写的 |
| [GOV.UK, “Use clear language”](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/) | Plain English 对专业读者也有价值；避免冗长词汇和 buzzword；`-ion` / `-ment` 名词化常使句子变复杂；术语第一次出现要解释；用 must / need / can 区分要求强度；优先主动语态；段落通常不超过 5 句，超过 25 词的句子考虑拆分 | B | 面向英国政府公开内容；长度数字是编辑指南，不是所有文体的硬阈值。中文不能机械照搬英文词数和语法 |
| [GOV.UK, “Use the right tone”](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/right-tone/) | 具体、信息充分、清楚简洁、正式但不摆架子；直接称呼读者；不必反复说 please；正式场合也要像在对一个人说话 | B | 政府公开服务的语气，不适用于所有私人消息或文学作品 |
| [Google developer documentation style guide, “Voice and tone”](https://developers.google.com/style/tone) | 像知识丰富的朋友说话，但不照搬口语；避免俚语、过度可爱、装饰性比喻、空话、重复开头；读出声检查；清楚直接比俏皮重要 | B | 英文开发者文档指南；其中 contractions、please 等规则不直接适用于中文 |
| [Microsoft Style Guide, “Top 10 tips for Microsoft style and voice”](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice) | 先给重要内容；让选择和下一步明显；删多余词；避免弱化的 there is / there are；指令尽量以动词开头 | B | 英文产品文档风格；短句和动词开头的具体做法要按中文文体调整 |
| [Diátaxis, “Start here”](https://diataxis.fr/start-here/) | 文档分为 tutorial、how-to、reference、explanation；四类服务不同需求，写法不同；混淆边界会造成大量文档问题 | B | 面向技术文档；可作为文体路由，不是所有组织都必须采用四分法 |
| ByteTech 内部文章《如何写好一篇文档？》（李云鹏，2024-02-21） | 自顶向下组织、先搭框架再填内容、关系用图、并列用表、排版服务阅读 | C/D | 旧 `doc-writing` 引用的中文工程写作经验；本次没有重新抓取全文，原文未随包分发 |
| [余光中《中文的常态与变态》](https://www.rmzxw.com.cn/c/2017-09-04/1768389.shtml) | 批评“万能动词 + 抽象名词”、过量介词、过长定语和滥用被动；同时明确说适度、高妙的西化可以截长补短 | C | 文学性论述，不是现代汉语语法标准。不能把所有欧化、长句和被动一律判错 |
| [叶圣陶《怎样写作》](https://www.chinawriter.com.cn/403936/419343/index.html) | 好文章要“诚实”和“精密”；“通”是用词适合、篇章调顺；修改文字本质上也是修改思想 | C | 面向一般写作的经典论述，不是可执行的质量指标；用于支持“先想清楚再改字” |
| [Barbara Minto, *The Minto Pyramid Principle* 官方概念页](https://www.barbaraminto.com/concept) | 先形成单一的中心思想，再按逻辑层级组织，引导读者沿金字塔向下阅读 | C | 商业写作方法，官方站点为概念介绍；本 Skill 只借用“结论先行、分层支撑”，不把 SCQ 当成所有文体的固定模板 |
| [Digital.gov, “Test for understanding”](https://digital.gov/guides/plain-language/test) | 把测试纳入写作过程，而不是写完才做；可用复述测试、任务可用性测试和对比研究检查读者是否理解 | B | 美国政府数字服务指南；方法以英文公开内容为背景，样本和流程要按本地条件调整。它支持“做读者测试”，不规定中文文本的具体样本量 |
| [Digital.gov, “Writing for understanding”](https://digital.gov/guides/plain-language/writing) | 先明确读者和目的，再组织内容；用读者熟悉的词、短句和具体例子；把重要信息放在读者容易找到的位置 | B | 政府公开写作指南；其中词长、句长等英文指标不能机械套到中文 |

## 旧版 Skill 的处理

项目早期使用的 `haohao-shuohua`、`doc-writing`、`de-ai-tech-writing`、`operation-doc-template` 提供了大量可用的经验，例如：

- 保真优先于风格。
- 先读全文，不逐句翻译。
- 业务名词进正文，标识符下沉。
- 操作步骤写清位置、动作、对象和结果。
- 事实与推断分开。
- 正式场合保留敬语和气势。

这些经验被吸收进新 Skill，但旧规则中的绝对化条目没有被原样继承。例如“章节编号零容忍”“破折号零容忍”“所有成稿必须附修改报告”“段落不超过五行”都不再作为跨文体硬规则。原因是它们会误伤操作步骤、法规引用、真正的并列、正式文案和必要的长句。

旧 `haohao-shuohua` 的 README 提到过 50 条 BadCase 和 9/8 误报率，但当前目录没有对应的可核对数据。本 Skill 不把这些数字当作已验证证据。

旧 `operation-doc-template` 还引用了团队内部操作文档模板。本 Skill 吸收了其中的章节映射、Verb + Task、全局前提与限制、成功确认和流程聚合规则；该模板未随包分发，访问权限和当前版本未在本次核验，团队实际使用时仍以最新模板为准。

旧 Skill 目录已在开发环境归档，不随发布包分发。归档只用于追溯，不参与当前技能路由。

## 旧能力落点

| 旧能力 | 在新 Skill 中的位置 |
|---|---|
| 读者任务、先总后分、框架、排版 | `SKILL.md` 的写作流程，`references/document-design.md` |
| 技术正文、标识符下沉、证据与推断、图 | `references/technical-writing.md` |
| 操作文档模板、Verb + Task、流程聚合、成功确认 | `references/operation-docs.md` |
| 去 AI 味、翻译腔、结构排比、词不配位 | `references/style-diagnostics.md` |
| 改稿流程、意义合同、受保护跨度、读者测试 | `references/editing-workflow.md` |
| 修改前后对照和保真边界 | `references/examples.md` |
| 机械扫描和测试 | `scripts/clarity_check.py`、`tests/test_clarity_check.py` |

## 未验证部分

- 没有做中文读者盲评，也没有比较不同模型使用本 Skill 前后的理解或执行效果。
- 没有验证脚本在真实长文档上的误报率和漏报率。
- 没有做跨文体的大规模人工评分。
- ISO 24495-1 只核对了预览页，不是完整标准。
- PNAS 研究是英文语料，不能直接当作中文 AI 味检测依据。
- GB/T 15834 和 GB/T 15835 的本地文件是扫描件，未成功抽取正文，因此没有把其中条款当作规则依据。

因此，本 Skill 的规则是“有来源支持的编辑原则”，不是“已经证明对所有中文文本有效的算法”。实际使用时要保留作者判断和读者反馈。
