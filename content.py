# -*- coding: utf-8 -*-
"""《潮汐拾荒者》内容数据（给人类开发者维护用）。

AI 玩家请不要阅读本文件——这里是全部剧透：物品、概率、隐藏地点和剧情。
打包脚本 build.py 会把本文件和 engine.py 一起封进 island.py。
"""

# ───────── 稀有度 ─────────
RARITY = {
    "C": {"label": "常见", "w": 100},
    "U": {"label": "少见", "w": 34},
    "R": {"label": "稀有", "w": 9},
    "E": {"label": "珍贵", "w": 2.2},
    "L": {"label": "传说", "w": 0.5},
}

CATS = {
    "res": "基础资源", "food": "食物", "mat": "建筑材料", "tool": "工具",
    "sell": "杂货", "coll": "收藏品", "relic": "古董遗物", "quest": "任务道具",
    "seed": "种子", "meal": "料理",
}

# ───────── 物品 ─────────
# id: (名字, 类别, 稀有度, 出售价, 描述, 附加属性)
# 附加属性：food=恢复体力；dur=工具耐久；heal=治伤；open=可打开；grow=(产物,数量,天数)
ITEMS = {
    # —— 海滩 ——
    "shell": ("白贝壳", "res", "C", 1, "最普通的扇贝壳，背面一圈圈纹路像树的年轮。", {}),
    "driftwood": ("漂流木", "mat", "C", 2, "被海水泡得发白的木头，轻，干了以后很好烧。", {}),
    "kelp": ("海带", "food", "C", 1, "缠成一团的海带，洗干净能嚼，有股咸味。", {"food": 6}),
    "sea_glass": ("海玻璃", "mat", "U", 4, "被浪磨圆的玻璃碎片，对着光是浅绿色的。", {}),
    "rope_scrap": ("旧绳头", "res", "C", 1, "一截磨毛的麻绳头，还能编进新绳子里。", {}),
    "bottle_cap": ("锈瓶盖", "sell", "C", 1, "一枚锈透了的瓶盖，背面印着看不清的汽水牌子。", {}),
    "crab": ("小螃蟹", "food", "C", 2, "横着跑的小螃蟹，被你抓住时一脸不服。", {"food": 8}),
    "conch": ("海螺", "sell", "U", 6, "贴在耳边能听见很远的潮声——也可能是你自己的心跳。", {}),
    "cowrie": ("宝贝螺", "sell", "U", 8, "背面油亮的花斑螺，据说古时候被当成钱用。", {}),
    "pumice": ("浮石", "res", "C", 1, "满身小孔的轻石头，能浮在水上。磨东西很好用。", {}),
    "sand_dollar": ("沙钱", "sell", "U", 6, "扁平圆润的海胆骨骼，上面有一朵五瓣花。", {}),
    "plastic_duck": ("褪色黄鸭", "coll", "U", 5, "一只洗澡用的塑料鸭，漂了不知多少年，颜色快褪成奶白。", {}),
    "tin_soldier": ("锡兵人", "coll", "R", 18, "缺了一条腿的锡兵，还保持着敬礼的姿势。", {}),
    "glass_float": ("玻璃浮球", "coll", "R", 30, "老式渔网上的绿色玻璃浮球，里面封着一个小气泡。", {}),
    "amber_lump": ("琥珀块", "sell", "R", 40, "蜂蜜色的树脂化石，里面困着一只很小很小的虫。", {}),
    "old_coin": ("铜币", "relic", "U", 12, "一枚磨平的旧铜币，只看得出一个“通”字。", {}),
    "carved_bird": ("漂流木雕鸟", "coll", "R", 25, "有人用小刀把漂流木刻成了一只海鸥，翅膀刻得很认真。", {}),
    "broken_compass": ("破罗盘", "relic", "R", 35, "指针卡死了，永远指着西北偏北。", {}),
    "tin_box": ("铁皮盒", "res", "U", 3, "被沙子半埋的铁皮盒子，摇一摇里面有东西在响。（可以 open 打开）", {"open": "tin_box"}),
    "baleen": ("鲸须", "coll", "R", 45, "风暴后被冲上岸的一片鲸须，梳子一样，摸起来像指甲。", {}),
    "broken_mast": ("断桅杆", "mat", "U", 6, "一截粗壮的断桅杆，是盖房子的好料。拆开能得不少木材。", {}),
    "ship_lamp": ("船灯残骸", "relic", "R", 30, "一盏破船灯，玻璃罩还在，灯芯早就没了。", {}),
    "glow_algae": ("夜光藻", "res", "U", 4, "只在夜里的浪尖上发光的藻类，装进瓶子里能亮好一阵。", {}),
    "sand_crab": ("幽灵沙蟹", "food", "U", 4, "夜里出来的白色沙蟹，跑得比风快。", {"food": 10}),
    "turtle_shell_frag": ("龟甲残片", "coll", "R", 22, "一片海龟背甲，纹路像一张地图。", {}),
    "message_note": ("空白信纸", "res", "C", 0, "一张干透的信纸，只写了“见字如面”四个字。", {}),
    # —— 礁滩 ——
    "mussel": ("贻贝", "food", "C", 2, "黑亮的贻贝一串串挂在礁石上。", {"food": 8}),
    "limpet": ("帽贝", "food", "C", 1, "像小斗笠一样吸在石头上，很难撬。", {"food": 5}),
    "starfish": ("海星", "sell", "C", 2, "橘红色的五角海星，翻过来会慢慢把自己翻回去。", {}),
    "sea_urchin": ("海胆", "food", "U", 5, "浑身是刺，里面却是一勺金黄。", {"food": 12}),
    "coral_branch": ("珊瑚枝", "sell", "U", 8, "被冲断的一枝红珊瑚，像一棵很小的树。", {}),
    "octopus": ("小章鱼", "food", "U", 6, "躲在石缝里的小章鱼，被发现时喷了你一脸墨。", {"food": 14}),
    "abalone": ("鲍鱼", "food", "R", 18, "贴得极紧的鲍鱼，壳内侧闪着彩虹。", {"food": 22}),
    "reef_fish": ("礁石鱼", "food", "C", 3, "退潮后困在水洼里的小鱼。", {"food": 9}),
    "pearl": ("珍珠", "sell", "U", 45, "从贝壳里撬出来的一颗珍珠，有一点点不圆。", {}),
    "black_pearl": ("黑珍珠", "sell", "E", 160, "孔雀绿色光泽的黑珍珠，几百只贝里才有一颗。", {}),
    "copper_ore": ("铜矿石", "mat", "U", 6, "嵌在礁岩里的绿锈色矿石。", {}),
    "tide_crystal": ("潮汐晶", "mat", "R", 30, "只在退潮最低时露出的透明晶簇，摸上去是凉的，像握着一小口海水。", {}),
    "sea_hare": ("海兔", "sell", "U", 4, "软乎乎的海兔，碰一下会吐出紫色的墨。你又把它放回去……不，你没放。", {}),
    "barnacle_bell": ("藤壶铃", "coll", "R", 35, "一只铜铃被藤壶长满了，晃起来声音闷闷的，像在水下响。", {}),
    "hermit_house": ("寄居蟹的旧房子", "coll", "U", 7, "一只螺壳，里面的住户刚刚搬走，留下一点湿沙。", {}),
    # —— 森林 ——
    "wood": ("木材", "mat", "C", 3, "干燥结实的木柴，盖房子、做工具都离不开。", {}),
    "fiber": ("植物纤维", "res", "C", 1, "从藤蔓和草茎里剥出来的纤维，能搓成绳子、编成鞋。", {}),
    "resin": ("松脂", "res", "U", 3, "黏糊糊的松脂，闻起来像圣诞节。可以当胶，也能点火。", {}),
    "mushroom": ("林菇", "food", "C", 2, "褐色的小蘑菇，确认过了，能吃。", {"food": 7}),
    "glowcap": ("荧光菇", "food", "U", 6, "夜里在树根下发蓝光的蘑菇，吃下去舌头会麻一会儿。", {"food": 10}),
    "berries": ("雾莓", "food", "C", 2, "雾里长的小浆果，酸得人眯眼。", {"food": 7}),
    "herb": ("止血草", "res", "U", 4, "叶子揉碎了敷在伤口上会清凉。能治轻伤。", {"heal": True}),
    "owl_feather": ("林鸮羽毛", "coll", "U", 6, "一根带横纹的柔软羽毛，飞起来几乎没有声音。", {}),
    "mist_antler": ("雾鹿角", "coll", "R", 30, "一只鹿换角时掉下的角。岛上真的有鹿？", {}),
    "stone_idol": ("石偶", "relic", "R", 45, "手掌大的石头小人，捧着一只碗，不知道是给谁的供品。", {}),
    "moss_stone": ("苔石", "mat", "C", 1, "长满青苔的石块，垒灶台、铺小路都用得上。", {}),
    "honeycomb": ("野蜂巢", "food", "U", 8, "从倒下的树干里掏出来的蜂巢，代价是手上两个包。", {"food": 16}),
    "mist_orchid": ("雾兰", "coll", "E", 120, "只在浓雾天开花的兰花，花瓣薄得像雾本身。", {}),
    "bird_nest": ("空鸟巢", "sell", "U", 3, "一只编得很精细的空鸟巢，里面垫着蓝色的线头。", {}),
    "carved_slab": ("刻字石板", "relic", "R", 40, "半埋在落叶里的石板，刻着一行字：“灯不灭，船自归”。", {}),
    "pine_cone": ("松果", "res", "C", 1, "很大的松果，被松鼠啃了一半。", {}),
    "berry_seed": ("雾莓种子", "seed", "U", 3, "可以种在小花园里。", {"grow": ("berries", 3, 4)}),
    "herb_seed": ("药草种子", "seed", "U", 4, "可以种在小花园里。", {"grow": ("herb", 2, 3)}),
    "thrift_seed": ("海石竹种子", "seed", "R", 10, "可以种在小花园里。开粉色的小绒球花。", {"grow": ("sea_thrift", 1, 5)}),
    "sea_thrift": ("海石竹花束", "coll", "R", 25, "一束粉色的海石竹，风再大也不倒。", {}),
    "squirrel_stash": ("松鼠的私房", "res", "U", 2, "一小堆藏在树洞里的坚果和……一颗玻璃弹珠？（可以 open 打开）", {"open": "stash"}),
    "rusty_key": ("生锈的钥匙", "quest", "R", 0, "一把很小的铜钥匙，钥匙柄上刻着一座塔。", {}),
    # —— 沉船 ——
    "nails": ("铁钉", "mat", "C", 2, "从船板上拔下来的铁钉，弯的可以敲直。", {}),
    "iron_scrap": ("废铁", "mat", "C", 2, "锈蚀的铁件，熔掉或者敲一敲还能用。", {}),
    "brass_gear": ("黄铜齿轮", "mat", "U", 8, "一枚小齿轮，转起来还很顺。", {}),
    "canvas": ("帆布", "mat", "U", 5, "从破帆上割下来的厚帆布，洗洗还能用。", {}),
    "porcelain": ("青花瓷片", "relic", "U", 15, "一片青花碎瓷，画着半条鱼。", {}),
    "silver_spoon": ("银汤匙", "relic", "R", 35, "柄上刻着“晨星”两个小字。", {}),
    "sextant": ("六分仪", "relic", "E", 150, "黄铜六分仪，镜片碎了一片。曾经有人用它找到过回家的方向。", {}),
    "ship_bell": ("晨星号船钟", "relic", "E", 180, "一口沉重的船钟，钟壁上铸着“晨星号”三个字。", {}),
    "old_rum": ("陈年朗姆", "sell", "R", 40, "一瓶封口完好的朗姆酒，标签被水泡成了一团云。", {}),
    "music_box": ("旧八音盒", "coll", "E", 100, "拧几圈发条，叮叮咚咚响起一首没听过的摇篮曲。", {}),
    "captain_pipe": ("船长烟斗", "relic", "R", 38, "石楠木烟斗，咬痕很深。", {}),
    "cannonball": ("生锈炮弹", "sell", "U", 6, "实心铁球，重得要死。你为什么要捡这个。", {}),
    "doubloon": ("金币", "relic", "R", 60, "一枚异国金币，被海水洗得发亮。", {}),
    "logbook_page": ("航海日志残页", "quest", "U", 0, "晨星号的航海日志，字迹被水晕开了一半。（可以 read logbook 阅读）", {}),
    "map_a": ("海图残片·甲", "quest", "R", 0, "一角海图，画着一道弯弯的海岬。", {}),
    "map_b": ("海图残片·乙", "quest", "R", 0, "一角海图，标着一个小小的鲸鱼记号。", {}),
    "map_c": ("海图残片·丙", "quest", "R", 0, "一角海图，写着“退潮时可步行”。", {}),
    "spyglass": ("黄铜望远镜", "tool", "R", 40, "能拉长的单筒望远镜。拿着它探索时更容易看见远处闪光的东西。", {"dur": 999}),
    # —— 灯塔 ——
    "keeper_page": ("守塔人日记页", "quest", "U", 0, "温守岚的日记，一页一页散落在灯塔里。（可以 read diary 阅读）", {}),
    "dusty_book": ("受潮的书", "coll", "U", 10, "一本《潮汐与月相》，书页鼓成了波浪。", {}),
    "brass_plate": ("铜铭牌", "relic", "R", 32, "灯塔铭牌：“雾屿灯塔，光照十八海里”。", {}),
    "old_photo": ("褪色照片", "coll", "R", 28, "照片上是一个年轻水手和一个扎辫子的女孩，背后写着“阿禾，等我”。", {}),
    "tide_table": ("潮汐表", "tool", "R", 0, "守塔人手抄的潮汐表。带在身上，状态里会显示接下来的潮汐。", {"dur": 999}),
    "pigeon_ring": ("信鸽脚环", "coll", "U", 9, "一枚小铝环，刻着编号 0427。", {}),
    "keeper_cup": ("守塔人的搪瓷杯", "coll", "R", 20, "杯底一圈茶渍，杯身印着褪色的“先进个人”。", {}),
    # —— 海蚀洞 ——
    "cave_crystal": ("洞窟水晶", "sell", "R", 45, "长在黑暗里的水晶，提灯一照满洞星光。", {}),
    "echo_stone": ("回声石", "coll", "R", 40, "对着它说话，它会在很久以后小声地重复一遍。", {}),
    "blue_ore": ("蓝晶矿", "mat", "R", 30, "深蓝色的矿脉，敲下来的碎块会发出风铃一样的声音。", {}),
    "ammonite": ("菊石化石", "relic", "R", 55, "一圈圈旋进去的远古贝壳，比岛上任何东西都老。", {}),
    "blind_shrimp": ("盲虾", "food", "U", 5, "洞里没有光，这些虾干脆不长眼睛了。", {"food": 11}),
    "deep_idol": ("深海石像", "relic", "E", 140, "一尊半人半鱼的石像，表情像在笑，也像在哭。", {}),
    "tide_heart": ("潮汐之心", "coll", "L", 500, "一颗拳头大的蓝色晶体，里面有潮水在涨落。握着它，你能感觉到整片海在呼吸。", {}),
    "fresnel_lens": ("菲涅尔透镜", "quest", "E", 0, "灯塔失落的透镜，一圈圈同心的棱，能把一点火光送到十八海里外。", {}),
    "cave_pearl": ("洞穴珍珠", "sell", "R", 50, "水滴千年磨出来的石头珍珠，乳白色。", {}),
    # —— 鲸骨湾（隐藏）——
    "whale_bone": ("鲸骨", "mat", "U", 10, "巨大的肋骨，白得像月光。", {}),
    "ambergris": ("龙涎香", "sell", "E", 300, "灰白的蜡质块，闻起来像海、像泥土、像很旧的木头柜子。", {}),
    "whale_ivory": ("鲸牙雕", "relic", "E", 140, "一颗鲸牙上刻满了船和浪，是哪个水手漫长的夜晚。", {}),
    "bone_flute": ("骨笛", "coll", "R", 60, "用鸟骨做的短笛，吹出来是很低的呜呜声，像鲸在唱歌。", {}),
    "whale_song_shell": ("鲸歌螺", "coll", "L", 400, "一只巨大的螺，贴在耳边能听见鲸的歌，而且每天的歌都不一样。", {}),
    "giant_scale": ("古鲸鳞", "coll", "R", 50, "鲸是没有鳞的。可这片东西就在鲸骨旁边。", {}),
    # —— 雾中小岛（隐藏）——
    "starsand": ("星砂", "coll", "R", 30, "一小瓶星星形状的砂粒，其实是很小的贝壳。", {}),
    "moon_lily": ("月光百合", "coll", "E", 120, "只在有月亮的夜里开的白百合，花心里有一点银。", {}),
    "figurehead": ("晨星号船首像", "relic", "L", 600, "一个木雕的女孩，双手捧着一颗星。漆掉光了，她还在笑。", {}),
    "tide_clock": ("潮汐钟", "relic", "L", 450, "一座不按时间走、按潮水走的钟。", {}),
    "xiaoman_letter": ("小满的最后一封信", "quest", "E", 0, "装在油布包里，从来没有被放进瓶子。（可以 read letter 阅读）", {}),
    # —— 杂项 / 商店 / 制作 ——
    "ration": ("干粮", "food", "C", 2, "压缩饼干，难吃但顶饱。", {"food": 20}),
    "bandage": ("绷带", "res", "C", 3, "干净的绷带，能处理伤口。", {"heal": True}),
    "rope": ("绳索", "tool", "C", 4, "结实的长绳。进沉船、下深潭都要用。", {"dur": 12}),
    "crowbar": ("撬棍", "tool", "U", 12, "一根铁撬棍，什么都想撬一下。", {"dur": 25}),
    "shovel": ("小铲子", "tool", "C", 9, "在沙滩上挖东西用。有它会挖出埋着的东西。", {"dur": 30}),
    "net": ("捞网", "tool", "C", 4, "手编的捞网，能在礁滩捞鱼。", {"dur": 20}),
    "knife": ("贝刀", "tool", "C", 8, "撬贝壳专用的短刀。有它才撬得开鲍鱼和珍珠贝。", {"dur": 30}),
    "axe": ("斧头", "tool", "U", 14, "砍木头更快，也能劈开林子深处的藤墙。", {"dur": 30}),
    "lantern": ("提灯", "tool", "U", 18, "防风提灯。夜里和洞里都靠它。", {"dur": 40}),
    "reef_boots": ("防滑草鞋", "tool", "C", 2, "纤维编的草鞋，鞋底缠了粗绳，走礁石不打滑。", {"dur": 25}),
    "pickaxe": ("矿镐", "tool", "U", 20, "能敲下矿石的小镐。", {"dur": 30}),
    "skiff": ("小舢板", "tool", "E", 0, "你亲手造的小船，能划进雾里。", {"dur": 999}),
    "glass_pane": ("灯室玻璃", "mat", "U", 3, "用海玻璃熔铸的厚玻璃板。", {}),
    "lamp_oil": ("灯油", "mat", "U", 3, "用鱼油和松脂熬出来的灯油，烧起来很亮。", {}),
    "grilled_fish": ("烤鱼", "meal", "C", 4, "外焦里嫩，撒了一点海盐。", {"food": 30}),
    "seafood_soup": ("海鲜汤", "meal", "U", 8, "贻贝、海胆和海带煮的一锅汤，喝完浑身暖和，伤口也不那么疼了。", {"food": 45, "heal": True}),
    "berry_pie": ("雾莓派", "meal", "U", 8, "酸酸甜甜，是这座岛上最接近蛋糕的东西。", {"food": 40}),
    "mushroom_stew": ("菌菇炖", "meal", "C", 5, "一锅咕嘟冒泡的菌菇。", {"food": 32}),
    "honey_tea": ("蜂蜜热茶", "meal", "U", 6, "雨夜里一杯，什么都好起来了。", {"food": 25, "heal": True}),
    # —— 旅行商人 ——
    "star_chart": ("星图", "coll", "R", 40, "一张手绘星图，有几颗星星被人用铅笔圈了起来。", {}),
    "snow_globe": ("雪花玻璃球", "coll", "R", 35, "里面是一座小灯塔，摇一摇就下雪。", {}),
    "foreign_tea": ("异国红茶", "food", "U", 6, "装在小铁罐里的红茶，喝完一整天都精神。", {"food": 35}),
    "wind_chime": ("贝壳风铃", "coll", "U", 15, "商人说是他奶奶做的。他每次都这么说。", {}),
    "silk_ribbon": ("丝带", "coll", "U", 12, "一条勃艮第红的丝带。挂在帐篷门口很好看。", {}),
    "marble": ("玻璃弹珠", "coll", "U", 4, "里面有一道蓝色的螺旋，像一个很小的漩涡。", {}),
    "music_roll": ("八音盒曲卷", "coll", "E", 90, "一卷打着小孔的铜片，好像能装进某个八音盒里。", {}),
}

