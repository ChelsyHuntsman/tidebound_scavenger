# -*- coding: utf-8 -*-
"""功能测试：用打包好的 island.py 跑，覆盖存档、随机种子、各系统和异常情况。

用法：python3 tests/test_island.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], check=True, capture_output=True)

PASS, FAIL = [], []


def check(name, cond, info=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✔ " if cond else "  ✘ ") + name + ("" if cond else f"  ← {info}"))


def fresh_dir():
    d = tempfile.mkdtemp(prefix="island_t_")
    shutil.copy(os.path.join(ROOT, "island.py"), d)
    return d


def run_py(d, code):
    """在独立进程里 import island 跑一段代码（模拟重新导入）。"""
    env = dict(os.environ)
    env.pop("ISLAND_SAVE", None)
    r = subprocess.run([sys.executable, "-c", "import island\n" + code], cwd=d, env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout


def main():
    print("【存档与重新导入】")
    d = fresh_dir()
    out = run_py(d, "print(island.new_game(seed=123))\nprint(island.cmd('explore 5'))")
    check("新游戏 + 探索能运行", "连续探索" in out, out[:200])
    save = json.load(open(os.path.join(d, "island_save.json"), encoding="utf-8"))
    check("自动存档写入", save["explores"] >= 1)
    out2 = run_py(d, "print(island.cmd('status'))")
    check("重新导入后接着玩", f"累计探索 {save['explores']}" in out2, out2[:200])
    out3 = run_py(d, "print(island.new_game(seed=5))")
    check("已有进度时 new_game 不会直接覆盖", "已经有一局" in out3, out3)
    out4 = run_py(d, "print(island.new_game(seed=5, force=True))")
    olds = [f for f in os.listdir(d) if ".old-" in f]
    check("force 重开会先备份旧档", "新的一局" in out4 and olds, os.listdir(d))

    print("【存档损坏恢复】")
    run_py(d, "island.cmd('explore 2')")
    run_py(d, "island.cmd('explore 1')")  # 让 .bak 存在
    with open(os.path.join(d, "island_save.json"), "w") as f:
        f.write("{坏掉的 json")
    out5 = run_py(d, "print(island.cmd('status'))")
    check("主存档坏了从 .bak 恢复", "从备份恢复" in out5 and "累计探索" in out5, out5[:200])

    print("【随机种子可复现】")
    seq = "explore 10;goto forest;explore 6;goto beach;sleep;explore 8"
    a, b = fresh_dir(), fresh_dir()
    ra = run_py(a, f"island.new_game(seed=777)\nprint(island.cmd({seq!r}))")
    rb = run_py(b, f"island.new_game(seed=777)\nprint(island.cmd({seq!r}))")
    check("同种子同指令 → 结果完全一样", ra == rb)
    rc = run_py(fresh_dir(), f"island.new_game(seed=778)\nprint(island.cmd({seq!r}))")
    check("不同种子 → 结果不同", ra != rc)

    print("【指令与系统】")
    os.environ["ISLAND_SAVE"] = os.path.join(tempfile.mkdtemp(), "s.json")
    sys.path.insert(0, ROOT)
    import engine as E
    E.new_game(seed=42, force=True)
    g = E._game()
    r = E.cmd("fly to moon")
    check("无效指令有清楚提示", "不认识的指令" in r)
    r = E.cmd("explore abc")
    check("参数错误有提示", "看不懂参数" in r)
    r = E.cmd("goto narnia")
    check("未知地点有提示", "不知道去那里的路" in r)
    r = E.cmd("buy unicorn")
    check("买不存在的东西有提示", "店里没有" in r)
    r = E.cmd("help")
    for c in ("explore", "choose", "goto", "shop", "buy", "sell", "craft", "build", "keep", "journal",
              "encyclopedia", "lighthouse", "read", "plant", "harvest", "repair", "rest", "sleep", "map"):
        if c not in r:
            check(f"help 里列出了 {c}", False, "缺失")
    check("help 列出全部主要指令", all(c in E.HELP for c in E.COMMANDS if c not in ("inv", "cook", "use", "open", "garden", "vault", "take", "eat", "wait", "status", "look", "quests", "achievements", "recipes", "inventory", "bottles", "help")))
    r = E.cmd(";".join(["status"] * 10))
    check("一次超过 8 条会截断并提示", "最多 8 条" in r)
    r = E.cmd("explore 50")
    check("批量探索上限 20", "/20 次" in r or "/20" in r, r[:120])

    print("【体力耗尽与恢复】")
    E.new_game(seed=9, force=True)
    g = E._game()
    for _ in range(4):
        E.cmd("explore 20")
    check("体力会耗尽并停下", g.s["sta"] < 10)
    r = E.cmd("explore")
    check("体力不够时给出恢复办法", "体力不够" in r and "sleep" in r)
    E.cmd("sleep")
    check("睡觉恢复体力", g.s["sta"] >= 60)
    E.cmd("goto forest")
    g.s["sta"] = 0
    r = E.cmd("goto beach")
    check("体力为 0 也能走回营地（不会死档）", g.s["loc"] == "beach")
    r = E.cmd("rest")
    check("rest 在哪都能回体力", g.s["sta"] >= 15)

    print("【买卖与经济】")
    E.new_game(seed=10, force=True)
    g = E._game()
    profit = [k for k, p in E.SHOP.items() if E._sell_price(g, k) >= p]
    check("商店里没有买了再卖能赚钱的东西", not profit, profit)
    tprofit = [k for k, p in E.TRAVELER_STOCK if E._sell_price(g, k) >= p]
    check("旅行商人的货也不能倒卖", not tprofit, tprofit)
    g.s["coins"] = 100
    E.cmd("buy ration 3")
    check("买东西扣钱进背包", g.s["coins"] == 76 and g.s["inv"]["ration"] == 5)
    g.s["inv"]["conch"] = 3
    g.s["inv"]["pearl"] = 1
    g.s["inv"]["music_box"] = 1
    E.cmd("keep pearl")
    E.cmd("sell junk")
    check("sell junk 只卖杂货，不碰收藏柜和收藏品", "conch" not in g.s["inv"] and g.s["vault"].get("pearl") == 1
          and g.s["inv"].get("music_box") == 1)
    r = E.cmd("sell logbook_page")
    check("任务道具不能卖", "背包里没有" in r or "不能卖" in r)

    print("【制作与建造】")
    E.new_game(seed=11, force=True)
    g = E._game()
    g.s["inv"].update({"rope_scrap": 8, "fiber": 30, "driftwood": 30, "wood": 40, "iron_scrap": 10, "nails": 20, "moss_stone": 10})
    g.s["coins"] = 500
    for k in ("rope_scrap", "fiber", "driftwood", "wood", "iron_scrap", "nails", "moss_stone"):
        g.s["enc"][k] = {"d": 1, "loc": "beach"}
    r = E.cmd("craft rope 2")
    check("制作：绳索", g.s["inv"].get("rope") == 2, r)
    r = E.cmd("craft crowbar")
    check("没有工作台时提示需要设施", "工作台" in r)
    E.cmd("build workbench")
    E.cmd("craft crowbar")
    check("建工作台后能做撬棍", g.have("crowbar"))
    E.cmd("build bed")
    check("床铺提高体力上限", g.sta_max() == 110)
    E.cmd("build storage")
    check("储物箱扩大背包", g.carry_max() == 110)
    E.cmd("build gearrack")
    g.s["dur"]["crowbar"] = 3
    E.cmd("repair crowbar")
    check("装备架可以修工具", g.s["dur"]["crowbar"] == 25)
    E.cmd("build base")
    check("营地升级", g.s["base"] == 1)
    E.cmd("build garden")
    g.s["inv"]["berry_seed"] = 1
    E.cmd("plant berry_seed")
    E.cmd("wait 12;wait 12;wait 12;wait 12;wait 12;wait 12;wait 12;wait 12")
    r = E.cmd("harvest")
    check("花园：种下、等待、收获", "收获 雾莓" in r, r)

    print("【事件与抉择】")
    E.new_game(seed=12, force=True)
    g = E._game()
    stopped_on_choice = False
    for _ in range(60):
        E.cmd("sleep")
        r = E.cmd("explore 20")
        if g.s["pending"]:
            stopped_on_choice = True
            check("批量探索遇到抉择会停下并列出选项", "choose" in r and "1." in r, r[-300:])
            r2 = E.cmd("explore 5")
            check("有抉择没做时不能继续探索", "等你决定" in r2)
            E.cmd("choose 99")
            check("非法选项不会出错", g.s["pending"] is not None)
            e = E.EVENT_BY_ID[g.s["pending"]]
            ok = next(i for i, o in enumerate(e["opts"], 1) if not g.opt_missing(o))
            E.cmd(f"choose {ok}")
            check("做出选择后事件结束", g.s["pending"] is None)
            break
    check("能遇到需要抉择的事件", stopped_on_choice)
    every_event_has_free_option = all(any(not o.get("need") and not o.get("tool") for o in e["opts"])
                                      for e in E.EVENTS if "opts" in e)
    check("每个抉择事件都有不需要道具的选项（不会卡死）", every_event_has_free_option)

    print("【受伤与治疗】")
    E.new_game(seed=13, force=True)
    g = E._game()
    note = []
    g.injure(note)
    c_inj = g.explore_cost("beach")
    check("受伤后探索更费体力", c_inj > E.LOCS["beach"]["sta"])
    g.s["inv"]["herb"] = 1
    E.cmd("use herb")
    check("止血草能治伤", g.s["inj"] == 0)
    g.injure(note)
    E.cmd("sleep")
    E.cmd("sleep")
    check("睡两晚自然痊愈", g.s["inj"] == 0)

    print("【日记、图鉴、漂流瓶】")
    E.cmd("journal add 今天找到一个旧音乐盒，我决定留下它。")
    r = E.cmd("journal")
    check("日记可以手写并保存", "✍今天找到一个旧音乐盒" in r)
    saved = json.load(open(os.environ["ISLAND_SAVE"], encoding="utf-8"))
    check("日记写进了存档", any("旧音乐盒" in j[2] for j in saved["journal"]))
    r = E.cmd("look 潮汐之心")
    check("没见过的东西显示 ？？？", "？？？" in r)
    r = E.cmd("encyclopedia")
    check("图鉴不剧透未发现物品名", "潮汐之心" not in r)
    r = E.cmd("map")
    check("地图不提前显示隐藏地点", "鲸骨湾" not in r and "雾中小岛" not in r)
    for _ in range(9):
        g.bottle([])
    titles = [b for b in g.s["bottles"] if b.startswith("s")]
    check("主线信件按顺序到达（时机未到的先给闲信）", titles[:3] == ["s1", "s2", "s3"], titles)
    check("第二封信揭示灯塔", "lighthouse" in g.s["unlocked"])

    print("【指令出错时回滚】")
    before = json.dumps(g.s, sort_keys=True)
    orig = E.COMMANDS["status"]
    E.COMMANDS["status"] = lambda gg, a: (gg.s.__setitem__("coins", -999), 1 / 0)
    r = E.cmd("status")
    E.COMMANDS["status"] = orig
    check("出错的指令被撤销、存档不受影响", "已经撤销" in r and json.dumps(g.s, sort_keys=True) == before)

    print("【长时间连续游玩（机器人）】")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "playtest.py"), "3"], capture_output=True, text=True)
    ok = r.returncode == 0 and "错误0" in r.stdout and r.stdout.count("'letter'") >= 2
    check("机器人 3 局：无报错，并且至少 2 局走完主线", ok, r.stdout[-800:] + r.stderr[-800:])
    print(r.stdout)

    print(f"\n通过 {len(PASS)}，失败 {len(FAIL)}")
    if FAIL:
        print("失败：", FAIL)
        sys.exit(1)


if __name__ == "__main__":
    main()
