"""
Generate the profile-views badge.

Counts repo-page traffic (GitHub's traffic/views API covers the last
14 days) and accumulates a persistent total in assets/viewcount.json —
each daily run merges new day buckets on top. Badge matches the status
badges' style: dark card, colored border, tinted label section.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, xml_escape, INDIGO
from github_client import get_traffic_views
from generate_badges import _badge_widths, BADGE_H

VIEWS_FILE = "viewcount.json"
COLOR = "#7287fd"  # INDIGO


def _load(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"total": 0, "recorded": {}}


def generate_views(username, assets_dir):
    """Update the cumulative view counter and render the badge SVG."""
    vc_path = os.path.join(assets_dir, VIEWS_FILE)
    data = _load(vc_path)

    traffic = get_traffic_views(username)
    if traffic:
        for day in traffic["views"]:
            d = day["timestamp"][:10]
            data["recorded"][d] = max(data["recorded"].get(d, 0), day["uniques"])
        data["total"] = sum(data["recorded"].values())
        with open(vc_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    else:
        print("  ! traffic unavailable - keeping stored total")

    label_w, value_w = _badge_widths("Views", str(data["total"]))
    w = label_w + value_w
    svg = svg_header(w, BADGE_H)
    svg += (f'  <clipPath id="vclip"><rect width="{w}" height="{BADGE_H}" rx="4"/></clipPath>\n')
    svg += f'  <rect width="{w}" height="{BADGE_H}" rx="4" fill="#0d1117" stroke="{COLOR}" stroke-width="1"/>\n'
    svg += (f'  <rect width="{label_w:.1f}" height="{BADGE_H}" fill="{COLOR}" '
            f'opacity="0.15" clip-path="url(#vclip)"/>\n')
    svg += (f'  <line x1="{label_w:.1f}" y1="0.5" x2="{label_w:.1f}" y2="{BADGE_H - 0.5}" '
            f'stroke="{COLOR}" stroke-width="1" opacity="0.5"/>\n')
    svg += (f'  <text x="{label_w / 2:.1f}" y="21" font-size="11" '
            f'font-family="Segoe UI, sans-serif" font-weight="bold" fill="{COLOR}" '
            f'text-anchor="middle">Views</text>\n')
    svg += (f'  <text x="{label_w + value_w / 2:.1f}" y="21" font-size="11" '
            f'font-family="Segoe UI, sans-serif" font-weight="bold" fill="#c9d1d9" '
            f'text-anchor="middle">{data["total"]}</text>\n')
    svg += svg_footer()

    out = os.path.join(assets_dir, "views.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  Views badge ({data['total']} views) -> {out}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    generate_views(sys.argv[1] if len(sys.argv) > 1 else "ATSDopi", assets)