# 收藏系列（全部放进收藏柜、并且建了展示柜后获得永久加成）
SETS = {
    "drift_toys": {"name": "漂流玩具", "items": ["plastic_duck", "tin_soldier", "marble", "glass_float"],
                   "bonus": ("luck", 1), "desc": "探索时稍微更容易遇到稀有物"},
    "morning_star": {"name": "晨星号遗物", "items": ["ship_bell", "sextant", "silver_spoon", "captain_pipe", "figurehead"],
                     "bonus": ("stamina_max", 15), "desc": "体力上限 +15"},
    "tide_gems": {"name": "潮汐宝石", "items": ["pearl", "black_pearl", "tide_crystal", "cave_pearl", "tide_heart"],
                  "bonus": ("sell", 10), "desc": "所有出售价格 +10%"},
    "forest_keeps": {"name": "林间珍藏", "items": ["owl_feather", "mist_antler", "stone_idol", "mist_orchid", "carved_slab"],
                     "bonus": ("forest", 1), "desc": "森林探索体力消耗 -30%"},
    "keeper_memory": {"name": "守塔人的记忆", "items": ["old_photo", "keeper_cup", "brass_plate", "dusty_book", "snow_globe"],
                      "bonus": ("sleep", 15), "desc": "睡觉多恢复 15 体力"},
    "whale_songs": {"name": "鲸之歌", "items": ["baleen", "bone_flute", "whale_ivory", "giant_scale", "whale_song_shell"],
                    "bonus": ("luck", 1), "desc": "探索时稍微更容易遇到稀有物"},
}

