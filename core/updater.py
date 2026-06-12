import re
import requests

GITHUB_OWNER = "effesessa"
GITHUB_REPO = "credentials-jenkins-decryptor"

LATEST_RELEASE_API = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)
RELEASES_PAGE = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

TIMEOUT = 5  # short: the check must never make the app feel slow


def _parse_version(text):
    """'v2.1.3' / '2.1' -> (2, 1, 3). Non-numeric parts are ignored."""
    return tuple(int(n) for n in re.findall(r"\d+", text or ""))


def is_newer(latest, current):
    """True if `latest` is a strictly higher version than `current`.

    Both are zero-padded to the same length so '2.1' and '2.1.0' compare equal
    (otherwise the tuple comparison would flag a phantom update)."""
    a, b = _parse_version(latest), _parse_version(current)
    n = max(len(a), len(b))
    a += (0,) * (n - len(a))
    b += (0,) * (n - len(b))
    return a > b


def check_for_update(current_version):
    """Query GitHub for the latest release.

    Returns {"available": bool, "latest": str | None, "url": str}. On any
    failure (offline, GitHub down, rate-limited, no releases, bad JSON) it
    returns available=False with latest=None and never raises."""
    try:
        resp = requests.get(
            LATEST_RELEASE_API,
            headers={"Accept": "application/vnd.github+json"},
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            return {"available": False, "latest": None, "url": RELEASES_PAGE}
        data = resp.json()
        latest = data.get("tag_name", "")
        if not latest:
            # A release with no tag name is unusable: treat as a failed check
            # ("could not check") rather than a misleading "up to date".
            return {"available": False, "latest": None, "url": RELEASES_PAGE}
        url = data.get("html_url") or RELEASES_PAGE
        return {
            "available": is_newer(latest, current_version),
            "latest": latest,
            "url": url,
        }
    except (requests.RequestException, ValueError):
        return {"available": False, "latest": None, "url": RELEASES_PAGE}
