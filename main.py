import asyncio
import logging
import re
from twitter.twitterAPI import API
from db.database import DB
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

bot = Bot(token="6493200218:AAE69gUOVw3Wlf9LI4IknBG_iV6LF_ne3oI")
dp = Dispatcher()


def user_status_text(user_id):
    db = DB()
    user = db.get_user(str(user_id))
    text = f"*Your proxies*: {user['proxy']}\n" \
           f"*Your token*: {user['token']}\n" \
           f"\n" \
           f"*Commands*: \n" \
           f"/proxy <user:passwd@ip:port> - set your proxies\n" \
           f"/token <your-twitter-auth-token> - set your token\n" \
           f"/parse <@username> - parse user's subs"
    return text


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        text=user_status_text(
            user_id=message.from_user.id
        ),
        parse_mode="Markdown"
    )


@dp.message(Command("proxy"))
async def proxy(message: types.Message):
    db = DB()
    prx = message.text.split(' ')[1]
    m = re.fullmatch(r".*:.*@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,6}", prx)
    if m is None:
        await message.answer(
            text="*Invalid format*\n\nPlease send proxy like: _username:password@host:port_",
            parse_mode="Markdown"
        )
        return
    db.set_proxy(
        user_id=str(message.from_user.id),
        proxy=prx
    )
    text = "Success\n" + user_status_text(message.from_user.id)
    await message.answer(
        text=text,
        parse_mode="Markdown"
    )


@dp.message(Command("token"))
async def token(message: types.Message):
    db = DB()
    tok = message.text.split(' ')[1]
    m = re.fullmatch(r".{40}", tok)
    if m is None:
        await message.answer(
            text="*Invalid format*\n\nPlease send token like: _cfd7296c6a1ffa111eb97cad18awaq111111xxxx_",
            parse_mode="Markdown"
        )
        return
    db.set_token(
        user_id=str(message.from_user.id),
        token=tok
    )
    text = "Success\n" + user_status_text(message.from_user.id)
    await message.answer(
        text=text,
        parse_mode="Markdown"
    )


@dp.message(Command("parse"))
async def parse(message: types.Message):
    db = DB()
    username = message.text.split(' ')[1]
    m = re.fullmatch(r"@.*", username)
    if m is None:
        await message.answer(
            text="*Invalid format*\n\nPlease send username like: @username",
            parse_mode="Markdown"
        )
        return

    user = db.get_user(str(message.from_user.id))
    if user['proxy'] is None:
        await message.answer(
            text="*Warning*\n\nPlease set your proxy first",
            parse_mode="Markdown"
        )
        return
    if user['token'] is None:
        await message.answer(
            text="*Warning*\n\nPlease set your token first",
            parse_mode="Markdown"
        )
        return

    proxies = {
        'http': f"http://{user['proxy']}",
        'https': f"http://{user['proxy']}"
    }
    client = API(
        proxies=proxies,
        auth=user['token']
    )
    followings = client.user_followings(
        rest_id=client.user_by_screen_name(
            screen_name=username
        )['rest_id']
    )
    text = '\n'.join(followings)
    await message.answer(text)



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())