# ───────── 地点 ─────────
LOCS = {
    "beach": {"name": "退潮海滩", "hours": 1, "sta": 8, "danger": 0,
              "desc": "你醒来的地方。灰白的沙滩一直延伸进雾里，每一次退潮都会留下点什么。你的帐篷就在礁石背风的那一边。"},
    "forest": {"name": "雾隐森林", "hours": 2, "sta": 12, "danger": 1,
               "desc": "海滩后面的松林，雾气常年挂在树梢上。林子深处好像有石头砌的东西。"},
    "reef": {"name": "潮间礁滩", "hours": 1, "sta": 10, "danger": 1,
             "desc": "黑色的礁石一路伸进海里。退潮时会露出一个个水洼和石缝，涨潮时只剩浪。"},
    "wreck": {"name": "搁浅沉船", "hours": 2, "sta": 14, "danger": 2,
              "desc": "一艘侧躺在礁石上的旧货船，船身上的字只剩“…星号”。船舱一半泡在水里。"},
    "lighthouse": {"name": "废弃灯塔", "hours": 1, "sta": 9, "danger": 1,
                   "desc": "岬角尽头的白色灯塔，灯室的玻璃碎了，铁门被锈封着。已经很多年没有亮过。"},
    "cave": {"name": "地下海蚀洞", "hours": 2, "sta": 18, "danger": 3,
             "desc": "礁石缝下的海蚀洞，只有退潮时才露出入口。里面冷，黑，有水滴的回声。"},
    "whalefall": {"name": "鲸骨湾", "hours": 2, "sta": 14, "danger": 1,
                  "desc": "海岬背面一处安静的小湾，一副巨大的鲸骨半埋在沙里，肋骨像一座白色的教堂。"},
    "islet": {"name": "雾中小岛", "hours": 2, "sta": 12, "danger": 1,
              "desc": "只有灯塔亮着时才找得到的小岛。岛上有一片开着白花的空地，和一间很小的木屋。"},
}
LOC_ORDER = ["beach", "forest", "reef", "wreck", "lighthouse", "cave", "whalefall", "islet"]

