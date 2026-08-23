"""Chinese copy templates. Slots: name, point, points, audience, price, brand, category."""

from __future__ import annotations

# Hook spoken lines keyed by (platform_id, style_id)
HOOK_SPOKEN: dict[tuple[str, str], tuple[str, ...]] = {
    ("douyin", "grass"): (
        "停！{point}。",
        "先别划走——{point}。",
        "先别划走——这个{name}，我瞒了同事整整一个月。",
        "用了三天{name}，{audience}都在问我是不是换了套装备。",
        "停。{price}能买到{point}？我本来也不信。",
    ),
    ("douyin", "howto"): (
        "收藏：{point}三步。",
        "只会把{name}当普通{category}用？那你亏大了。",
        "90 秒教你把{name}用出{point}，收藏比点赞更有用。",
        "三个步骤，让{name}从「吃灰」变成每天必用。",
    ),
    ("douyin", "story"): (
        "差点退了。",
        "我差点把{name}退了，直到发生了这件事。",
        "昨天还在骂{category}都是智商税，今天我把话吞回去了。",
        "镜头别晃——{audience}最怕的坑，我刚踩完。",
    ),
    ("wechat", "grass"): (
        "{point}，是真的。",
        "跟你讲个真心话：{name}是我这个月唯一愿意安利的{category}。",
        "不是广告。{audience}真的可以看完这条再决定。",
        "我把{name}用了一周，只想说一句：{point}是真的。",
    ),
    ("wechat", "howto"): (
        "先别买，看用法。",
        "别急着下单。先看{name}正确的打开方式。",
        "我把{name}的用法压成三步，适合{audience}直接照做。",
        "视频号里少套路：{name}怎么用，才配得上{point}。",
    ),
    ("wechat", "story"): (
        "我被打脸了。",
        "上周我把{name}劝退了，结果……被打脸。",
        "朋友把{name}塞给我时我白眼都翻上天，后来沉默了。",
        "从怀疑到回购，只隔了一次真实体验。",
    ),
    ("bilibili", "grass"): (
        "结论：值。",
        "三连之前先听完：{name}到底值不值这份{point}。",
        "我是{audience}，测完{name}只给一个结论——值。",
        "别被封面骗了，{name}的真实体验比参数更狠。",
    ),
    ("bilibili", "howto"): (
        "先给结论：{point}。",
        "本期干货：把{name}拆成可复现的三步，章节在评论区。",
        "0 基础{audience}也能跟上，{name}正确用法一份带走。",
        "先给结论：想要{point}，别再用错{name}。",
    ),
    ("bilibili", "story"): (
        "弹幕先打打脸。",
        "我本来想做一期劝退{name}，素材拍到一半方向反了。",
        "从开箱翻车到真香，这期是我今年最不想承认的打脸。",
        "弹幕可以先打「打脸」，但请看到反转。",
    ),
}

HOOK_VISUAL: dict[str, tuple[str, ...]] = {
    "grass": (
        "口播近景突然伸手挡镜头，0.4 秒后产品怼脸入画，切使用前后对比。",
        "桌面俯拍，手把{name}推到画面中心，同时切环境音变干净。",
    ),
    "howto": (
        "白板/备忘录大字打出「3 步」，再切产品特写与第一步动作。",
        "分屏：左边错误用法，右边正确用法，0.5 秒对切。",
    ),
    "story": (
        "先拍失败现场（皱眉/翻车），黑场 0.2 秒，再切今天的结果。",
        "手持跟拍推门进场，忽然定格，字幕甩出冲突句。",
    ),
}

HOOK_SCREEN: dict[str, tuple[str, ...]] = {
    "grass": ("先别划走", "瞒了很久的私藏", "{point}"),
    "howto": ("3 步用法", "收藏这条", "你会用错"),
    "story": ("差点退货", "打脸现场", "看到最后"),
}

