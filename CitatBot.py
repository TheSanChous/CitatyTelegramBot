from config import API_TOKEN
from aiogram import Bot, Dispatcher, executor, types
from QuoteBotSourse import *

bot = Bot(token=API_TOKEN, parse_mode='Markdown')
dp = Dispatcher(bot)

commands = {
    "start": ["/start", "start"],
    "help": ["/help", "help", "помощь"],
    "menu": ["меню", "Меню", "menu", "/menu"],
    "random": ["/random", "/rand", "random", "случайная цитата", "случайная", "найди любую"]
}


@dp.callback_query_handler(lambda call: True)
async def callback_query(call: types.CallbackQuery):
    if call.data == "random":
        await click_random(call.message)
    elif call.data == "menu":
        await click_main_menu(call.message)
    elif call.data == "search":
        await click_search(call.message)
    elif call.data.startswith("move"):
        await move_button_click(call)


@dp.message_handler(content_types=["text"])
async def text_messages(message: types.Message):
    if message.text in commands["start"]:
        await send_hello(message)
    elif message.text in commands["menu"]:
        await send_main_menu(message)
    elif message.text in commands["random"]:
        await send_random_list(message)
    elif message.text in commands["help"]:
        pass
    else:
        await send_search_list(message)


def start_bot():
    executor.start_polling(dp, skip_updates=True)