# ───────── 掉落表 ─────────
# (物品, 权重, 条件, 数量下限, 数量上限)
# 条件键：tide(low/mid/high) time(day/dusk/night) weather(sunny/cloudy/rain/fog/storm)
#        season(春夏秋冬) tool(需带工具) poststorm(风暴刚过) stage(灯塔修复阶段≥) flag
LOOT = {
    "beach": [
        ("shell", 60, None, 1, 3), ("driftwood", 55, None, 1, 3), ("kelp", 35, None, 1, 2),
        ("rope_scrap", 30, None, 1, 2), ("bottle_cap", 18, None, 1, 1), ("crab", 22, None, 1, 1),
        ("pumice", 20, None, 1, 2), ("sea_glass", 26, None, 1, 2), ("conch", 12, None, 1, 1),
        ("cowrie", 10, None, 1, 1), ("sand_dollar", 10, {"tide": ["low"]}, 1, 1),
        ("plastic_duck", 6, None, 1, 1), ("tin_soldier", 3, None, 1, 1),
        ("glass_float", 3, None, 1, 1), ("amber_lump", 2, None, 1, 1),
        ("old_coin", 6, {"tool": "shovel"}, 1, 2), ("tin_box", 6, {"tool": "shovel"}, 1, 1),
        ("carved_bird", 2, None, 1, 1), ("broken_compass", 1.5, {"tool": "shovel"}, 1, 1),
        ("turtle_shell_frag", 2, {"season": ["夏"]}, 1, 1),
        ("glow_algae", 25, {"time": ["night"]}, 1, 2), ("sand_crab", 20, {"time": ["night"]}, 1, 1),
        ("baleen", 6, {"poststorm": True}, 1, 1), ("broken_mast", 22, {"poststorm": True}, 1, 1),
        ("ship_lamp", 5, {"poststorm": True}, 1, 1), ("nails", 14, {"poststorm": True}, 1, 3),
        ("canvas", 10, {"poststorm": True}, 1, 1), ("marble", 3, None, 1, 1),
        ("glass_float", 8, {"weather": ["rain"], "time": ["night"]}, 1, 1),
        ("amber_lump", 5, {"weather": ["rain"], "time": ["night"]}, 1, 1),
    ],
    "forest": [
        ("wood", 60, None, 1, 2), ("wood", 40, {"tool": "axe"}, 2, 3), ("fiber", 55, None, 2, 4),
        ("resin", 18, None, 1, 2), ("mushroom", 30, {"season": ["春", "夏", "秋"]}, 1, 2),
        ("mushroom", 30, {"weather": ["rain"]}, 2, 3), ("berries", 28, {"season": ["夏", "秋"]}, 1, 3),
        ("glowcap", 22, {"time": ["night", "dusk"]}, 1, 2), ("herb", 14, None, 1, 1),
        ("owl_feather", 8, {"time": ["dusk", "night"]}, 1, 1), ("moss_stone", 30, None, 1, 3),
        ("honeycomb", 9, {"season": ["春", "夏"]}, 1, 1), ("bird_nest", 8, {"season": ["春"]}, 1, 1),
        ("pine_cone", 25, None, 1, 2), ("mist_antler", 2.5, {"season": ["冬", "春"]}, 1, 1),
        ("mist_orchid", 4, {"weather": ["fog"]}, 1, 1), ("stone_idol", 2, {"tool": "axe"}, 1, 1),
        ("carved_slab", 1.5, {"tool": "axe"}, 1, 1), ("berry_seed", 6, None, 1, 2),
        ("herb_seed", 5, None, 1, 1), ("thrift_seed", 1.5, None, 1, 1), ("squirrel_stash", 6, {"season": ["秋", "冬"]}, 1, 1),
    ],
    "reef": [
        ("mussel", 50, None, 1, 3), ("limpet", 40, None, 1, 3), ("starfish", 26, None, 1, 1),
        ("sea_urchin", 18, {"tide": ["low"]}, 1, 2), ("coral_branch", 12, {"tide": ["low"]}, 1, 1),
        ("octopus", 12, {"tide": ["low", "mid"]}, 1, 1), ("reef_fish", 30, {"tool": "net"}, 1, 3),
        ("abalone", 6, {"tool": "knife", "tide": ["low"]}, 1, 1), ("pearl", 4, {"tool": "knife"}, 1, 1),
        ("black_pearl", 0.6, {"tool": "knife"}, 1, 1), ("copper_ore", 14, {"tool": "pickaxe"}, 1, 2),
        ("tide_crystal", 4, {"tide": ["low"], "tool": "pickaxe"}, 1, 1), ("sea_hare", 10, None, 1, 1),
        ("barnacle_bell", 1.5, {"tide": ["low"]}, 1, 1), ("hermit_house", 10, None, 1, 1),
        ("kelp", 20, None, 1, 2), ("sea_glass", 8, None, 1, 1),
    ],
    "wreck": [
        ("nails", 50, None, 2, 4), ("iron_scrap", 45, None, 1, 3), ("canvas", 22, None, 1, 2),
        ("brass_gear", 16, None, 1, 1), ("porcelain", 16, None, 1, 1), ("rope_scrap", 20, None, 1, 3),
        ("cannonball", 10, None, 1, 1), ("silver_spoon", 4, None, 1, 1), ("old_rum", 4, None, 1, 1),
        ("captain_pipe", 3, None, 1, 1), ("doubloon", 3, {"tool": "crowbar"}, 1, 2),
        ("music_box", 1.2, None, 1, 1), ("sextant", 0.8, None, 1, 1),
        ("logbook_page", 10, None, 1, 1), ("driftwood", 20, None, 1, 2),
    ],
    "lighthouse": [
        ("dusty_book", 20, None, 1, 1), ("pigeon_ring", 14, None, 1, 1), ("iron_scrap", 22, None, 1, 2),
        ("nails", 18, None, 1, 2), ("keeper_page", 22, {"stage": 2}, 1, 1),
        ("brass_plate", 4, {"stage": 2}, 1, 1), ("keeper_cup", 4, {"stage": 2}, 1, 1),
        ("old_photo", 3, {"stage": 3}, 1, 1), ("glow_algae", 8, None, 1, 1), ("resin", 6, None, 1, 1),
        ("owl_feather", 10, None, 1, 1),
    ],
    "cave": [
        ("blind_shrimp", 30, None, 1, 2), ("cave_crystal", 10, None, 1, 1), ("echo_stone", 6, None, 1, 1),
        ("blue_ore", 14, {"tool": "pickaxe"}, 1, 2), ("copper_ore", 20, {"tool": "pickaxe"}, 1, 3),
        ("ammonite", 5, {"tool": "pickaxe"}, 1, 1), ("cave_pearl", 6, None, 1, 1),
        ("deep_idol", 0.9, None, 1, 1), ("tide_heart", 0.25, {"tide": ["low"]}, 1, 1),
        ("tide_crystal", 10, None, 1, 1), ("moss_stone", 15, None, 1, 2),
    ],
    "whalefall": [
        ("whale_bone", 40, None, 1, 2), ("shell", 30, None, 1, 3), ("ambergris", 1.5, None, 1, 1),
        ("whale_ivory", 2, None, 1, 1), ("bone_flute", 4, None, 1, 1), ("giant_scale", 4, None, 1, 1),
        ("whale_song_shell", 0.4, {"time": ["night"]}, 1, 1), ("baleen", 8, None, 1, 1),
        ("sea_glass", 20, None, 1, 2), ("driftwood", 25, None, 1, 2), ("conch", 15, None, 1, 1),
    ],
    "islet": [
        ("starsand", 15, None, 1, 1), ("moon_lily", 4, {"time": ["night"]}, 1, 1),
        ("tide_clock", 0.6, None, 1, 1), ("wood", 25, None, 1, 2), ("berries", 25, None, 1, 3),
        ("herb", 20, None, 1, 2), ("thrift_seed", 8, None, 1, 1), ("shell", 20, None, 1, 2),
    ],
}

# ───────── 商店（寄居蟹老板“老钳”，开在海滩上的大螺壳里）─────────
SHOP = {
    "ration": 8, "bandage": 10, "rope": 14, "crowbar": 40, "shovel": 30, "knife": 26,
    "axe": 48, "lantern": 65, "pickaxe": 75, "net": 18, "reef_boots": 12,
    "berry_seed": 10, "herb_seed": 12, "nails": 6,
}
TRAVELER_STOCK = [
    ("star_chart", 120), ("snow_globe", 110), ("foreign_tea", 25), ("wind_chime", 50),
    ("silk_ribbon", 40), ("marble", 15), ("thrift_seed", 40), ("music_roll", 260),
    ("spyglass", 200), ("lamp_oil", 18), ("glass_pane", 20), ("tin_soldier", 70),
]

# ───────── 制作 ─────────
# 配方id: (产出数量, 材料, 需要的设施等级)；"@"后缀表示同一产物的另一种做法
RECIPES = {
    "rope": (1, {"rope_scrap": 4}, {}),
    "rope@fiber": (1, {"fiber": 6}, {}),
    "reef_boots": (1, {"fiber": 5, "rope_scrap": 1}, {}),
    "net": (1, {"fiber": 8, "driftwood": 2}, {}),
    "bandage": (1, {"fiber": 3, "herb": 1}, {}),
    "crowbar": (1, {"iron_scrap": 4}, {"workbench": 1}),
    "axe": (1, {"iron_scrap": 3, "wood": 2}, {"workbench": 1}),
    "shovel": (1, {"iron_scrap": 2, "driftwood": 2}, {"workbench": 1}),
    "knife": (1, {"iron_scrap": 2, "shell": 3}, {"workbench": 1}),
    "lantern": (1, {"iron_scrap": 3, "sea_glass": 2, "glow_algae": 2}, {"workbench": 1}),
    "pickaxe": (1, {"iron_scrap": 4, "wood": 2, "copper_ore": 1}, {"workbench": 1}),
    "glass_pane": (1, {"sea_glass": 3, "pumice": 1}, {"workbench": 1}),
    "lamp_oil": (1, {"reef_fish": 2, "resin": 1}, {"workbench": 1}),
    "lamp_oil@algae": (1, {"glow_algae": 3, "resin": 1}, {"workbench": 1}),
    "skiff": (1, {"wood": 20, "canvas": 4, "nails": 15, "rope": 2, "resin": 4}, {"workbench": 2}),
    "wood@mast": (4, {"broken_mast": 1}, {}),
    "grilled_fish": (1, {"reef_fish": 2}, {"kitchen": 1}),
    "seafood_soup": (1, {"mussel": 2, "sea_urchin": 1, "kelp": 1}, {"kitchen": 1}),
    "berry_pie": (1, {"berries": 4, "honeycomb": 1}, {"kitchen": 1}),
    "mushroom_stew": (1, {"mushroom": 3, "kelp": 1}, {"kitchen": 1}),
    "honey_tea": (1, {"honeycomb": 1, "herb": 1}, {"kitchen": 1}),
}

