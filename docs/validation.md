# 验证记录

验证日期：2026-11-26。环境：macOS，Python 3.9.6。

## 已执行

### Skill 元数据

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" \
  skills/clear-writing
```

输出：

```text
Skill is valid!
```

### 脚本回归测试

```bash
python3 -m unittest discover -s skills/clear-writing/tests -v
```

输出：

```text
Ran 17 tests in 1.743s

OK
```

### 半角标点严格检查

```bash
python3 skills/clear-writing/scripts/clarity_check.py \
  --strict --checks half \
  skills/clear-writing/SKILL.md \
  skills/clear-writing/references/*.md
```

输出：

```text
半角标点         0 处
合计 0 处；模式=提示；--strict 时仅“半角标点”命中会让退出码为 1
exit=0
```

### 完整提示扫描

```bash
python3 skills/clear-writing/scripts/clarity_check.py --json \
  skills/clear-writing/SKILL.md \
  skills/clear-writing/references/*.md
```

汇总：

| 检查项 | 命中 |
|---|---:|
| 半角标点 | 0 |
| 万能动词 | 17 |
| 空泛元话语 | 2 |
| 机械编号标题 | 17 |
| 长句无气口 | 0 |
| 长段落 | 0 |
| 连续相同开头 | 1 |
| 对比翻案结构 | 5 |
| 免责尾巴 | 4 |
| 合计 | 46 |

这些命中主要来自示例、诊断词表和工具说明，属于预期结果。脚本默认只报告，退出码为 0；没有为了清零而改掉示例或词表。

### Markdown 内部链接

用脚本检查 `SKILL.md`、`README.md` 和 `references/*.md` 中的相对链接，所有目标文件都存在。外部链接未逐一重新抓取。

## 发布后验证

仓库：<https://github.com/SgtBaixiao/clear-writing>

### GitHub Actions

首次推送的校验因工作流没有安装 PyYAML 失败，失败原因是 `ModuleNotFoundError: No module named 'yaml'`。补上 `PyYAML==6.0.3` 后重新推送，校验通过：

- 工作流：`Validate skill package`
- 运行：<https://github.com/SgtBaixiao/clear-writing/actions/runs/45775388810>
- 结果：`success`，7 秒
- 步骤：元数据检查、17 个回归测试、半角标点严格检查均通过

运行环境为 GitHub Actions 的 Ubuntu 和 Python 3.12，与本机 Python 3.9.6 不同。两个环境都通过，说明脚本在这两个 Python 版本上都能运行。

### 从 GitHub 安装

在临时 `HOME` 中运行 README 的原始命令：

```bash
npx skills add SgtBaixiao/clear-writing --skill clear-writing -a codex -g
```

结果：

```text
✓ clear-writing (copied)
  → ~/.agents/skills/clear-writing
```

随后用 `quick_validate.py` 检查安装目录，输出 `Skill is valid!`。临时安装的 `SKILL.md` 与本机文件 SHA-256 相同，说明发布包内容与本地验证过的版本一致。这次测试没有改动真实的 `~/.agents/skills/clear-writing`。

## 未验证

- 没有做中文读者盲评，也没有比较不同模型使用本 Skill 前后的理解或执行效果。
- 没有做真实读者测试，不能声称读者理解或任务完成率已经提升。
- 没有验证脚本在真实长文档上的误报率和漏报率。
- 没有做跨文体的大规模人工评分。
- ISO 24495-1 只核对了预览页，不是完整标准。
- PNAS 研究基于英文语料，不能直接当作中文 AI 味检测依据。
- GB/T 15834 和 GB/T 15835 的本地文件是扫描件，未成功抽取正文，因此没有把其中条款当作规则依据。

## 结论

结构、脚本和测试已通过；这证明仓库中的 Skill 包可以安装、脚本可以运行、回归用例通过。它不证明对所有中文文本、所有读者和所有文体都有效。真实使用中的读者反馈仍是下一层证据。
