from aiogram import types, executor, Bot, Dispatcher
from tbot.secret_key_bot import BOT_SECRET_KEYS
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from runners.constants import postgresql

storage = MemoryStorage()
bot = Bot(BOT_SECRET_KEYS['TELEBOT_ID'])
dp = Dispatcher(bot, storage=storage)


class FilterStatesGroup(StatesGroup):
    city = State()
    lowprice = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=
    [
        [KeyboardButton('/SetUpFilter'), KeyboardButton('/help')]
    ])

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton('/cancel')]
])


@dp.message_handler(commands=['start'])
async def start_cmd_handler(message: types.Message):
    await message.answer('Bot works', reply_markup=kb)

@dp.message_handler(commands=['help'])
async def help_cmd_handler(message: types.Message):
    await message.answer('Нажмите кнопку SetUpFilter для того, чтобы настроить фильтр '
                        'объявлений, которые будут к Вам приходить')


@dp.message_handler(commands=['SetUpFilter'])
async def setup_cmd_handler(message: types.Message):
    await message.answer('Напиши название города', reply_markup=cancel_kb)
    await FilterStatesGroup.city.set()

@dp.message_handler(state=FilterStatesGroup.city)
async def city_state_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    inl_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=
                                  [
                                      [InlineKeyboardButton(text="Все", callback_data='0'),
                                       InlineKeyboardButton(text="Только ниже рынка", callback_data='1')]
                                  ])
    await message.answer("А теперь выбери, хочешь ли ты видеть все объявления или только те,"
                         " что ниже рыночной стоиомости?", reply_markup=inl_kb)
    await FilterStatesGroup.next()


@dp.callback_query_handler(state=FilterStatesGroup.lowprice)
async def lowprice_sate_habndler(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data == '0':
            data['lowprice'] = False
        else:
            data['lowprice'] = True
        dc = {'userid': callback.from_user.id, 'city': data['city'], 'lowprice': data['lowprice']}
        postgresql.add_filter(dc)
        await bot.send_message(callback.from_user.id, text=f" City = {data['city']}, PriceFlag = {data['lowprice']}",
                               reply_markup=kb)
    await state.finish()


@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.reply('Вы прервали создание фильтра',
                        reply_markup=kb)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
