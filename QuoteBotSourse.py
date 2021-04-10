import QuoteRepos
from aiogram import Bot, Dispatcher, executor, types
import random

quotes_comments = [
    "Вот что мы нашли:",
    "Как ловко сказанно:",
    "Смотрите что мы нашли!",
    "Прям в точку...",
    "Это то что мы искали!",
    "Вы просто прочитайте это...",
    "Вот! Отличная цитата:",
    "Смотрите как повезло:"
]


async def send_hello(message: types.Message):
    await message.answer(text="*Ура!*\nВы успешно подписались на этого бота!\nДавайте начнем c /help, или поищем что-то интересное - /random", reply_markup=get_menu_buttons())


async def send_random_list(message: types.Message):
    quote = await QuoteRepos.get_random_present()
    text = quote['text']
    picture = quote['picture']
    await message.answer(text=f'_{random.choice(quotes_comments)}_\n{text}[⁯]({picture})', reply_markup=get_move_buttons(query="random"))


async def send_main_menu(message: types.Message):
    await message.answer(text="*Главное меню:*", reply_markup=get_menu_buttons())


async def send_random(message: types.Message):
    quote = await QuoteRepos.get_random_present()
    text = quote['text']
    picture = quote['picture']
    await message.answer(text=f'_{random.choice(quotes_comments)}_\n{text}[⁯]({picture})', reply_markup=get_menu_button())
    

async def send_search_list(message: types.Message):
    try:
        quotes = await QuoteRepos.search(message.text)
    except QuoteRepos.SearchError as err:
        await message.answer(f"_Ничего не найдено по запросу_ *'{err.message}'*", reply_markup=get_menu_buttons())
        return
    keyboard = get_move_buttons(query=message.text, is_last=len(quotes) < 1)
    await message.answer(text=f'_{random.choice(quotes_comments)}_\n*{quotes[0]}{1}/{len(quotes)}*', reply_markup=keyboard)


async def click_main_menu(message: types.Message):
    await message.edit_text(text="*Главное меню:*", reply_markup=get_menu_buttons())


async def click_random(message: types.Message):
    quote = await QuoteRepos.get_random_present()
    text = quote['text']
    picture = quote['picture']
    await message.edit_text(text=f'_{random.choice(quotes_comments)}_\n*"{quote["text"]}"* [⁯]({quote["picture"]})', reply_markup=get_move_buttons("random", id=0, is_last=False))


async def click_search_list(message: types.Message):
    try:
        quotes = await QuoteRepos.search(message.text)
    except QuoteRepos.SearchError as err:
        await message.edit_text(f'_Ничего не найдено по запросу_ *"{err.message}"*', reply_markup=get_menu_buttons())
        return
    keyboard = get_move_buttons(query=message.text, is_last=len(quotes) < 1)
    await message.edit_text(f"_{random.choice(quotes_comments)}_\n{quotes[0]}", reply_markup=keyboard)


async def click_search(message: types.Message):
    await message.edit_text(text="Чтобы начать посик, напишите мне пару ключевых слов.\n_Например: солнце_", reply_markup=get_menu_buttons())


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
    if query == "random":
        await click_random(call.message)
        return
    id = int(args[1])
    if direction == "back":
        id -= 1
    elif direction == "next":
        id += 1
    quotes = await QuoteRepos.search(query)
    keyboard = get_move_buttons(query=query, id=id, is_last=len(quotes)-1 == id)
    await call.message.edit_text(f'_{random.choice(quotes_comments)}_\n*"{quotes[id]}"*\n_{id+1}/{len(quotes)}_')
    await call.message.edit_reply_markup(keyboard)
