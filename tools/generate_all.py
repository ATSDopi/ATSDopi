"""
Master orchestrator — runs all asset generators in sequence.

Each step is isolated: if one generator crashes (API hiccup, bad data…),
the others still run and previously generated assets stay untouched.
Usage: python generate_all.py [username]
"""

import sys
import os
import traceback

# Windows consoles (cp1252) can't print ✓/✗ — reconfigure stdout for local runs
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(__file__))

from generate_banner import generate_header, generate_footer
from generate_typing import generate_typing
from generate_stats import generate_stats_card, generate_top_langs
from generate_streak import generate_streak
from generate_trophies import generate_trophies
from generate_activity import generate_activity_graph
from generate_skills import generate_skills
from generate_badges import generate_badges
from generate_contributions import generate_contributions
from generate_pacman import generate_pacman
from generate_socials import generate_all_socials
from generate_projects import generate_projects
from generate_feed import generate_feed
from generate_quote import generate_quote
from github_client import compute_stats, get_contributions


def _step(label, fn, failures):
    """Run one generation step; record (not raise) failures."""
    try:
        fn()
    except Exception as e:
        failures.append((label, e))
        print(f"  ✗ {label} FAILED: {e}")
        traceback.print_exc(limit=1)


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    assets = os.path.abspath(assets)
    os.makedirs(assets, exist_ok=True)
    out = lambda name: os.path.join(assets, name)

    print(f"\n{'=' * 60}")
    print(f"  Generating all assets for @{username}")
    print(f"{'=' * 60}\n")

    failures = []

    # ─── Static assets (no API needed) ───
    print("[1] Banner + Footer...")
    _step("banner", lambda: (
        generate_header("ATS-Dopi", "Cybersecurity Student • CTF Toolbox Builder", out("banner.svg")),
        generate_footer(out("footer.svg"))), failures)

    print("[2] Typing animation...")
    _step("typing", lambda: generate_typing([
        "Cybersecurity Student",
        "CTF Toolbox Developer",
        "Full-Stack Developer",
        "Python | TypeScript | Rust",
    ], out("typing.svg")), failures)

    print("[3] Skills badges...")
    _step("skills", lambda: generate_skills([
        ["Python", "TypeScript", "JavaScript", "C", "C++", "C#", "Java", "PHP", "Rust", "Swift", "Kotlin"],
        ["HTML5", "React", "Next.js", "Node.js", "Electron", "WordPress", "Android"],
        ["MySQL", "PostgreSQL", "Firebase", "Docker", "PowerShell"],
        ["Figma", "Photoshop", "Lightroom", "After Effects", "Arduino"],
    ], out("skills.svg")), failures)

    print("[4] Status badges...")
    _step("badges", lambda: generate_badges([
        ("Status", "Online", "#00d4ff"),
        ("Focus", "CTF & Security", "#a333d8"),
        ("Role", "Student", "#7287fd"),
    ], out("badges.svg")), failures)

    print("[5] Social badges...")
    _step("socials", lambda: generate_all_socials(assets), failures)

    print("[6] Quote of the day...")
    _step("quote", lambda: generate_quote(out("quote.svg")), failures)

    # ─── API-dependent assets (single fetch, shared) ───
    print("\n  Fetching GitHub data (this may take a few seconds)...")
    stats = None
    contribs = None
    try:
        stats = compute_stats(username)
        contribs = stats["contributions"]
    except Exception as e:
        print(f"  ! GitHub stats fetch failed: {e} — API cards keep previous data")
        try:
            contribs = get_contributions(username)
        except Exception as e2:
            print(f"  ! contributions fetch failed too: {e2}")

    if stats:
        print("[7] Stats card + Top languages...")
        _step("stats", lambda: generate_stats_card(stats, out("stats.svg")), failures)
        _step("top-langs", lambda: generate_top_langs(stats, out("top-langs.svg")), failures)

        print("[8] Trophies...")
        _step("trophies", lambda: generate_trophies(stats, out("trophies.svg")), failures)

        print("[9] Featured projects...")
        _step("projects", lambda: generate_projects(username, assets), failures)

    if contribs:
        print("[10] Streak card...")
        _step("streak", lambda: generate_streak(username, out("streak.svg"), contribs), failures)

        print("[11] Activity graph...")
        _step("activity-graph", lambda: generate_activity_graph(username, out("activity-graph.svg"), contribs), failures)

        print("[12] Contribution heatmap...")
        _step("contributions", lambda: generate_contributions(username, out("contributions.svg"), contribs), failures)

        print("[13] Pac-Man animation...")
        _step("pacman", lambda: generate_pacman(username, out("pacman.svg"), contribs), failures)

    print("[14] Recent activity feed...")
    _step("feed", lambda: generate_feed(username, out("feed.svg")), failures)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"  ⚠ Done with {len(failures)} failure(s): {', '.join(l for l, _ in failures)}")
        print("  Failed assets keep their previous version on disk.")
    else:
        print("  ✅ All assets generated in /assets/")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