# ───────── 基地与设施 ─────────
BASE_LEVELS = [
    {"name": "破旧营地", "sta": 100, "carry": 80, "sleep": 70, "cost": {}},
    {"name": "简易木屋", "sta": 110, "carry": 100, "sleep": 85,
     "cost": {"coins": 60, "wood": 15, "driftwood": 10, "nails": 10}},
    {"name": "海边小屋", "sta": 125, "carry": 120, "sleep": 100,
     "cost": {"coins": 200, "wood": 30, "nails": 25, "canvas": 6, "glass_pane": 2}},
    {"name": "探索者之家", "sta": 145, "carry": 150, "sleep": 130,
     "cost": {"coins": 550, "wood": 45, "copper_ore": 10, "brass_gear": 6, "glass_pane": 4, "moss_stone": 20}},
]
FACILITIES = {
    "storage": {"name": "储物箱", "levels": [
        {"base": 0, "cost": {"coins": 20, "driftwood": 8, "fiber": 6}, "eff": "背包可携带 +30 件"},
        {"base": 1, "cost": {"coins": 70, "wood": 10, "nails": 8}, "eff": "背包可携带再 +40 件"},
    ]},
    "workbench": {"name": "工作台", "levels": [
        {"base": 0, "cost": {"coins": 30, "driftwood": 6, "wood": 4}, "eff": "解锁工具、灯塔材料等制作配方"},
        {"base": 1, "cost": {"coins": 120, "iron_scrap": 6, "brass_gear": 2, "wood": 8}, "eff": "能造船"},
    ]},
    "bed": {"name": "床铺", "levels": [
        {"base": 0, "cost": {"coins": 25, "fiber": 10, "wood": 6}, "eff": "睡觉多恢复 20 体力，体力上限 +10"},
        {"base": 2, "cost": {"coins": 120, "canvas": 4, "owl_feather": 5}, "eff": "再多恢复 20，睡一觉能治好轻伤"},
    ]},
    "gearrack": {"name": "装备架", "levels": [
        {"base": 0, "cost": {"coins": 40, "wood": 6, "nails": 6}, "eff": "工具损耗减半；可以 repair 修理工具"},
    ]},
    "display": {"name": "展示柜", "levels": [
        {"base": 1, "cost": {"coins": 80, "wood": 8, "sea_glass": 4}, "eff": "收藏柜不再限种类；集齐系列获得永久加成"},
    ]},
    "kitchen": {"name": "简易厨房", "levels": [
        {"base": 1, "cost": {"coins": 70, "moss_stone": 10, "iron_scrap": 4}, "eff": "可以 cook 做料理"},
    ]},
    "garden": {"name": "小花园", "levels": [
        {"base": 1, "cost": {"coins": 50, "fiber": 6, "moss_stone": 6}, "eff": "3 块地，可以 plant 种东西"},
        {"base": 2, "cost": {"coins": 150, "wood": 10, "shell": 15}, "eff": "扩到 6 块地，长得更快"},
    ]},
}

# 灯塔修复阶段
LH_STAGES = [
    {"name": "撬开锈死的铁门", "need": {}, "tool": "crowbar",
     "text": "铁门“嘎吱”一声开了一条缝，灰尘像雪一样落下。一楼堆满了旧木箱和鸟巢。"},
    {"name": "修好螺旋楼梯", "need": {"wood": 12, "nails": 10}, "tool": None,
     "text": "你把断掉的踏板一块块换上新木头。楼梯通到了二楼——守塔人的房间。桌上还摊着没写完的日记。"},
    {"name": "换上灯室玻璃", "need": {"glass_pane": 4}, "tool": None,
     "text": "灯室重新有了窗。风进不来了，你站在里面，第一次看清整座群岛：海滩、森林、礁滩……还有雾里一个说不清的影子。"},
    {"name": "装回透镜", "need": {"fresnel_lens": 1}, "tool": None,
     "text": "透镜严丝合缝地落进铜座。你转了一下，它很轻地转动起来，像一直在等这一刻。"},
    {"name": "注满灯油", "need": {"lamp_oil": 2}, "tool": None,
     "text": "油槽满了。现在只差一根火柴——和一个对的夜晚。（在夜里来灯塔，用 lighthouse light 点灯）"},
]

# ───────── 漂流瓶 ─────────
BOTTLE_STORY = [
    {"id": "s1", "need": {}, "title": "致阿禾（一）", "text":
     "阿禾：\n船上的饭比家里难吃一百倍。大副说我是全船最能吃的人，我说那是因为我在长身体。"
     "今天看到了海豚，一大群，跟着船跑了半个下午。我想你要是在就好了。\n——小满，晨星号上"},
    {"id": "s2", "need": {}, "title": "守塔人的字条", "eff": "reveal_lighthouse", "text":
     "给捡到这只瓶子的人：\n岬角尽头的灯塔，已经很久没亮了。那是我的错。\n"
     "如果你在这座岛上，请替我去看看它。门锈住了，要撬。\n——温守岚"},
    {"id": "s3", "need": {}, "title": "致阿禾（二）", "text":
     "阿禾：\n我们往南走了九天。船长说这一趟回去就能给我结一整年的工钱，我给你买那双红皮鞋。"
     "雾越来越大，船长说别担心，雾屿有灯塔，照十八海里。\n——小满"},
    {"id": "s4", "need": {"flag": "lh_open"}, "title": "没写完的信", "text":
     "今晚雾太大了。油不够，透镜的座子又松了。我下去拿工具，就一会儿。\n"
     "（这一行之后，字迹换了一种很乱的笔画）\n灯灭了二十分钟。只有二十分钟。"},
    {"id": "s5", "need": {}, "title": "致阿禾（三）", "text":
     "阿禾：\n船撞上了。很响，然后是很安静。我们几个抱着一块船板漂到了一个很小的岛上。"
     "这里有淡水，有果子。别哭，我们在等船。我把这封信放进朗姆酒瓶里，大副说他不介意。\n——小满"},
    {"id": "s6", "need": {"flag": "lh_open"}, "title": "海图的事", "eff": "give_map_b", "text":
     "温先生：\n我们在小岛上捡到你的瓶子了。你不要怪自己。"
     "我把船长的海图撕成三片，一片跟着这封信，一片我藏在船上，一片……你那里也许会有。"
     "拼起来能找到一个有鲸骨的地方，船长说那里退潮时能走过去。\n——小满\n（瓶底卡着一角海图）"},
    {"id": "s7", "need": {"stage": 2}, "title": "致阿禾（四）", "text":
     "阿禾：\n今天是我在小岛上的第三个冬天。其他人都被路过的渔船接走了，我留下了，因为大副病了，走不了。"
     "后来大副也走了，我把他埋在了白花底下。\n我种了很多百合。它们只在有月亮的晚上开。\n——小满"},
    {"id": "s8", "need": {"stage": 3}, "title": "守塔人的最后一张字条", "text":
     "如果你修好了灯室的窗，就能看见雾里的那个影子。\n我看了它很多年。我不敢划过去。\n"
     "我只敢每年往海里扔一只瓶子，问一句：你还在那儿吗？\n——温守岚"},
    {"id": "s9", "need": {"flag": "lh_lit"}, "title": "很旧很旧的瓶子", "text":
     "（瓶子被海草缠得严严实实，信纸却意外地干）\n\n"
     "如果灯又亮了，那一定是有人来了。\n谢谢你。\n我在这边看得见。\n——小满"},
]
BOTTLE_MISC = [
    ("给隔壁的猫", "如果你捡到这个瓶子，请告诉我隔壁那只橘猫：鱼是我吃的，不是它。我良心不安。"),
    ("一张收据", "收到：海风一阵，晚霞若干，好心情一份。已付清。——海边小卖部"),
    ("练习", "你好你好你好。我在练习写字。今天学会了“海”。海。海。海。"),
    ("没有收件人", "今天是我第一次一个人出海。我有点害怕，但我没有告诉任何人。现在告诉你了。"),
    ("寻物启事", "寻：一只左脚的红色雨靴。如有拾获，请把它和右脚那只放在一起。它们感情很好。"),
    ("菜谱", "海带汤：海带，水，盐。别的都不要放。相信我。"),
    ("考试", "如果这个瓶子漂到了你那里，说明我数学及格了。我跟自己打了个赌。"),
    ("致未来的我", "你现在还怕黑吗？我希望不怕了。如果还怕，也没关系，带个灯就好。"),
    ("一幅画", "（纸上画着一条歪歪扭扭的鱼，旁边写着：我钓了一整天，只钓到这只瓶子。哈。）"),
    ("天气预报", "明天：晴。后天：晴。大后天：我不知道，但我希望晴。"),
    ("告白（未寄出）", "我一直想跟你说……算了，我还是扔进海里吧。海会替我保密的。"),
    ("致岛上的人", "如果你读到这里，说明海把它送对了人。祝你好运。"),
]

