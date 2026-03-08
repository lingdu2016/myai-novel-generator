"""
预设提示词模板 - 去AI化版本
让生成的内容更自然、更像人类作家

版权所有 © 2026 新疆幻城网安科技有限责任公司 (幻城科技)
作者：幻城
"""

from typing import Optional, Dict, List

# ========== 风格约束模板（用于添加到任何提示词末尾）==========

STYLE_CONSTRAINTS = """
【本次写作禁忌】
别用这些词：突然、竟然、霎时间、不由得、禁不住
别在段首用：在...的时候、在...的背景下、随着...的发展
对话要口语化，别让人物说话像念书
描写要具体，别用空洞形容词（美丽的、壮观的、惊人的）
别用括号注释人物
别在结尾总结人生感悟
"""

# ========== 写作示例 ==========

WRITING_EXAMPLES = {
    "good": [
        "他点燃一支烟，烟雾在灯光下缓缓升起。\"事情没那么简单。\"他没看她。",
        "门口站着个人。一身黑，手里拎着个包。\"找谁？\"\"找你。\"",
        "雨下了一夜。天亮的时候，院子里积了水，漂着几片落叶。",
        "她把信折好，放进抽屉最里面。那是三年前的事了。",
        "\"吃饭没？\"\"吃了。\"\"吃的啥？\"\"面。\"\"啥面？\"\"牛肉面。\"",
        "楼下的狗叫了一整夜。第二天早上，狗死了。",
        "他抬头看了看天。要下雨了。\"走。\"她说。他就跟着走了。",
    ],
    "bad": [
        "突然，他感到一阵强烈的情绪涌上心头！这竟然是他从未体验过的感觉...",
        "在漆黑的夜晚背景下，随着雨越下越大，他不由得陷入了沉思...",
        "他（李明）看着她（王芳），心中涌起了复杂的情感（爱与恨交织）...",
        "霎时间，一股难以言喻的震撼感涌上心头，他终于明白了人生的真谛！",
        "她那美丽的脸庞上浮现出不可思议的笑容，让他心中不禁涌起阵阵涟漪...",
    ],
}

# ========== 重写风格模板 ==========

