from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *


api = "7685742774:AAGT0px4BEPsER9DkfnxEWzDjhaS9_qI1AE"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button0 = KeyboardButton(text='Купить')
kb.add(button1, button2, button0)

kbi = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kbi.add(button3, button4)

# keyboard = InlineKeyboardMarkup(row_width=2)
# button11 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
# button12 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
# button13 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
# button14 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
# keyboard.add(button11, button12, button13, button14)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kbi)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.answer()
    formula_message = "Для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161."
    await call.message.answer(formula_message)


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введите свой возраст(г):")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    await message.answer("Введите свой рост(см):")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    growth = message.text
    await state.update_data(growth=growth)
    await message.answer("Введите свой вес(кг):")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def finish(message: types.Message, state: FSMContext):
    weight = message.text
    await state.update_data(weight=weight)
    data = await state.get_data()
    kcal = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161
    await message.answer(f"Женщине Вашего возраста, веса и роста необходимо потреблять "
                         f"{kcal} ккал в сутки")
    await state.finish()


async def get_all_products():
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    cursor.execute("SELECT title, description, price, image_filename FROM Products")
    all_products = cursor.fetchall()
    connection.close()
    return all_products


@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    all_products = await get_all_products()
    keyboard = InlineKeyboardMarkup(row_width=2)

    for product in all_products:
        title = product[0]
        description = product[1]
        price = product[2]
        image_filename = product[3]

        product_info = f"Название: {title} | Описание: {description} | Цена: {price}"
        button = InlineKeyboardButton(text=title, callback_data=f'product_buying_{title}')
        keyboard.add(button)

        await message.answer(product_info)

        if image_filename:
            image_path = f'files/{image_filename}'
            with open(image_path, "rb") as picture:
                await message.answer_photo(picture)

        await message.answer('Выберите продукт для покупки:', reply_markup=keyboard)


@dp.callback_query_handler(text="product_buying")
async def handle_product_buying(call):
    await send_confirm_message(call)


async def send_confirm_message(call):
    await call.answer("Вы успешно приобрели продукт!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
