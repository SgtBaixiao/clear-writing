# Clear Writing

![Validate skill package](https://github.com/SgtBaixiao/clear-writing/actions/workflows/validate.yml/badge.svg)

一个面向中文写作、改写、审稿和交付前自检的 Agent Skill。它先确认读者要完成的任务，再组织结构、句子和措辞；把事实、数字、术语、模态和承诺的保真放在风格之前。

它不替作者决定观点，也不改写代码、配置、日志、公式和引文本身。纯翻译、代码和接口语义不在改写范围内。

## 覆盖什么

| 场景 | 重点 |
|---|---|
| 聊天、邮件、群消息 | 先给答案或请求，再补必要背景和下一步 |
| 周报、状态同步 | 结果、证据、风险、阻塞和需要谁支持 |
| 技术方案、决策文档 | 推荐结论、目标与非目标、选项取舍、实施和验证 |
| 事故复盘 | 影响、时间线、根因、处置、防止再发和未确认项 |
| 操作文档 | 前提、入口、一步一个动作、成功确认和异常处理 |
| README、Reference、Explanation | 按读者任务选择教程、操作、参考或解释逻辑 |
| 公开通知、评审、纪要 | 影响范围、所需动作、结论、分歧和行动项 |

它也处理“说人话”“去 AI 味”“翻译腔”“读着累”这类改写请求，但判断标准不是文字像不像人，而是目标读者能否找到、理解并执行。

## 安装

用 skills CLI 安装最新主分支：

```bash
npx skills add SgtBaixiao/clear-writing --skill clear-writing -a codex -g
```

也可以手动安装：

```bash
git clone https://github.com/SgtBaixiao/clear-writing.git
cp -R clear-writing/skills/clear-writing ~/.agents/skills/
```

把 `clear-writing` 放进你的 Agent 技能目录即可。Codex 常见目录是 `~/.agents/skills/` 或 `~/.codex/skills/`，以本机实际配置为准。已有同名 Skill 时先保留旧副本，再替换。

## 使用

```text
$clear-writing 把这段周报改成先给结果和风险，再写下一步。
$clear-writing 审这篇技术方案，指出结构、事实和表达问题，不要改我的观点。
$clear-writing 这段操作文档读者执行不下去，按一步一个动作重写，保留所有命令。
```

写回飞书、对外发布或进入长期文档库的中文成稿，建议运行：

```bash
python3 "$HOME/.agents/skills/clear-writing/scripts/clarity_check.py" <文件>
```

脚本默认只报告，不改变退出码；`--strict` 只把中文正文中的半角标点等字面项作为失败条件。它不判断作者意图，也不输出“AI 分数”。

## 包里有什么

| 路径 | 作用 |
|---|---|
| `skills/clear-writing/SKILL.md` | Skill 入口：读者、任务、六项标准、写作流程和交付自检 |
| `skills/clear-writing/references/document-design.md` | 读者、场景、文体结构、信息层级和排版 |
| `skills/clear-writing/references/technical-writing.md` | 技术正文、证据、术语、标识符和图 |
| `skills/clear-writing/references/operation-docs.md` | 操作文档、模板映射、步骤、警告和异常处理 |
| `skills/clear-writing/references/style-diagnostics.md` | AI 味、中文欧化、正反例和误报边界 |
| `skills/clear-writing/references/editing-workflow.md` | 意义合同、改稿力度、受保护跨度和读者测试 |
| `skills/clear-writing/references/examples.md` | 聊天、周报、方案、复盘、操作文档和通知的对照案例 |
| `skills/clear-writing/references/sources.md` | 证据等级、来源、适用范围和未验证部分 |
| `skills/clear-writing/scripts/clarity_check.py` | 可选的表面问题扫描脚本 |
| `skills/clear-writing/tests/test_clarity_check.py` | 脚本的 17 个回归测试 |
| `docs/validation.md` | 本次验证命令、结果和边界 |

## 验证

本次发布前实际运行过：

- `quick_validate.py` → `Skill is valid!`
- 17 个单元测试 → `OK`
- `clarity_check.py --strict --checks half` → 半角标点 0 处，退出码 0

完整提示扫描有 46 处建议，主要来自示例、诊断词表和工具说明。这些是编辑线索，不是失败。详细命令、输出和未验证部分见 [验证记录](docs/validation.md)。

## 边界

- 它不是“AI 检测器”，不能根据几个词判断一段文字是否由模型生成。
- 本次没有做中文读者盲评，也没有做真实读者测试；不能声称已经证明对所有中文文本有效。
- PNAS 的 LLM 文体研究基于英文语料，不能直接当作中文 AI 味检测依据。
- ISO 24495-1 只核对了预览页，不是完整标准。
- 脚本没有在真实长文档上验证误报率和漏报率；`--strict` 之外的命中都需要人判断。

## 来源与许可

规则来源、证据等级和适用范围见 [sources.md](skills/clear-writing/references/sources.md)。仓库只保留出处链接和归纳，不包含原网页、论文或内部模板正文。

本仓库原创规则、脚本和测试采用 [MIT License](LICENSE)。