PRESET_TEMPLATES = {
    # ========== 重写风格模板 ==========
    "重写风格 - 默认": """请重写以下内容。要求：自然、流畅、像真人在写。

原文：
{content}

重写时注意：
- 删掉AI味道的词（突然、竟然、不由得、心中涌起...）
- 对话要像真人说话
- 描写要具体，不要空洞形容词
- 保持原意和情节

重写：""",

    "重写风格 - 玄幻仙侠": """以古典仙侠风格重写以下内容。

原文：
{content}

风格要求：
- 用词典雅，但别太文言
- 要有仙气和意境
- 修炼感悟要写出层次
- 战斗要有画面感
- 别用AI味太重的词

重写：""",

    "重写风格 - 都市言情": """以现代都市言情风格重写以下内容。

原文：
{content}

风格要求：
- 语言轻松自然
- 情感互动要细腻
- 心理描写要有代入感
- 对话要像真人说话
- 别写得太狗血

重写：""",

    "重写风格 - 悬疑惊悚": """以悬疑惊悚风格重写以下内容。

原文：
{content}

风格要求：
- 营造紧张氛围
- 埋下线索和悬念
- 节奏要紧凑
- 别用俗套的惊吓方式
- 逻辑要严密

重写：""",

    "重写风格 - 科幻硬核": """以硬科幻风格重写以下内容。

原文：
{content}

风格要求：
- 科学设定要严谨
- 技术细节要有
- 但别写成论文
- 要有人性思考
- 逻辑自洽

重写：""",

    "重写风格 - 武侠江湖": """以金庸古龙式武侠风格重写以下内容。

原文：
{content}

风格要求：
- 语言要有江湖气
- 武功招式要有画面感
- 人物要有侠义精神
- 恩怨情仇要分明
- 对白要简洁有力

重写：""",

    "重写风格 - 古代宫斗": """以古代宫廷风格重写以下内容。

原文：
{content}

风格要求：
- 语言典雅
- 宫廷礼仪要准确
- 权谋算计要有深度
- 人物关系复杂微妙
- 别把所有人都写得很坏

重写：""",

    "重写风格 - 现代军事": """以现代军事风格重写以下内容。

原文：
{content}

风格要求：
- 语言硬朗
- 战术描写要专业
- 军人气质要到位
- 战友情要真实
- 别把战争写得太浪漫

重写：""",

    "重写风格 - 历史演义": """以历史演义风格重写以下内容。

原文：
{content}

风格要求：
- 语言古朴庄重
- 历史背景要准确
- 人物要有传记感
- 要有宏大视角
- 别篡改重大史实

重写：""",

    "重写风格 - 灵异玄幻": """以灵异玄幻风格重写以下内容。

原文：
{content}

风格要求：
- 氛围要神秘诡异
- 超自然元素要合理
- 民间传说要尊重
- 因果要有逻辑
- 别太迷信

重写：""",

    "重写风格 - 青春校园": """以青春校园风格重写以下内容。

原文：
{content}

风格要求：
- 语言清新活泼
- 要有少年感
- 校园生活要真实
- 别太狗血
- 别太成人化

重写：""",

    "重写风格 - 职场商战": """以职场商战风格重写以下内容。

原文：
{content}

风格要求：
- 语言干练
- 商业细节要专业
- 职场博弈要真实
- 别写成宫斗
- 要有专业感

重写：""",

    "重写风格 - 赛博朋克": """以赛博朋克风格重写以下内容。

原文：
{content}

风格要求：
- 科技感要足
- 高科技低生活
- 要有反乌托邦色彩
- 义体、虚拟现实等元素
- 视觉要霓虹闪烁

重写：""",

    "重写风格 - 西幻魔法": """以西方奇幻风格重写以下内容。

原文：
{content}

风格要求：
- 要有史诗感
- 魔法体系要清晰
- 种族特点要鲜明
- 中世纪氛围
- 别写成西式修仙

重写：""",

    "重写风格 - 恐怖悬疑": """以恐怖悬疑风格重写以下内容。

原文：
{content}

风格要求：
- 氛围要阴森压抑
- 心理暗示要到位
- 悬念要埋好
- 别用jump scare
- 最可怕的是人心

重写：""",

    "重写风格 - 幽默搞笑": """以幽默搞笑风格重写以下内容。

原文：
{content}

风格要求：
- 对白要有机锋
- 夸张但要合理
- 别硬挠人痒痒
- 人物要可爱
- 尴尬场面是好素材

重写：""",

    "重写风格 - 文艺清新": """以文艺清新风格重写以下内容。

原文：
{content}

风格要求：
- 语言优美清新
- 意境要深远
- 情感要细腻
- 要有画面感
- 别太矫情

重写：""",

    "重写风格 - 热血冒险": """以热血冒险风格重写以下内容。

原文：
{content}

风格要求：
- 语言要激昂
- 冒险元素要足
- 战斗场面要有画面感
- 友情羁绊要真挚
- 要有正能量

重写：""",

    # ========== 章节生成模板 ==========
    "generation - 默认": """请根据以下信息创作章节。

小说：{title}
类型：{genre}

第{chapter_num}章：{chapter_title}
大纲：{chapter_desc}

前文：
{context}

要求：
- 字数约{target_words}字
- 风格：{style}
- 接着前文写，保持连贯
- 人物性格保持一致
- 对话要像真人说话
- 别用AI味太重的词

开始创作：""",

    "generation - 玄幻仙侠": """请创作玄幻仙侠小说的章节。

小说：{title}
世界观：{world_setting}
人物：{character_setting}

第{chapter_num}章：{chapter_title}
大纲：{chapter_desc}

前文：
{context}

要求：
- 字数约{target_words}字
- 战斗要有画面感
- 修炼要有层次感
- 语言要有古韵但别太文言
- 仙气要有，地气也要有

开始创作：""",

    "generation - 都市言情": """请创作都市言情小说的章节。

小说：{title}
类型：{genre}
主角：{character_setting}

第{chapter_num}章：{chapter_title}
大纲：{chapter_desc}

前文：
{context}

要求：
- 字数约{target_words}字
- 情感互动要细腻
- 对话要像真人
- 要有生活气息
- 节奏要明快

开始创作：""",

    "generation - 悬疑推理": """请创作悬疑推理小说的章节。

小说：{title}
类型：{genre}
核心谜题：{plot_idea}

第{chapter_num}章：{chapter_title}
大纲：{chapter_desc}

前文：
{context}

要求：
- 字数约{target_words}字
- 要有悬念和线索
- 氛围要紧张
- 逻辑要严密
- 别让读者太早猜到

开始创作：""",

    # ========== 大纲生成模板 ==========
    "outline - 默认": """请为以下小说创作大纲。

小说：{title}
类型：{genre}
世界观：{world_setting}
人物：{character_setting}
主线：{plot_idea}

要求：
- 共{chapter_count}章
- 每章写：章节名、主要情节、字数建议
- 结构要完整
- 节奏要张弛有度
- 每章都要有明确目的

大纲格式：
第X章 | 章节名
主要情节：xxx
本章目的：推进剧情/塑造人物/埋伏笔
字数建议：xxx字

开始创作：""",

    # ========== 角色生成模板 ==========
    "character - 创建": """请创建一个角色。

小说类型：{genre}
世界观：{world_setting}
姓名：{character_name}
定位：{character_role}

请写：
- 外貌（具体，有特点）
- 性格（用行为表现，不用形容词堆砌）
- 背景（简洁有故事）
- 能力/特长
- 人际关系
- 说话风格（口头禅、说话特点）

角色档案：""",

    # ========== 世界观生成模板 ==========
    "world - 创建": """请创建世界观。

小说类型：{genre}
核心创意：{plot_idea}

请写：
- 世界概述（历史、地理、社会）
- 力量体系/规则
- 重要地点
- 重要势力/组织
- 世界特色

要具体，要有用，别写虚的。

世界观设定：""",
}


