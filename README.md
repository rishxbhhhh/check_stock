# Amul Product Stock Checker

This script automates the process of checking the stock of specific Amul products on their online store and sends alerts via Telegram when a product is in stock.

## Features

- Checks for product availability at a set interval.
- Sends Telegram notifications for in-stock and out-of-stock products.
- Headless browser automation using Selenium.

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

3.  **Configure the script:**

    -   Open `main.py` and edit the following variables:
        -   `PINCODE`: Your area pincode.
        -   `PRODUCT_NAMES`: A list of product names to check.
        -   `REFRESH_INTERVAL`: The time in seconds between each check.

4.  **Set up Telegram Bot:**

    -   Create a new Telegram bot by talking to the [BotFather](https://t.me/BotFather).
    -   Get your bot token and add it to the `send_telegram_alert` function in `main.py`.
    -   Get your chat ID by sending a message to your bot and visiting `https://api.telegram.org/bot<YourBOTToken>/getUpdates`.
    -   Add your chat ID to the `chat_ids` list in the `send_telegram_alert` function.

## Usage

Run the script from your terminal:

```bash
python main.py
```

## How it Works

The script uses `selenium-wire` to intercept network requests made by the Amul website. It specifically looks for a request to `ms.products` which returns a JSON object containing product data. The script then parses this data to check the availability of the products listed in `PRODUCT_NAMES`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
