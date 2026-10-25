"""
Check that the frontend is wired to the backend.

For every page, verifies that:
  * each element ID that static/terminal.js writes to exists in that page;
  * each /api/... URL that terminal.js (or a page) calls is a real route in app.py.

Run from the project root:
    python scripts/check_frontend_wiring.py

Exits with status 1 when anything is unwired.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
APP = ROOT / "app.py"

# terminal.js section header -> page it drives
SECTION_PAGES = {
    "1. OVERVIEW": "index.html",
    "2. INGESTION": "ingestion.html",
    "3. STATIC": "risk.html",
    "4. VOLATILITY": "volatility.html",
    "5. MONTE CARLO": "monte_carlo.html",
}

# Ids written by the shared helpers (sidebar, toasts) live on every page.
SHARED_PAGES = ["index.html", "ingestion.html", "risk.html", "volatility.html", "monte_carlo.html"]

ID_CALL = re.compile(r"""(?:getElementById|setText|setSvg)\(\s*["']([A-Za-z0-9_-]+)["']""")
ID_ATTR = r'id="{}"'
# Prefix-built ids such as `${elPrefix}-mae` in the volatility section.
VOL_IDS = [f"{prefix}-{metric}" for prefix in ["vol-rolling", "vol-ewma", "vol-garch", "vol-lstm"]
           for metric in ["mae", "rmse", "corr"]]
VOL_IDS += ["latest-garch-forecast", "latest-lstm-forecast"]
MC_IDS = ["mc-mean-value", "mc-mean-pct", "mc-median-value", "mc-median-pct", "mc-p95-value",
          "mc-p95-pct", "mc-var-value", "mc-var-pct", "mc-cvar-value", "mc-cvar-pct",
          "mc-worst-value", "mc-worst-pct", "scenarios-container"]


def route_paths():
    text = APP.read_text(encoding="utf-8")
    return set(re.findall(r'@app\.(?:get|post)\("([^"]+)"', text))


def split_sections(js):
    """Map each section header to the JS text that follows it."""
    sections = {}
    current = None
    for line in js.splitlines():
        match = re.match(r"\s*// (\d\. [A-Z ]+)", line)
        if match:
            current = next((k for k in SECTION_PAGES if match.group(1).startswith(k)), None)
            continue
        if current:
            sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def html_for(page):
    return (STATIC / page).read_text(encoding="utf-8")


def main():
    js = (STATIC / "terminal.js").read_text(encoding="utf-8")
    routes = route_paths()
    problems = []

    # 1. Element ids per page.
    sections = split_sections(js)
    for section, page in SECTION_PAGES.items():
        body = sections.get(section, "")
        ids = set(ID_CALL.findall(body))
        if section == "4. VOLATILITY":
            ids.update(VOL_IDS)
        if section == "5. MONTE CARLO":
            ids.update(MC_IDS)
        page_html = html_for(page)
        for element_id in sorted(ids):
            if ID_ATTR.format(element_id) not in page_html:
                problems.append(f"{page}: missing id=\"{element_id}\" (used by terminal.js)")

    # The sidebar aggregate equity is filled by terminal.js wherever the block exists.
    for page in SHARED_PAGES:
        page_html = html_for(page)
        if "Aggregate Equity" in page_html and ID_ATTR.format("nav-equity") not in page_html:
            problems.append(f"{page}: sidebar shows Aggregate Equity but has no id=\"nav-equity\"")

    # The user-facing page: its script and markup must agree.
    home_js = (STATIC / "home.js").read_text(encoding="utf-8")
    home_html = html_for("home.html")
    for element_id in sorted(set(re.findall(r'\$\("([A-Za-z0-9_-]+)"\)', home_js))
                             | set(re.findall(r'setText\("([A-Za-z0-9_-]+)"', home_js))
                             | set(re.findall(r'getElementById\("([A-Za-z0-9_-]+)"\)', home_js))
                             | set(re.findall(r'setSvg\("([A-Za-z0-9_-]+)"', home_js))):
        if ID_ATTR.format(element_id) not in home_html:
            problems.append(f"home.html: missing id=\"{element_id}\" (used by home.js)")

    # 2. API URLs called from the frontend must exist as routes.
    api_calls = set(re.findall(r'["\'](/api/[A-Za-z0-9/_-]+)["\']', js))
    api_calls.update(re.findall(r'["\'](/api/[A-Za-z0-9/_-]+)["\']', home_js))
    for page in SECTION_PAGES.values():
        api_calls.update(re.findall(r'["\'](/api/[A-Za-z0-9/_-]+)["\']', html_for(page)))
    for call in sorted(api_calls):
        if call not in routes:
            problems.append(f"frontend calls {call} but app.py has no such route")

    # 3. Routes the pages link to must exist.
    for page in SHARED_PAGES + ["kinetix.html"]:
        for href in re.findall(r'href="(/[a-z-]*)"', html_for(page)):
            if href not in routes and href != "/":
                problems.append(f"{page}: link to {href} has no route")

    if problems:
        print(f"{len(problems)} wiring problem(s):")
        for problem in problems:
            print("  -", problem)
        return 1

    print("Frontend is wired: all element ids and API routes resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
