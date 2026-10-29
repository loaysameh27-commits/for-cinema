import datetime
import http.server
import socketserver
import threading
import time
import requests
from bs4 import BeautifulSoup

# --- بيانات البوت ---
BOT_TOKEN = "9105331830:AAFrnY5EYjpCbs8VlQ7TuJqw-rczJcaQCco"
CHAT_ID = "5050317718"

URL = "https://district5.scenecinemas.com/"
TARGET_MOVIES = {
    "dune": "Dune 3",
    "doomsday": "Avengers: Doomsday"
}

CHECK_INTERVAL_SECONDS = 120
notified_movies = set()


# سيرفر ويب بسيط لإبقاء خدمة Render المجانية تعمل
def run_dummy_server():
    class SimpleHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Cinema Bot is running!")

        def log_message(self, format, *args):
            return  # كتم سجلات الويب

    import os
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), SimpleHandler) as httpd:
        httpd.serve_forever()


def send_telegram(message: str):
    endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    try:
        res = requests.post(endpoint, json=payload, timeout=10)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"[!] خطأ تليجرام: {e}")
        return False


def check_for_movies():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    }
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(separator=" ").lower()

        found = []
        for keyword, movie_name in TARGET_MOVIES.items():
            if keyword in page_text and keyword not in notified_movies:
                found.append((keyword, movie_name))
        return found
    except Exception as err:
        print(f"[!] خطأ اتصال: {err}")
        return []


def monitor_loop():
    print("[*] بدأ فحص الموقع...")
    send_telegram("✅ *تم تفعيل البوت على Render مجاناً!*\nجاري مراقبة تذاكر Dune 3 و Avengers: Doomsday.")

    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        found_movies = check_for_movies()

        for keyword, movie_name in found_movies:
            alert = (
                f"🚨 *الحق يا صاحبي! تذاكر {movie_name} نزلت في ديسكت 5!*\n\n"
                f"احجز فوراً من الرابط:\n{URL}"
            )
            send_telegram(alert)
            notified_movies.add(keyword)
            print(f"[{timestamp}] تم إرسال تنبيه: {movie_name}")

        if len(notified_movies) == len(TARGET_MOVIES):
            break

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    # تشغيل مراقبة السينما في خلفية السيرفر
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()

    # تشغيل سيرفر الويب لإرضاء Render
    run_dummy_server()
