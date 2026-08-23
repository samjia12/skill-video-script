# skill-video-script

根据产品信息和目标平台（抖音 / 视频号 / B 站），一次生成 **3 个不同风格** 的短视频脚本。每一版都包含分镜表、口播稿、黄金 3 秒开头、BGM 建议和字幕建议。

本仓库同时是：

- 可被 Agent 加载的 **Skill**（`SKILL.md`）
- 可离线运行的 **Python CLI / 库**（运行时仅标准库）

[English README](README.md)

## 功能特性

- **固定 3 风格：** 种草安利、干货教程、剧情反转。
- **平台 playbook：** 时长、节奏、话题、CTA、字幕安全区按平台区分。
- **黄金 3 秒：** 口播 + 画面 + 屏上大字 + 技法标签。
- **分镜表：** 时间轴连续，含机位与逐镜口播。
- **BGM：** 只给曲库搜索词与闪避建议，不给盗版曲名。
- **字幕：** 字体、位置、高亮色、每行字数上限。
- **默认离线。** 可选 `--backend llm` 走 OpenAI 兼容接口做润色。
- **边界防御：** 空输入、超长、非法 JSON、特殊字符、权限、限流、网络失败。

## 环境要求

- Python 3.9+
- 跑测试时需要 `pytest`（见 `requirements.txt`）

默认模板引擎 **不需要** API Key。

## 安装

```bash
git clone https://github.com/samjia12/skill-video-script.git
cd skill-video-script
python3 -m pip install -r requirements.txt
```

库代码在 `src/`。CLI 会自动加入该路径，不必先 `pip install -e .`。

作为 Grok / Claude / Codex Skill：把本目录拷进 agent 的 skills 路径，让 `SKILL.md` 可被发现。触发方式：`/skill-video-script`，或直接说「写一条抖音 / 视频号 / B 站脚本」。

## 快速开始

```bash
python3 scripts/generate_script.py \
  --name "清润防晒霜" \
  --platform douyin \
  --points "清爽不黏腻,SPF50+,学生党价格" \
  --audience "通勤学生和上班族" \
  --category "美妆防晒" \
  --price "79元"
```

JSON 文件：

```bash
python3 scripts/generate_script.py examples/douyin_skincare.json
python3 scripts/generate_script.py examples/wechat_coffee.json -o output/coffee.md --format md
python3 scripts/generate_script.py examples/bilibili_keyboard.json --format json
```

库调用：

```python
from video_script import generate, parse_brief, render_markdown

brief = parse_brief({
    "name": "清润防晒霜",
    "platform": "抖音",
    "selling_points": ["清爽不黏腻", "SPF50+"],
})
print(render_markdown(generate(brief)))
```

## 使用示例

`examples/` 下的文件均可在仓库根目录直接运行。

### 1. 抖音 · 防晒霜（种草 / 干货 / 反转）

**输入**（`examples/douyin_skincare.json`）：

```json
{
  "name": "清润防晒霜",
  "platform": "douyin",
  "category": "美妆防晒",
  "selling_points": ["清爽不黏腻", "SPF50+", "学生党价格"],
  "audience": "通勤学生和上班族",
  "price": "79元",
  "brand": "晴川",
  "duration_sec": 27
}
```

```bash
python3 examples/01_douyin_skincare.py
# 或：python3 scripts/generate_script.py examples/douyin_skincare.json
```

**输出摘录（版本 1 · 种草安利）：**

```
# 清润防晒霜 · 抖音 短视频脚本

## 版本 1 · 种草安利（`grass`）
- **标题：** 通勤学生和上班族请收藏：清润防晒霜真的有清爽不黏腻
- **时长：** 27s
- **话题：** #清润防晒霜 #美妆防晒 #清爽不黏腻 #种草 #日常 #抖音

### 黄金 3 秒开头
- **技法：** 结果前置（`result_first`）
- **时长：** 3.0s
- **口播：** 停！清爽不黏腻。
- **画面：** 桌面俯拍，手把清润防晒霜推到画面中心，同时切环境音变干净。
- **屏上大字：** 先别划走

### 分镜表
| # | 时间 | 角色 | 口播 |
| 1 | 0.0–3.0s | hook | 停！清爽不黏腻。 |
| 7 | 23.8–27.0s | cta | 还有想看对比实测的 |

### 口播稿
[0:00.0-0:03.0] 停！清爽不黏腻。
...
[0:23.8-0:27.0] 还有想看对比实测的

### BGM 建议
- 搜索词：夏日清爽 / 种草 / 轻快日常 / 阳光
- 闪避：口播相对对白 -18~-22 LUFS

### 字幕建议
- 字体：抖音美好体 / 思源黑体 Bold
- 每行不超过 11 字，高亮 #FFE500
```

