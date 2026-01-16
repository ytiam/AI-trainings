import asyncio
import json
import time
from urllib.parse import urlparse

from playwright.async_api import async_playwright


TARGET_URL = "https://tendertiger.co.in/Result/ResultList?searchtext=Netweb%20Tcehnologies%20India%20Private%20Limited"

import json
import csv

INPUT_JSON_FILE = "captured_tendertiger_json.json"
OUTPUT_CSV_FILE = "tendertiger_tenderlist.csv"


def json_to_csv():
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Find the object that contains the TenderList
    tender_list = None

    for item in payload:
        data = item.get("data", {})
        tender_list = data.get("TenderList", None)
        if tender_list is not None:
            break

    if not tender_list:
        print("⚠️ TenderList is empty. CSV will not be created.")
        return

    # Collect all keys across all rows (robust even if some rows have missing keys)
    all_keys = set()
    for row in tender_list:
        all_keys.update(row.keys())

    # Stable ordering (optional: you can customize this)
    fieldnames = sorted(all_keys)

    with open(OUTPUT_CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tender_list)

    print(f"✅ Extracted {len(tender_list)} tenders")
    print(f"✅ Saved CSV to: {OUTPUT_CSV_FILE}")


def looks_like_results_api(url: str) -> bool:
    u = url.lower()

    # These are common patterns for “table data / search results”
    keywords = [
        "result",
        "resultlist",
        "search",
        "tender",
        "tenders",
        "list",
        "filter",
        "pagination",
        "datatable",
        "grid",
        "api",
        "graphql",
    ]

    # Ignore useless stuff
    ignore = [
        ".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2",
        "google", "gtm", "analytics", "doubleclick", "facebook", "hotjar"
    ]

    if any(x in u for x in ignore):
        return False

    return any(k in u for k in keywords)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = await browser.new_context()

        page = await context.new_page()

        found_json_responses = []

        async def on_response(response):
            url = response.url

            if not looks_like_results_api(url):
                return

            try:
                ct = (response.headers.get("content-type") or "").lower()

                # Many sites return JSON but with weird content-type, so we attempt json() anyway
                if "application/json" in ct or "text/json" in ct or "json" in ct:
                    data = await response.json()
                else:
                    # try parse json anyway
                    text = await response.text()
                    text_stripped = text.strip()
                    if not (text_stripped.startswith("{") or text_stripped.startswith("[")):
                        return
                    data = json.loads(text_stripped)

                found_json_responses.append({"url": url, "data": data})

                print("\n✅ JSON API RESPONSE CAPTURED")
                print("URL:", url)
                print("Top-level type:", type(data).__name__)

            except Exception:
                # not JSON or failed to parse
                return

        page.on("response", on_response)

        print("Opening:", TARGET_URL)
        await page.goto(TARGET_URL, wait_until="domcontentloaded")

        # Wait a bit for network calls + dynamic rendering to finish
        await page.wait_for_timeout(8000)

        # Try a small scroll to trigger lazy-load
        await page.mouse.wheel(0, 1200)
        await page.wait_for_timeout(3000)

        # Dump all captured JSON for inspection
        out_file = "captured_tendertiger_json.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(found_json_responses, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Saved captured JSON responses to: {out_file}")
        print(f"Total JSON responses captured: {len(found_json_responses)}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
    time.sleep(3)
    json_to_csv()