LOGBOOK = [
    "第一日：晨星号离港。货：棉布、茶叶、两箱八音盒。船长林瞻。大副周远。水手七人。天气晴。",
    "第五日：风向转南。小满又被大副罚洗甲板，因为偷吃了船长的腊肉。",
    "第九日：入雾。航速减半。照规矩，见到雾屿灯塔光后向西偏转三十度。",
    "第十日：仍未见灯光。船长下令鸣钟，每刻钟一次。",
    "第十日夜：触礁。（这一页后面全是空白，只在最下面有一行小字：钟声没人听见。）",
]
KEEPER_DIARY = [
    "三月初七，晴。添油，擦透镜。灯塔里只有我一个人，我和透镜说话，它不回答，但它听着。",
    "四月廿二，雾。看见一艘货船的影子往南去了。挂的是晨星的旗。年轻人们在甲板上唱歌。",
    "五月初一，大雾。透镜的座子松了，我得下去拿扳手。只要一会儿。",
    "五月初二。我不想写。",
    "六月。我每天晚上都点灯，比以前点得早，熄得晚。没有用了，可我还是点。",
    "（最后一页）钥匙我放在林子里了，和那块写着字的石头在一起。透镜我推进了洞里最深的水潭——我不配再用它。",
]

XIAOMAN_LETTER = (
    "给点灯的人：\n\n"
    "你好。我不知道你是谁，但你一定是个有耐心的人，因为那座灯塔坏得很厉害。\n\n"
    "我叫小满，是晨星号上最能吃的水手。船沉以后我在这座小岛上住了很多年。"
    "我每天晚上都看着岬角那边，等那座塔亮起来。它一直没亮，我也一直没走。\n\n"
    "后来我想明白了：灯不是为了让船回来才亮的，是为了让还在海上的人知道，有人在等。\n\n"
    "温先生大概不在了。阿禾大概也老了。我写了很多信，有的扔进了海里，有的没有。"
    "这一封我留在这里，因为我知道，能看到它的人，一定已经替我们把灯点亮了。\n\n"
    "谢谢你。\n这座岛以后就交给你了。屋后的百合要记得看，有月亮的晚上它们会开。\n\n"
    "——小满"
)

