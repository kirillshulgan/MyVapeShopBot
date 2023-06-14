from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Каталог').add('Корзина').add('Контакты')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('Каталог').add('Корзина').add('Контакты').add('Админ-панель')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар').add('Удалить товар').add('Сделать рассылку').add('Назад')

catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='Жидкости', callback_data='fluids'),
                 InlineKeyboardButton(text='Испарители', callback_data='atomaizers'),
                 InlineKeyboardButton(text='Устройства', callback_data='devices'))



cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')
