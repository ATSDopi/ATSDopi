"""
Generate a "Recent Activity" feed card from the user's public GitHub events.
Shows the latest distinct actions (pushes, releases, PRs, stars…) with
relative timestamps — keeps the profile feeling alive between commits here.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, card_bg, text_el, xml_escape, time_ago,
    PURPLE, CYAN, INDIGO, CARD_BG, BORDER, TEXT, TEXT_DIM, GREEN, ORANGE
)
from github_client import get_public_events

W = 460
MAX_ROWS = 6
ROW_H = 26
TOP_H = 48
BOTTOM_PAD = 14

# event type → accent color
EVENT_COLORS = {
    "PushEvent": GREEN,
    "CreateEvent": CYAN,
    "PullRequestEvent": PURPLE,
    "PullRequestReviewEvent": PURPLE,
    "IssuesEvent": ORANGE,
    "IssueCommentEvent": ORANGE,
    "WatchEvent": CYAN,
    "ForkEvent": INDIGO,
    "ReleaseEvent": ORANGE,
    "DeleteEvent": TEXT_DIM,
    "PublicEvent": TEXT_DIM,
}


def _short_repo(full_name, username):
    """Strip the 'username/' prefix for own repos."""
    prefix = f"{username}/"
    return full_name[len(prefix):] if full_name.startswith(prefix) else full_name


def _describe(ev, username):
    """Turn a public event into a short sentence. Returns (text, color) or None."""
    t = ev.get("type")
    repo = _short_repo(ev.get("repo", {}).get("name", ""), username)
    p = ev.get("payload", {})
    color = EVENT_COLORS.get(t, TEXT_DIM)

    if t == "PushEvent":
        n = p.get("size") or len(p.get("commits") or [])
        return f"Pushed {n} commit{'s' if n != 1 else ''} to {repo}", color
    if t == "CreateEvent":
        ref_type = p.get("ref_type", "repository")
        ref = p.get("ref") or ""
        what = f"{ref_type} {ref}".strip() if ref_type != "repository" else "repository"
        return f"Created {what} in {repo}".replace("in in", "in"), color
    if t == "PullRequestEvent":
        action = p.get("action", "updated").replace("_", " ")
        return f"{action.capitalize()} a pull request in {repo}", color
    if t == "PullRequestReviewEvent":
        return f"Reviewed a pull request in {repo}", color
    if t == "IssuesEvent":
        action = p.get("action", "updated")
        return f"{action.capitalize()} an issue in {repo}", color
    if t == "IssueCommentEvent":
        return f"Commented on an issue in {repo}", color
    if t == "WatchEvent":
        return f"Starred {ev.get('repo', {}).get('name', '')}", color
    if t == "ForkEvent":
        return f"Forked {ev.get('repo', {}).get('name', '')}", color
    if t == "ReleaseEvent":
        rel = (p.get("release") or {}).get("tag_name") or (p.get("release") or {}).get("name") or "a release"
        return f"Published {rel} in {repo}", color
    if t == "DeleteEvent":
        return f"Deleted {p.get('ref_type', 'ref')} in {repo}", color
    if t == "PublicEvent":
        return f"Open-sourced {repo}", color
    return None


def generate_feed(username, output_path, max_rows=MAX_ROWS):
    """Generate the recent-activity card SVG."""
    print(f"  Fetching public events for {username}...")
    try:
        events = get_public_events(username)
    except Exception as e:
        print(f"  ! events fetch failed: {e}")
        events = []

    # Dedupe on (type, repo) — a burst of PR events collapses to one row
    seen = set()
    rows = []
    for ev in events:
        key = (ev.get("type"), ev.get("repo", {}).get("name"))
        if key in seen:
            continue
        seen.add(key)
        described = _describe(ev, username)
        if not described:
            continue
        text, color = described
        rows.append((text, color, time_ago(ev.get("created_at"))))
        if len(rows) >= max_rows:
            break

    H = TOP_H + max(len(rows), 1) * ROW_H + BOTTOM_PAD

    svg = svg_header(W, H)
    svg += card_bg(W, H)

    # Title
    svg += text_el(20, 30, "Recent Activity", font_size=16, fill=PURPLE, weight="bold")
    svg += f'  <rect x="20" y="38" width="140" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    if not rows:
        svg += text_el(W // 2, TOP_H + 20, "Quiet lately — building in stealth mode",
                       font_size=12, fill=TEXT_DIM, anchor="middle", opacity=0.8)
    else:
        y = TOP_H + 12
        for text, color, ago in rows:
            # Event dot
            svg += f'  <circle cx="26" cy="{y - 4}" r="4" fill="{color}"/>\n'
            # Action text (truncate to fit before the timestamp column)
            max_chars = 52
            if len(text) > max_chars:
                text = text[:max_chars - 1].rstrip() + "…"
            svg += text_el(40, y, xml_escape(text), font_size=12, fill=TEXT)
            svg += text_el(W - 18, y, ago, font_size=11, fill=TEXT_DIM, anchor="end")
            y += ROW_H

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Activity feed ({len(rows)} events) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_feed(username, os.path.join(assets, "feed.svg"))
