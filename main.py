from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import quote_html
from app import keyboards as kb
from app import database as db
from dotenv import load_dotenv
import os

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(_):
    await db.db_start()
    print('Bot is started!')


class NewOrder(StatesGroup):
    type = State()
    name = State()
    desc = State()
    count = State()
    price = State()    
    photo = State()

stickers = {
    1: 'CAACAgIAAx0CdDFszQADDWSHek6G2Un1QVxrD4ZU3-cPN4TUAALJGwACYljISjMBjnrIS4yQLwQ', #жижка есть вкусная?
    2: 'CAACAgIAAx0CdDFszQADD2SHeoEpit4sGCChgRmgPTLqpvBTAAKeHQACv1_BSsKH40nEFqG-LwQ', #словил гарика
    3: 'CAACAgIAAx0CdDFszQADEWSHeoUAAWC8yc4Q96O8eU5H5FLOrgACUBgAAroFwUoG-YGq-rqihC8E', #вот это жара
    4: 'CAACAgIAAx0CdDFszQADE2SHeotqfBxJCG0GC5iQUHXKkppJAAL_GwACuGfBSsSm_L7UYjHPLwQ', #ярик бочек потик
    5: 'CAACAgIAAx0CdDFszQADFWSHepCtnuzvc9fLIIaANWre-18ZAAKlGQAC8PrJSn_oz0AzJWgKLwQ' #скоро буду
}

temp_msg = None


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await db.cmd_start_db(message.from_user.id)
    await message.answer_sticker(stickers[3])
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Вы авторизовались как администратор!', reply_markup=kb.main_admin)
    else:
        await message.answer(f'{message.from_user.first_name}, добро пожаловать в Твой вейп-шоп!', reply_markup=kb.main)


@dp.message_handler(commands=['id'])
async def cmd_id(message: types.Message):
    await message.answer(f'{message.from_user.id}')


@dp.message_handler(text='Каталог')
async def catalog(message: types.Message):
    await message.answer('Выберите категорию', reply_markup=kb.catalog_list)


@dp.message_handler(text='Корзина')
async def cart(message: types.Message):
    finish_message = 'Ваша корзина:\n\n'
    total_cost = 0
    user_cart = await db.get_cart(message.from_user.id)

    if not user_cart:
        await message.answer(text='Корзина пуста!')
    else:
        user_items = user_cart[0][2].split('|')
        for i in range(1, len(user_items)):        
            item_brand = user_items[i][user_items[i].find('.')+1:]
            item_id = user_items[i][0:user_items[i].find('.')]
            item = await db.get_item(item_brand, item_id)
            finish_message += item[0][1] + '\n'
            total_cost += int(item[0][3])

        confrim = InlineKeyboardMarkup(row_width=1)
        confrim.add(InlineKeyboardButton(text='Оплатить', callback_data= 'pay' + str(user_cart[0][1])))
        confrim.add(InlineKeyboardButton(text='Очистить', callback_data= 'clear' + str(user_cart[0][1])))

        await message.answer(text=finish_message + '\nИтоговая цена: ' + str(total_cost) + 'р.', reply_markup=confrim)


@dp.message_handler(text='Контакты')
async def contacts(message: types.Message):
    await message.answer('Покупать товар у него: @dobryak_k')


