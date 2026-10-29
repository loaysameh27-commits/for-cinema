import datetime
import time
import requests
from bs4 import BeautifulSoup

# --- بيانات البوت الخاصة بك ---
BOT_TOKEN = "9105331830:AAFrnY5EYjpCbs8VlQ7TuJqw-rczJcaQCco"
CHAT_ID = "5050317718"

URL = "https://district5.scenecinemas.com/"

# قائمة الأفلام المطلوب مراقبتها
TARGET_MOVIES = {
    "dune": "Dune 3",
    "doomsday": "Avengers: Doomsday"
}

CHECK_INTERVAL_SECONDS = 120  # الفحص كل دقيقتين
notified_movies = set()  # لتسجيل الفيلم اللي تم إرسال تنبيه له لمنع التكرار


def send_telegram(message: str):
    """إرسال إشعار فوري إلى تليجرام"""
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
        print(f"[!] خطأ في إرسال التليجرام: {e}")
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
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] كود الاستجابة: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(separator=" ").lower()

        found = []
        for keyword, movie_name in TARGET_MOVIES.items():
            if keyword in page_text and keyword not in notified_movies:
                found.append((keyword, movie_name))

        return found

    except requests.RequestException as err:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] تعذر الاتصال بالموقع: {err}")

    return []


def main():
    print("[*] تم بدء تشغيل السكربت لمراقبة الفيلمين (Dune & Doomsday)...")

    test_msg = "✅ *تم تفعيل البوت!*\nسأقوم بإرسال إشعار بمجرد توفر تذاكر Dune 3 أو Avengers: Doomsday في ديسكت 5."
    if send_telegram(test_msg):
        print("[+] تم إرسال رسالة التأكيد على تليجرام.")
    else:
        print("[!] تأكد من الضغط على Start داخل شات البوت على تليجرام.")

    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        found_movies = check_for_movies()

        for keyword, movie_name in found_movies:
            alert = (
                f"🚨 *الحق يا صاحبي! تذاكر {movie_name} نزلت في ديسكت 5!*\n\n"
                "ادخل احجز فوراً من الرابط:\n"
                f"{URL}"
            )
            send_telegram(alert)
            notified_movies.add(keyword)
            print(f"[{timestamp}] تم العثور على {movie_name} وإرسال التنبيه!")

        # إذا نزل الفيلمين خلاص، يوقف البرنامج
        if len(notified_movies) == len(TARGET_MOVIES):
            print("[*] تم نزول جميع الأفلام المحددة، إنهاء السكربت.")
            break

        print(f"[{timestamp}] جاري المراقبة.. الفحص القادم بعد دقيقتين.")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()