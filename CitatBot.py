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
    """
    for first time
    if UsersRepos.ensure_subscribe_user(call.message.chat.id):
        await send_admin_on_subscribe(call.message)
    """
    if call.data == "random":
        await click_random(call)
    elif call.data == "menu":
        await click_main_menu(call.message)
    elif call.data == "search":
        await click_search(call.message)
    elif call.data == "save":
        await click_save(call)
    elif call.data == "delete":
        await click_delete(call)
    elif call.data == "saves":
        await click_saves(call.message)
    elif call.data.startswith("move"):
        await move_button_click(call)
    elif call.data == "close_menu":
        await call.message.delete()


@dp.message_handler(content_types=["text"])
async def text_messages(message: types.Message):
    """for first time
    if UsersRepos.ensure_subscribe_user(message.chat.id):
        await send_admin_on_subscribe(message)
    """
    if message.text in commands["start"]:
        await send_hello(message)
    elif message.text in commands["menu"]:
        await send_main_menu(message)
    elif message.text in commands["random"]:
        await send_list(message, "random")
    elif message.text in commands["help"]:
        await send_help(message)
    else:
        await send_list(message, query=message.text)


def start_bot():
    executor.start_polling(dp, skip_updates=True)
