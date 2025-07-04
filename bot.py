import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
FILTERS = {
    'RTX 3060': 700,
    'RTX 3060 Ti': 750,
    'RTX 4060': 950,
    'RTX 5060': 1200,
    'RTX 5060 Ti': 1600,
}

bot = Bot(token=TOKEN)

def parse_kufar():
    # простейший парсер, ищущий по страницам
    url = 'https://www.kufar.by/l/computer/video-cards/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []
    for block in soup.select('.styles_wrapper__CfRgk'):
        title = block.select_one('.styles_title__1QyZE')
        price = block.select_one('.styles_price__2Wk5i')
        link = block.select_one('a')
        if not title or not price or not link:
            continue
        title_text = title.text
        price_text = price.text.replace(' ', '').replace('руб.', '').strip()
        try:
            price_val = int(price_text)
        except:
            continue
        href = 'https://www.kufar.by' + link['href']
        for model, threshold in FILTERS.items():
            if model.lower() in title_text.lower() and price_val <= threshold:
                items.append((model, price_val, href))
    return items

def main():
    sent = set()
    while True:
        try:
            found = parse_kufar()
            for model, price, href in found:
                key = f"{model}-{href}"
                if key not in sent:
                    text = f"🚀 {model} за {price} руб\n{href}"
                    bot.send_message(chat_id=CHAT_ID, text=text)
                    sent.add(key)
        except Exception as e:
            print('Error:', e)
        time.sleep(180)  # каждые ~3 минуты

if __name__ == '__main__':
    main()
