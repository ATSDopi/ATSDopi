"""
Splice generated link fragments into README.md between HTML markers.

The SVG cards can't carry links (they're embedded as <img>), so the README
wraps each card in an <a>. Those hrefs used to be hardcoded and went stale
whenever the pinned repos or social list changed — this keeps them synced.

Markers:
  <!-- PROJECT_CARDS:START --> ... <!-- PROJECT_CARDS:END -->
  <!-- SOCIALS:START -->       ... <!-- SOCIALS:END -->
"""

import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SECTIONS = {
    "PROJECT_CARDS": "assets/projects-fragment.html",
    "SOCIALS": "assets/socials-fragment.html",
}


def update_readme(root=ROOT):
    readme_path = os.path.join(root, "README.md")
    with open(readme_path, encoding="utf-8") as f:
        readme = f.read()

    changed = False
    for marker, frag_rel in SECTIONS.items():
        frag_path = os.path.join(root, frag_rel)
        if not os.path.exists(frag_path):
            print(f"  ! fragment missing, section skipped: {frag_rel}")
            continue
        fragment = open(frag_path, encoding="utf-8").read().strip("\n")

        pattern = re.compile(
            rf"(<!--\s*{marker}:START\s*-->).*?(<!--\s*{marker}:END\s*-->)",
            re.DOTALL,
        )
        updated, n = pattern.subn(
            lambda m: m.group(1) + "\n" + fragment + "\n" + m.group(2),
            readme,
            count=1,
        )
        if not n:
            print(f"  ! markers not found in README.md: {marker}")
            continue
        if updated != readme:
            readme = updated
            changed = True

    if changed:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)
        print("  ✓ README.md updated from generated fragments")
    else:
        print("  - README.md already up to date")
    return changed


if __name__ == "__main__":
    update_readme()
