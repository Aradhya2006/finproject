import requests

BASE_URL = "https://www.nseindia.com"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.8",
    "Referer": "https://www.nseindia.com/report-detail/eq_security",
}

session.headers.update(headers)

# Step 1: Establish an NSE session
session.get(
    f"{BASE_URL}/report-detail/eq_security",
    timeout=30,
)

# Step 2: Request historical equity data
url = f"{BASE_URL}/api/historicalOR/generateSecurityWiseHistoricalData"

params = {
    "symbol": "TCS",
    "series": "EQ",
    "type": "priceVolumeDeliverable",
    "from": "01-01-2015",
    "to": "31-01-2015",
    "csv": "true",
}

response = session.get(
    url,
    params=params,
    timeout=30,
)

print("Status:", response.status_code)
print("URL:", response.url)
print()
print("Content-Type:", response.headers.get("Content-Type"))
print()
print("Response:")
print(response.text[:3000])