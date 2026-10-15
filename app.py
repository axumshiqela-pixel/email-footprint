
import os
import re
from urllib.parse import quote

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CX = os.getenv("GOOGLE_CX", "")
HIBP_KEY = os.getenv("HIBP_API_KEY", "")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "EmailFootprint/1.0"})


def valid_email(value):
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
            r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}"
            r"[A-Za-z0-9])?(?:\.[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+",
            value
        )
    )


def public_search(email):
    results = []

    if not GOOGLE_KEY or not GOOGLE_CX:
        return results

    try:
        response = SESSION.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_KEY,
                "cx": GOOGLE_CX,
                "q": '"' + email + '"',
                "num": 10
            },
            timeout=15
        )
        response.raise_for_status()

        for item in response.json().get("items", []):
            results.append({
                "source": "Public web",
                "title": item.get("title", "Untitled"),
                "url": item.get("link", ""),
                "description": item.get("snippet", ""),
                "evidence": "Public page mentions this email"
            })

    except requests.RequestException:
        pass

    return results


def breach_search(email):
    if not HIBP_KEY:
        return [], "HIBP_API_KEY is not configured"

    try:
        response = SESSION.get(
            "https://haveibeenpwned.com/api/v3/breachedAccount/"
            + quote(email, safe=""),
            headers={
                "hibp-api-key": HIBP_KEY,
                "user-agent": "EmailFootprint/1.0"
            },
            params={"truncateResponse": "false"},
            timeout=20
        )

        if response.status_code == 404:
            return [], None

        if response.status_code == 401:
            return [], "HIBP API key is invalid"

        if response.status_code == 429:
            return [], "HIBP rate limit reached"

        response.raise_for_status()
        results = []

        for breach in response.json():
            name = breach.get("Name", "Unknown breach")
            domain = breach.get("Domain", "")

            results.append({
                "source": "HIBP breach database",
                "title": name,
                "url": (
                    "https://" + domain
                    if domain else
                    "https://haveibeenpwned.com/"
                ),
                "description": (
                    "Breach date: "
                    + str(breach.get("BreachDate", "Unknown"))
                    + " | Exposed data types: "
                    + ", ".join(breach.get("DataClasses", []))
                ),
                "evidence": "Known data breach"
            })

        return results, None

    except requests.RequestException:
        return [], "Could not reach the breach service"


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/check")
def check_email():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip()

    if len(email) > 254 or not valid_email(email):
        return jsonify({"error": "Enter a valid email address"}), 400

    # Only run a lookup after the caller confirms this is their email.
    if data.get("own_email") is not True:
        return jsonify({
            "error": "Confirm that this is your own email address"
        }), 400

    web_results = public_search(email)
    breach_results, breach_error = breach_search(email)

    return jsonify({
        "email": email,
        "results": web_results + breach_results,
        "counts": {
            "public_pages": len(web_results),
            "breaches": len(breach_results)
        },
        "warnings": [
            message for message in [
                (
                    "Google search is not configured"
                    if not GOOGLE_KEY or not GOOGLE_CX else None
                ),
                breach_error
            ] if message
        ]
    })


@app.get("/api/sites")
def list_sites():
    import json
    from pathlib import Path

    path = Path(__file__).with_name("sites.json")

    try:
        with path.open("r", encoding="utf-8") as file:
            sites = json.load(file)
    except (OSError, ValueError):
        return jsonify({"error": "Could not load website list"}), 500

    return jsonify({
        "total": len(sites),
        "sites": [
            {
                "name": site["name"],
                "domain": site["domain"],
                "status": "unknown"
            }
            for site in sites
        ]
    })




@app.route("/api/holehe", methods=["POST"])
def api_holehe():
    import subprocess
    import re
    from flask import request, jsonify

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()

    if data.get("own_email") is not True:
        return jsonify({"error": "Confirm this is your own email."}), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Enter a valid email address."}), 400

    try:
        result = subprocess.run(
            [
                "/data/data/com.termux/files/usr/bin/holehe",
                "--no-clear",
                "--no-color",
                "--no-password-recovery",
                email
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        results = []
        for line in result.stdout.splitlines():
            match = re.match(r"^\s*(\[\+\]|\[-\]|\[x\])\s+(.+)$", line)
            if not match:
                continue

            symbol, site = match.groups()
            status = {
                "[+]": "found",
                "[-]": "not_found",
                "[x]": "unknown"
            }[symbol]

            results.append({"site": site.strip(), "status": status})

        return jsonify({
            "email": email,
            "total": len(results),
            "results": results
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Holehe timed out. Try again."}), 504
    except Exception:
        app.logger.exception("Holehe check failed")
        return jsonify({"error": "Holehe check failed."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
