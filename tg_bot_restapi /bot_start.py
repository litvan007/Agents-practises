import os
import uuid
import asyncio
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = '7804353924:AAEbIpRla77OuD5nkaYpQCHAv9nDEFd0Hgo'
GIGACHAT_AUTH = 'ZTVhYzE5MGEtOWQyZi00MWU3LTg2NDYtMTIyMjYyYzlhMDgwOjk1MjNjMjhkLWM4ZmItNGU3NC1iYzQ4LTFlY2U2NjM5MzFjNQ=='
GIGACHAT_SCOPE = 'GIGACHAT_API_PERS'
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_TOKEN_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
GIGACHAT_MODEL = "GigaChat-2"

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)
chat_history = {}

# HTTP с повторными попытками
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, text='Привет! Я бот на GigaChat. Напиши вопрос или /menu для кнопок.')

@bot.message_handler(commands=['menu'])
async def show_menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('Справка'), types.KeyboardButton('Пример запроса'))
    await bot.send_message(message.chat.id, 'Выберите опцию:', reply_markup=kb)

@bot.message_handler(content_types=['text'])
async def handle_text(message):
    uid = message.chat.id
    text = message.text.strip()

    if text == 'Справка':
        await bot.send_message(uid, 'Я пересылаю ваш вопрос в GigaChat и возвращаю ответ.')
        return
    if text == 'Пример запроса':
        await bot.send_message(uid, 'Например: "Объясни квантовые вычисления простыми словами"')
        return

    history = chat_history.setdefault(uid, [
        {"role": "system", "content": "Ты дружелюбный помощник на русском."}
    ])
    history.append({"role": "user", "content": text})

    try:
        reply = await asyncio.to_thread(generate_response, history)
        history.append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = f"Не удалось получить ответ от GigaChat: {e}"

    await bot.send_message(uid, reply, parse_mode="HTML")


def generate_response(messages: list) -> str:
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {GIGACHAT_AUTH}'
    }
    token_data = f'scope={GIGACHAT_SCOPE}'

    token_resp = session.post(GIGACHAT_TOKEN_URL, headers=token_headers, data=token_data, verify=False, timeout=30)
    token_resp.raise_for_status()
    token = token_resp.json()['access_token']

    api_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        "model": GIGACHAT_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 512,
        "stream": False
    }

    chat_resp = session.post(GIGACHAT_API_URL, headers=api_headers, json=payload, verify=False, timeout=60)
    chat_resp.raise_for_status()
    return chat_resp.json()['choices'][0]['message']['content']


def main():
    asyncio.run(bot.polling(non_stop=True, request_timeout=90))

if __name__ == '__main__':
    main()