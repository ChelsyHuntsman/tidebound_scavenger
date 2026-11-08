# -*- coding: utf-8 -*-
"""把 content.py + engine.py 打包成给 AI 玩家用的 island.py（盲玩封装）。

这只是 base64 封装，让 AI 玩家“不小心瞄到也读不懂”，不是加密。
用法：python3 build.py
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))

HEADER = '''"""🏝️ 潮汐拾荒者（Tidebound Scavenger）· 盲玩版

【给 AI 玩家的说明】
你是这个游戏的「玩家」，不是开发者。你被潮水冲上了一座被雾包围的群岛。
靠 cmd() 返回的文字去探索、做决定：

    import island
    print(island.cmd("help"))       # 看全部指令
    print(island.cmd("status"))     # 看当前状态
    print(island.cmd("explore"))    # 在当前地点探索一次
    print(island.cmd("explore 10")) # 连续探索 10 次，只回一个汇总
    print(island.cmd("journal add 今天找到一个旧音乐盒，我决定留下它。"))

⚠️ 请不要解码 / 查看下面的 _BLOB：那里面是整座岛的剧透（有哪些东西、藏在哪、
概率多少、剧情怎么走）。这只是方便盲玩的 base64 封装，不是加密——请自觉当一个
蒙着眼睛的探索者。想维护游戏的人类，请看同目录的 engine.py / content.py。

接口：island.cmd("指令") 返回文字；island.new_game(seed=None, force=False) 重开。
存档：同目录 island_save.json（每次操作自动保存，重新 import 会接着玩）。
"""
import base64
_BLOB = (
'''


def build():
    parts = []
    for name in ("content.py", "engine.py"):
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            parts.append(f"# ==== {name} ====\n" + f.read())
    code = "\n\n".join(parts)
    blob = base64.b64encode(code.encode("utf-8")).decode("ascii")
    with open(os.path.join(HERE, "island.py"), "w", encoding="utf-8") as f:
        f.write(HEADER)
        for i in range(0, len(blob), 76):
            f.write(f'    "{blob[i:i + 76]}"\n')
        f.write(')\nexec(compile(base64.b64decode(_BLOB).decode("utf-8"), "<island>", "exec"), globals())\n')
        f.write("del _BLOB\n")
    return len(code)


if __name__ == "__main__":
    print("built island.py from", build(), "chars of source")
