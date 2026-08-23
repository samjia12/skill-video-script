# skill-video-script 设计记录（阶段 1）

## 目标

输入产品信息与目标平台（抖音 / 视频号 / B 站），输出 **3 版不同风格** 的短视频脚本。每版必须包含：

- 分镜表
- 口播稿
- 黄金 3 秒开头方案
- BGM 建议
- 字幕建议

本仓库同时是：

1. 可被 Agent 加载的 Skill（`SKILL.md`）
2. 可独立运行的开源 Python CLI / 库

---

## 方案 A — Python 模板策略引擎 + 可选 LLM 适配器（stdlib 运行时）

**技术选型**

- Python 3.9+，运行时仅标准库
- 生成主路径：平台 playbook × 风格策略 × 模板槽位填充
- 可选 LLM 后端：`urllib` 调用兼容 OpenAI Chat Completions 的 HTTP API
- 测试：pytest
- 分发：src layout + `scripts/generate_script.py` CLI

**目录结构**

```
skill-video-script/
  SKILL.md
  src/video_script/      # 库（校验、生成、渲染、LLM）
  scripts/               # CLI 入口
  tests/
  examples/
  requirements.txt
```

**依赖**

- 运行时：无第三方依赖
- 开发：pytest

**优点**

- 无 API Key 也能完整运行，开源友好、CI 稳定、离线可用
- 输出确定可测：同一输入得到同一脚本，便于单元测试与回归
- 平台规则（时长、节奏、字幕安全区、CTA）可编码为数据，而不是散落在 prompt 里
- 可选 LLM 只在用户显式开启时介入，失败可回退模板，满足「网络失败 / 限流」等边界

**缺点**

- 文案上限受模板覆盖度约束，不如大模型「即兴」多样
- 新平台 / 新风格需要补策略数据，而不是只改一段 prompt

---

## 方案 B — Python + 强制 LLM SDK（OpenAI / Anthropic）

**技术选型**

- Python 3.10+ + `openai` 或 `anthropic` SDK + `tenacity` + `pydantic`
- 几乎全部文案由模型生成，代码只做 prompt 与 JSON schema 校验
- 目录类似方案 A，但 `generator.py` 变为 prompt 编排器

**依赖**

- openai / anthropic、python-dotenv、tenacity、pydantic、pytest

**优点**

- 文案更「像人」，少模板感
- 新增风格往往只改 prompt

**缺点**

- 没有密钥就不能运行，违反「完整可运行」
- 测试非确定、易 flake，还要付费与处理 ToS
- 平台硬约束（黄金 3 秒、时长、口播字数）容易被模型忽略，必须再写一层校验 / 重试，复杂度回到方案 A，却多了网络故障面
- 开源贡献者的第一道门槛过高

---

## 方案 C — TypeScript / Node.js 包（zod + commander）

**技术选型**

- Node 18+、TypeScript、zod 校验、commander CLI
- 模板或 LLM 二选一
- 以 npm 包形式发布

**依赖**

- typescript、zod、commander、vitest；若走 LLM 再加 openai

**优点**

- npm 生态分发成熟，前端 / 剪辑工具链集成方便
- zod 对 JSON 输入的类型体验好

**缺点**

- 当前 Agent Skill 惯例以 `SKILL.md` + Python `scripts/` 为主，TS 增加 Agent 执行摩擦
- 依赖树更大，Windows / 无 Node 环境贡献者成本更高
- 对「短视频中文口播 + 平台规则」没有语言优势，只是换了运行时

---

## 对比

| 维度 | 方案 A | 方案 B | 方案 C |
| --- | --- | --- | --- |
| 无密钥可运行 | 是 | 否 | 视实现 |
| 测试确定性 | 高 | 低 | 中高 |
| Agent Skill 契合度 | 高 | 中 | 低 |
| 文案上限 | 中（可 LLM 增强） | 高 | 中 |
| 平台硬约束可控性 | 高 | 低（需补丁层） | 中 |
| 维护成本 | 低 | 高 | 中 |
| 边界场景可测性 | 高（可注入 transport） | 中 | 中 |

---

## 选定方案

**选定方案 A。**

理由：

1. 本项目首先是开源 Agent Skill，必须在零配置下产出合格脚本；方案 B 做不到。
2. 分镜时长、黄金 3 秒、口播字速、字幕行宽是**硬约束**，用数据 + 策略实现比 prompt 更可测。
3. 把 LLM 做成可选适配器，既覆盖「网络失败 / 限流 / 权限」测试面，又不绑架运行时。
4. Python 3.9+ / stdlib 与现有 Skill 生态一致，贡献门槛最低。

不选 B：把可用性建立在密钥上，测试与贡献都会碎。
不选 C：运行时换血收益不足以覆盖 Skill 场景的摩擦。