# ───────── 事件 ─────────
# loc: 地点 id 或 "any"；w: 权重；cond: 条件；once: 只发生一次；cd: 冷却（探索次数）；pity: 每次没遇到权重乘这个数
# opts: [{"t": 文字, "need": {物品: 数量}（选了就消耗）, "tool": 工具（有损耗）, "out": 结果}]
# 结果键：text gain lose coins sta hours flag injure secret unlock journal goto lose_random chance{p,ok,fail} reset
# reset=True：一次性事件这次不算用掉，以后还会再遇到
EVENTS = [
    # —— 主线推进 ——
    {"id": "fog_path", "loc": "beach", "w": 0, "once": True, "trigger": "beach_count>=5", "out": {
        "text": "雾忽然散开一角。你看见沙滩后面有一片松林，林子边上有一条被踩出来的小路——不是你踩的。",
        "unlock": "forest", "journal": "雾散了一角，我发现海滩后面有片森林。小路不是我踩出来的。"}},
    {"id": "reef_path", "loc": "beach", "w": 0, "once": True, "trigger": "beach_count>=9", "out": {
        "text": "今天退潮退得特别远。海滩东头露出一大片黑色礁石，水洼里有东西在动。光脚走上去有点滑——要是有双防滑的鞋就好了。",
        "unlock": "reef", "journal": "退潮时，海滩东边露出一片礁滩。最好编双防滑草鞋再去。"}},
    {"id": "see_wreck", "loc": "reef", "w": 30, "once": True, "cond": {"tide": ["low", "mid"]}, "out": {
        "text": "礁滩尽头露出一艘侧躺的大船，船身上的字只剩“…星号”。要进去，得有绳子攀下去，还得有东西撬开舱门。",
        "unlock": "wreck", "journal": "礁滩尽头有一艘搁浅的船。进去需要绳索和撬棍。"}},
    {"id": "cave_wind", "loc": "reef", "w": 10, "once": True, "cond": {"tide": ["low"], "flag": "wreck_seen"}, "out": {
        "text": "一道礁石缝里吹出冷风，风里有回声。缝隙下面是黑的，深得看不见底——那是一个洞。没有灯不能进，而且只有退潮时入口才露出水面。",
        "unlock": "cave", "journal": "礁石缝下有个海蚀洞，退潮才能进，要带灯。"}},
    {"id": "forest_lh", "loc": "forest", "w": 14, "once": True, "cond": {"notflag": "lh_seen"}, "out": {
        "text": "你爬上一块高石头，雾在脚下流。岬角尽头立着一座白色的灯塔，灯室黑着。",
        "unlock": "lighthouse", "journal": "从森林高处看到岬角尽头有座灯塔。"}},
    {"id": "find_key", "loc": "forest", "w": 25, "once": True, "cond": {"flag": "diary_key", "tool": "axe"}, "out": {
        "text": "你劈开藤墙，找到那块写着“灯不灭，船自归”的石板。石板底下压着一把小小的铜钥匙。",
        "gain": {"rusty_key": 1, "carved_slab": 1}, "journal": "在刻字石板下找到了守塔人的钥匙。"}},
    {"id": "hidden_room", "loc": "lighthouse", "w": 40, "once": True, "cond": {"stage": 2, "have": "rusty_key"}, "opts": [
        {"t": "用钥匙打开楼梯下的小门", "out": {
            "text": "门后是一间很小的储藏室。墙上钉着一张泛黄的海图，缺了一角；角落里有一盒没拆的灯芯，和一只装满信纸的木箱——每一张都写着“你还在那儿吗？”",
            "gain": {"map_c": 1, "lamp_oil": 1}, "lose": {"rusty_key": 1}, "secret": "keeper_room",
            "journal": "打开了灯塔的密室。一整箱写给小岛的信，都没有寄出去。"}},
        {"t": "先不打开", "out": {"text": "你把钥匙放回口袋。门在那里，不会跑。", "reset": True}},
    ]},
    {"id": "wreck_map", "loc": "wreck", "w": 18, "once": True, "cond": {"flag": "letter_s6"}, "opts": [
        {"t": "潜进半淹的船长室", "tool": "rope", "out": {"chance": {"p": 0.75,
            "ok": {"text": "你憋着气摸到船长的书桌，抽屉里有一个油布包——是一角海图。", "gain": {"map_a": 1},
                   "journal": "在沉船船长室找到了海图残片。"},
            "fail": {"text": "水太冷了，你呛了一口水，只好先浮上来。东西还在那儿。", "sta": -15, "reset": True}}}},
        {"t": "改天再来", "out": {"text": "你记住了船长室的位置。", "reset": True}},
    ]},
    {"id": "lens_pool", "loc": "cave", "w": 6, "pity": 1.6, "once": True, "cond": {"stage": 3}, "opts": [
        {"t": "系上绳子下到深潭里", "tool": "rope", "out": {"chance": {"p": 0.7,
            "ok": {"text": "潭底有一块巨大的、一圈一圈的玻璃，被海藻裹着。你把它抱上来，提灯一照，满洞都是转动的光——是灯塔的透镜。",
                   "gain": {"fresnel_lens": 1}, "journal": "在海蚀洞深潭找到了灯塔的透镜！"},
            "fail": {"text": "绳结滑了一下，你及时抓住岩壁，手掌划破了。", "injure": True, "reset": True}}}},
        {"t": "用提灯照一照就走", "out": {"text": "潭底有什么在反光，一圈一圈的，像很大的眼睛。你决定下次准备好了再来。", "reset": True}},
    ]},
    {"id": "islet_glimpse", "loc": "lighthouse", "w": 0, "once": True, "trigger": "lit", "out": {
        "text": "光柱扫过海面。在雾最浓的地方，光照出了一座小岛的轮廓——岛上有一片白花，和一间木屋。屋前好像有人挥了挥手。也许只是风。",
        "unlock": "islet", "journal": "灯塔亮了。光里出现了一座小岛。要划船过去。"}},
    {"id": "xiaoman_house", "loc": "islet", "w": 50, "once": True, "out": {
        "text": "木屋的门没有锁。屋里很干净，桌上有一个油布包，上面写着：“给点灯的人”。",
        "gain": {"xiaoman_letter": 1}, "journal": "在小岛的木屋里找到了小满留给“点灯的人”的信。", "secret": "xiaoman"}},
    {"id": "figurehead_ev", "loc": "islet", "w": 6, "once": True, "cond": {"flag": "read_xiaoman"}, "opts": [
        {"t": "把她从沙里挖出来", "out": {"text": "你花了很久，挖出一个木雕的女孩，双手捧着星星。是晨星号的船首像。小满一直把她放在能看见灯塔的地方。",
            "gain": {"figurehead": 1}, "sta": -20, "journal": "挖出了晨星号的船首像。"}},
        {"t": "让她留在这里，继续看着灯塔", "out": {"text": "你在她身边坐了一会儿，然后起身离开。有些东西就该待在原地。",
            "flag": "figurehead_left", "secret": "figurehead_left",
            "journal": "我没有带走船首像。她在那里看灯塔，看了四十年，就让她继续看吧。"}},
    ]},
    # —— 海滩 ——
    {"id": "trader_crab", "loc": "beach", "w": 4, "cd": 25, "out": {
        "text": "老钳从螺壳里探出一只钳子：“今天的风不错。”它又缩了回去。这大概是它表达友好的方式。", "coins": 2}},
    {"id": "buried_chest", "loc": "beach", "w": 4, "cd": 30, "cond": {"tool": "shovel"}, "opts": [
        {"t": "挖下去", "tool": "shovel", "out": {"text": "挖了半天，是一只铁皮盒。", "gain": {"tin_box": 1}, "sta": -8}},
        {"t": "算了，可能只是石头", "out": {"text": "你没挖。它也许真的只是块石头。"}},
    ]},
    {"id": "seal", "loc": "beach", "w": 3, "cd": 40, "cond": {"time": ["day", "dusk"]}, "opts": [
        {"t": "分它一条鱼", "need": {"reef_fish": 1}, "out": {"text": "海豹叼起鱼，打了个响亮的嗝。第二天你的帐篷门口多了几块很漂亮的海玻璃。",
            "gain": {"sea_glass": 3}, "secret": "seal_friend", "journal": "喂了一只海豹。它居然回礼了。"}},
        {"t": "远远地看着它晒太阳", "out": {"text": "它翻了个身，把肚子对着太阳。你也坐下来晒了一会儿。", "sta": 6}},
    ]},
    {"id": "storm_debris", "loc": "beach", "w": 10, "cond": {"weather": ["storm"]}, "opts": [
        {"t": "顶着风去抢冲上来的东西", "out": {"chance": {"p": 0.6,
            "ok": {"text": "你抢下了一截桅杆和一卷帆布。浪差点把你也卷走。", "gain": {"broken_mast": 1, "canvas": 1}, "sta": -10},
            "fail": {"text": "一个浪把你拍倒在沙子里。东西没抢到，膝盖磕破了。", "injure": True, "sta": -10}}}},
        {"t": "躲回帐篷，等风停了再说", "out": {"text": "你缩在帐篷里听风。风停了以后，沙滩上会有更多东西。", "hours": 2}},
    ]},
    {"id": "sandcastle", "loc": "beach", "w": 2, "once": True, "cond": {"weather": ["sunny"]}, "opts": [
        {"t": "堆一座沙堡", "out": {"text": "你堆了一座很像样的沙堡，还给它插了一根海鸥羽毛当旗。下次涨潮它就会没了，但你记得它。",
            "sta": -5, "journal": "今天堆了一座沙堡。", "secret": "sandcastle"}},
        {"t": "算了，正事要紧", "out": {"text": "你踢了一脚沙子，继续找东西。", "reset": True}},
    ]},
    {"id": "night_glow", "loc": "beach", "w": 3, "cd": 30, "cond": {"time": ["night"]}, "out": {
        "text": "海浪每拍一次岸，就亮起一道蓝光。你在发光的浪边站了很久。", "sta": 5, "gain": {"glow_algae": 1}}},
    {"id": "gull_thief", "loc": "beach", "w": 3, "cd": 20, "out": {"chance": {"p": 0.5,
        "ok": {"text": "一只海鸥盯着你的包看了半天，最后什么都没偷，走了。"},
        "fail": {"text": "一只海鸥俯冲下来，叼走了你的一只小螃蟹，还回头叫了一声，像在笑。", "lose": {"crab": 1}}}}},
    # —— 森林 ——
    {"id": "lost_fog", "loc": "forest", "w": 8, "cd": 15, "cond": {"weather": ["fog"]}, "opts": [
        {"t": "沿着溪水声走", "out": {"chance": {"p": 0.7,
            "ok": {"text": "溪水把你领出了林子，还在溪边捡到一些东西。", "gain": {"herb": 1, "fiber": 2}},
            "fail": {"text": "你在雾里转了很久，又回到了原地。累得腿都软了。", "sta": -15, "hours": 2}}}},
        {"t": "坐下来等雾散", "out": {"text": "你等了两个小时。雾散的时候，你发现自己就在小路边上。", "hours": 2}},
        {"t": "用提灯照路", "tool": "lantern", "out": {"text": "提灯的光圈里，路一下清楚了。你还在树根下看见了几朵发蓝光的蘑菇。", "gain": {"glowcap": 2}}},
    ]},
    {"id": "deer", "loc": "forest", "w": 3, "cd": 40, "cond": {"weather": ["fog", "cloudy"]}, "opts": [
        {"t": "不动，屏住呼吸", "out": {"text": "一只浅灰色的鹿从雾里走出来，看了你很久，然后走了。它刚才站的地方有一截掉下来的角。",
            "gain": {"mist_antler": 1}, "secret": "deer", "journal": "我在林子里见到了一只鹿。原来岛上真的有鹿。"}},
        {"t": "想悄悄靠近", "out": {"text": "你踩断了一根树枝。鹿一下就不见了。"}},
    ]},
    {"id": "beehive", "loc": "forest", "w": 4, "cd": 20, "cond": {"season": ["春", "夏"]}, "opts": [
        {"t": "直接掏", "out": {"chance": {"p": 0.5, "ok": {"text": "你掏到了一大块蜂巢，只被蛰了一下。", "gain": {"honeycomb": 2}},
            "fail": {"text": "蜜蜂追了你半片林子。", "sta": -12, "gain": {"honeycomb": 1}}}}},
        {"t": "用松脂点烟熏一熏", "need": {"resin": 1}, "out": {"text": "烟一熏，蜜蜂都晕乎乎的。你从容地取走了蜂巢。", "gain": {"honeycomb": 3}}},
        {"t": "绕开走", "out": {"text": "你绕了个大圈。蜜蜂嗡嗡地，好像在说谢谢。"}},
    ]},
    {"id": "ruin_altar", "loc": "forest", "w": 4, "once": True, "cond": {"tool": "axe"}, "opts": [
        {"t": "在石台上放一样吃的", "need": {"berries": 2}, "out": {"text": "你在石偶的碗里放了两颗雾莓。起风了，雾里好像有人轻轻笑了一声。之后，你总觉得林子对你温柔了些。",
            "flag": "forest_blessing", "secret": "altar", "journal": "在林中石台上放了雾莓。"}},
        {"t": "看看就走", "out": {"text": "石台上刻着波浪和一座塔。你记住了图案。", "reset": True}},
    ]},
    {"id": "squirrel", "loc": "forest", "w": 4, "cd": 25, "out": {
        "text": "一只松鼠从树上扔下一颗松果，准准砸在你头上。它看起来非常满意。", "gain": {"pine_cone": 1}, "sta": -1}},
    {"id": "fallen_tree", "loc": "forest", "w": 4, "cd": 20, "cond": {"poststorm": True}, "opts": [
        {"t": "用斧头劈开倒下的树", "tool": "axe", "out": {"text": "一棵被风刮倒的大松树，够你劈好一阵子。", "gain": {"wood": 6, "resin": 2}, "sta": -12}},
        {"t": "捡点小枝就走", "out": {"text": "你捡了一抱树枝。", "gain": {"wood": 1}}},
    ]},
    # —— 礁滩 ——
    {"id": "tide_rush", "loc": "reef", "w": 6, "cd": 12, "cond": {"tide": ["mid"]}, "opts": [
        {"t": "再撬一个就走", "out": {"chance": {"p": 0.55,
            "ok": {"text": "你撬下一只大鲍鱼，转身时水已经没过脚踝。", "gain": {"abalone": 1}},
            "fail": {"text": "浪一下打上来，你摔在礁石上，包里掉了点东西。", "injure": True, "lose_random": 1}}}},
        {"t": "马上往回撤", "out": {"text": "你刚爬上高处，刚才站的地方就被浪吞了。"}},
    ]},
    {"id": "trapped_fish", "loc": "reef", "w": 5, "cd": 15, "cond": {"tide": ["low"]}, "opts": [
        {"t": "把水洼里的小鱼放回海里", "out": {"text": "你一条条把它们捧回海里。最后一条游走前，在你手心里蹭了一下。", "flag": "fish_kind",
            "secret": "fish_kind", "sta": -4}},
        {"t": "抓几条当晚饭", "out": {"text": "晚饭有着落了。", "gain": {"reef_fish": 3}}},
    ]},
    {"id": "octopus_trade", "loc": "reef", "w": 3, "cd": 40, "cond": {"flag": "fish_kind"}, "out": {
        "text": "一只章鱼从石缝里伸出一条触手，放下一颗珍珠，又缩了回去。好像是在谢谁。", "gain": {"pearl": 1}}},
    {"id": "slip", "loc": "reef", "w": 5, "cd": 10, "cond": {"notool": "reef_boots"}, "out": {
        "text": "礁石上的青苔太滑，你摔了一跤。", "injure": True, "sta": -6}},
    # —— 沉船 ——
    {"id": "wreck_crate", "loc": "wreck", "w": 8, "cd": 12, "opts": [
        {"t": "撬开木箱", "tool": "crowbar", "out": {"chance": {"p": 0.8,
            "ok": {"text": "箱子里是一卷卷泡烂的棉布，最底下压着一只完好的小木盒。", "gain": {"canvas": 2, "porcelain": 1, "brass_gear": 1}},
            "fail": {"text": "撬棍一滑，箱子里只有泥水。", "sta": -5}}}},
        {"t": "不碰它", "out": {"text": "这只箱子在这里四十年了，也不差这一天。"}},
    ]},
    {"id": "wreck_bell", "loc": "wreck", "w": 3, "once": True, "cond": {"logs": 3}, "opts": [
        {"t": "把船钟拆下来带走", "tool": "crowbar", "out": {"text": "船钟很沉。你拖着它走了好久。钟壁上铸着“晨星号”。",
            "gain": {"ship_bell": 1}, "sta": -25, "journal": "带回了晨星号的船钟。"}},
        {"t": "敲一下钟", "out": {"text": "“当——”声音传得很远很远。雾好像退了一点。四十年前那一夜，大概也有人这样敲过。",
            "secret": "ring_bell", "journal": "我敲响了晨星号的钟。", "reset": True}},
    ]},
    {"id": "eel", "loc": "wreck", "w": 4, "cd": 20, "opts": [
        {"t": "伸手去够舱底那个发光的东西", "out": {"chance": {"p": 0.4,
            "ok": {"text": "你摸到一枚金币，一条海鳗从你手边游过，没理你。", "gain": {"doubloon": 1}},
            "fail": {"text": "一条海鳗咬了你一口！", "injure": True}}}},
        {"t": "用撬棍捅一捅", "tool": "crowbar", "out": {"text": "海鳗不高兴地游走了。你捞起了一枚金币。", "gain": {"doubloon": 1}}},
        {"t": "离它远点", "out": {"text": "黑暗里有一双小眼睛一直盯着你。"}},
    ]},
    {"id": "rotten_floor", "loc": "wreck", "w": 4, "cd": 15, "out": {"chance": {"p": 0.5,
        "ok": {"text": "脚下的甲板咯吱一声，好在没断。"},
        "fail": {"text": "腐烂的甲板塌了，你掉进下层船舱，摔得不轻。好在下面是水。", "injure": True, "gain": {"iron_scrap": 1}}}}},
    # —— 灯塔 ——
    {"id": "lh_owl", "loc": "lighthouse", "w": 4, "cd": 30, "out": {
        "text": "一只林鸮住在一楼的旧木箱上，冷冷地看着你。你们达成了互不打扰的协议。", "gain": {"owl_feather": 1}}},
    {"id": "lh_tide_table", "loc": "lighthouse", "w": 12, "once": True, "cond": {"stage": 2}, "out": {
        "text": "守塔人的桌上压着一本手抄的潮汐表，一直抄到了很多年以后。好像他知道自己会在这里待很久。",
        "gain": {"tide_table": 1}, "journal": "找到了守塔人的潮汐表。以后看潮水就方便了。"}},
    {"id": "lh_night_watch", "loc": "lighthouse", "w": 6, "cd": 20, "cond": {"flag": "lh_lit", "time": ["night"]}, "out": {
        "text": "你在灯室里守了一会儿夜。光一圈圈扫过海面。远处的小岛上，好像也有一点小小的光回应了一下。", "sta": 10}},
    # —— 海蚀洞 ——
    {"id": "cave_echo", "loc": "cave", "w": 5, "cd": 20, "opts": [
        {"t": "对着洞喊一声", "out": {"text": "回声来了，一声、两声……第七声的时候，好像不是你的声音了。", "secret": "cave_echo"}},
        {"t": "安静地听", "out": {"text": "你听见了潮水在岩石里流动的声音，像这座岛的心跳。", "sta": 5}},
    ]},
    {"id": "cave_lantern_out", "loc": "cave", "w": 4, "cd": 25, "opts": [
        {"t": "摸黑往回走", "out": {"chance": {"p": 0.6, "ok": {"text": "你扶着岩壁一步步挪了出去。", "goto": "reef"},
            "fail": {"text": "你在黑暗里撞了好几下才找到出口。", "injure": True, "goto": "reef"}}}},
        {"t": "用夜光藻照路", "need": {"glow_algae": 1}, "out": {"text": "夜光藻发着微弱的蓝光，够你重新点上提灯了。还顺便照见了岩缝里一颗洞穴珍珠。", "gain": {"cave_pearl": 1}}},
    ]},
    {"id": "deep_pool_glow", "loc": "cave", "w": 2, "cd": 40, "cond": {"tide": ["low"]}, "out": {
        "text": "洞最深处的水潭忽然整个亮起来，像有一颗蓝色的心在水底跳了一下。然后又暗了。", "secret": "tide_heart_glimpse"}},
    # —— 鲸骨湾 / 小岛 ——
    {"id": "whale_song", "loc": "whalefall", "w": 4, "cd": 30, "cond": {"time": ["night", "dusk"]}, "out": {
        "text": "风穿过鲸骨，发出很低很长的声音。像一头鲸在唱歌，唱给另一头很远很远的鲸。", "sta": 8, "secret": "whale_song"}},
    {"id": "islet_grave", "loc": "islet", "w": 5, "once": True, "opts": [
        {"t": "在白花中间的木牌前站一会儿", "out": {"text": "木牌上刻着：“周远，晨星号大副。爱船长，恨自己。”下面又刻了一行小字：“船长说他从来没怪过你。”",
            "secret": "first_mate", "journal": "在小岛上找到了大副的墓。"}},
        {"t": "给他放一束花", "need": {"sea_thrift": 1}, "out": {"text": "你把海石竹放在木牌前。风很大，花没倒。木牌背面也刻着字：“周远，晨星号大副。爱船长，恨自己。”",
            "secret": "first_mate_flower", "journal": "给晨星号的大副放了一束海石竹。"}},
    ]},
    # —— 任何地方 ——
    {"id": "rainbow", "loc": "any", "w": 2, "cd": 50, "cond": {"weather": ["rain", "cloudy"], "time": ["day"]}, "out": {
        "text": "雨停了一下，海面上架起一道很完整的彩虹。你什么都没捡，就这么看着。", "sta": 8, "secret": "rainbow"}},
    {"id": "shooting_star", "loc": "any", "w": 2, "cd": 50, "cond": {"weather": ["sunny"], "time": ["night"]}, "out": {
        "text": "一颗流星划过去。你来不及许愿。下次吧。", "secret": "shooting_star"}},
]