def get_style_constraints() -> str:
    """获取风格约束模板"""
    return STYLE_CONSTRAINTS


def get_writing_examples() -> Dict[str, List[str]]:
    """获取写作示例"""
    return WRITING_EXAMPLES


def get_preset_template(category: str, name: str) -> str:
    """
    获取预设模板

    Args:
        category: 类别（generation/rewrite/outline等）
        name: 模板名称

    Returns:
        模板内容，如果不存在则返回空字符串
    """
    key = f"{category} - {name}"
    return PRESET_TEMPLATES.get(key, "")


def list_preset_templates(category: Optional[str] = None) -> Dict[str, List[str]]:
    """
    列出预设模板

    Args:
        category: 类别，None表示所有

    Returns:
        {category: [template_names]}
    """
    result = {}

    for key in PRESET_TEMPLATES.keys():
        if " - " in key:
            cat, name = key.split(" - ", 1)

            if category and cat != category:
                continue

            if cat not in result:
                result[cat] = []

            result[cat].append(name)

    return result


def build_chapter_prompt(
    title: str,
    genre: str,
    chapter_num: int,
    chapter_title: str,
    chapter_desc: str,
    context: str,
    target_words: int,
    style: str = "默认",
    world_setting: str = "",
    character_setting: str = "",
    plot_idea: str = "",
) -> str:
    """
    构建章节生成提示词

    Args:
        title: 小说标题
        genre: 小说类型
        chapter_num: 章节号
        chapter_title: 章节标题
        chapter_desc: 章节描述
        context: 前文内容
        target_words: 目标字数
        style: 风格
        world_setting: 世界观设定
        character_setting: 人物设定
        plot_idea: 核心剧情

    Returns:
        完整的章节生成提示词
    """
    # 选择合适的模板
    template_key = f"generation - {style}"
    template = PRESET_TEMPLATES.get(template_key, PRESET_TEMPLATES["generation - 默认"])

    # 填充模板
    prompt = template.format(
        title=title,
        genre=genre,
        chapter_num=chapter_num,
        chapter_title=chapter_title,
        chapter_desc=chapter_desc,
        context=context,
        target_words=target_words,
        style=style,
        world_setting=world_setting,
        character_setting=character_setting,
        plot_idea=plot_idea,
    )

    # 添加风格约束
    prompt += STYLE_CONSTRAINTS

    return prompt