@dp.message_handler(text='Админ-панель')
async def contacts(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Вы вошли в админ-панель', reply_markup=kb.admin_panel)
    else:
        await message.reply('Я тебя не понимаю.')

@dp.message_handler(text='Назад')
async def catalog(message: types.Message):
    await message.answer_sticker(stickers[3])
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Вы авторизовались как администратор!', reply_markup=kb.main_admin)
    else:
        await message.answer(f'{message.from_user.first_name}, добро пожаловать в Твой вейп-шоп!', reply_markup=kb.main)


@dp.message_handler(text='Добавить товар')
async def add_item(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await NewOrder.type.set()
        await message.answer('Выберите тип товара', reply_markup=kb.catalog_list)
    else:
        await message.reply('Я тебя не понимаю.')


@dp.callback_query_handler(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer('Напишите название товара', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Напишите описание товара')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.desc)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.answer('Напишите количество товара')
    await NewOrder.next()

@dp.message_handler(state=NewOrder.count)
async def add_item_count(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count'] = message.text
    await message.answer('Напишите цену товара')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.price)
async def add_item_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.answer('Отправьте фотографию товара')
    await NewOrder.next()


@dp.message_handler(lambda message: not message.photo, state=NewOrder.photo)
async def add_item_photo_check(message: types.Message):
    await message.answer('Это не фотография!')


@dp.message_handler(content_types=['photo'], state=NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await db.add_item(state)
    await message.answer('Товар успешно создан!', reply_markup=kb.admin_panel)
    await state.finish()


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Я тебя не понимаю.')


@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    fluids = await db.get_items('fluids')
    fluids1, fluids2, fluids3, fluids4, fluids5, fluids6, fluids7 = map(list, zip(*fluids))
    del fluids2, fluids3, fluids4, fluids5, fluids6, fluids7

    if callback_query.data == 'fluids':
        item_list = InlineKeyboardMarkup(row_width=1)
        for row in fluids:
            item_list.add(InlineKeyboardButton(text=row[1], callback_data=row[0]))
        await bot.send_sticker(chat_id=callback_query.from_user.id, sticker=stickers[1])
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали жидкости', reply_markup=item_list)

    elif callback_query.data == 'atomaizers':
        await bot.send_sticker(chat_id=callback_query.from_user.id, sticker=stickers[2])
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали испарители')
    elif callback_query.data == 'devices':
        await bot.send_sticker(chat_id=callback_query.from_user.id, sticker=stickers[4])
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали устройства')

    elif callback_query.data == 'closed_cart':
            await callback_query.answer('Заказ завершен!')

    elif callback_query.data[:4] == 'cart':
        result = callback_query.data[4:]
        id = result[0:result.find('|')]
        brand = result[result.find('|')+1:]
        await db.add_to_cart(callback_query.from_user.id, id + '.' + brand)
        await callback_query.answer('Товар добавлен в корзину')

    elif callback_query.data[:3] == 'pay':
        result = callback_query.data[3:]

        idname = await bot.get_chat(result)
        named = quote_html(idname.username)

        finish_message = 'Заказ @' + str(named) + '\n\n'
        total_cost = 0
        user_cart = await db.get_cart(result)
        user_items = user_cart[0][2].split('|')
        for i in range(1, len(user_items)):        
            item_brand = user_items[i][user_items[i].find('.')+1:]
            item_id = user_items[i][0:user_items[i].find('.')]
            item = await db.get_item(item_brand, item_id)
            finish_message += item[0][1] + '\n'
            total_cost += int(item[0][3])

        end_cart = InlineKeyboardMarkup(row_width=1)
        end_cart.add(InlineKeyboardButton(text='Завершить заказ', callback_data= 'end' + str(result)))

        global temp_msg 
        temp_msg = await bot.send_message(chat_id=int(os.getenv('ADMIN_ID')), text=finish_message + '\nИтоговая цена: ' + str(total_cost) + 'р.', reply_markup=end_cart)
        await bot.send_sticker(chat_id=callback_query.from_user.id, sticker=stickers[5])
        await callback_query.answer('Заказ отправлен, ожидайте')

    elif callback_query.data[:3] == 'end':
        result = callback_query.data[3:]
        await db.remove_cart(result)

        close_cart = InlineKeyboardMarkup(row_width=1)
        close_cart.add(InlineKeyboardButton(text='Заказ завершен', callback_data= 'closed_cart'))

        await temp_msg.edit_text('Заказ завершен', reply_markup=close_cart)
        await callback_query.answer('Заказ завершен')

    elif callback_query.data[:5] == 'clear':
        result = callback_query.data[5:]
        await db.remove_cart(result)        
        await callback_query.answer('Ваша корзина очищена')


    elif int(callback_query.data) in fluids1:
        item = await db.get_item('fluids', int(callback_query.data))

        add_to_cart = InlineKeyboardMarkup(row_width=1)
        add_to_cart.add(InlineKeyboardButton(text='Добавить в корзину', callback_data= 'cart' + str(item[0][0]) + '|' + str(item[0][6])))

        await bot.send_photo(chat_id=callback_query.from_user.id, photo=item[0][5], 
                             caption=f'<b>{item[0][1]}</b>\n\n{item[0][2]}\n\nСтоимость: <b>{item[0][3]}р.</b>', parse_mode="HTML", reply_markup=add_to_cart)
    
    


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