SECRET_NAMES = {
    "keeper_room": "灯塔的密室", "xiaoman": "给点灯的人", "figurehead_left": "让她继续看着灯塔",
    "seal_friend": "海豹的回礼", "sandcastle": "沙堡", "deer": "雾里的鹿", "altar": "林中的供品",
    "fish_kind": "放生", "ring_bell": "钟声", "cave_echo": "第七声回音", "tide_heart_glimpse": "潭底的心跳",
    "whale_song": "鲸骨的歌", "first_mate": "大副的墓", "first_mate_flower": "一束海石竹",
    "rainbow": "彩虹", "shooting_star": "流星",
}

# ───────── 成就 ─────────
ACHIEVEMENTS = {
    "first_find": ("第一件拾获", "捡到第一样东西", 5),
    "bottle_1": ("海的来信", "捡到第一只漂流瓶", 10),
    "bottle_all": ("所有的信都到了", "读完全部主线瓶中信", 80),
    "forest": ("走进雾里", "发现雾隐森林", 10),
    "reef": ("踩上礁石", "第一次去潮间礁滩", 10),
    "wreck": ("登船", "第一次进入沉船", 20),
    "lh_open": ("吱呀", "打开灯塔的门", 20),
    "lh_lit": ("灯不灭", "点亮灯塔", 100),
    "cave": ("下到黑暗里", "第一次进入海蚀洞", 30),
    "whalefall": ("鲸落", "找到鲸骨湾", 50),
    "islet": ("雾里的岛", "登上雾中小岛", 80),
    "home": ("这里是家了", "把基地升级到探索者之家", 100),
    "enc_25": ("拾荒学徒", "图鉴收录 25 种物品", 20),
    "enc_50": ("拾荒老手", "图鉴收录 50 种物品", 50),
    "enc_80": ("群岛博物学家", "图鉴收录 80 种物品", 120),
    "legend": ("传说", "找到一件传说物品", 60),
    "set_1": ("收藏家", "集齐一个收藏系列", 40),
    "rich": ("小有积蓄", "同时拥有 1000 枚贝币", 0),
    "explore_100": ("走了很远的路", "累计探索 100 次", 30),
    "explore_500": ("岛上的老住户", "累计探索 500 次", 100),
    "injured": ("小伤而已", "第一次受伤", 0),
    "secrets_5": ("看见了别人没看见的", "发现 5 个秘密", 40),
    "skiff": ("出海", "造好一条小船", 40),
}
