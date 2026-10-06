"""Fetch the Codeforces rating and rewrite the badge in README.md."""
import json
import re
import urllib.request
from pathlib import Path

HANDLE = "VitCore"
README = Path(__file__).resolve().parent.parent / "README.md"

# Codeforces rank colours
RANKS = [
    (3000, "FF0000"), (2600, "FF0000"), (2400, "FF0000"), (2300, "FF8C00"),
    (2100, "FF8C00"), (1900, "AA00AA"), (1600, "0000FF"), (1400, "03A89E"),
    (1200, "008000"), (0, "808080"),
]


def color(rating: int) -> str:
    return next(c for limit, c in RANKS if rating >= limit)


def fetch() -> dict:
    url = f"https://codeforces.com/api/user.info?handles={HANDLE}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    if data.get("status") != "OK":
        raise RuntimeError(data)
    return data["result"][0]


def main() -> None:
    user = fetch()
    rating, rank = user["rating"], user.get("rank", "unrated")
    maxr = user.get("maxRating", rating)
    # HTML, а не Markdown: бейдж лежит внутри <div align="center">, где Markdown не разбирается
    badge = (
        f'<a href="https://codeforces.com/profile/{HANDLE}">'
        f'<img src="https://img.shields.io/badge/Codeforces-{rating}-{color(rating)}'
        f'?style=flat-square&logo=codeforces&logoColor=white" alt="Codeforces"/></a>'
    )
    line = f"{rank.title()}, **{rating}** (max {maxr})"
    text = README.read_text(encoding="utf-8")
    text = re.sub(r"(<!--CF_BADGE-->).*?(<!--/CF_BADGE-->)",
                  lambda m: m.group(1) + badge + m.group(2), text, flags=re.S)
    text = re.sub(r"(<!--CF_TEXT-->).*?(<!--/CF_TEXT-->)",
                  lambda m: m.group(1) + line + m.group(2), text, flags=re.S)
    README.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
