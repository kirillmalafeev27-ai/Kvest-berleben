#!/usr/bin/env python3
"""Точка входа в прототип BERLIN: ÜBERLEBEN.

Примеры:
    python play.py                      # интерактив (офлайн-заглушки или Claude, если есть ключ)
    python play.py --stub               # принудительно офлайн
    python play.py --debug              # показывать интенты/оси/«ведёт к»
    python play.py --load manual        # загрузить сейв
    python play.py --script demo.txt    # автопрогон по строкам файла
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from berlin.cli import CLI  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="BERLIN: ÜBERLEBEN — текстовый прототип")
    ap.add_argument("--content", default=os.path.join(os.path.dirname(__file__), "content"))
    ap.add_argument("--save", default="berlin_save.sqlite")
    ap.add_argument("--load", default=None, help="слот сейва для загрузки")
    ap.add_argument("--script", default=None, help="файл со сценарием ввода (по строке на ход)")
    ap.add_argument("--stub", action="store_true", help="принудительно офлайн (без Claude)")
    ap.add_argument("--debug", action="store_true", help="показывать интенты/оси/ведёт-к")
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--line", default="soiskatel",
                    help="линия: soiskatel|bezhenec|vossoedinenie|student|voyna|zarabotok|nevidimka")
    args = ap.parse_args()

    cli = CLI(args.content, save_path=args.save, force_stub=args.stub,
              debug=args.debug, seed=args.seed, line=args.line)

    if args.script:
        with open(args.script, encoding="utf-8") as f:
            cli.run_script(f.readlines())
    else:
        cli.run_interactive(load=args.load)


if __name__ == "__main__":
    main()
