from config import API_TOKEN
from aiogram import Bot, Dispatcher, executor, types
import CitatRepos

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

commands = {
    "start": ["/start"],
    "help": ["/help", "help", "помощь"],
    "menu": ["меню", "menu", "/menu"],
    "random": ["/random", "/rand", "random", "случайная цитата", "случайная", "найди любую"]
}


async def send_main_menu(message: types.Message):
    await message.answer(text="Меню", reply_markup=get_menu_buttons())


async def send_random(message: types.Message):
    citat = await CitatRepos.get_random_present()
    text = citat['text']
    picture = citat['picture']
    await message.answer(text=f'{citat["text"]}[⁯]({citat["picture"]})', parse_mode='Markdown', reply_markup=get_menu_button())


async def send_search_list(message: types.Message):
    try:
        citats = await CitatRepos.search(message.text)
    except CitatRepos.SearchError as err:
        await message.answer(f"Ничего не найдено по запросу '{err.message}'", reply_markup=get_menu_buttons())
        return
    keyboard = get_move_buttons(query=message.text, is_last=len(citats) < 1)
    await message.answer(f"Вот что мы нашли по теме {message.text}:{citats[0]}{id+1}/{len(citats)}", reply_markup=keyboard)


async def click_main_menu(message: types.Message):
    await message.edit_text(text="Меню", reply_markup=get_menu_buttons())


async def click_random(message: types.Message):
    citat = await CitatRepos.get_random_present()
    text = citat['text']
    picture = citat['picture']
    await message.edit_text(text=f'{citat["text"]}[⁯]({citat["picture"]})', parse_mode='Markdown', reply_markup=get_menu_button())


async def click_search_list(message: types.Message):
    try:
        citats = await CitatRepos.search(message.text)
    except CitatRepos.SearchError as err:
        await message.edit_text(f"Ничего не найдено по запросу '{err.message}'", reply_markup=get_menu_buttons())
        return
    keyboard = get_move_buttons(query=message.text, is_last=len(citats) < 1)
    await message.edit_text(f"Вот что мы нашли по теме {message.text}:{citats[0]}", reply_markup=keyboard)


def get_menu_button():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Главное меню", callback_data="menu")
    )
    return keyboard


def get_random_menu_buttons():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Случайная цитата", callback_data="random"),
        types.InlineKeyboardButton(text="Главное меню", callback_data="menu")
    )
    return keyboard


def get_menu_buttons():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Случайная цитата", callback_data="random"),
        types.InlineKeyboardButton(text="Найти цитату", callback_data="search")
    )
    return keyboard


def get_move_buttons(query: str, id: int = 0, is_last: bool = False):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if id > 0 and not is_last:
        keyboard.add(types.InlineKeyboardButton(text="Предыдущая", callback_data=f'move_back[{query};{id}]'),
                     types.InlineKeyboardButton(text="Следующая", callback_data=f'move_next[{query};{id}]'))
    elif id > 0:
        keyboard.add(types.InlineKeyboardButton(text="Предыдущая", callback_data=f'move_back[{query};{id}]'))
    elif not is_last:
        keyboard.add(types.InlineKeyboardButton(text="Следующая", callback_data=f'move_next[{query};{id}]'))
    keyboard.add(types.InlineKeyboardButton(text="Главное меню", callback_data="menu"))
    return keyboard


async def move_button_click(call: types.CallbackQuery):
    await call.answer(text="Идет поиск...")
    args = call.data[10:-1].split(";")
    direction = call.data[5:9]
    query = args[0]
    id = int(args[1])
    if direction == "back":
        id -= 1
    elif direction == "next":
        id += 1
    citats = await CitatRepos.search(query)
    keyboard = get_move_buttons(query=query, id=id, is_last=len(citats)-1 == id)
    await call.message.edit_text(f"Вот что мы нашли по теме {query}:{citats[id]}{id+1}/{len(citats)}")
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(lambda call: True)
async def callback_query(call: types.CallbackQuery):
    if call.data == "random":
        await click_random(call.message)
    elif call.data == "menu":
        await click_main_menu(call.message)
    elif call.data.startswith("move"):
        await move_button_click(call)


@dp.message_handler(content_types=["text"])
async def text_messages(message: types.Message):
    if message.text in commands["start"]:
        pass
    elif message.text in commands["menu"]:
        await send_main_menu(message)
    elif message.text in commands["random"]:
        await send_random(message)
    elif message.text in commands["help"]:
        pass
    else:
        await send_search_list(message)


def start_bot():
    executor.start_polling(dp, skip_updates=True)
