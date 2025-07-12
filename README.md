📦 Check_Stock Monitor — Telegram-Controlled Product Availability Tracker

This project is a Python-based automation tool to monitor stock availability on a certain commodity website and send Telegram alerts in real time. It supports multi-user notifications, bot-controlled pause/resume, out-of-stock filtering, and custom intervals.

🚀 Features
- ✅ Real-time product availability monitoring using Selenium Wire
- ✅ Alerts sent via Telegram to registered users
- ✅ Supports multiple recipients with dynamic opt-in via /addme
- ✅ Toggle monitoring with /start and /stop
- ✅ Suppress out-of-stock spam with /stopoutofstock
- ✅ Resume full alerts with /startoutofstock
- ✅ Update refresh interval with /setinterval <seconds>
- ✅ Clean matching using alias-based lookup (strip() + casefold())
- ✅ Runs in headless mode on lightweight AWS EC2 instances (Amazon Linux Free Tier)
- ✅ Background execution with nohup, tmux, or systemd support
- ✅ No need to install ChromeDriver explicitly when system Chrome is present
- ✅ Easily extensible and modular codebase

📲 Bot Controls
Interact with your Telegram bot to control the monitoring behavior:
1. /start           - to resume all monitoring
2. /stop            - to stop all monitoring
3. /startoutofstock - to resume out of stock monitoring
4. /stopoutofstock  - to stop out of stock monitoring
5. /setinterval     - to set custom interval (e.g. /setinterval 60)
6. /addme           - to add your Telegram ID to alert recipients
7. /removeme        - to remove yourself from alerts

Note: Alerts are sent only to users registered via /addme.

## Prerequisites

- Python 3.x
- Google Chrome

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/rishxbhhhh/check_stock.git
    cd check_stock
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    ```bash
    curl https://intoli.com/install-google-chrome.sh | bash
    ```

3.  **Configure the script:**

    -   Open `main.py` and edit the following variables:
        -   `PINCODE`: Your area pincode. (India)
        -   `PRODUCT_NAMES`: A list of product names to check.
        -   `REFRESH_INTERVAL`: The time in seconds between each check. (You can skip it now and can configure it in running application.)

4.  **Set up Telegram Bot:**

    -   Create a new Telegram bot by talking to the [BotFather](https://t.me/BotFather).
    -   Get your bot token and add it to the .env file in `main.py`.
    -   Start the application and text `/addme` to the bot on telegram.

## Usage

Run the script from your terminal:

```bash
    nohup python3 check_stock/main.py >> stock.log 2>&1 &
```

## How it Works

The script uses `selenium-wire` to intercept network requests made by the respective store website. It specifically looks for a request to `ms.products` which returns a JSON object containing product data. The script then parses this data to check the availability of the products listed in `PRODUCT_NAMES`.

🧩 Feature Breakdown & Implementation Paths
1. 🎛️ User-Specific Alert Preferences
Goal: Each Telegram user can customize the types of alerts they receive.

Sub-features:
- Enable/disable in-stock alerts
- Enable/disable out-of-stock alerts
- Toggle silent notifications
- Add/remove products specific to their preferences
Implementation Path:
- Track each user’s preferences in a dictionary or database:
user_prefs = {
    "1152471448": {
        "in_stock": True,
        "out_of_stock": False,
        "silent": False,
        "products": ["amul-high-protein-milk-250-ml-or-pack-of-8"]
    }
}
- Parse commands like /mysettings, /addproduct, /silents, etc.
- Filter alerts based on each user’s preferences during dispatch.

2. 🔒 Admin-Only Control Features via Bot
Goal: Restrict sensitive commands (e.g. global /stop, /setinterval) to admins only.

Implementation Path:
- Define an ADMIN_CHAT_IDS list:
ADMIN_CHAT_IDS = ["1152471448"]
- Check before executing:
if sender_id in ADMIN_CHAT_IDS:
    # allow control
else:
    send_telegram_alert("❌ You are not authorized to run this command", True)
- Optionally implement /promote <user> and /demote <user> (admin-only)

3. 💾 Persistent Opt-In Tracking via Disk or Database
Goal: Retain users who opt in via /addme and remove via /removeme.

Options:
- 🔹 Text file (recipients.txt or prefs.json)
- 🔹 SQLite database (lightweight, structured, queryable)
Implementation Path:
- On /addme, write chat_id to file/db
- On /removeme, remove chat_id
- Load on startup and update in-memory chat_ids or user_prefs

4. 📊 Web Dashboard for Monitoring
Goal: Visualize product status, user metrics, and system uptime.

Options:
- Flask or FastAPI-based backend with Bootstrap frontend
- Display:
- Current product statuses ✅❌
- Live user list and preferences
- Toggle controls for admins
- Logs of recent alerts
Bonus: Add password protection or Telegram auth for dashboard access.


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
