"""Spider public evecount repositories with GitHub Pages enabled and generate docs/catalog.md."""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

API_BASE = "https://api.github.com/users/evecount/repos?per_page=100&page="
OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "catalog.md"

FEATURED_REPOS = {
    "expansive_tokenization",
    "text_classification_by_audience",
    "diffusion_model_oops_britney",
    "Coordinate_Index-Based-Sparse-Adapter-Compression",
    "quantum_rotation",
    "milkyways_NASA",
    "Flothink",
    "lecturesinplace",
    "quantum-at-work",
    "evecount_qrotate",
    "qshift_lab",
}


def fetch_repos() -> list[dict]:
    repos: list[dict] = []
    headers = {"User-Agent": "evecount-workshops-spider"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for page in (1, 2, 3):
        req = urllib.request.Request(f"{API_BASE}{page}", headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            batch = json.loads(resp.read().decode("utf-8"))
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    return repos


def build_table(items: list[dict]) -> list[str]:
    lines = [
        "| Repository | Live Site | Description |",
        "| :--- | :--- | :--- |",
    ]
    for r in items:
        name = r["name"]
        repo_url = r["html_url"]
        pages_url = f"https://evecount.github.io/{name}/"
        desc = (r.get("description") or "Open-source workshop & research repository.").replace("|", "\\|").strip()
        lines.append(f"| [`{name}`]({repo_url}) | [Live Site →]({pages_url}) | {desc} |")
    return lines


def main() -> None:
    all_repos = fetch_repos()
    pages_repos = [
        r for r in all_repos
        if r.get("has_pages") and r["name"].lower() != "workshops"
    ]
    pages_repos.sort(key=lambda r: r["name"].lower())

    featured = [r for r in pages_repos if r["name"] in FEATURED_REPOS]
    others = [r for r in pages_repos if r["name"] not in FEATURED_REPOS]

    out: list[str] = [
        "# Live Repository Index (Auto-Spidered)",
        "",
        f"Automatically indexed **{len(pages_repos)}** public `evecount` repositories with GitHub Pages enabled.",
        "",
        "## Featured Workshop & Research Sites",
        "",
        *build_table(featured),
        "",
        "## All Other Live `evecount.github.io` Sites",
        "",
        *build_table(others),
        "",
    ]

    OUT_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {len(pages_repos)} repositories to {OUT_PATH}")


if __name__ == "__main__":
    main()
