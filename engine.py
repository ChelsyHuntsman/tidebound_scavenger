# -*- coding: utf-8 -*-
"""《潮汐拾荒者》游戏引擎（人类开发者维护用）。

AI 玩家请用 island.py：import island; print(island.cmd("help"))
本文件与 content.py 由 build.py 打包进 island.py。
"""
import json
import os
import shutil
import time as _time

if "ITEMS" not in globals():  # 打包后内容已经在全局里了
    from content import *  # noqa: F401,F403

VERSION = 1
MAX_BATCH = 20


# ───────── 可存档的确定性随机数（mulberry32）─────────
class Rng:
    def __init__(self, state):
        self.state = state & 0xFFFFFFFF

    def random(self):
        self.state = (self.state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self.state
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    def randint(self, a, b):
        return a + int(self.random() * (b - a + 1))

    def chance(self, p):
        return self.random() < p

    def choice(self, seq):
        return seq[int(self.random() * len(seq))]

    def weighted(self, pairs):
        total = sum(w for _, w in pairs)
        if total <= 0:
            return None
        r = self.random() * total
        for x, w in pairs:
            r -= w
            if r < 0:
                return x
        return pairs[-1][0]


# ───────── 常量 ─────────
WX = {"sunny": "晴", "cloudy": "多云", "rain": "雨", "fog": "浓雾", "storm": "风暴"}
WX_NEXT = {
    "sunny": [("sunny", 55), ("cloudy", 30), ("fog", 10), ("rain", 5)],
    "cloudy": [("sunny", 30), ("cloudy", 30), ("rain", 25), ("fog", 10), ("storm", 5)],
    "rain": [("cloudy", 35), ("rain", 35), ("storm", 12), ("fog", 10), ("sunny", 8)],
    "fog": [("fog", 40), ("cloudy", 30), ("sunny", 20), ("rain", 10)],
    "storm": [("storm", 25), ("rain", 45), ("cloudy", 30)],
}
SEASONS = ["春", "夏", "秋", "冬"]
TIDE_CN = {"low": "退潮", "mid": "平潮", "high": "涨潮"}
TOD_CN = {"day": "白天", "dusk": "黄昏", "night": "夜晚"}
CARRY_CATS = {"res", "mat", "food", "sell", "seed", "meal"}
LOC_TOOLS = {
    "beach": ["shovel"], "forest": ["axe"], "reef": ["reef_boots", "net", "knife", "pickaxe"],
    "wreck": ["rope", "crowbar"], "cave": ["lantern", "pickaxe"], "lighthouse": [],
    "whalefall": [], "islet": [],
}
FIRST_FIND = {"C": 1, "U": 3, "R": 8, "E": 20, "L": 50}
RANK = {"C": 0, "U": 1, "R": 2, "E": 3, "L": 4}
EVENT_BY_ID = {e["id"]: e for e in EVENTS}
START_TEXT = "我在一片灰白的沙滩上醒来。身后有一顶破帐篷，口袋里有两块干粮和一点旧绳头。"


def _save_path():
    p = os.environ.get("ISLAND_SAVE")
    if p:
        return p
    base = os.path.dirname(os.path.abspath(globals().get("__file__", "island.py")))
    return os.path.join(base, "island_save.json")


def _fresh_state(seed):
    st = {
        "v": VERSION, "seed": seed, "rng": seed, "turn": 0, "explores": 0,
        "day": 1, "hour": 7, "weather": "cloudy", "poststorm": 0,
        "loc": "beach", "coins": 20, "sta": 100, "inj": 0,
        "inv": {"rope_scrap": 2, "ration": 2}, "dur": {}, "vault": {},
        "base": 0, "fac": {}, "unlocked": ["beach"], "visited": ["beach"],
        "flags": [], "lh": 0, "enc": {}, "secrets": [], "ach": [],
        "journal": [], "bottles": [], "misc_seen": [], "pending": None,
        "cd": {}, "done": [], "pity": {}, "beach_count": 0, "garden": [],
        "traveler": None, "diary_read": 0,
        "stats": {"earned": 0, "spent": 0, "injuries": 0, "bottles": 0, "logs": 0},
    }
    for i in st["inv"]:
        st["enc"][i] = {"d": 1, "loc": "beach"}
    st["journal"].append([1, 7, START_TEXT, 1])
    return st


class Game:
    def __init__(self, state, path):
        self.s = state
        self.path = path
        self.rng = Rng(state["rng"])
        self.out = []

    # ───── 基础 ─────
    def say(self, *lines):
        self.out.extend(x for x in lines if x is not None)

    def save(self):
        self.s["rng"] = self.rng.state
        data = json.dumps(self.s, ensure_ascii=False)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        if os.path.exists(self.path):
            try:
                shutil.copyfile(self.path, self.path + ".bak")
            except OSError:
                pass
        os.replace(tmp, self.path)

    @property
    def abs_hour(self):
        return (self.s["day"] - 1) * 24 + self.s["hour"]

    def season(self):
        return SEASONS[((self.s["day"] - 1) // 7) % 4]

    def tod(self, hour=None):
        h = self.s["hour"] if hour is None else hour
        if 6 <= h < 17:
            return "day"
        if 17 <= h < 20:
            return "dusk"
        return "night"

    def tide(self, day=None, hour=None):
        d = self.s["day"] if day is None else day
        h = self.s["hour"] if hour is None else hour
        ph = (h + d) % 12
        if ph <= 2:
            return "low"
        if 5 <= ph <= 8:
            return "high"
        return "mid"

    def flag(self, f):
        return f in self.s["flags"]

    def setflag(self, f):
        if f not in self.s["flags"]:
            self.s["flags"].append(f)

    def name(self, iid):
        return ITEMS[iid][0] if iid in ITEMS else iid

    def have(self, iid, n=1):
        return self.s["inv"].get(iid, 0) >= n

    def owned(self, iid):
        return self.s["inv"].get(iid, 0) + self.s["vault"].get(iid, 0)

    def journal(self, text, auto=True):
        self.s["journal"].append([self.s["day"], self.s["hour"], text, 1 if auto else 0])

    # ───── 体力 / 背包 / 收藏加成 ─────
    def sta_max(self):
        m = BASE_LEVELS[self.s["base"]]["sta"]
        if self.s["fac"].get("bed", 0) >= 1:
            m += 10
        return m + self.set_bonus("stamina_max")

    def carry_max(self):
        c = BASE_LEVELS[self.s["base"]]["carry"]
        lv = self.s["fac"].get("storage", 0)
        return c + (30 if lv >= 1 else 0) + (40 if lv >= 2 else 0)

    def carry_now(self):
        return sum(n for i, n in self.s["inv"].items() if ITEMS[i][1] in CARRY_CATS)

    def add_sta(self, n):
        self.s["sta"] = max(0, min(self.sta_max(), self.s["sta"] + n))

    def done_sets(self):
        if self.s["fac"].get("display", 0) < 1:
            return []
        return [sid for sid, st in SETS.items() if all(self.s["vault"].get(i, 0) > 0 for i in st["items"])]

    def set_bonus(self, kind):
        return sum(SETS[sid]["bonus"][1] for sid in self.done_sets() if SETS[sid]["bonus"][0] == kind)

    # ───── 时间 ─────
    def advance(self, hours):
        for _ in range(int(hours)):
            self.s["hour"] += 1
            if self.s["hour"] >= 24:
                self.s["hour"] = 0
                self.s["day"] += 1
                if (self.s["day"] - 1) % 7 == 0:
                    self.say(f"🍂 季节变成了{self.season()}。")
            if self.s["poststorm"] > 0:
                self.s["poststorm"] -= 1
            if self.s["hour"] % 6 == 0:
                self._weather_step()
            if self.s["hour"] == 6:
                self._morning()

    def _weather_step(self):
        cur = self.s["weather"]
        sea = self.season()
        opts = []
        for w, p in WX_NEXT[cur]:
            if sea == "冬" and w in ("storm", "fog"):
                p *= 1.6
            if sea == "夏" and w == "sunny":
                p *= 1.4
            if sea == "秋" and w == "fog":
                p *= 1.3
            opts.append((w, p))
        nxt = self.rng.weighted(opts)
        if cur == "storm" and nxt != "storm":
            self.s["poststorm"] = 10
            self.say("🌊 风暴过去了。海滩上大概冲来了不少东西。")
        elif nxt != cur:
            self.say(f"（天气变了：{WX[cur]} → {WX[nxt]}）")
        self.s["weather"] = nxt

    def _morning(self):
        tr = self.s.get("traveler")
        if tr and self.abs_hour >= tr["until"]:
            self.s["traveler"] = None
            self.say("（旅行商人的小船已经走了。）")
        if not self.s["traveler"] and self.s["day"] >= 3 and self.rng.chance(0.22):
            pool = list(TRAVELER_STOCK)
            stock = []
            for _ in range(3):
                pick = self.rng.choice(pool)
                pool.remove(pick)
                stock.append([pick[0], pick[1], 0])
            self.s["traveler"] = {"until": self.abs_hour + 24, "stock": stock}
            self.say("🔔 海面上漂来一条挂铃铛的小船——旅行商人来海滩了，待到明早。（在海滩 shop 看货）")

    # ───── 条件 ─────
    def cond_ok(self, c):
        if not c:
            return True
        s = self.s
        if "tide" in c and self.tide() not in c["tide"]:
            return False
        if "time" in c and self.tod() not in c["time"]:
            return False
        if "weather" in c and s["weather"] not in c["weather"]:
            return False
        if "season" in c and self.season() not in c["season"]:
            return False
        if "tool" in c and not self.have(c["tool"]):
            return False
        if "notool" in c and self.have(c["notool"]):
            return False
        if c.get("poststorm") and s["poststorm"] <= 0:
            return False
        if "stage" in c and s["lh"] < c["stage"]:
            return False
        if "flag" in c and not self.flag(c["flag"]):
            return False
        if "notflag" in c and self.flag(c["notflag"]):
            return False
        if "have" in c and not self.have(c["have"]):
            return False
        if "logs" in c and s["stats"].get("logs", 0) < c["logs"]:
            return False
        return True

    def access(self, loc):
        """None = 现在可以在这里探索；否则返回原因。"""
        s = self.s
        if loc not in s["unlocked"]:
            return "你还不知道这个地方。"
        wx, td = s["weather"], self.tide()
        if loc in ("reef", "wreck", "cave", "whalefall", "islet") and wx == "storm":
            return "风暴里去那里太危险了，等风停（wait / rest）。"
        if loc == "wreck":
            miss = [self.name(t) for t in ("rope", "crowbar") if not self.have(t)]
            if miss:
                return "要下到船舱里，需要：" + "、".join(miss) + "。"
            if td == "high":
                return "涨潮了，船舱灌满了水。等退潮或平潮再来。"
        if loc == "lighthouse" and s["lh"] < 1:
            return "灯塔的铁门锈死了。在这里用 lighthouse restore 撬开它（需要撬棍）。"
        if loc == "cave":
            if not self.have("lantern"):
                return "洞里一片漆黑，没有提灯不能进。"
            if td != "low":
                return "洞口被潮水淹着，只有退潮时才露出来。"
        if loc == "whalefall" and td == "high":
            return "去鲸骨湾的那段海岸被潮水淹没了，等潮水退一点。"
        if loc == "islet":
            if not self.have("skiff"):
                return "需要一条小船才能划过去。"
            if not (self.tod() in ("night", "dusk") or wx == "fog"):
                return "白天的晴光里看不见那座岛。等黄昏、夜里，或者起雾的时候。"
        return None

    # ───── 物品 ─────
    def gain(self, iid, n, note):
        """把 n 个 iid 放进背包，返回实际放进去的数量。提示写进 note。"""
        if n <= 0:
            return 0
        cat = ITEMS[iid][1]
        got = n
        if cat in CARRY_CATS:
            got = max(0, min(n, self.carry_max() - self.carry_now()))
            if got < n:
                note.append(f"🎒 背包满了，{self.name(iid)}×{n - got} 没装下。（sell 卖掉一些 / 升级储物箱）")
        if got <= 0:
            return 0
        inv = self.s["inv"]
        if cat == "tool" and iid not in inv:
            self.s["dur"][iid] = ITEMS[iid][5].get("dur", 20)
        inv[iid] = inv.get(iid, 0) + got
        if iid not in self.s["enc"]:
            rar = ITEMS[iid][2]
            self.s["enc"][iid] = {"d": self.s["day"], "loc": self.s["loc"]}
            bonus = FIRST_FIND[rar]
            self.s["coins"] += bonus
            note.append(f"🆕 首次发现：{self.name(iid)}（{RARITY[rar]['label']}）——{ITEMS[iid][4]}  +{bonus}贝币")
            if RANK[rar] >= 2:
                self.journal(f"第一次找到了{self.name(iid)}（{RARITY[rar]['label']}）。")
            if rar == "L":
                self.ach("legend")
        if iid == "logbook_page":
            self.s["stats"]["logs"] = self.s["stats"].get("logs", 0) + got
            if self.s["stats"]["logs"] == len(LOGBOOK):
                note.append("（航海日志的残页凑齐了。read logbook）")
        if iid == "keeper_page" and self.owned(iid) == len(KEEPER_DIARY):
            note.append("（守塔人的日记页凑齐了。read diary 读一读）")
        if iid in ("map_a", "map_b", "map_c"):
            self._check_maps(note)
        return got

    def lose(self, iid, n=1):
        have = self.s["inv"].get(iid, 0)
        n = min(n, have)
        if n <= 0:
            return 0
        self.s["inv"][iid] = have - n
        if self.s["inv"][iid] <= 0:
            del self.s["inv"][iid]
            if ITEMS[iid][1] == "tool":
                self.s["dur"].pop(iid, None)
        return n

    def _check_maps(self, note):
        if all(self.have(m) for m in ("map_a", "map_b", "map_c")) and "whalefall" not in self.s["unlocked"]:
            note.append("🗺️ 三片海图拼在了一起：海岬背面有一个鲸鱼记号，旁边写着“退潮时可步行”。")
            self.unlock("whalefall", note)
            self.journal("三片海图拼齐了，找到了去鲸骨湾的路。")

    def wear(self, tool, note):
        if not self.have(tool) or ITEMS[tool][5].get("dur", 0) >= 999:
            return
        if self.s["fac"].get("gearrack", 0) >= 1 and self.rng.chance(0.5):
            return
        full = ITEMS[tool][5].get("dur", 20)
        d = self.s["dur"].get(tool, full) - 1
        if d <= 0:
            self.lose(tool, 1)
            note.append(f"🔧 {self.name(tool)}坏掉了。" + ("（换上了备用的）" if self.have(tool) else "（可以再买 / 再做一个）"))
            self.journal(f"{self.name(tool)}用坏了。")
            if self.have(tool):
                self.s["dur"][tool] = full
        else:
            self.s["dur"][tool] = d

    def injure(self, note):
        if self.s["inj"] == 0:
            self.s["stats"]["injuries"] += 1
            self.ach("injured")
            self.journal("受伤了。")
        self.s["inj"] = 2
        note.append("🩹 你受伤了：探索更费体力，睡觉恢复变少。（use 止血草/绷带，喝汤，或睡两晚会好）")

    # ───── 成就 ─────
    def ach(self, aid):
        if aid in self.s["ach"] or aid not in ACHIEVEMENTS:
            return
        self.s["ach"].append(aid)
        n, d, r = ACHIEVEMENTS[aid]
        self.s["coins"] += r
        self.out.append(f"🏅 成就：{n}（{d}）" + (f" +{r}贝币" if r else ""))

    def check_ach(self):
        s = self.s
        n = len(s["enc"])
        if n >= 3:
            self.ach("first_find")
        for k in (25, 50, 80):
            if n >= k:
                self.ach(f"enc_{k}")
        if s["coins"] >= 1000:
            self.ach("rich")
        if s["explores"] >= 100:
            self.ach("explore_100")
        if s["explores"] >= 500:
            self.ach("explore_500")
        if len(s["secrets"]) >= 5:
            self.ach("secrets_5")
        if self.done_sets():
            self.ach("set_1")
        if s["base"] >= 3:
            self.ach("home")
        if self.have("skiff"):
            self.ach("skiff")
        if all(b["id"] in s["bottles"] for b in BOTTLE_STORY):
            self.ach("bottle_all")

    # ───── 事件 ─────
    def eligible_events(self, loc):
        s = self.s
        res = []
        for e in EVENTS:
            if e.get("trigger") or e.get("w", 0) <= 0 or e["loc"] not in (loc, "any"):
                continue
            if e.get("once") and e["id"] in s["done"]:
                continue
            last = s["cd"].get(e["id"])
            if last is not None and s["explores"] - last < e.get("cd", 0):
                continue
            if not self.cond_ok(e.get("cond")):
                continue
            w = e["w"]
            if e.get("pity"):
                w *= e["pity"] ** min(12, s["pity"].get(e["id"], 0))
            res.append((e, w))
        return res

    def start_event(self, e, note):
        """开始一个事件。需要抉择时返回 True。"""
        s = self.s
        s["cd"][e["id"]] = s["explores"]
        if e.get("pity"):
            s["pity"][e["id"]] = 0
        if "opts" in e:
            s["pending"] = e["id"]
            note.append("❗【事件】" + self.event_prompt(e))
            note.extend(self.event_opts(e))
            note.append("（用 choose <编号> 做决定；决定之前不能继续探索）")
            return True
        if e.get("once"):
            s["done"].append(e["id"])
        self.apply_out(e["out"], note)
        return False

    def event_prompt(self, e):
        return EVENT_PROMPTS.get(e["id"], "发生了一件事。")

    def event_opts(self, e):
        lines = []
        for i, o in enumerate(e["opts"], 1):
            req = self.opt_missing(o)
            lines.append(f"  {i}. {o['t']}" + (f"（需要：{req}）" if req else ""))
        return lines

    def opt_missing(self, o):
        miss = [f"{self.name(k)}×{v}" for k, v in o.get("need", {}).items() if not self.have(k, v)]
        if o.get("tool") and not self.have(o["tool"]):
            miss.append(self.name(o["tool"]))
        return "、".join(miss)

    def resolve(self, o):
        """把带 chance 的结果掷骰，返回最终结果字典。"""
        if "chance" in o:
            ch = o["chance"]
            sub = ch["ok"] if self.rng.chance(ch["p"]) else ch["fail"]
            merged = {k: v for k, v in o.items() if k != "chance"}
            merged.update(sub)
            return merged
        return o

    def apply_out(self, o, note):
        s = self.s
        o = self.resolve(o)
        if o.get("text"):
            note.append(o["text"])
        for k, v in o.get("lose", {}).items():
            if self.lose(k, v):
                note.append(f"（失去 {self.name(k)}×{v}）")
        if o.get("lose_random"):
            pool = sorted(i for i, n in s["inv"].items() if ITEMS[i][1] in ("res", "food", "sell") and n > 0)
            if pool:
                it = self.rng.choice(pool)
                self.lose(it, 1)
                note.append(f"（掉了 {self.name(it)}×1）")
        for k, v in o.get("gain", {}).items():
            got = self.gain(k, v, note)
            if got:
                note.append(f"获得 {self.name(k)}×{got}")
        if o.get("coins"):
            s["coins"] += o["coins"]
            note.append(f"贝币 {o['coins']:+d}")
        if o.get("sta"):
            self.add_sta(o["sta"])
            note.append(f"体力 {o['sta']:+d}")
        if o.get("hours"):
            self.advance(o["hours"])
        if o.get("flag"):
            self.setflag(o["flag"])
        if o.get("injure"):
            self.injure(note)
        if o.get("secret") and o["secret"] not in s["secrets"]:
            s["secrets"].append(o["secret"])
            note.append("✨ 你发现了一个秘密。（encyclopedia secrets）")
        if o.get("unlock"):
            self.unlock(o["unlock"], note)
        if o.get("journal"):
            self.journal(o["journal"])
        if o.get("goto"):
            s["loc"] = o["goto"]
            note.append(f"（你回到了{LOCS[o['goto']]['name']}）")
        return o

    def unlock(self, loc, note):
        s = self.s
        if loc in s["unlocked"]:
            return
        s["unlocked"].append(loc)
        note.append(f"🗺️ 新地点：【{LOCS[loc]['name']} {loc}】（goto {loc}）")
        if loc == "wreck":
            self.setflag("wreck_seen")
        if loc == "lighthouse":
            self.setflag("lh_seen")
        if loc == "forest":
            self.ach("forest")

    # ───── 漂流瓶 ─────
    def bottle(self, note):
        s = self.s
        s["stats"]["bottles"] += 1
        self.ach("bottle_1")
        for b in BOTTLE_STORY:
            if b["id"] in s["bottles"]:
                continue
            if self.cond_ok(b["need"]):
                s["bottles"].append(b["id"])
                self.setflag("letter_" + b["id"])
                note.append(f"📜 漂流瓶！瓶里卷着一封信——《{b['title']}》\n{b['text']}")
                self.journal(f"捡到漂流瓶：《{b['title']}》。")
                if b.get("eff") == "reveal_lighthouse":
                    self.unlock("lighthouse", note)
                if b.get("eff") == "give_map_b":
                    if self.gain("map_b", 1, note):
                        note.append("获得 海图残片·乙×1")
                return
            break  # 主线信件按顺序来；下一封的时机没到，就先给一封闲信
        left = [i for i in range(len(BOTTLE_MISC)) if i not in s["misc_seen"]]
        if left and self.rng.chance(0.85):
            i = self.rng.choice(left)
            s["misc_seen"].append(i)
            s["bottles"].append(f"m{i}")
            t, txt = BOTTLE_MISC[i]
            note.append(f"📜 漂流瓶！《{t}》\n{txt}")
        else:
            note.append("📜 漂流瓶……是空的。瓶口塞得很紧，里面只有一点点很旧的空气。")

    # ───── 探索 ─────
    def explore_cost(self, loc):
        c = LOCS[loc]["sta"]
        if self.tod() == "night" and not self.have("lantern") and loc != "islet":
            c *= 1.4
        if self.s["inj"]:
            c *= 1.3
        if loc == "forest":
            if self.set_bonus("forest"):
                c *= 0.7
            if self.flag("forest_blessing"):
                c *= 0.85
        return max(1, int(round(c)))

    def explore_once(self, note):
        """探索一次。返回标记：new / rare / event / bottle / stop。"""
        s = self.s
        loc = s["loc"]
        tags = set()
        why = self.access(loc)
        if why:
            note.append("⛔ " + why)
            tags.add("stop")
            return tags
        cost = self.explore_cost(loc)
        if s["sta"] < cost:
            note.append(f"⛔ 体力不够了（需要 {cost}，现有 {s['sta']}）。eat 吃点东西，rest 歇一会儿，或回海滩 sleep。")
            tags.add("stop")
            return tags
        self.add_sta(-cost)
        s["explores"] += 1
        s["turn"] += 1
        if loc == "beach":
            s["beach_count"] += 1
        if loc not in s["visited"]:
            s["visited"].append(loc)
            self.journal(f"第一次来到{LOCS[loc]['name']}。")
            self.ach(loc)
        self.advance(LOCS[loc]["hours"])
        for t in LOC_TOOLS.get(loc, []):
            self.wear(t, note)
        if self.tod() == "night" and loc not in ("beach", "cave"):
            self.wear("lantern", note)
        for e in EVENTS:
            if e.get("pity") and e["loc"] == loc and e["id"] not in s["done"] and self.cond_ok(e.get("cond")):
                s["pity"][e["id"]] = s["pity"].get(e["id"], 0) + 1
        # 1. 剧情触发
        trig = self._trigger(loc)
        if trig:
            if self.start_event(trig, note):
                tags.add("stop")
            tags.add("event")
            return tags
        # 2. 漂流瓶
        pb = {"beach": 0.05, "reef": 0.02, "whalefall": 0.04, "islet": 0.03}.get(loc, 0)
        if loc == "beach" and (s["weather"] == "storm" or s["poststorm"] > 0):
            pb = 0.12
        if pb and self.rng.chance(pb):
            self.bottle(note)
            tags.add("bottle")
            return tags
        # 3. 随机事件
        evs = self.eligible_events(loc)
        if evs and self.rng.chance(0.14):
            e = self.rng.weighted(evs)
            if self.start_event(e, note):
                tags.add("stop")
            tags.add("event")
            return tags
        # 4. 风险
        danger = LOCS[loc]["danger"] * 0.015
        if self.tod() == "night" and not self.have("lantern"):
            danger += 0.03
        if danger and self.rng.chance(danger):
            if self.rng.chance(0.5):
                self.injure(note)
            else:
                note.append("（脚下一滑，什么都没找到，白跑了一趟。）")
                return tags
        # 5. 拾获
        if self.rng.chance(0.07):
            note.append(self.rng.choice([
                "（什么都没找到。风把你的脚印吹平了。）", "（空手而归。你坐着看了一会儿海。）",
                "（今天这里什么都没有，只有雾。）", "（翻了半天，只找到一个你自己早上留下的脚印。）"]))
            return tags
        self.loot(loc, note, tags)
        return tags

    def _trigger(self, loc):
        s = self.s
        for e in EVENTS:
            tr = e.get("trigger")
            if not tr or e["id"] in s["done"] or e["loc"] != loc:
                continue
            if tr.startswith("beach_count>="):
                if s["beach_count"] >= int(tr.split(">=")[1]):
                    return e
            elif tr == "lit" and self.flag("lh_lit"):
                return e
        return None

    def luck(self):
        return 1.0 + 0.3 * self.set_bonus("luck") + (0.3 if self.have("spyglass") else 0)

    def loot(self, loc, note, tags):
        pages = self.owned("keeper_page")
        table = [e for e in LOOT[loc] if self.cond_ok(e[2])
                 and not (e[0] == "keeper_page" and pages >= len(KEEPER_DIARY))
                 and not (e[0] == "logbook_page" and self.s["stats"].get("logs", 0) >= len(LOGBOOK))]
        if not table:
            note.append("（这里暂时没有什么可捡的。）")
            return
        lk = self.luck()
        pairs = [(e, e[1] * (lk if RANK[ITEMS[e[0]][2]] >= 2 else 1.0)) for e in table]
        picks = 1 + (1 if self.rng.chance(0.4) else 0) + (1 if self.rng.chance(0.12) else 0)
        got = []
        for _ in range(picks):
            e = self.rng.weighted(pairs)
            n = self.rng.randint(e[3], e[4])
            seen = e[0] in self.s["enc"]
            g = self.gain(e[0], n, note)
            if not g:
                continue
            got.append((e[0], g))
            if not seen:
                tags.add("new")
            if RANK[ITEMS[e[0]][2]] >= 2:
                tags.add("rare")
                if seen:
                    note.append(f"✦ {RARITY[ITEMS[e[0]][2]]['label']}：{self.name(e[0])}")
        if got:
            note.append("拾获：" + "、".join(f"{self.name(i)}×{n}" for i, n in got))

    # ───── 状态栏 ─────
    def bar(self):
        s = self.s
        d = {"day": s["day"], "time": f"{s['hour']:02d}:00{TOD_CN[self.tod()]}", "season": self.season(),
             "wx": WX[s["weather"]], "tide": TIDE_CN[self.tide()], "loc": LOCS[s["loc"]]["name"],
             "sta": f"{s['sta']}/{self.sta_max()}", "coins": s["coins"],
             "bag": f"{self.carry_now()}/{self.carry_max()}", "enc": f"{len(s['enc'])}/{len(ITEMS)}"}
        if s["inj"]:
            d["injured"] = True
        if s["pending"]:
            d["pending"] = "choose"
        if s["traveler"]:
            d["traveler"] = "在海滩"
        return "📊 " + json.dumps(d, ensure_ascii=False)


EVENT_PROMPTS = {
    "hidden_room": "楼梯下面有一扇很小的木门，门上的锁孔和你口袋里那把铜钥匙一样大。",
    "wreck_map": "船长室半淹在水里。小满信里说，海图有一片藏在船上。",
    "lens_pool": "洞最深处有一汪很深的潭，潭底有什么东西一圈一圈地反着提灯的光。",
    "figurehead_ev": "白花丛后面的沙里露出一截彩漆剥落的木头，像一只捧着什么的手。",
    "buried_chest": "铲子碰到了硬东西，“当”的一声。",
    "seal": "一只胖海豹躺在礁石上晒太阳，盯着你的包。",
    "storm_debris": "风暴把很多东西冲到了浪边，浪还很大。",
    "sandcastle": "今天的沙子很细，阳光很好。",
    "lost_fog": "雾太浓了，你分不清哪边是来路。",
    "deer": "雾里有什么东西在看着你。很大，很安静。",
    "beehive": "一棵倒下的树干里传来嗡嗡声——是野蜂巢。",
    "ruin_altar": "藤墙后面是一座长满青苔的小石台，台上有一个捧着碗的石偶。碗是空的。",
    "fallen_tree": "风暴刮倒了一棵大松树，横在小路上。",
    "tide_rush": "潮水开始往回涨了，你脚边那块礁石上还贴着一只大鲍鱼。",
    "trapped_fish": "一个快要干掉的水洼里困着几条小鱼，挤成一团。",
    "wreck_crate": "货舱角落有一只钉死的木箱，箱子上印着“晨星号·货”。",
    "wreck_bell": "船艏挂着一口铜钟，链子锈得快断了。",
    "eel": "舱底有个东西在发光，旁边的黑洞里探出一个尖尖的脑袋。",
    "cave_echo": "洞很深，深得像能把声音吞进去。",
    "cave_lantern_out": "一阵冷风，提灯忽地灭了。四周一片漆黑。",
    "islet_grave": "白花中间立着一块小木牌。",
}


# ───────── 指令工具 ─────────
def _find_item(q, pool=None):
    q = q.strip()
    keys = list(pool) if pool is not None else list(ITEMS.keys())
    if q in keys:
        return q
    for k in keys:
        if ITEMS[k][0] == q:
            return k
    for k in keys:
        if q and q in ITEMS[k][0]:
            return k
    return None


def _parse_n(parts, default=1):
    if parts and parts[-1].isdigit():
        return max(1, int(parts[-1])), parts[:-1]
    return default, parts


def _cost_str(g, cost):
    out = []
    for k, v in cost.items():
        if k == "coins":
            out.append(f"贝币{v}" + ("" if g.s["coins"] >= v else f"(有{g.s['coins']})"))
        else:
            have = g.s["inv"].get(k, 0)
            nm = g.name(k) if (k in g.s["enc"] or RANK[ITEMS[k][2]] < 2) else "？？？"
            out.append(f"{nm}×{v}" + ("" if have >= v else f"(有{have})"))
    return "、".join(out)


def _can_pay(g, cost):
    for k, v in cost.items():
        if (g.s["coins"] if k == "coins" else g.s["inv"].get(k, 0)) < v:
            return False
    return True


def _pay(g, cost):
    for k, v in cost.items():
        if k == "coins":
            g.s["coins"] -= v
            g.s["stats"]["spent"] += v
        else:
            g.lose(k, v)


def _at_beach(g, what="这件事"):
    if g.s["loc"] != "beach":
        g.say(f"{what}要回营地（海滩）才能做：goto beach")
        return False
    return True


HELP = """【潮汐拾荒者】你被潮水冲上了一座雾里的群岛。拾荒、探索、盖房子、拼凑这座岛的过去——做什么由你决定。
用法：island.cmd("指令")；多条指令用 ; 分隔，一次最多 8 条。物品、地点可写 id 或中文名。
 观察  status｜map｜look [物品/地点]｜inventory(inv)｜quests｜achievements
 探索  explore [N] [stop=new,rare,event,bottle]   在当前地点探索 N 次（1~20）。需要抉择的事件一定会停下
       choose <编号>                            对事件做决定
       goto <地点id>                            移动（1 小时，少量体力）
       wait <小时>｜rest（歇 2 小时）｜sleep（在营地睡到早上）
       eat <食物> [数量]｜use <物品>｜open <盒子>
 营地（都在海滩）
       shop｜buy <物品> [数量]｜sell <物品> [数量]｜sell junk（只卖“杂货”类）
       recipes｜craft <配方> [数量]｜cook <料理>
       build（看列表）｜build base｜build <设施id>｜repair <工具>
       keep <物品> [数量]（放进收藏柜：出售、制作、建造都不会动它）｜take <物品> [数量]｜vault
       plant <种子>｜garden｜harvest
 故事  lighthouse [restore|light]｜bottles｜read <bottle 编号|logbook|diary|letter>
 记录  encyclopedia [sets|secrets]｜journal [页码]｜journal add <文字>
每次返回的最后一行是 📊 状态栏，看它就够了。进度每步自动保存。
重开：island.new_game(seed=None, force=True)（旧存档会先备份）。"""


def run(g, line):
    parts = line.strip().split()
    if not parts:
        return
    c, args = parts[0].lower(), parts[1:]
    s = g.s
    free = ("choose", "status", "help", "inventory", "inv", "look", "journal", "map", "quests",
            "encyclopedia", "vault", "bottles", "read", "achievements", "recipes")
    if s["pending"] and c not in free:
        e = EVENT_BY_ID[s["pending"]]
        g.say("❗ 还有一件事等你决定：" + g.event_prompt(e), *g.event_opts(e), "（choose <编号>）")
        return
    fn = COMMANDS.get(c)
    if not fn:
        g.say(f"❓ 不认识的指令「{parts[0]}」。用 help 看全部指令。")
        return
    fn(g, args)


# ───────── 指令 ─────────
def c_help(g, a):
    g.say(HELP)


def c_status(g, a):
    s = g.s
    lines = [f"【状态】第{s['day']}天 {s['hour']:02d}:00（{TOD_CN[g.tod()]}）· {g.season()} · {WX[s['weather']]} · {TIDE_CN[g.tide()]}",
             f"位置：{LOCS[s['loc']]['name']}　体力 {s['sta']}/{g.sta_max()}　贝币 {s['coins']}　背包 {g.carry_now()}/{g.carry_max()}",
             f"营地：{BASE_LEVELS[s['base']]['name']}　设施：" +
             ("、".join(f"{FACILITIES[k]['name']}Lv{v}" for k, v in s["fac"].items()) or "无"),
             f"图鉴 {len(s['enc'])}/{len(ITEMS)}　秘密 {len(s['secrets'])}　累计探索 {s['explores']}"]
    if s["inj"]:
        lines.append("🩹 受伤中")
    if s["poststorm"] > 0:
        lines.append("🌊 风暴刚过，海滩上冲来了很多东西。")
    if g.have("tide_table"):
        fut = []
        for dh in range(1, 13):
            ah = g.abs_hour + dh
            t = g.tide(ah // 24 + 1, ah % 24)
            if not fut or fut[-1][1] != t:
                fut.append((f"{ah % 24:02d}:00", t))
        lines.append("潮汐表：" + " → ".join(f"{x}{TIDE_CN[y]}" for x, y in fut[:5]))
    tools = [f"{g.name(t)}({'∞' if ITEMS[t][5].get('dur', 0) >= 999 else s['dur'].get(t, '?')})"
             for t in s["inv"] if ITEMS[t][1] == "tool"]
    if tools:
        lines.append("工具（剩余耐久）：" + "、".join(tools))
    g.say(*lines)


def c_map(g, a):
    s = g.s
    lines = [f"【地图】现在：{WX[s['weather']]}、{TIDE_CN[g.tide()]}、{TOD_CN[g.tod()]}"]
    for loc in LOC_ORDER:
        if loc not in s["unlocked"]:
            continue
        L = LOCS[loc]
        why = g.access(loc)
        mark = "✦" if s["loc"] == loc else "·"
        lines.append(f" {mark} {L['name']}　{loc}　每次{L['hours']}小时·体力{g.explore_cost(loc)}　" + ("可探索" if not why else why))
    if any(l not in s["unlocked"] for l in LOC_ORDER):
        lines.append("  雾里还有一些你没去过的地方。")
    g.say(*lines)


def c_look(g, a):
    s = g.s
    if not a:
        L = LOCS[s["loc"]]
        g.say(f"【{L['name']}】{L['desc']}")
        return
    q = " ".join(a)
    for loc, L in LOCS.items():
        if q in (loc, L["name"]):
            if loc in s["unlocked"]:
                found = len([1 for v in s["enc"].values() if v.get("loc") == loc])
                g.say(f"【{L['name']} {loc}】{L['desc']}", f"你在这里第一次发现过 {found} 种东西。")
            else:
                g.say("？？？——你还不知道这个地方。")
            return
    iid = _find_item(q)
    if not iid or iid not in s["enc"]:
        g.say("？？？——你还没见过它。")
        return
    n, cat, r, v, d, ex = ITEMS[iid]
    extra = []
    if ex.get("food"):
        extra.append(f"吃了恢复 {ex['food']} 体力")
    if ex.get("heal"):
        extra.append("能治伤")
    if ex.get("open"):
        extra.append("可以 open")
    if ex.get("grow"):
        extra.append(f"可以种，约 {ex['grow'][2]} 天")
    g.say(f"【{n}】{CATS[cat]}·{RARITY[r]['label']}　出售价 {v if v else '不可出售'}　背包 {s['inv'].get(iid, 0)}　收藏柜 {s['vault'].get(iid, 0)}",
          d, "；".join(extra) if extra else None)


def c_inventory(g, a):
    s = g.s
    groups = {}
    for i, n in sorted(s["inv"].items()):
        groups.setdefault(ITEMS[i][1], []).append(f"{g.name(i)}×{n}")
    lines = [f"【背包】{g.carry_now()}/{g.carry_max()}（工具、收藏品、古董、任务道具不占格）　贝币 {s['coins']}"]
    for cat in ("tool", "food", "meal", "res", "mat", "sell", "seed", "coll", "relic", "quest"):
        if cat in groups:
            lines.append(f" {CATS[cat]}：" + "、".join(groups[cat]))
    if len(lines) == 1:
        lines.append(" 空的。")
    if s["vault"]:
        lines.append(f" （收藏柜里还有 {sum(s['vault'].values())} 件，vault 查看）")
    g.say(*lines)


def c_goto(g, a):
    s = g.s
    if not a:
        c_map(g, a)
        return
    q = " ".join(a)
    loc = next((k for k, L in LOCS.items() if q in (k, L["name"])), None)
    if not loc or loc not in s["unlocked"]:
        g.say("你不知道去那里的路。用 map 看已知地点。")
        return
    if loc == s["loc"]:
        g.say(f"你已经在{LOCS[loc]['name']}了。")
        return
    s["loc"] = loc
    s["turn"] += 1
    g.add_sta(-3)
    g.advance(1)
    g.say(f"来到【{LOCS[loc]['name']}】。{LOCS[loc]['desc']}")
    why = g.access(loc)
    if why:
        g.say("⚠️ 现在还不能在这里探索：" + why)
    if loc == "beach" and s["traveler"]:
        g.say("🔔 旅行商人的小船停在浪边。")


def c_explore(g, a):
    s = g.s
    n, stops = 1, set()
    for x in a:
        if x.isdigit():
            n = max(1, min(MAX_BATCH, int(x)))
        elif x.startswith("stop="):
            stops |= set(x[5:].split(","))
        else:
            g.say(f"看不懂参数「{x}」。用法：explore [次数] [stop=new,rare,event,bottle]")
            return
    if n == 1:
        note = []
        g.explore_once(note)
        g.say(*note)
        return
    start = (s["sta"], s["day"], s["hour"])
    loc_name = LOCS[s["loc"]]["name"]
    merged, lines, done = {}, [], 0
    for i in range(n):
        note = []
        tags = g.explore_once(note)
        if "stop" in tags and not (tags - {"stop"}):
            lines.extend(note)  # 没能探索（体力 / 潮水 / 工具）
            break
        done += 1
        notable = []
        for x in note:
            if x.startswith("拾获："):
                for part in x[3:].split("、"):
                    nm, _, cnt = part.rpartition("×")
                    merged[nm] = merged.get(nm, 0) + int(cnt)
            else:
                notable.append(x)
        if notable:
            lines.append(f"— 第{i + 1}次 —")
            lines.extend(notable)
        if s["pending"]:
            break
        hit = stops & tags
        if hit:
            lines.append(f"（遇到了 {'/'.join(sorted(hit))}，按你的设置先停下）")
            break
    if done == 0:
        g.say(*lines)
        return
    g.say(f"🧭 在{loc_name}连续探索 {done}/{n} 次", *lines)
    if merged:
        g.say("合计拾获：" + "、".join(f"{k}×{v}" for k, v in merged.items()))
    g.say(f"体力 {start[0]}→{s['sta']}　时间 第{start[1]}天{start[2]:02d}:00 → 第{s['day']}天{s['hour']:02d}:00")


def c_choose(g, a):
    s = g.s
    if not s["pending"]:
        g.say("现在没有需要决定的事。")
        return
    e = EVENT_BY_ID[s["pending"]]
    if not a or not a[0].isdigit():
        g.say(g.event_prompt(e), *g.event_opts(e))
        return
    k = int(a[0]) - 1
    if not 0 <= k < len(e["opts"]):
        g.say("没有这个选项。")
        return
    o = e["opts"][k]
    miss = g.opt_missing(o)
    if miss:
        g.say(f"做不到：需要 {miss}。换一个选项吧。")
        return
    for it, v in o.get("need", {}).items():
        g.lose(it, v)
    note = []
    if o.get("tool"):
        g.wear(o["tool"], note)
    s["pending"] = None
    s["turn"] += 1
    final = g.apply_out(o["out"], note)
    if e.get("once") and not final.get("reset"):
        s["done"].append(e["id"])
    g.say(*note)


def c_wait(g, a):
    h = int(a[0]) if a and a[0].isdigit() else 1
    h = max(1, min(12, h))
    g.s["turn"] += 1
    g.advance(h)
    g.say(f"你等了 {h} 小时。现在 {g.s['hour']:02d}:00，{WX[g.s['weather']]}、{TIDE_CN[g.tide()]}。")


def c_rest(g, a):
    g.s["turn"] += 1
    g.advance(2)
    g.add_sta(15)
    g.say(f"你找了个背风的地方歇了两个小时。体力 +15（{g.s['sta']}/{g.sta_max()}）")


def c_sleep(g, a):
    s = g.s
    if not _at_beach(g, "睡觉"):
        return
    hours = (6 - s["hour"]) % 24 or 24
    if hours < 5:
        hours = 8
    s["turn"] += 1
    g.advance(hours)
    bed = s["fac"].get("bed", 0)
    rec = BASE_LEVELS[s["base"]]["sleep"] + (20 if bed >= 1 else 0) + (20 if bed >= 2 else 0) + g.set_bonus("sleep")
    if s["inj"]:
        rec -= 20
        s["inj"] = 0 if bed >= 2 else s["inj"] - 1
    g.add_sta(rec)
    g.say(f"你在{BASE_LEVELS[s['base']]['name']}里一觉睡到第{s['day']}天 {s['hour']:02d}:00。体力 +{rec}（{s['sta']}/{g.sta_max()}）")
    ready = [1 for seed, t in s["garden"] if _grown(g, seed, t)]
    if ready:
        g.say(f"🌱 花园里有 {len(ready)} 块地可以收了（harvest）。")


def c_eat(g, a):
    n, a = _parse_n(a)
    iid = _find_item(" ".join(a), [k for k in g.s["inv"] if ITEMS[k][5].get("food")])
    if not iid:
        g.say("背包里没有这种能吃的东西。")
        return
    n = min(n, g.s["inv"][iid])
    rec = ITEMS[iid][5]["food"] * n
    g.lose(iid, n)
    g.add_sta(rec)
    g.s["turn"] += 1
    msg = f"吃了 {g.name(iid)}×{n}，体力 +{rec}（{g.s['sta']}/{g.sta_max()}）"
    if ITEMS[iid][5].get("heal") and g.s["inj"]:
        g.s["inj"] = 0
        msg += "。伤也好了。"
    g.say(msg)


def c_use(g, a):
    iid = _find_item(" ".join(a), list(g.s["inv"].keys()))
    if not iid:
        g.say("背包里没有这个。")
        return
    ex = ITEMS[iid][5]
    if ex.get("food"):
        c_eat(g, [iid])
    elif ex.get("heal"):
        if not g.s["inj"]:
            g.say("你现在没受伤，先留着吧。")
            return
        g.lose(iid, 1)
        g.s["inj"] = 0
        g.s["turn"] += 1
        g.say(f"用了 {g.name(iid)}。伤好了。")
    elif ex.get("open"):
        c_open(g, [iid])
    elif iid in ("logbook_page", "keeper_page", "xiaoman_letter"):
        c_read(g, [{"logbook_page": "logbook", "keeper_page": "diary", "xiaoman_letter": "letter"}[iid]])
    else:
        g.say(f"{g.name(iid)} 没有什么可以直接“用”的。（look 看看它的用途）")


def c_open(g, a):
    s = g.s
    iid = _find_item(" ".join(a), [k for k in s["inv"] if ITEMS[k][5].get("open")])
    if not iid:
        g.say("没有可以打开的东西。")
        return
    g.lose(iid, 1)
    s["turn"] += 1
    note = []
    if ITEMS[iid][5]["open"] == "tin_box":
        r = g.rng.random()
        if r < 0.35:
            c = g.rng.randint(8, 30)
            s["coins"] += c
            note.append(f"盒子里是一卷用油纸包好的旧贝币。+{c}贝币")
        elif r < 0.55:
            note.append("盒子里有几枚铜币。")
            note.append(f"获得 铜币×{g.gain('old_coin', 2, note)}")
        elif r < 0.7:
            g.gain("marble", 1, note)
            note.append("盒子里只有一颗玻璃弹珠，在锈迹里亮晶晶的。")
        elif r < 0.82:
            g.gain("tin_soldier", 1, note)
            note.append("盒子里躺着一个锡兵。")
        elif r < 0.92:
            note.append("盒子里卷着一张纸——")
            g.bottle(note)
        else:
            g.gain("broken_compass", 1, note)
            note.append("盒子里是一只破罗盘。")
    else:
        for it, lo, hi in (("pine_cone", 1, 3), ("berry_seed", 0, 2)):
            k = g.rng.randint(lo, hi)
            if k:
                note.append(f"获得 {g.name(it)}×{g.gain(it, k, note)}")
        if g.rng.chance(0.4):
            g.gain("marble", 1, note)
            note.append("还有一颗玻璃弹珠——这只松鼠品位不错。")
    g.say(f"打开了 {g.name(iid)}：", *note)


# ───── 商店 ─────
def c_shop(g, a):
    if not _at_beach(g, "买卖东西"):
        return
    lines = ["【老钳的螺壳杂货铺】寄居蟹老板从壳里探出一只钳子。（buy <id> [数量]）"]
    for k, p in SHOP.items():
        lines.append(f"  {k}　{g.name(k)}　{p}贝币")
    tr = g.s["traveler"]
    if tr:
        lines.append("【旅行商人】小船上的货，每样只有一件：")
        for it, p, sold in tr["stock"]:
            lines.append(f"  {it}　{g.name(it)}　{p}贝币" + ("（已售出）" if sold else ""))
    lines.append(f"你有 {g.s['coins']} 贝币。卖东西：sell <物品> [数量]；sell junk 一次卖掉全部“杂货”。")
    g.say(*lines)


def c_buy(g, a):
    if not _at_beach(g, "买东西"):
        return
    s = g.s
    n, a = _parse_n(a)
    tr = s["traveler"]
    pool = list(SHOP.keys()) + ([x[0] for x in tr["stock"] if not x[2]] if tr else [])
    iid = _find_item(" ".join(a), pool)
    if not iid:
        g.say("店里没有这个。用 shop 看货。")
        return
    row = None
    if iid in SHOP:
        price = SHOP[iid]
    else:
        row = next(x for x in tr["stock"] if x[0] == iid)
        price, n = row[1], 1
    if s["coins"] < price * n:
        n = s["coins"] // price
        if n <= 0:
            g.say(f"贝币不够（{g.name(iid)} {price}贝币，你有 {s['coins']}）。")
            return
    note = []
    got = g.gain(iid, n, note)
    if got <= 0:
        g.say(*note)
        return
    s["coins"] -= price * got
    s["stats"]["spent"] += price * got
    s["turn"] += 1
    if row:
        row[2] = 1
        g.journal(f"从旅行商人那里买了{g.name(iid)}。")
    g.say(*note, f"买了 {g.name(iid)}×{got}，花了 {price * got} 贝币。剩 {s['coins']}。")


def _sell_price(g, iid):
    base = ITEMS[iid][3]
    if ITEMS[iid][1] == "tool":
        base = max(1, base // 2)
    return int(base * (1 + g.set_bonus("sell") / 100))


def c_sell(g, a):
    if not _at_beach(g, "卖东西"):
        return
    s = g.s
    if a and a[0].lower() in ("junk", "all"):
        items = sorted((i, n) for i, n in s["inv"].items() if ITEMS[i][1] == "sell")
        if not items:
            g.say("没有杂货可卖。（sell junk 只卖“杂货”类；资源、收藏品、古董要单独 sell <物品>）")
            return
        total = sum(_sell_price(g, i) * n for i, n in items)
        for i, n in items:
            g.lose(i, n)
        s["coins"] += total
        s["stats"]["earned"] += total
        s["turn"] += 1
        g.say("卖掉了：" + "、".join(f"{g.name(i)}×{n}" for i, n in items), f"得 {total} 贝币，现有 {s['coins']}。")
        return
    n, a = _parse_n(a)
    iid = _find_item(" ".join(a), list(s["inv"].keys()))
    if not iid:
        g.say("背包里没有这个。（收藏柜里的要先 take 出来）")
        return
    if ITEMS[iid][3] <= 0:
        g.say(f"{g.name(iid)} 不能卖。")
        return
    n = min(n, s["inv"][iid])
    p = _sell_price(g, iid) * n
    g.lose(iid, n)
    s["coins"] += p
    s["stats"]["earned"] += p
    s["turn"] += 1
    g.say(f"卖掉 {g.name(iid)}×{n}，得 {p} 贝币，现有 {s['coins']}。")


# ───── 制作 ─────
def _recipe_lock(g, req):
    for fac, lv in req.items():
        if g.s["fac"].get(fac, 0) < lv:
            return f"需要{FACILITIES[fac]['name']}Lv{lv}"
    return None


def c_recipes(g, a):
    lines = ["【配方】craft <配方> [数量]（料理也可以用 cook）"]
    shown = 0
    for rid, (k, mats, req) in RECIPES.items():
        out = rid.split("@")[0]
        if out not in g.s["enc"] and not all(m in g.s["enc"] for m in mats):
            continue
        lock = _recipe_lock(g, req)
        lines.append(f"  {rid}　{g.name(out)}×{k} ← {_cost_str(g, mats)}" + (f"　〔{lock}〕" if lock else ""))
        shown += 1
    lines.append(f"（只列出你见过材料的配方，还有 {len(RECIPES) - shown} 个没想到。）")
    g.say(*lines)


def c_craft(g, a):
    s = g.s
    if not _at_beach(g, "做东西"):
        return
    n, a = _parse_n(a)
    q = " ".join(a)
    cands = [r for r in RECIPES if q in (r, r.split("@")[0], g.name(r.split("@")[0]))]
    if not cands:
        g.say("没有这个配方。用 recipes 看。")
        return
    made, note, err = 0, [], None
    for _ in range(min(n, 20)):
        ok = False
        for r in cands:
            k, mats, req = RECIPES[r]
            lock = _recipe_lock(g, req)
            if lock:
                err = lock
                continue
            if not _can_pay(g, mats):
                err = "材料不够：" + _cost_str(g, mats)
                continue
            _pay(g, mats)
            made += g.gain(r.split("@")[0], k, note)
            ok = True
            break
        if not ok:
            break
    out = cands[0].split("@")[0]
    if made:
        s["turn"] += 1
        g.advance(1)
        g.say(*note, f"做好了 {g.name(out)}×{made}。" + (f"（只做成了 {made} 个：{err}）" if err and made < n else ""))
        if out == "skiff":
            g.journal("小船造好了。它很小，但是是我的。")
    else:
        g.say(*note, f"做不了：{err}")


# ───── 建造 ─────
def c_build(g, a):
    s = g.s
    if not _at_beach(g, "建造"):
        return
    if not a:
        lines = [f"【营地】现在是：{BASE_LEVELS[s['base']]['name']}"]
        if s["base"] + 1 < len(BASE_LEVELS):
            nx = BASE_LEVELS[s["base"] + 1]
            lines.append(f"  build base → {nx['name']}（体力上限{nx['sta']}·背包{nx['carry']}·睡觉恢复{nx['sleep']}）：{_cost_str(g, nx['cost'])}")
        for fid, F in FACILITIES.items():
            lv = s["fac"].get(fid, 0)
            if lv >= len(F["levels"]):
                lines.append(f"  {fid}　{F['name']}　已满级")
                continue
            L = F["levels"][lv]
            lock = "" if s["base"] >= L["base"] else f"〔要先升到{BASE_LEVELS[L['base']]['name']}〕"
            lines.append(f"  build {fid}　{F['name']}Lv{lv + 1}：{L['eff']}　{_cost_str(g, L['cost'])} {lock}")
        g.say(*lines)
        return
    t = a[0].lower()
    if t == "base":
        if s["base"] + 1 >= len(BASE_LEVELS):
            g.say("营地已经是最好的样子了。")
            return
        nx = BASE_LEVELS[s["base"] + 1]
        if not _can_pay(g, nx["cost"]):
            g.say(f"还差点：{_cost_str(g, nx['cost'])}")
            return
        _pay(g, nx["cost"])
        s["base"] += 1
        s["turn"] += 1
        g.advance(4)
        g.say(f"🏠 营地升级成了【{nx['name']}】。体力上限、背包、睡眠都变好了。")
        g.journal(f"营地升级成了{nx['name']}。")
        return
    if t not in FACILITIES:
        g.say("没有这个设施。用 build 看列表。")
        return
    F = FACILITIES[t]
    lv = s["fac"].get(t, 0)
    if lv >= len(F["levels"]):
        g.say(f"{F['name']}已经满级了。")
        return
    L = F["levels"][lv]
    if s["base"] < L["base"]:
        g.say(f"要先把营地升到{BASE_LEVELS[L['base']]['name']}。")
        return
    if not _can_pay(g, L["cost"]):
        g.say(f"还差点：{_cost_str(g, L['cost'])}")
        return
    _pay(g, L["cost"])
    s["fac"][t] = lv + 1
    s["turn"] += 1
    g.advance(2)
    g.say(f"🔨 建好了 {F['name']}Lv{lv + 1}：{L['eff']}")
    g.journal(f"建好了{F['name']}Lv{lv + 1}。")


def c_repair(g, a):
    s = g.s
    if s["fac"].get("gearrack", 0) < 1:
        g.say("要先建装备架（build gearrack）。")
        return
    if not _at_beach(g, "修理"):
        return
    iid = _find_item(" ".join(a), [k for k in s["inv"] if ITEMS[k][1] == "tool"])
    if not iid:
        g.say("没有这个工具。")
        return
    full = ITEMS[iid][5].get("dur", 20)
    if s["dur"].get(iid, full) >= full:
        g.say("它还好好的。")
        return
    cost = {"iron_scrap": 1, "coins": 5}
    if not _can_pay(g, cost):
        g.say(f"修理需要：{_cost_str(g, cost)}")
        return
    _pay(g, cost)
    s["dur"][iid] = full
    s["turn"] += 1
    g.say(f"{g.name(iid)} 修好了，耐久回到 {full}。")


# ───── 收藏柜 ─────
def c_keep(g, a):
    s = g.s
    n, a = _parse_n(a)
    iid = _find_item(" ".join(a), list(s["inv"].keys()))
    if not iid:
        g.say("背包里没有这个。")
        return
    if ITEMS[iid][1] == "tool":
        g.say("工具要带在身上用，不能放进收藏柜。")
        return
    if s["fac"].get("display", 0) < 1 and iid not in s["vault"] and len(s["vault"]) >= 5:
        g.say("帐篷角落的小铁匣只放得下 5 种东西。建了展示柜（build display）就不限了。")
        return
    n = min(n, s["inv"][iid])
    g.lose(iid, n)
    s["vault"][iid] = s["vault"].get(iid, 0) + n
    s["turn"] += 1
    g.say(f"把 {g.name(iid)}×{n} 收进了收藏柜。出售、制作、建造都不会动它。")
    _check_sets(g)


def _check_sets(g):
    for sid in g.done_sets():
        key = "set_" + sid
        if not g.flag(key):
            g.setflag(key)
            g.say(f"🏆 集齐了收藏系列【{SETS[sid]['name']}】：{SETS[sid]['desc']}")
            g.journal(f"集齐了收藏系列「{SETS[sid]['name']}」。")


def c_take(g, a):
    s = g.s
    n, a = _parse_n(a)
    iid = _find_item(" ".join(a), list(s["vault"].keys()))
    if not iid:
        g.say("收藏柜里没有这个。")
        return
    n = min(n, s["vault"][iid])
    s["vault"][iid] -= n
    if s["vault"][iid] <= 0:
        del s["vault"][iid]
    s["inv"][iid] = s["inv"].get(iid, 0) + n  # 拿回来不受背包上限限制，免得东西卡在柜里
    s["turn"] += 1
    g.say(f"从收藏柜拿出了 {g.name(iid)}×{n}。")


def c_vault(g, a):
    s = g.s
    if not s["vault"]:
        g.say("收藏柜是空的。keep <物品> 可以把珍贵的东西放进来。")
        return
    kind = "展示柜" if s["fac"].get("display") else f"帐篷角落的小铁匣（{len(s['vault'])}/5 种）"
    g.say(f"【收藏柜】{kind}", "  " + "、".join(f"{g.name(i)}×{n}" for i, n in s["vault"].items()))


# ───── 花园 ─────
def _plots(g):
    lv = g.s["fac"].get("garden", 0)
    return [0, 3, 6][lv]


def _grow_days(g, seed):
    return max(1, ITEMS[seed][5]["grow"][2] - (1 if g.s["fac"].get("garden", 0) >= 2 else 0))


def _grown(g, seed, t):
    return g.abs_hour - t >= _grow_days(g, seed) * 24


def c_plant(g, a):
    s = g.s
    if _plots(g) == 0:
        g.say("要先建小花园（build garden）。")
        return
    if not _at_beach(g, "种东西"):
        return
    iid = _find_item(" ".join(a), [k for k in s["inv"] if ITEMS[k][1] == "seed"])
    if not iid:
        g.say("没有这种种子。")
        return
    if len(s["garden"]) >= _plots(g):
        g.say("地都种满了。")
        return
    g.lose(iid, 1)
    s["garden"].append([iid, g.abs_hour])
    s["turn"] += 1
    g.say(f"种下了 {g.name(iid)}。大约 {_grow_days(g, iid)} 天后可以收。")


def c_garden(g, a):
    s = g.s
    if _plots(g) == 0:
        g.say("还没有花园（build garden）。")
        return
    lines = [f"【小花园】{len(s['garden'])}/{_plots(g)} 块地"]
    for seed, t in s["garden"]:
        left = _grow_days(g, seed) * 24 - (g.abs_hour - t)
        lines.append(f"  {g.name(seed)}：" + ("可以收了！" if left <= 0 else f"还要约 {left // 24 + 1} 天"))
    g.say(*lines)


def c_harvest(g, a):
    s = g.s
    if _plots(g) == 0:
        g.say("还没有花园（build garden）。")
        return
    if not _at_beach(g, "收菜"):
        return
    keep, note = [], []
    for seed, t in s["garden"]:
        if _grown(g, seed, t):
            out, k, _ = ITEMS[seed][5]["grow"]
            note.append(f"收获 {g.name(out)}×{g.gain(out, k, note)}")
            if g.rng.chance(0.4):
                g.gain(seed, 1, note)
                note.append(f"还留下了一颗{g.name(seed)}")
        else:
            keep.append([seed, t])
    if not note:
        g.say("还没有成熟的。")
        return
    s["garden"] = keep
    s["turn"] += 1
    g.say(*note)


# ───── 灯塔 ─────
def c_lighthouse(g, a):
    s = g.s
    if "lighthouse" not in s["unlocked"]:
        g.say("你还不知道灯塔在哪。")
        return
    sub = a[0].lower() if a else ""
    st = s["lh"]
    if sub == "restore":
        if s["loc"] != "lighthouse":
            g.say("要先去灯塔（goto lighthouse）。")
            return
        if st >= len(LH_STAGES):
            g.say("灯塔已经修好了。" + ("灯亮着。" if g.flag("lh_lit") else "在夜里用 lighthouse light 点灯。"))
            return
        stg = LH_STAGES[st]
        if stg["tool"] and not g.have(stg["tool"]):
            g.say(f"「{stg['name']}」需要：{g.name(stg['tool'])}")
            return
        if not _can_pay(g, stg["need"]):
            g.say(f"「{stg['name']}」需要：{_cost_str(g, stg['need'])}")
            return
        if s["sta"] < 15:
            g.say("修灯塔是力气活，体力至少要 15。")
            return
        _pay(g, stg["need"])
        note = []
        if stg["tool"]:
            g.wear(stg["tool"], note)
        s["lh"] += 1
        s["turn"] += 1
        g.add_sta(-15)
        g.advance(2)
        g.say(*note, f"🗼 {stg['name']}：{stg['text']}")
        g.journal(f"灯塔：{stg['name']}。")
        if s["lh"] == 1:
            g.setflag("lh_open")
            g.ach("lh_open")
        return
    if sub == "light":
        if s["loc"] != "lighthouse":
            g.say("要在灯塔里点灯。")
            return
        if g.flag("lh_lit"):
            g.say("灯已经亮着了。光一圈一圈扫过海面。")
            return
        if st < len(LH_STAGES):
            g.say(f"灯塔还没修好。下一步：{LH_STAGES[st]['name']}。")
            return
        if g.tod() != "night":
            g.say("白天点灯，谁也看不见。等到夜里（20 点以后）。")
            return
        g.setflag("lh_lit")
        s["turn"] += 1
        g.say("🔥 你划着火柴，凑近灯芯。火苗跳了一下，然后稳稳地亮起来。透镜开始转动——",
              "一道光从塔顶射出去，穿过雾，照到十八海里外。四十年来第一次。")
        g.journal("我点亮了灯塔。")
        g.ach("lh_lit")
        note = []
        g.start_event(EVENT_BY_ID["islet_glimpse"], note)
        g.say(*note)
        return
    lines = [f"【雾屿灯塔】修复进度 {st}/{len(LH_STAGES)}" + ("　🔥已点亮" if g.flag("lh_lit") else "")]
    for i, stg in enumerate(LH_STAGES):
        if i < st:
            lines.append(f"  ✔ {stg['name']}")
        elif i == st:
            req = [_cost_str(g, stg["need"])] if stg["need"] else []
            if stg["tool"]:
                req.append(g.name(stg["tool"]))
            lines.append(f"  → {stg['name']}（需要：{'、'.join(req)}；在灯塔里 lighthouse restore）")
        else:
            lines.append("  · ？？？")
    if st >= len(LH_STAGES) and not g.flag("lh_lit"):
        lines.append("  → 等一个夜晚，在灯塔里 lighthouse light。")
    g.say(*lines)


# ───── 阅读 ─────
def c_bottles(g, a):
    s = g.s
    if not s["bottles"]:
        g.say("还没捡到过漂流瓶。")
        return
    story = {b["id"]: b for b in BOTTLE_STORY}
    lines = [f"【瓶中信】{len(s['bottles'])} 封（read bottle <编号>）"]
    for i, bid in enumerate(s["bottles"], 1):
        title = story[bid]["title"] if bid in story else BOTTLE_MISC[int(bid[1:])][0]
        lines.append(f"  {i}. 《{title}》")
    g.say(*lines)


def c_read(g, a):
    s = g.s
    if not a:
        g.say("read bottle <编号> ｜ read logbook ｜ read diary ｜ read letter")
        return
    t = a[0].lower()
    if t in ("bottle", "瓶"):
        if len(a) < 2 or not a[1].isdigit():
            c_bottles(g, [])
            return
        k = int(a[1]) - 1
        if not 0 <= k < len(s["bottles"]):
            g.say("没有这一封。")
            return
        bid = s["bottles"][k]
        story = {b["id"]: b for b in BOTTLE_STORY}
        if bid in story:
            g.say(f"《{story[bid]['title']}》", story[bid]["text"])
        else:
            t2, txt = BOTTLE_MISC[int(bid[1:])]
            g.say(f"《{t2}》", txt)
    elif t in ("logbook", "logbook_page", "日志"):
        n = min(s["stats"].get("logs", 0), len(LOGBOOK))
        if n <= 0:
            g.say("你还没有航海日志的残页。")
            return
        g.say(f"【晨星号航海日志】（{n}/{len(LOGBOOK)} 页）", *LOGBOOK[:n])
    elif t in ("diary", "keeper_page", "日记"):
        n = min(max(g.owned("keeper_page"), s["diary_read"]), len(KEEPER_DIARY))
        if n <= 0:
            g.say("你还没有守塔人的日记页。")
            return
        s["diary_read"] = n
        g.say(f"【温守岚的日记】（{n}/{len(KEEPER_DIARY)} 页）", *KEEPER_DIARY[:n])
        if n >= len(KEEPER_DIARY) and not g.flag("diary_key"):
            g.setflag("diary_key")
            g.say("（最后一页提到了林子里那块写字的石头。带上斧头去找找？）")
            g.journal("读完了守塔人的日记。钥匙在林子里，和写字的石头在一起；透镜在洞里最深的水潭。")
    elif t in ("letter", "xiaoman_letter", "信"):
        if not g.owned("xiaoman_letter"):
            g.say("你没有这封信。")
            return
        g.say(XIAOMAN_LETTER)
        if not g.flag("read_xiaoman"):
            g.setflag("read_xiaoman")
            g.journal("读了小满的最后一封信。这座岛以后就交给我了。")
    else:
        g.say("读什么？read bottle <编号> ｜ read logbook ｜ read diary ｜ read letter")


# ───── 记录 ─────
def c_journal(g, a):
    s = g.s
    if a and a[0].lower() == "add":
        text = " ".join(a[1:]).strip()
        if not text:
            g.say("要写什么？journal add <文字>")
            return
        g.journal(text[:300], auto=False)
        s["turn"] += 1
        g.say("📝 记下了。")
        return
    J = s["journal"]
    per = 12
    pages = max(1, (len(J) + per - 1) // per)
    p = int(a[0]) if a and a[0].isdigit() else pages
    p = max(1, min(pages, p))
    lines = [f"【探险日记】第 {p}/{pages} 页（journal <页码> 翻页；✍ 是你自己写的）"]
    for d, h, t, auto in J[(p - 1) * per: p * per]:
        lines.append(f"  第{d}天{h:02d}时 {'' if auto else '✍'}{t}")
    g.say(*lines)


def c_encyclopedia(g, a):
    s = g.s
    sub = a[0].lower() if a else ""
    if sub == "secrets":
        g.say(f"【秘密】{len(s['secrets'])}/{len(SECRET_NAMES)}",
              "  " + ("、".join(SECRET_NAMES.get(x, x) for x in s["secrets"]) or "还没有。"),
              "  岛上还藏着一些——要在对的时候，做对的事。")
        return
    if sub == "sets":
        lines = ["【收藏系列】整组放进收藏柜（并且建了展示柜），就能得到永久加成。"]
        for st in SETS.values():
            if not any(i in s["enc"] for i in st["items"]):
                lines.append("  ？？？（还没见过这一系列的东西）")
                continue
            have = len([i for i in st["items"] if s["vault"].get(i)])
            names = "、".join((g.name(i) + ("✔" if s["vault"].get(i) else "")) if i in s["enc"] else "？？？" for i in st["items"])
            lines.append(f"  {st['name']}（柜中 {have}/{len(st['items'])}）：{names} → {st['desc']}")
        g.say(*lines)
        return
    lines = [f"【图鉴】{len(s['enc'])}/{len(ITEMS)} 种（encyclopedia sets ｜ encyclopedia secrets ｜ look <名字>）"]
    for cat, label in CATS.items():
        allc = [i for i in ITEMS if ITEMS[i][1] == cat]
        found = [g.name(i) for i in allc if i in s["enc"]]
        lines.append(f"  {label} {len(found)}/{len(allc)}：" + ("、".join(found) or "—"))
    lines.append(f"  地点 {len(s['unlocked'])}/{len(LOCS)}：" + "、".join(LOCS[l]["name"] for l in LOC_ORDER if l in s["unlocked"]))
    g.say(*lines)


def c_quests(g, a):
    s = g.s
    L = []
    if "forest" not in s["unlocked"]:
        L.append("海滩后面的雾很浓。多在海滩走走，也许会散开。")
    elif "reef" not in s["unlocked"]:
        L.append("退潮退得远的日子，海滩东头好像有什么。继续在海滩转转。")
    if "reef" in s["unlocked"] and not g.have("reef_boots"):
        L.append("礁石很滑。编一双防滑草鞋（recipes）会好走很多。")
    if "wreck" in s["unlocked"] and "wreck" not in s["visited"]:
        L.append("沉船：需要绳索和撬棍才能下去。")
    if "lighthouse" not in s["unlocked"] and "forest" in s["unlocked"]:
        L.append("岬角那边好像有什么。从林子高处也许看得见。")
    if "lighthouse" in s["unlocked"]:
        if s["lh"] < len(LH_STAGES):
            L.append(f"灯塔：下一步「{LH_STAGES[s['lh']]['name']}」（lighthouse 查看）")
        elif not g.flag("lh_lit"):
            L.append("灯塔修好了。等一个夜晚，去点灯。")
    maps = [m for m in ("map_a", "map_b", "map_c") if g.have(m)]
    if 0 < len(maps) < 3:
        L.append(f"海图残片 {len(maps)}/3")
    if g.owned("keeper_page") >= len(KEEPER_DIARY) and not g.flag("diary_key"):
        L.append("守塔人的日记页凑齐了，读一读（read diary）。")
    if g.flag("diary_key") and not g.have("rusty_key") and "keeper_room" not in s["secrets"]:
        L.append("守塔人把钥匙留在了林子里那块写字的石头旁边。")
    if g.have("rusty_key"):
        L.append("生锈的钥匙：灯塔里哪扇门用得上？")
    if s["lh"] == 3 and not g.have("fresnel_lens"):
        L.append("透镜不在灯塔里。" + ("守塔人说他把它推进了洞里最深的水潭。" if g.flag("diary_key") else "也许守塔人的日记里有线索。"))
    if "islet" in s["unlocked"] and not g.have("skiff"):
        L.append("去雾里的岛需要一条船（工作台 Lv2 可以造）。")
    if g.owned("xiaoman_letter") and not g.flag("read_xiaoman"):
        L.append("你还没读小满留下的信（read letter）。")
    if not L:
        L.append("现在没有明确的线索。随便走走吧——这座岛还有很多你没见过的东西。")
    g.say("【线索】", *("  · " + x for x in L))


def c_achievements(g, a):
    s = g.s
    lines = [f"【成就】{len(s['ach'])}/{len(ACHIEVEMENTS)}"]
    for k in s["ach"]:
        n, d, r = ACHIEVEMENTS[k]
        lines.append(f"  ✔ {n}：{d}")
    lines.append(f"  还有 {len(ACHIEVEMENTS) - len(s['ach'])} 个没解锁。")
    g.say(*lines)


COMMANDS = {
    "help": c_help, "status": c_status, "map": c_map, "look": c_look,
    "inventory": c_inventory, "inv": c_inventory, "goto": c_goto, "explore": c_explore,
    "choose": c_choose, "wait": c_wait, "rest": c_rest, "sleep": c_sleep, "eat": c_eat,
    "use": c_use, "open": c_open, "shop": c_shop, "buy": c_buy, "sell": c_sell,
    "recipes": c_recipes, "craft": c_craft, "cook": c_craft, "build": c_build, "repair": c_repair,
    "keep": c_keep, "take": c_take, "vault": c_vault, "plant": c_plant, "garden": c_garden,
    "harvest": c_harvest, "lighthouse": c_lighthouse, "bottles": c_bottles, "read": c_read,
    "journal": c_journal, "encyclopedia": c_encyclopedia, "quests": c_quests,
    "achievements": c_achievements,
}


# ───────── 模块接口 ─────────
_G = None


def _load(path):
    for p in (path, path + ".bak"):
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                st = json.load(f)
            if st.get("v") == VERSION and isinstance(st.get("inv"), dict):
                base = _fresh_state(st.get("seed", 1))
                base.update(st)
                return base, p != path
        except (OSError, ValueError):
            continue
    return None, False


def _game():
    global _G
    if _G is None:
        path = _save_path()
        st, recovered = _load(path)
        if st is None:
            _G = Game(_fresh_state(int(_time.time() * 1000) & 0xFFFFFFFF), path)
            _G.save()
        else:
            _G = Game(st, path)
            if recovered:
                _G.say("（主存档损坏了，已经从备份恢复。）")
    return _G


def cmd(text="status"):
    """执行指令，返回结果文字。多条指令用 ; 或换行分隔（一次最多 8 条）。"""
    g = _game()
    lines = [x.strip() for x in str(text).replace("；", ";").replace("\n", ";").split(";") if x.strip()]
    if not lines:
        lines = ["status"]
    over = len(lines) > 8
    lines = lines[:8]
    multi = len(lines) > 1
    for ln in lines:
        if multi:
            g.out.append(f"▶ {ln}")
        snapshot = json.dumps(g.s, ensure_ascii=False)
        rng_state = g.rng.state
        try:
            run(g, ln)
            g.check_ach()
            g.save()
        except Exception as ex:  # 一条坏指令不能弄坏存档：回滚这一条
            g.s = json.loads(snapshot)
            g.rng = Rng(rng_state)
            g.out.append(f"⚠️ 这条指令出错了（{type(ex).__name__}: {ex}），已经撤销，存档没受影响。")
        if multi:
            g.out.append("")
    if over:
        g.out.append("（一次最多 8 条，后面的没有执行）")
    res = "\n".join(g.out).rstrip() + "\n" + g.bar()
    g.out = []
    return res


def new_game(seed=None, force=False):
    """开始新游戏。已有进度时要 force=True，旧存档会备份成 island_save.old-<时间戳>.json。"""
    global _G
    path = _save_path()
    if os.path.exists(path):
        st, _ = _load(path)
        if st and st.get("turn", 0) > 0 and not force:
            return (f"⚠️ 已经有一局在进行中（第{st['day']}天，探索 {st['explores']} 次）。"
                    f"确定要重开，请用 new_game(seed, force=True)，旧存档会先自动备份。")
        root, ext = os.path.splitext(path)
        shutil.copyfile(path, f"{root}.old-{int(_time.time())}{ext}")
    if seed is None:
        seed = int(_time.time() * 1000) & 0xFFFFFFFF
    _G = Game(_fresh_state(int(seed) & 0xFFFFFFFF), path)
    _G.save()
    return ("🌊 新的一局。你在一片灰白的沙滩上醒来，潮水刚刚退去。\n"
            "身后是一顶破帐篷，雾很浓。先 help 看看能做什么，然后 explore 吧。\n" + _G.bar())