同一次运行还会给出版本 2（三步用法）和版本 3（差点退货的反转）。

### 2. 视频号 · 便携胶囊咖啡机

**输入**（`examples/wechat_coffee.json`）：299 元胶囊机，面向租房党，36 秒。

```bash
python3 examples/02_wechat_coffee.py
```

**输出摘录：**

```
# 便携胶囊咖啡机 · 视频号 短视频脚本
- **平台：** 视频号（`wechat`）

## 版本 1 · 种草安利
- **标题：** 299元档的30秒出杯，我选便携胶囊咖啡机
- **话题：** #便携胶囊咖啡机 #小家电 #30秒出杯 #真实分享
- 黄金 3 秒口播：30秒出杯，是真的。
- 8 镜 / 36 秒；CTA 是关注 + 私信，而不是小黄车
```

该示例默认打印 JSON，方便接到后续工具。

### 3. B 站 · 客制化键盘套件

**输入**（`examples/bilibili_keyboard.json`）：499 元热插拔套件，面向第一次组装的人，60 秒。

```bash
python3 examples/03_bilibili_keyboard.py
```

**输出摘录：**

```
# 星核机械键盘套件 · B站 短视频脚本
- **平台：** B站（`bilibili`）
- **话题：** #星核机械键盘套件 #外设 #热插拔 #开箱 #测评

## 版本 1 · 种草安利
- **黄金 3 秒口播：** 结论：值。
- 9 镜 / 60 秒，口播更密，CTA 要三连；字幕给顶部弹幕留通道
```

一次跑完三个示例：

```bash
bash examples/run_all.sh
```

## 配置说明

| 环境变量 | 默认 | 含义 |
| --- | --- | --- |
| `VIDEO_SCRIPT_API_KEY` | 空 | 仅 `--backend llm` 时需要 |
| `VIDEO_SCRIPT_API_BASE` | `https://api.openai.com/v1` | OpenAI 兼容网关 |
| `VIDEO_SCRIPT_MODEL` | `gpt-4o-mini` | Chat Completions 模型名 |
| `VIDEO_SCRIPT_TIMEOUT` | `20` | HTTP 超时（秒） |

CLI 参数：

| 参数 | 说明 |
| --- | --- |
| `--name` / `--platform` / `--points` | 不写 JSON 时的产品字段 |
| `--audience` `--category` `--price` `--brand` `--description` `--duration` | 可选 |
| `--backend template\|llm` | 默认 `template`（离线） |
| `--format md\|json\|both` | 默认 `md` |
| `-o` / `--output` | 输出文件（自动建目录） |
| `--stdout` | 即使写了 `-o` 也打印 |
| `input` 或 `-` | JSON 路径或标准输入 |

平台别名：`抖音` / `douyin` / `tiktok`，`视频号` / `wechat` / `channels`，`B站` / `bilibili` / `哔哩哔哩`。

硬限制（见 `src/video_script/constants.py`）：名称 ≤ 80 字，卖点 ≤ 12 条，时长 8–180 秒，整包 ≤ 8000 字。

## FAQ

**一定要有大模型密钥吗？**
不用。默认是确定性的模板 / 策略引擎。只有显式 `--backend llm` 才会走网络；没密钥会直接失败，不会默默生成空稿。

**为什么口播是中文？**
抖音、视频号、B 站的内容场就是中文。Markdown 的章节名也保持中文，方便剪辑同学直接粘贴。

**能加 TikTok / Shorts / Reels 吗？**
1.0.0 不做。音乐授权和 CTA 表面都不一样。请开 issue，或扩展 `platforms.py` 与 `copy_bank.py`。

**会不会推荐一首有版权的热歌？**
不会。BGM 只输出情绪、BPM、类型和 **曲库搜索词**。

**黄金 3 秒看起来被截断了？**
引擎按平台口播字速卡字数，保证主播能在 3 秒内读完。产品名很长时请缩短名称，或把完整卖点放到后续分镜。

**怎样给 Agent 用？**
让 Agent 读取 `SKILL.md`。Skill 要求先收齐 brief，再跑 `scripts/generate_script.py`，并按固定顺序展示 3 个版本。

**退出码？**
`0` 成功，`2` 输入非法，`3` 网络，`4` 缺密钥或无写权限。

## 贡献指南

1. Fork 并开分支。
2. 运行时请保持标准库；新依赖要先在 issue 里讨论。
3. 改行为就近补测试（`tests/`）。
4. 提交前运行 `python3 -m pytest tests`。
5. 不要提交 API Key；不要往 `copy_bank.py` 里写盗版曲名。
6. PR 请附变更说明、测试输出、如有新示例请带 JSON。

三套实现方案的对比见 [`DESIGN.md`](DESIGN.md)。

## 许可证

[MIT](LICENSE) © 2026 skill-video-script contributors
