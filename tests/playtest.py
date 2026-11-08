# -*- coding: utf-8 -*-
"""自动试玩：一个按目标行动的小机器人，验证整条主线能走通、经济不崩、不卡关。

用法：python3 tests/playtest.py [种子数量]
它会偷看引擎状态来做决定（真正的 AI 玩家看不到这些）。
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="island_test_")
os.environ["ISLAND_SAVE"] = os.path.join(TMP, "save.json")

import engine as E  # noqa: E402

SOURCE = {
    "fiber": "forest", "wood": "forest", "resin": "forest", "moss_stone": "forest", "herb": "forest",
    "owl_feather": "lighthouse", "driftwood": "beach", "sea_glass": "beach", "pumice": "beach",
    "rope_scrap": "beach", "glow_algae": "beach", "shell": "beach", "nails": "wreck",
    "iron_scrap": "wreck", "brass_gear": "wreck", "canvas": "wreck", "reef_fish": "reef",
    "copper_ore": "reef", "keeper_page": "lighthouse", "berries": "forest",
}


class Bot:
    def __init__(self, seed, verbose=False, limit=3000):
        self.log = []
        print_ = E.new_game(seed=seed, force=True)
        self.g = E._game()
        self.verbose = verbose
        self.limit = limit
        self.calls = 0
        self.errors = []

    @property
    def s(self):
        return self.g.s

    def c(self, text):
        self.calls += 1
        r = E.cmd(text)
        if "⚠️ 这条指令出错了" in r:
            self.errors.append((text, r))
        if self.verbose:
            print(">>", text, "\n", r[:600])
        return r

    def has(self, i, n=1):
        return self.s["inv"].get(i, 0) >= n

    # —— 目标：当前缺的东西 ——
    def needs(self):
        s, g = self.s, self.g
        n = {}

        def want(i, k):
            n[i] = max(n.get(i, 0), k)
        if "reef" in s["unlocked"] and not self.has("reef_boots"):
            want("fiber", 5)
        if s["fac"].get("workbench", 0) < 1:
            want("driftwood", 6)
            want("wood", 4)
        if "lighthouse" in s["unlocked"] and s["lh"] == 1:
            want("wood", 12)
            want("nails", 10)
        if s["lh"] == 2:
            want("sea_glass", 12)
            want("pumice", 4)
        if s["lh"] >= 4 and s["lh"] < 5 and s["inv"].get("lamp_oil", 0) < 2:
            if self.has("net"):
                want("reef_fish", 6)
            want("resin", 3)
        if s["lh"] >= 3 and s["base"] < 1:
            want("wood", 15)
            want("driftwood", 10)
            want("nails", 10)
        if s["base"] >= 1 and s["fac"].get("workbench", 0) < 2:
            want("iron_scrap", 6)
            want("brass_gear", 2)
            want("wood", 8)
        if s["fac"].get("workbench", 0) >= 2 and not self.has("skiff"):
            want("wood", 20)
            want("canvas", 4)
            want("nails", 15)
            want("resin", 4)
            want("rope_scrap", 8)
        if s["lh"] >= 2:
            n["keeper_page"] = 6
            if g.owned("keeper_page") >= 6:
                n.pop("keeper_page")
        return n

    def target(self):
        s, g = self.s, self.g
        if "forest" not in s["unlocked"] or "reef" not in s["unlocked"]:
            return "beach"
        if "lighthouse" not in s["unlocked"]:
            return "forest"
        if "wreck" not in s["unlocked"]:
            return "reef"
        if g.flag("diary_key") and not self.has("rusty_key") and "keeper_room" not in s["secrets"] and self.has("axe"):
            return "forest"
        if self.has("rusty_key") and s["lh"] >= 2:
            return "lighthouse"
        if g.flag("letter_s6") and not self.has("map_a") and "wreck_map" not in s["done"] and g.access("wreck") is None:
            return "wreck"
        if s["lh"] == 3 and not self.has("fresnel_lens"):
            if "cave" not in s["unlocked"]:
                return "reef"
            if self.has("lantern") and self.has("rope"):
                return "cave"
        if g.flag("lh_lit") and self.has("skiff") and "islet" in s["unlocked"]:
            if not g.owned("xiaoman_letter") or ("figurehead_ev" not in s["done"]):
                return "islet"
        if "whalefall" in s["unlocked"] and "whalefall" not in s["visited"]:
            return "whalefall"
        nd = self.needs()
        for i, k in nd.items():
            if i in SOURCE and s["inv"].get(i, 0) < k:
                loc = SOURCE[i]
                if loc in s["unlocked"]:
                    return loc
        if not g.flag("letter_s6") or len([b for b in s["bottles"] if b.startswith("s")]) < 9:
            return "beach"
        return "reef"

    # —— 营地事务 ——
    def camp(self):
        s, g = self.s, self.g
        self.c("sell junk")
        nd = self.needs()
        for i, n in list(s["inv"].items()):
            cat = E.ITEMS[i][1]
            keep = {"res": 4, "mat": 8, "food": 5, "seed": 2, "meal": 4}.get(cat)
            if i in nd:
                keep = max(keep or 0, nd[i])
            if cat in ("coll", "relic") and E.ITEMS[i][3] > 0 and i not in self.vault_wish():
                self.c(f"sell {i} {n}")
            elif keep is not None and n > keep and E.ITEMS[i][3] > 0:
                self.c(f"sell {i} {n - keep}")
        if g.carry_now() > 0.6 * g.carry_max():
            for i, n in list(s["inv"].items()):
                if E.ITEMS[i][1] in ("res", "mat", "seed", "sell") and i not in nd and E.ITEMS[i][3] > 0:
                    self.c(f"sell {i} {n}")
        for i in list(s["inv"]):
            if i in self.vault_wish() and (s["fac"].get("display") or len(s["vault"]) < 5 or i in s["vault"]):
                self.c(f"keep {i}")
        # 造东西
        if not self.has("reef_boots") and self.has("fiber", 5):
            self.c("craft reef_boots")
        if s["fac"].get("workbench", 0) < 1:
            self.c("build workbench")
        if s["fac"].get("bed", 0) < 1 and s["coins"] > 60:
            self.c("build bed")
        if s["fac"].get("storage", 0) < 1 and s["coins"] > 40:
            self.c("build storage")
        if not self.has("rope"):
            self.c("craft rope")
            if not self.has("rope") and s["coins"] >= 14:
                self.c("buy rope")
        if "wreck" in s["unlocked"] and not self.has("crowbar"):
            self.c("craft crowbar")
            if not self.has("crowbar") and s["coins"] >= 40:
                self.c("buy crowbar")
        if s["lh"] >= 2 and s["inv"].get("glass_pane", 0) < 4:
            self.c("craft glass_pane 4")
        if s["lh"] >= 2 and not self.has("lantern"):
            self.c("craft lantern")
            if not self.has("lantern") and s["coins"] >= 65:
                self.c("buy lantern")
        if s["lh"] >= 3 and not self.has("net") and s["coins"] >= 18:
            self.c("buy net")
        if s["lh"] >= 4:
            self.c("craft lamp_oil 2")
        if g.flag("diary_key") and not self.has("axe") and s["coins"] >= 48:
            self.c("craft axe")
            if not self.has("axe"):
                self.c("buy axe")
        if s["lh"] >= 3 and s["base"] < 1:
            self.c("build base")
        if s["base"] >= 1 and s["fac"].get("workbench", 0) < 2:
            self.c("build workbench")
        if s["fac"].get("workbench", 0) >= 2 and not self.has("skiff"):
            if s["inv"].get("rope", 0) < 2:
                self.c("craft rope")
            self.c("craft skiff")
        if s["fac"].get("gearrack", 0) < 1 and s["coins"] > 150:
            self.c("build gearrack")
        if s["base"] >= 1 and s["fac"].get("display", 0) < 1 and s["coins"] > 150:
            self.c("build display")
        if s["base"] >= 1 and s["fac"].get("kitchen", 0) < 1 and s["coins"] > 200:
            self.c("build kitchen")
        if s["base"] >= 1 and s["fac"].get("garden", 0) < 1 and s["coins"] > 200:
            self.c("build garden")
        if s["fac"].get("garden"):
            self.c("harvest")
            for seed in ("berry_seed", "herb_seed", "thrift_seed"):
                if self.has(seed):
                    self.c(f"plant {seed}")
        if s["base"] == 1 and s["coins"] > 400:
            self.c("build base")
        if s["base"] == 2 and s["coins"] > 800:
            self.c("build base")
        if s["traveler"] and s["coins"] > 500:
            for it, p, sold in s["traveler"]["stock"]:
                if not sold and s["coins"] > p + 300:
                    self.c(f"buy {it}")
        for it in ("tin_box", "squirrel_stash"):
            while self.has(it):
                self.c(f"open {it}")

    def vault_wish(self):
        return {i for st in E.SETS.values() for i in st["items"]}

    def step(self):
        s, g = self.s, self.g
        if s["pending"]:
            e = E.EVENT_BY_ID[s["pending"]]
            for k, o in enumerate(e["opts"], 1):
                if not g.opt_missing(o):
                    self.c(f"choose {k}")
                    return
            raise RuntimeError("事件没有可选项: " + e["id"])
        if s["inj"]:
            for h in ("herb", "bandage"):
                if self.has(h):
                    self.c(f"use {h}")
                    break
        # 读东西
        if g.owned("keeper_page") >= 6 and not g.flag("diary_key"):
            self.c("read diary")
        if g.owned("xiaoman_letter") and not g.flag("read_xiaoman"):
            self.c("read letter")
        tgt = self.target()
        cost = g.explore_cost(tgt) if tgt in s["unlocked"] else 10
        if s["sta"] < cost + 4:
            foods = sorted((i for i in s["inv"] if E.ITEMS[i][5].get("food")), key=lambda i: E.ITEMS[i][3])
            if foods and s["loc"] != "beach":
                self.c(f"eat {foods[0]} 3")
                if s["sta"] >= cost + 4:
                    return
            if s["loc"] != "beach":
                self.c("goto beach")
            self.camp()
            self.c("sleep")
            return
        # 灯塔修复
        if tgt == "lighthouse" or (s["lh"] < 5 and "lighthouse" in s["unlocked"] and self.can_restore()):
            if s["loc"] != "lighthouse":
                self.c("goto lighthouse")
            if self.can_restore():
                self.c("lighthouse restore")
                return
        if s["lh"] >= 5 and not g.flag("lh_lit"):
            if s["loc"] != "lighthouse":
                self.c("goto lighthouse")
            if g.tod() != "night":
                self.c("wait 3")
            else:
                self.c("lighthouse light")
            return
        if s["loc"] != tgt:
            if s["loc"] == "beach":
                self.camp()
            self.c(f"goto {tgt}")
        why = g.access(tgt)
        if why:
            if "潮" in why or "风暴" in why or "看不见" in why:
                self.c("wait 2")
            else:
                self.c("goto beach")
                self.camp()
                self.c("explore 3")
            return
        self.c("explore 4")

    def can_restore(self):
        s, g = self.s, self.g
        if s["lh"] >= len(E.LH_STAGES):
            return False
        st = E.LH_STAGES[s["lh"]]
        return (not st["tool"] or self.has(st["tool"])) and E._can_pay(g, st["need"]) and s["sta"] >= 15

    def run(self):
        milestones = {}
        while self.calls < self.limit:
            self.step()
            s = self.s
            for key, ok in (("forest", "forest" in s["unlocked"]), ("reef", "reef" in s["unlocked"]),
                            ("wreck", "wreck" in s["visited"]), ("lh_open", s["lh"] >= 1),
                            ("lh_stage3", s["lh"] >= 3), ("lens", s["lh"] >= 4), ("lit", self.g.flag("lh_lit")),
                            ("skiff", self.has("skiff")), ("islet", "islet" in s["visited"]),
                            ("letter", self.g.flag("read_xiaoman")), ("whalefall", "whalefall" in s["visited"]),
                            ("home", s["base"] >= 3)):
                if ok and key not in milestones:
                    milestones[key] = (s["explores"], s["day"])
            if "letter" in milestones and "whalefall" in milestones and s["explores"] > 400:
                break
        return milestones


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    worst = {}
    for seed in range(1, n + 1):
        b = Bot(seed)
        try:
            ms = b.run()
        except Exception as ex:
            print(f"seed {seed}: 崩溃 {type(ex).__name__}: {ex}")
            raise
        s = b.s
        print(f"seed {seed}: 调用{b.calls} 探索{s['explores']} 第{s['day']}天 贝币{s['coins']} "
              f"图鉴{len(s['enc'])}/{len(E.ITEMS)} 秘密{len(s['secrets'])} 成就{len(s['ach'])} 营地Lv{s['base']} "
              f"灯塔{s['lh']} 瓶{len(s['bottles'])} 受伤{s['stats']['injuries']} 错误{len(b.errors)}")
        print("   里程碑(探索次数,天):", ms)
        for k, v in ms.items():
            worst[k] = max(worst.get(k, (0, 0)), v)
        for t, r in b.errors[:3]:
            print("   ERR", t, r[:200])
    print("最慢的里程碑：", worst)


if __name__ == "__main__":
    main()
