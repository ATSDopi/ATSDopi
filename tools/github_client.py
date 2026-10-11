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
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoryContributions
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

    coll = data["data"]["user"]["contributionsCollection"]
    cal = coll["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            days.append(day)
    return {
        "total": cal["totalContributions"],
        "colors": cal["colors"],
        "days": days,
        "commits": coll["totalCommitContributions"],
        "issues": coll["totalIssueContributions"],
        "pull_requests": coll["totalPullRequestContributions"],
        "reviews": coll["totalPullRequestReviewContributions"],
        "repos_created": coll["totalRepositoryContributions"],
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
    return {"total": sum(d["contributionCount"] for d in days), "colors": [], "days": days,
            "commits": 0, "issues": 0, "pull_requests": 0, "reviews": 0, "repos_created": 0}


def get_pinned_repos(username, count=4):
    """
    Fetch the user's pinned repositories via GraphQL.
    Falls back to the top public non-fork repos by stars if pinning data
    is unavailable (no token) or there are fewer than `count` pins.
    """
    pinned = []
    token = _get_token()
    if token:
        query = """
        query($login: String!) {
          user(login: $login) {
            pinnedItems(first: 6, types: REPOSITORY) {
              nodes {
                ... on Repository {
                  name
                  description
                  url
                  stargazerCount
                  forkCount
                  primaryLanguage { name color }
                }
              }
            }
          }
        }
        """
        try:
            r = requests.post(
                GITHUB_GRAPHQL,
                json={"query": query, "variables": {"login": username}},
                headers=_headers(),
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            nodes = (data.get("data") or {}).get("user", {}).get("pinnedItems", {}).get("nodes", [])
            for n in nodes:
                pinned.append(_normalize_repo(n))
        except Exception as e:
            print(f"  ! pinnedItems query failed ({e}) — falling back to top repos")

    pinned_names = {p["name"].lower() for p in pinned}
    repos = []
    if len(pinned) < count:
        # Fill remaining slots with top-starred public repos (not already pinned,
        # not forks, not the profile README repo itself)
        candidates = sorted(
            (r for r in get_repos(username)
             if not r.get("fork") and r["name"].lower() != username.lower()
             and r["name"].lower() not in pinned_names),
            key=lambda r: (
                r.get("stargazers_count", 0),
                r.get("description") is not None,
                r.get("updated_at") or "",
            ),
            reverse=True,
        )
        for r in candidates:
            if len(pinned) + len(repos) >= count:
                break
            repos.append({
                "name": r["name"],
                "description": r.get("description"),
                "url": r["html_url"],
                "stargazerCount": r.get("stargazers_count", 0),
                "forkCount": r.get("forks_count", 0),
                "primaryLanguage": {"name": r["language"], "color": None} if r.get("language") else None,
            })
    return (pinned + repos)[:count]


def _normalize_repo(node):
    """Normalize a GraphQL repository node into a plain dict."""
    return {
        "name": node["name"],
        "description": node.get("description"),
        "url": node["url"],
        "stargazerCount": node.get("stargazerCount", 0),
        "forkCount": node.get("forkCount", 0),
        "primaryLanguage": node.get("primaryLanguage"),
    }


def get_public_events(username, max_events=20):
    """Fetch recent public events via REST (PushEvent, CreateEvent, etc.)."""
    r = requests.get(
        f"{GITHUB_REST}/users/{username}/events/public",
        headers=_headers(),
        params={"per_page": max_events},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


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

    # Get contribution totals (GraphQL adds per-type counters when a token exists)
    contribs = get_contributions(username)

    return {
        "username": username,
        "name": user.get("name") or username,
        "bio": user.get("bio") or "",
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "total_repos": total_repos,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_commits": contribs.get("commits") or contribs["total"],
        "total_contributions": contribs["total"],
        "total_prs": contribs.get("pull_requests", 0),
        "total_issues": contribs.get("issues", 0),
        "total_reviews": contribs.get("reviews", 0),
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
