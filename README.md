# 24 November 2026: 57 stories, a UTC timeline and a date check

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/aryatrifebrian423/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/aryatrifebrian423/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up Tuesday 24 November 2026 in world news: 57
verified stories across 7 regions, a UTC timeline strip, a dot-matrix
world map, and a visible date check. The cover carries the day's three
biggest numbers: 24 dead in the Banten factory fire, Nvidia up 31%
(+$952bn in a day) as Jensen Huang returns as CEO, and CrowdStrike's
$43.9bn all-stock deal for Zscaler.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no numpy,
no network. It draws the poster with an embedded 5×7 bitmap font and
a hand-built PNG encoder (`zlib` + `struct`), and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).
Output is fully deterministic: two runs write byte-identical files.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verification

Every story is sourced in `SOURCES.md`, with the method and the
wrong-day items that were dropped. The image is 1024×1024 and under
1 MiB.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x9vj0gh6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
