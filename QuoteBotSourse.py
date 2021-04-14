import QuoteRepos
from aiogram import Bot, Dispatcher, executor, types
import random
import UsersRepos

quotes_comments = [
    "Вот что мы нашли:",
    "Как метко сказанно:",
    "Смотрите что мы нашли!",
    "Прям в точку...",
    "Это то что мы искали!",
    "Вы просто прочитайте это...",
    "Вот! Отличная цитата:",
    "Смотрите как повезло:"
]


async def send_hello(message: types.Message):
    if UsersRepos.ensure_subscribe_user(message.chat.id):
        await message.answer(
            text="*Ура!*\nВы успешно подписались!\nДавайте начнем - /help\nИли поищем что-то интересное - /random",
            reply_markup=get_menu_buttons())
    else:
        await message.answer(
            text="*Ура!*\nВы уже подписанны!\nДавайте начнем - /help\nИли поищем что-то интересное - /random",
            reply_markup=get_menu_buttons())


async def send_help(message: types.Message):
    await message.answer(text="""
    Этот бот поможет найти цитату на любую тему, для 🌅 фото  в инстаграм ❤️ и других соц. сетях, или просто узнать для себя что-то новое. 🔎

⚒Как пользоваться?

Просто напиши мне пару ключевых слов и я начну поиск!
Например: солнце

✔️Так же используй команды:

/start - Запуск бота 🔌
/menu - Главное меню  🏠
/random - Случайная цитата ♻️
/help - Помощь ✏️

@AlexChous
    """, reply_markup=get_menu_button())


async def send_list(message: types.Message, query: str, id: int = 0):
    header = f"{random.choice(quotes_comments)}\n"
    content = None
    keyboard = None
    picture_url = ""
    list_length = 1
    if query is "random":
        content_dict = await QuoteRepos.get_random()
        content = content_dict["content"]
        themes = content_dict["themes"]
        if themes is not None:
            picture_url = await QuoteRepos.get_picture_by_themes(themes)
        keyboard = get_move_buttons("random")
    elif query == 'saves':
        content_dict = UsersRepos.get_user_saves(message.chat.id)
        content_dict = [i[0] for i in content_dict]
        if len(content_dict) == 0:
            header = "Вы еще ничего не сохранили."
            content = "..."
            keyboard = get_menu_button()
        else:
            content = content_dict[id]
            list_length = len(content_dict)
            keyboard = get_move_buttons(query="saves", id=id, is_last=list_length - 1 == id, saves=True)
    elif query == 'instagram':
        content_dict = QuoteRepos.get_for_instagram()

    else:
        try:
            content_list = await QuoteRepos.search(query)
        except QuoteRepos.SearchError as err:
            await message.answer(f"_Ничего не найдено по запросу_ *'{err.message}'*", reply_markup=get_menu_button())
            return
        content = content_list[id]["content"]
        themes = content_list[id]["themes"]
        if themes is not None:
            picture_url = await QuoteRepos.get_picture_by_themes(themes)
        list_length = len(content_list)
        keyboard = get_move_buttons(query=query, id=id, is_last=list_length - 1 == id)

    if message.from_user.is_bot:
        await message.edit_text(text=f'_{header}_*"{content}"*\n_{id + 1}/{list_length}_[⁯]({picture_url})',
                                reply_markup=keyboard)
    else:
        await message.answer(text=f'_{header}_*"{content}"*\n_{id + 1}/{list_length}_[⁯]({picture_url}',
                             reply_markup=keyboard)


async def send_main_menu(message: types.Message):
    await message.answer(text="*Главное меню:*", reply_markup=get_menu_buttons())


async def click_main_menu(message: types.Message):
    await message.edit_text(text="*Главное меню:*", reply_markup=get_menu_buttons())


async def click_random(call: types.CallbackQuery):
    await call.answer(text="Идет поиск...")
    await send_list(message=call.message, query="random")


async def click_search(message: types.Message):
    await message.edit_text(text="Чтобы начать посик, напишите мне пару ключевых слов.\n_Например: солнце_",
                            reply_markup=get_menu_buttons())


async def click_save(call: types.CallbackQuery):
    await call.answer(text="Сохраняем...")
    content = call.message.text
    content = content.split('"')[1].split('"')[0]
    UsersRepos.add_to_saves(call.message.chat.id, save=content)


async def click_delete(call: types.CallbackQuery):
    await call.answer(text="Удаляем...")
    content = call.message.text
    content = content.split('"')[1].split('"')[0]
    UsersRepos.try_delete_user_save(chat_id=call.message.chat.id, save=content)
    await click_saves(call.message)


async def click_saves(message: types.Message):
    await send_list(message=message, query="saves")


def get_menu_button():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Главное меню", callback_data="menu")
    )
    return keyboard


def get_menu_buttons():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Случайная цитата", callback_data="random"),
        types.InlineKeyboardButton(text="Найти цитату", callback_data="search"),
        types.InlineKeyboardButton(text="Избранное", callback_data="saves"),
        types.InlineKeyboardButton(text="Закрыть это меню", callback_data="close_menu")
    )
    return keyboard


def get_move_buttons(query: str, id: int = 0, is_last: bool = False, saves=False):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if id > 0 and not is_last:
        keyboard.add(types.InlineKeyboardButton(text="Предыдущая", callback_data=f'move_back[{query};{id}]'),
                     types.InlineKeyboardButton(text="Следующая", callback_data=f'move_next[{query};{id}]'))
    elif id > 0:
        keyboard.add(types.InlineKeyboardButton(text="Предыдущая", callback_data=f'move_back[{query};{id}]'))
    elif not is_last:
        keyboard.add(types.InlineKeyboardButton(text="Следующая", callback_data=f'move_next[{query};{id}]'))
    if not saves:
        keyboard.add(types.InlineKeyboardButton(text="Добавить в избранное", callback_data=f"save"))
    else:
        keyboard.add(types.InlineKeyboardButton(text="Убрать из избранных", callback_data="delete"))
    keyboard.add(types.InlineKeyboardButton(text="Главное меню", callback_data="menu"))
    return keyboard


async def move_button_click(call: types.CallbackQuery):
    args = call.data[10:-1].split(";")
    direction = call.data[5:9]
    query = args[0]
    if query == "random":
        await click_random(call)
        return
    id = int(args[1])
    if direction == "back":
        id -= 1
    elif direction == "next":
        id += 1
    await send_list(message=call.message, query=query, id=id)


async def send_admin_on_subscribe(message: types.Message):
    await message.bot.send_message(chat_id=1029619116,
                                   text=f"{message.from_user.full_name} ({message.chat.id}) subscribed!")
