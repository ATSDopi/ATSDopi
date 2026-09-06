"""
Shared GitHub API client.
Fetches user profile, repos, and contribution calendar data
via REST and GraphQL APIs.
"""

import os
import requests

GITHUB_REST = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"


def _get_token():
    """Retrieve GitHub token from env (set by GitHub Actions or user)."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _headers():
    token = _get_token()
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def get_user(username):
    """Fetch user profile info via REST."""
    r = requests.get(f"{GITHUB_REST}/users/{username}", headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def get_repos(username, max_pages=10):
    """Fetch all public repos via REST (paginated)."""
    repos = []
    for page in range(1, max_pages + 1):
        r = requests.get(
            f"{GITHUB_REST}/users/{username}/repos",
            headers=_headers(),
            params={"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
    return repos


def get_contributions(username):
    """
    Fetch the full contribution calendar via GraphQL.
    Returns a list of dicts: {date, contributionCount, color, weekday, ...}
    """
    token = _get_token()
    if not token:
        # Fallback: try REST endpoint that returns contribution data
        # This is a best-effort scrape of the public calendar page
        return _scrape_contributions(username)

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            colors
            weeks {
              contributionDays {
                contributionCount
                date
                color
                weekday
              }
            }
          }
        }
      }
    }
    """
    r = requests.post(
        GITHUB_GRAPHQL,
        json={"query": query, "variables": {"login": username}},
        headers=_headers(),
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return _scrape_contributions(username)

    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            days.append(day)
    return {
        "total": cal["totalContributions"],
        "colors": cal["colors"],
        "days": days,
    }


def _scrape_contributions(username):
    """
    Fallback: scrape the contribution calendar from the public HTML page.
    This works without a token but is less reliable.
    """
    import re
    r = requests.get(f"https://github.com/{username}", timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    html = r.text

    # Extract contribution counts from the data-count attributes
    pattern = r'data-date="([^"]+)"[^>]*data-count="(\d+)"[^>]*data-level="(\d+)"'
    matches = re.findall(pattern, html)
    if not matches:
        # Try alternate pattern
        pattern2 = r'data-count="(\d+)"[^>]*data-date="([^"]+)"'
        matches2 = re.findall(pattern2, html)
        if matches2:
            days = []
            for count, date in matches2:
                days.append({
                    "date": date,
                    "contributionCount": int(count),
                    "color": "#216e39" if int(count) > 0 else "#161b22",
                    "weekday": 0,
                })
            return {"total": sum(d["contributionCount"] for d in days), "colors": [], "days": days}
        return {"total": 0, "colors": [], "days": []}

    days = []
    for date, count, level in matches:
        levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
        days.append({
            "date": date,
            "contributionCount": int(count),
            "color": levels[int(level)] if int(level) < len(levels) else "#39d353",
            "weekday": 0,
        })
    return {"total": sum(d["contributionCount"] for d in days), "colors": [], "days": days}


def compute_stats(username):
    """
    Compute aggregate stats: total stars, forks, commits (from contributions),
    PRs, issues, repos, followers.
    """
    user = get_user(username)
    repos = get_repos(username)

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    total_repos = len(repos)

    # Count languages
    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    # Get contribution total
    contribs = get_contributions(username)
    total_commits = contribs["total"]

    return {
        "username": username,
        "name": user.get("name") or username,
        "bio": user.get("bio") or "",
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "total_repos": total_repos,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_commits": total_commits,
        "created_at": user.get("created_at", ""),
        "languages": lang_counts,
        "contributions": contribs,
    }


if __name__ == "__main__":
    import sys
    user = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    stats = compute_stats(user)
    for k, v in stats.items():
        if k != "contributions":
            print(f"  {k}: {v}")
    print(f"  contribution days: {len(stats['contributions']['days'])}")