# role -> spoken templates
SHOT_VO: dict[str, tuple[str, ...]] = {
    "hook": ("{hook_line}",),
    "pain": (
        "以前用普通{category}，最崩的就是做不到{point}，{audience}应该懂这种烦。",
        "不是我矫情，是真的懒得再踩坑。",
    ),
    "reveal": (
        "直到换上{name}，{point}这件事终于不用靠意志力硬撑。",
        "{brand}这个{name}，我是用完才肯开口的。",
    ),
    "closeup": (
        "细节给你们看：质感、上手、{point}，镜头不美化。",
        "靠近一点，{name}到底好在哪，屏幕里也能看清。",
    ),
    "proof": (
        "连续用下来，{points}这几件事都站得住，不是靠滤镜。",
        "我把最挑剔的点拿来压它，{name}没掉链子。",
    ),
    "lifestyle": (
        "现在它就待在我每天伸手就能够到的地方，{audience}的节奏完全接得住。",
        "不是堆参数，是真的能嵌进日常。",
    ),
    "promise": (
        "看完你会带走三件事：怎么选、怎么用、怎么避开最常见的错法。",
        "目标很明确——让{name}真正用出{point}。",
    ),
    "tip1": (
        "第一步，先别急着猛用。把{name}放对场景，{point}才出得来。",
        "选对时机比堆用量更重要，{audience}记这个就够。",
    ),
    "tip2": (
        "第二步，抓住{points}里最关键的那个点，重复到形成肌肉记忆。",
        "动作要慢、要稳，镜头怎么演示你就怎么做。",
    ),
    "tip3": (
        "第三步，用完做一次 10 秒复盘：有没有{point}？没有就回到第一步。",
        "可复现比一次拍得好看更重要。",
    ),
    "recap": (
        "复习一下：场景、动作、复盘。{name}不是玄学。",
        "三步走完，{audience}基本就不会再把{name}用废。",
    ),
    "setup": (
        "故事要从我第一次遇见{name}说起——当时我只觉得又是普通{category}。",
        "设定很简单：一个对{category}免疫的{audience}。",
    ),
    "conflict": (
        "结果第一天就翻车，我差点当众把它判死刑。",
        "评论区如果是我，这会儿已经在打「退退退」。",
    ),
    "twist": (
        "转机来得很没礼貌：我按对方法再用了一次，{point}直接打脸。",
        "不是产品突然变好，是我之前用错了。",
    ),
    "solution": (
        "{name}的解法其实就写在{points}上，对上了，戏就结束了。",
        "它不是救世主，但它把我的痛点砸准了。",
    ),
    "result": (
        "现在回头看，我感谢那个差点退货的自己。",
        "从翻车到真香，中间只隔一次正确体验。",
    ),
    "detail": (
        "再补一个容易被忽略的细节：{point}在真实场景里比参数表更明显。",
        "{description_or_point}",
    ),
    "demo": (
        "完整演示一遍，动作放慢，你们可以暂停跟做。",
        "手怎么放、停几秒，我按实际使用来，不演。",
    ),
    "reaction": (
        "我自己的反应很俗：沉默，然后打开回购页。",
        "{audience}用完大概也是这表情。",
    ),
    "compare": (
        "和普通{category}比，{name}赢在{point}，其他我不会吹。",
        "不全面拉踩，只比你最在意的那一项。",
    ),
    "cta": (
        "需要的话我把清单留评论区。觉得有用就留下，转发比点赞更狠。",
        "还有想看对比实测的，评论区报题，我做下一支。",
    ),
}

SHOT_VISUAL: dict[str, str] = {
    "hook": "黄金 3 秒镜头，见 hook.visual。",
    "pain": "生活痛点空镜：皱眉、放弃、把旧物推到一边。",
    "reveal": "产品出场：从包里/抽屉取出，光线干净的手持特写。",
    "closeup": "微距/近景扫过材质、按钮、质感与包装信息。",
    "proof": "使用过程实录 + 结果特写，避免过度滤镜。",
    "lifestyle": "把产品放回真实场景（通勤、桌面、出门），环境声保留。",
    "promise": "口播面对镜头，画面叠三行目录字幕。",
    "tip1": "第一步完整动作，可加箭头/圈画。",
    "tip2": "第二步动作，切多机位或俯拍更清楚。",
    "tip3": "第三步 + 结果确认镜头。",
    "recap": "三张关键帧快速回闪，配数字 1 2 3。",
    "setup": "建立人物与场景，稳定中景。",
    "conflict": "失败/尴尬瞬间，手持微晃可以，但字幕要稳。",
    "twist": "硬切：同一机位的「后来」状态，光线更亮。",
    "solution": "产品作为解题道具出现，动作干脆。",
    "result": "结果展示 + 情绪放松的中近景。",
    "detail": "补充特写，强调一个被忽略的卖点。",
    "demo": "跟做演示，镜头与双手同框。",
    "reaction": "真人反应，不要假装夸张。",
    "compare": "左右分屏或前后对比，标注「之前/现在」。",
    "cta": "产品 + 人脸同框，指向评论区/购物车/三连位置。",
}

