"""Module to check product stock and trigger instant messages through bot with interactive Telegram control."""

import gzip
import json
import os
import time
from datetime import datetime
from io import BytesIO

import pandas as pd
import requests
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

# Load environment variables
load_dotenv()

# Configuration
STORE_URL = "https://shop.amul.com/en"
CATEGORY = ""
PINCODE = os.getenv("PINCODE")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 60))
PRODUCTS = [
    "amul-high-protein-milk-250-ml-or-pack-of-8",
    "amul-high-protein-rose-lassi-200-ml-or-pack-of-30",
    "amul-high-protein-plain-lassi-200-ml-or-pack-of-30",
    "amul-high-protein-blueberry-shake-200-ml-or-pack-of-30",
    "amul-high-protein-buttermilk-200-ml-or-pack-of-30",
    "amul-peanut-butter-creamy-300-g"
]

DUPLICATES = []
MONITORING = True
SEND_OUT_OF_STOCK = True
chat_ids = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
print("REFRESH_INTERVAL: "+str(REFRESH_INTERVAL))
LAST_UPDATE_ID = None

BOT_CONTROLS = ''' ---Welcome to Check_Stock Bot---
1. /start           - to resume all monitoring
2. /stop            - to stop all monitoring
3. /startoutofstock - to resume out of stock monitoring
4. /stopoutofstock  - to stop out of stock monitoring
5. /addme           - to add user to alerts
6. /setinterval     - to set custom interval
'''

def send_telegram_alert(message, disable_notification):
    """Send a Telegram message to multiple recipients."""
    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id.strip(),
            "text": message,
            "disable_notification": disable_notification
        }
        try:
            requests.post(url, data=payload, timeout=10)
        except Exception as e:
            print(f"❌ Failed to send alert to {chat_id}:", e)

def check_telegram_commands():
    """Poll Telegram for control commands."""
    global MONITORING, REFRESH_INTERVAL, chat_ids, LAST_UPDATE_ID, SEND_OUT_OF_STOCK

    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"offset": LAST_UPDATE_ID + 1 if LAST_UPDATE_ID else None}

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        for update in data.get("result", []):
            LAST_UPDATE_ID = update["update_id"]
            message = update.get("message", {}).get("text", "").strip()
            sender_id = str(update.get("message", {}).get("chat", {}).get("id"))

            if not message:
                continue

            if message.lower() == "/stop":
                MONITORING = False
                send_telegram_alert("⏸️ Monitoring paused by user, waiting for /start ...", True)

            elif message.lower() == "/start":
                MONITORING = True
                send_telegram_alert("▶️ Monitoring resumed by user", True)

            elif message.startswith("/setinterval "):
                try:
                    REFRESH_INTERVAL = int(message.split()[1])
                    send_telegram_alert(f"⏱️ Interval set to {REFRESH_INTERVAL}s", True)
                except:
                    send_telegram_alert("❌ Invalid interval format", True)

            elif message.lower() == "/addme":
                if sender_id not in chat_ids:
                    chat_ids.append(sender_id)
                    send_telegram_alert("✅ You’ve been added to the alert list", False)

            elif message.lower() == "/stopoutofstock":
                SEND_OUT_OF_STOCK = False
                send_telegram_alert("🚫 Out-of-stock alerts disabled", True)

            elif message.lower() == "/startoutofstock":
                SEND_OUT_OF_STOCK = True
                send_telegram_alert("✅ Out-of-stock alerts enabled", True)

    except Exception as e:
        print("⚠️ Telegram command check failed:", e)

# Setup browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

try:
    # Step 1: Open page and enter pincode once
    driver.get(STORE_URL + CATEGORY)
    time.sleep(2)

    try:
        pincode_input = driver.find_element(By.ID, "search")
        pincode_input.send_keys(PINCODE)
        time.sleep(2)
        suggestion = driver.find_element(By.XPATH, f"//a[contains(@class, 'searchitem-name')]//p[text()='{PINCODE}']")
        driver.requests.clear()
        suggestion.click()
        print("✅ Pincode selected")
    except Exception as e:
        print("❌ Failed to enter pincode:", e)

    # Step 2: Loop to refresh and check availability
    send_telegram_alert(BOT_CONTROLS, False)
    while True:
        check_telegram_commands()

        if MONITORING:
            product_data = []
            now = datetime.now()
            time_message = "🔍 Product Availability at " + now.strftime("%I:%M:%S %p %Z on %d-%m-%Y")
            print(time_message)
            send_telegram_alert(time_message, True)

            for request in driver.requests:
                if request.response and "ms.products" in request.url:
                    body = request.response.body
                    try:
                        if body[:2] == b'\x1f\x8b':
                            with gzip.GzipFile(fileobj=BytesIO(body)) as f:
                                decompressed = f.read()
                        else:
                            decompressed = body

                        try:
                            data = json.loads(decompressed)
                            product_data = data.get("data", [])

                            if product_data:
                                df = pd.DataFrame(product_data)
                                FILTERED_PRODUCTS = [alias for alias in PRODUCTS if alias not in DUPLICATES]

                                for alias in FILTERED_PRODUCTS:
                                    match = df[df['alias'].str.strip().str.casefold() == alias.strip().casefold()]
                                    if not match.empty:
                                        available = match.iloc[0]['available']
                                        name = match.iloc[0]['name']
                                        DUPLICATES.append(alias)

                                        if available:
                                            STATUS = "✅ In Stock"
                                            URL = STORE_URL + f"/product/{alias}"
                                            SUCCESS_MESSAGE = f"{STATUS} — {name} - Quantity: {available} - Order here {URL}"
                                            print(SUCCESS_MESSAGE)
                                            send_telegram_alert(SUCCESS_MESSAGE, False)
                                        else:
                                            STATUS = "❌ Out of Stock"
                                            FAILURE_MESSAGE = f"{STATUS} — {name} - Quantity: {available}"
                                            print(FAILURE_MESSAGE)
                                            if SEND_OUT_OF_STOCK:
                                                send_telegram_alert(FAILURE_MESSAGE, True)
                                    else:
                                        print(f"⚠️ {alias}: Not found in data")
                            else:
                                print("⚠️ No product data found.")
                        except json.JSONDecodeError as e:
                            print("❌ JSON decoding failed:", e)
                            print("🔍 Raw response preview:", decompressed[:200])
                            continue

                        print(f"\n📦 Refreshed at {time.strftime('%H:%M:%S')} — {len(product_data)} products found")
                    except Exception as e:
                        print("❌ Failed to parse response:", e)

            print(f"⏳ Waiting {REFRESH_INTERVAL} seconds before next refresh...\n")
            time.sleep(REFRESH_INTERVAL)
            DUPLICATES.clear()
            driver.requests.clear()
            driver.refresh()
            time.sleep(2)

finally:
    driver.quit()
