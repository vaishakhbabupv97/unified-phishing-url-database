import requests
from urllib.parse import urlparse
from datetime import datetime
import os

# ==============================
# CONFIGURATION
# ==============================

FEEDS = {
    "openphish": "https://openphish.com/feed.txt",
    "urlabuse": "https://urlabuse.com/public/phishing_recent.txt",
    "urlhaus": "https://urlhaus.abuse.ch/downloads/text/",
    "phishing_database_active": "https://raw.githubusercontent.com/Phishing-Database/Phishing.Database/master/phishing-links-ACTIVE.txt"
}

TIMEOUT = 30

# ==============================
# HELPERS
# ==============================

def normalize_url(url):
    try:
        url = url.strip()
        if not url:
            return None, None

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path

        if domain.startswith("www."):
            domain = domain[4:]

        full_url = domain + path
        return domain, full_url

    except Exception:
        return None, None


def ensure_dirs():
    os.makedirs("feeds", exist_ok=True)
    os.makedirs("merged", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)

# ==============================
# MAIN LOGIC
# ==============================

def main():
    ensure_dirs()

    all_domains = set()
    all_urls = set()

    for name, url in FEEDS.items():
        print(f"[+] Fetching {name}")

        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()

            lines = response.text.splitlines()

            with open(f"feeds/{name}.txt", "w", encoding="utf-8") as f:
                f.write(response.text)

            for line in lines:
                domain, full_url = normalize_url(line)
                if domain:
                    all_domains.add(domain)
                if full_url:
                    all_urls.add(full_url)

        except Exception as e:
            print(f"[!] Failed to fetch {name}: {e}")

    # Write merged outputs
    with open("merged/phishing_domains.txt", "w", encoding="utf-8") as f:
        for d in sorted(all_domains):
            f.write(d + "\n")

    with open("merged/phishing_urls.txt", "w", encoding="utf-8") as f:
        for u in sorted(all_urls):
            f.write(u + "\n")

    # Metadata
    with open("metadata/last_updated.txt", "w") as f:
        f.write(datetime.utcnow().isoformat() + "Z")

    print("[✓] Update completed successfully")
    print(f"[✓] Domains: {len(all_domains)}")
    print(f"[✓] URLs: {len(all_urls)}")


if __name__ == "__main__":
    main()