SHOT_CAMERA: dict[str, str] = {
    "hook": "近景推镜 0.5 秒 + 硬切特写",
    "pain": "中景手持",
    "reveal": "腰平推近",
    "closeup": "微距或 2 倍焦距",
    "proof": "固定机位俯拍",
    "lifestyle": "跟拍/侧跟",
    "promise": "正面口播，眼神看镜头",
    "tip1": "过肩 + 俯拍",
    "tip2": "俯拍为主",
    "tip3": "正面 + 结果特写",
    "recap": "快切 3 镜",
    "setup": "中景稳定器",
    "conflict": "手持微晃",
    "twist": "硬切同机位",
    "solution": "产品特写插入",
    "result": "中近景",
    "detail": "微距",
    "demo": "双手入画俯拍",
    "reaction": "近景",
    "compare": "分屏或前后切",
    "cta": "中近景固定",
}

TITLES: dict[str, tuple[str, ...]] = {
    "grass": ("{audience}请收藏：{name}真的有{point}", "瞒着同事用的{name}", "{price}档的{point}，我选{name}"),
    "howto": ("{name}正确用法 3 步", "别再用错{name}", "{audience}专属：{name}最短路径"),
    "story": ("我差点把{name}退了", "从劝退到真香：{name}", "打脸现场，主角是{name}"),
}

COVERS: dict[str, tuple[str, ...]] = {
    "grass": ("先别买错", "私藏{category}", "{point}"),
    "howto": ("3 步就会", "收藏再看", "用对才值"),
    "story": ("差点退货", "反转来了", "真香警告"),
}

CTA_BY_PLATFORM: dict[str, tuple[str, ...]] = {
    "douyin": (
        "点赞收藏，评论区扣「清单」我把注意事项置顶；要下单走小黄车更稳。",
        "觉得有用就双击，想看对比款在评论区报名字。",
    ),
    "wechat": (
        "关注后在评论区告诉我你的使用场景，我按{audience}的情况补一版。",
        "喜欢就点个赞，需要链接或清单可以私信，不搞强迫。",
    ),
    "bilibili": (
        "三连是最大支持。评论区置顶章节和参数表，想看下一期对比就投个币。",
        "喜欢这种拆解就关注，下期做{category}横评，弹幕区报你想看的型号。",
    ),
}

BGM_BY_STYLE: dict[str, dict[str, str]] = {
    "grass": {
        "mood": "轻快、温暖、有一点小得意",
        "tempo_bpm": "96-110",
        "genre": "acoustic pop / light electronic",
        "energy": "mid",
        "avoid": "重金属、恐怖低音、歌词抢口播",
    },
    "howto": {
        "mood": "干净、专注、不煽情",
        "tempo_bpm": "104-120",
        "genre": "lo-fi beat / corporate electronic",
        "energy": "mid-low",
        "avoid": "旋律大起大落、人声哼唱盖过讲解",
    },
    "story": {
        "mood": "前半压抑，反转后上扬",
        "tempo_bpm": "80 then 118",
        "genre": "cinematic to pop",
        "energy": "low → high",
        "avoid": "全程同一条嗨曲，把反转拍平",
    },
}

BGM_KEYWORDS: dict[tuple[str, str], tuple[str, ...]] = {
    ("douyin", "grass"): ("夏日清爽", "种草", "轻快日常", "阳光"),
    ("douyin", "howto"): ("干货", "节奏稳定", "科技感轻", "专注"),
    ("douyin", "story"): ("反转", "剧情", "情绪", "打脸"),
    ("wechat", "grass"): ("温暖", "生活", "推荐", "真诚"),
    ("wechat", "howto"): ("教程", "干净", "轻音乐", "说明"),
    ("wechat", "story"): ("故事", "转折", "日常", "真实"),
    ("bilibili", "grass"): ("开箱", "治愈", "推荐", "VLOG"),
    ("bilibili", "howto"): ("教程", "知识", "BGM轻", "章节"),
    ("bilibili", "story"): ("剧情", "反转", "打脸", "高能"),
}

TECHNIQUE_LABELS = {
    "result_first": "结果前置",
    "curiosity_gap": "好奇缺口",
    "pattern_interrupt": "模式打断",
    "social_proof": "社交证明",
    "pain_point": "痛点直击",
}
