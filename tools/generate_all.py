"""
Master orchestrator — runs all asset generators in sequence.
Usage: python generate_all.py [username]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from generate_banner import generate_header, generate_footer
from generate_typing import generate_typing
from generate_stats import generate_stats_card, generate_top_langs
from generate_streak import generate_streak
from generate_trophies import generate_trophies
from generate_activity import generate_activity_graph
from generate_skills import generate_skills
from generate_badges import generate_badges
from generate_pacman import generate_pacman
from generate_socials import generate_all_socials
from github_client import compute_stats


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Generating all assets for @{username}")
    print(f"{'='*60}\n")

    # ─── Static assets (no API needed) ───
    print("[1/10] Banner + Footer...")
    generate_header("ATS-Dopi", "Cybersecurity Student • CTF Toolbox Builder",
                    os.path.join(assets, "banner.svg"))
    generate_footer(os.path.join(assets, "footer.svg"))

    print("[2/10] Typing animation...")
    generate_typing([
        "Cybersecurity Student",
        "CTF Toolbox Developer",
        "Full-Stack Developer",
        "Python | TypeScript | Rust",
    ], os.path.join(assets, "typing.svg"))

    print("[3/10] Skills badges...")
    generate_skills([
        ["Python", "TypeScript", "JavaScript", "C", "C++", "C#", "Java", "PHP", "Rust", "Swift", "Kotlin"],
        ["HTML5", "React", "Next.js", "Node.js", "Electron", "WordPress", "Android"],
        ["MySQL", "PostgreSQL", "Firebase", "Docker", "PowerShell"],
        ["Figma", "Photoshop", "Lightroom", "After Effects", "Arduino"],
    ], os.path.join(assets, "skills.svg"))

    print("[4/10] Status badges...")
    generate_badges([
        ("Status", "Online", "#00d4ff"),
        ("Focus", "CTF & Security", "#a333d8"),
        ("Role", "Student", "#7287fd"),
    ], os.path.join(assets, "badges.svg"))

    print("[5/10] Social badges (individual)...")
    generate_all_socials(assets)

    # ─── API-dependent assets ───
    print("\n  Fetching GitHub data (this may take a few seconds)...")
    stats = compute_stats(username)

    print("[6/10] Stats card + Top languages...")
    generate_stats_card(stats, os.path.join(assets, "stats.svg"))
    generate_top_langs(stats, os.path.join(assets, "top-langs.svg"))

    print("[7/10] Streak card...")
    generate_streak(username, os.path.join(assets, "streak.svg"))

    print("[8/10] Trophies...")
    generate_trophies(stats, os.path.join(assets, "trophies.svg"))

    print("[9/10] Activity graph...")
    generate_activity_graph(username, os.path.join(assets, "activity-graph.svg"))

    print("[10/10] Pac-Man animation...")
    generate_pacman(username, os.path.join(assets, "snake.svg"))

    print(f"\n{'='*60}")
    print(f"  ✅ All assets generated in /assets/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
