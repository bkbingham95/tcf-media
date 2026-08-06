#!/usr/bin/env python3
"""
Runner: reads a JSON spec on stdin, writes composites, optionally PUTs each
finished file to a Blotato presigned upload_url.

NOTE: rebuilt from scratch on 2026-08-06. The original tools/tcf_build.py
described in the handoff was never committed to the repo.

Spec shape:
{
  "date": "2026-08-07",
  "out_dir": "out/2026-08-07",
  "posts": [
    {"slot": 1, "photo": "photos/x.jpeg", "headline": "...",
     "style_index": 3, "yb": 0.45, "sa": 214, "bb": 0.44,
     "upload_url": "https://... (optional)"}
  ]
}

Prints a JSON report on stdout.
"""

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).parent))
from style import render  # noqa: E402


def put_file(url, path):
    data = Path(path).read_bytes()
    req = Request(url, data=data, method="PUT")
    req.add_header("Content-Type", "image/jpeg")
    req.add_header("x-upsert", "true")
    with urlopen(req, timeout=120) as resp:
        return resp.status


def main():
    spec = json.load(sys.stdin)
    root = Path(spec.get("root", "."))
    out_dir = root / spec.get("out_dir", "out")
    report = []

    for post in spec["posts"]:
        out_path = out_dir / f"slot{post['slot']}.jpg"
        info = render(
            root / post["photo"],
            post["headline"],
            post["style_index"],
            out_path,
            yb=post.get("yb", 0.5),
            sa=post.get("sa", 210),
            bb=post.get("bb", 0.42),
        )
        info["slot"] = post["slot"]
        info["photo"] = post["photo"]
        info["headline"] = post["headline"]

        if post.get("upload_url"):
            try:
                info["upload_status"] = put_file(post["upload_url"], out_path)
            except Exception as exc:  # noqa: BLE001
                info["upload_status"] = "FAILED"
                info["upload_error"] = f"{type(exc).__name__}: {exc}"
        report.append(info)

    json.dump({"report": report}, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
