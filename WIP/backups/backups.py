
#!/usr/bin/env python3
# Бот для Зета - РАБОЧАЯ версия с наценкой 150%+
# {на Зета, по запросу Альфы}

from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os
import requests
import json
from datetime import datetime
import random
import re

BOT_TOKEN = "8343993945:AAEOx7nBRhIWKdYakSXsTXS7RrdMdpmxsSo"
GROUP_CHAT_ID = "@fg5htr9khgyr5rgvgbu74"

# Конфигурация CryptoBot API
CRYPTOBOT_API_TOKEN = "478664:AA183lxiXRK06NSmAwdRvT19VjY40ewX5RA"
CRYPTOBOT_API_URL = "https://pay.crypt.bot/api/"

# Переменные для хранения данных
user_cities = {}
user_selections = {}
user_pending_confirmations = {}
user_temporary_data = {}  # Для ФИО и индекса аптеки

# ========== БАЗЫ ДАННЫХ ==========
# Все города
streets = {
    "Москва": ["Тверская", "Арбат", "Новый Арбат", "Пушкинская", "Ленинградский проспект"],
    "Санкт-Петербург": ["Невский проспект", "Литейный проспект", "Васильевский остров"],
    "Псков": ["Советская", "Ленина", "Октябрьский проспект"],
    "Петрозаводск": ["Ленина", "Антикайнена", "Андропова"],
    "Великий Новгород": ["Большая Московская", "Мерецкова-Волосова"],
    "Нижний Новгород": ["Большая Покровская", "Рождественская"],
    "Владивосток": ["Светланская", "Алеутская"],
    "Красноярск": ["Мира", "Карла Маркса"],
    "Екатеринбург": ["Малышева", "8 Марта"],
    "Йошкар-Ола": ["Первомайская", "Комсомольская"],
    "Казань": ["Баумана", "Татарстан"],
    "Калининград": ["Ленинский проспект", "Театральная"],
    "Сергиев Посад": ["Красной Армии", "Вознесенская"],
    "Ярославль": ["Кирова", "Свободы"],
    "Сочи": ["Навагинская", "Кирова"],
    "Коломна": ["Октябрьской Революции", "Ленина"],
    "Элиста": ["Ленина", "Пушкина"],
    "Тобольск": ["Ремезова", "Семена Ремезова"],
    "Выборг": ["Северный Вал", "Выборгская"],
    "Дербент": ["Таги-Заде", "7 Магал"],
    "Тамбов": ["Интернациональная", "Советская"],
    "Новосибирск": ["Ленина", "Советская"],
    "Уфа": ["Ленина", "Центральная"],
    "Самара": ["Куйбышева", "Ленинградская"],
    "Краснодар": ["Красная", "Седина"],
    "Волгоград": ["Ленина", "Мира"],
    "Пермь": ["Ленина", "Куйбышева"],
    "Ростов-на-Дону": ["Большая Садовая", "Темерницкая"],
}

# ТОВАРЫ С НАЦЕНКОЙ 150%+ ⚡
product_info = {
    # Дизайнерские
    "product_mefedron_flour": {"name": "Мефедрон (Мука)", "price": 4200, "file": "meph.jpg", "unit": "гр"},
    "product_mefedron_crystals": {"name": "Мефедрон (Кристаллы)", "price": 4800, "file": "meph.jpg", "unit": "гр"},
    "product_alpha_pvp_flour": {"name": "Альфа-ПвП (Мука)", "price": 4500, "file": "alpha.jpg", "unit": "гр"},
    "product_alpha_pvp_crystals": {"name": "Альфа-ПвП (Кристаллы)", "price": 5000, "file": "alpha.jpg", "unit": "гр"},
    
    # Эйфоретики
    "product_ecstasy": {"name": "Экстази (МДМА)", "price": 2800, "file": "ecstasy.jpg", "unit": "шт"},
    
    # Каннабис
    "product_hashish": {"name": "Гашиш ICE-O-LATOR", "price": 3800, "file": "hashish.jpg", "unit": "гр"},
    "product_marijuana": {"name": "Марихуана (Шишки)", "price": 3500, "file": "bumps.jpg", "unit": "гр"},
    
    # Аптека (НАЦЕНКА 150%+)
    "product_tramadol": {"name": "Трамадол 50мг (20таб)", "price": 3500, "file": "tramadol.jpg", "unit": "уп"},
    "product_atarax": {"name": "Атаракс 25мг (25таб)", "price": 1800, "file": "atarax.jpg", "unit": "уп"},
    "product_zolomax": {"name": "Золомакс алпрозолам 1мг (20таб)", "price": 4200, "file": "zolomax.jpg", "unit": "уп"},
    "product_phenazepam": {"name": "Феназепам 1мг (20таб)", "price": 3800, "file": "phenazepam.jpg", "unit": "уп"},
    "product_lyrica_300": {"name": "Лирика 300мг аптечная", "price": 4500, "file": "lyrica.jpg", "unit": "уп"},
    "product_lyrica_600": {"name": "Лирика 600мг крафтовая", "price": 800, "file": "lyrica_craft.jpg", "unit": "таб"},
    "product_gabapentin": {"name": "Габапентин 40капс", "price": 2800, "file": "gabapentin.jpg", "unit": "уп"},
    "product_teraligen": {"name": "Тералиджен 5мг (50таб)", "price": 3200, "file": "teraligen.jpg", "unit": "уп"},
    "product_paroxetine": {"name": "Пароксетин 20мг (30таб)", "price": 3800, "file": "paroxetine.jpg", "unit": "уп"},
    "product_sertraline": {"name": "Сертралин 50мг (30таб)", "price": 3500, "file": "sertraline.jpg", "unit": "уп"},
    "product_venlafaxine": {"name": "Венлафаксин 75мг (30таб)", "price": 4000, "file": "venlafaxine.jpg", "unit": "уп"},
    "product_escitalopram": {"name": "Эсциталопрам 10мг (30таб)", "price": 3600, "file": "escitalopram.jpg", "unit": "уп"},
    "product_mirtazapine": {"name": "Миртазапин 30мг (30таб)", "price": 3200, "file": "mirtazapine.jpg", "unit": "уп"},
    "product_bupropion": {"name": "Бупропион 150мг (30таб)", "price": 5000, "file": "bupropion.jpg", "unit": "уп"},
    "product_ketamine": {"name": "Кетамин 100мг/мл (10мл)", "price": 12000, "file": "ketamine.jpg", "unit": "фл"},
    "product_dxm": {"name": "Декстрометорфан сироп (200мл)", "price": 3800, "file": "dxm.jpg", "unit": "фл"},
}

# Аптечные товары (для ФИО)
postal_products = list(product_info.keys())[7:]  # Все товары начиная с трамадола

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def generate_addresses(city, product_key):
    """Генерирует адреса"""
    random.seed(f"{city}_{product_key}")
    city_streets = streets.get(city, ["Центральная", "Ленина", "Советская"])
    addresses = []
    
    for _ in range(2):
        street = random.choice(city_streets)
        house = random.randint(1, 150)
        location = random.choice([
            " (подъезд)", " (арка)", " (подвал)", 
            " (кодовый замок)", " (гараж)", " (ниша)"
        ])
        addresses.append(f"{street}, {house}{location}")
    
    return addresses

def get_usdt_rate():
    """Курс USDT"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB', timeout=5)
        return float(response.json()['price']) if response.status_code == 200 else 100.0
    except:
        return 100.0

def validate_fio(fio):
    """Проверяет ФИО"""
    return len(fio.strip().split()) >= 2 and 5 <= len(fio) <= 100

def validate_zip(zip_code):
    """Проверяет индекс"""
    return bool(re.match(r'^\d{6}$', zip_code))

def clear_user_data(user_id):
    """Очищает данные пользователя"""
    for data_dict in [user_temporary_data, user_selections, user_pending_confirmations]:
        if user_id in data_dict:
            del data_dict[user_id]

# ========== КОМАНДЫ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    clear_user_data(user_id)
    
    try:
        with open('welcome.jpg', 'rb') as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption="""🔥 Добро пожаловать на Дикий Запад!

💊 Аптека - почтовая доставка (требует ФИО и индекс)
🚚 Остальное - курьерская доставка

📍 Сначала выбери город:"""
            )
    except:
        await update.message.reply_text("🔥 Добро пожаловать на Зета! 💊 Выбери город /city")
    
    await show_city_selection(update.message)

async def city_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /city"""
    await show_city_selection(update.message)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /buy"""
    user_id = update.effective_user.id
    
    if user_id not in user_cities:
        await update.message.reply_text("❌ Сначала выбери город /city")
        return
    
    try:
        with open('buy.jpg', 'rb') as photo:
            keyboard = [
                [InlineKeyboardButton("💊 Дизайнерские", callback_data="cat_designer")],
                [InlineKeyboardButton("🌈 Эйфоретики", callback_data="cat_euphoriants")],
                [InlineKeyboardButton("🌿 Каннабис", callback_data="cat_cannabis")],
                [InlineKeyboardButton("💊 Аптека (почта)", callback_data="cat_pharmacy")],
            ]
            
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption=f"🛒 Категории товаров\n🏙️ Город: {user_cities[user_id]}\n\nВыбери категорию:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except:
        keyboard = [
            [InlineKeyboardButton("💊 Дизайнерские", callback_data="cat_designer")],
            [InlineKeyboardButton("🌈 Эйфоретики", callback_data="cat_euphoriants")],
            [InlineKeyboardButton("🌿 Каннабис", callback_data="cat_cannabis")],
            [InlineKeyboardButton("💊 Аптека (почта)", callback_data="cat_pharmacy")],
        ]
        await update.message.reply_text(
            f"🛒 Категории товаров\n🏙️ Город: {user_cities[user_id]}\n\nВыбери категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "📋 Команды:\n"
        "/start - начало\n"
        "/city - город\n"
        "/buy - товары\n"
        "/support - помощь"
    )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /support"""
    await update.message.reply_text(
        "🛠️ Техподдержка: @John_TexSupport\n"
        "📞 24/7, отвечаем быстро!"
    )

async def show_city_selection(message):
    """Показывает города"""
    keyboard = [
        [InlineKeyboardButton("Москва", callback_data="city_moscow")],
        [InlineKeyboardButton("Санкт-Петербург", callback_data="city_spb")],
        [InlineKeyboardButton("Псков", callback_data="city_pskov")],
        [InlineKeyboardButton("Петрозаводск", callback_data="city_petrozavodsk")],
        [InlineKeyboardButton("Великий Новгород", callback_data="city_novgorod")],
        [InlineKeyboardButton("Нижний Новгород", callback_data="city_nizhny_novgorod")],
        [InlineKeyboardButton("Владивосток", callback_data="city_vladivostok")],
        [InlineKeyboardButton("Красноярск", callback_data="city_krasnoyarsk")],
        [InlineKeyboardButton("Екатеринбург", callback_data="city_ekaterinburg")],
        [InlineKeyboardButton("Йошкар-Ола", callback_data="city_yoshkar_ola")],
        [InlineKeyboardButton("Казань", callback_data="city_kazan")],
        [InlineKeyboardButton("Калининград", callback_data="city_kaliningrad")],
        [InlineKeyboardButton("Сергиев Посад", callback_data="city_sergiyev_posad")],
        [InlineKeyboardButton("Ярославль", callback_data="city_yaroslavl")],
        [InlineKeyboardButton("Сочи", callback_data="city_sochi")],
        [InlineKeyboardButton("Коломна", callback_data="city_kolomna")],
        [InlineKeyboardButton("Элиста", callback_data="city_elista")],
        [InlineKeyboardButton("Тобольск", callback_data="city_tobolsk")],
        [InlineKeyboardButton("Выборг", callback_data="city_vyborg")],
        [InlineKeyboardButton("Дербент", callback_data="city_derbent")],
        [InlineKeyboardButton("Тамбов", callback_data="city_tambov")],
        [InlineKeyboardButton("Новосибирск", callback_data="city_novosibirsk")],
        [InlineKeyboardButton("Уфа", callback_data="city_ufa")],
        [InlineKeyboardButton("Самара", callback_data="city_samara")],
        [InlineKeyboardButton("Краснодар", callback_data="city_krasnodar")],
        [InlineKeyboardButton("Волгоград", callback_data="city_volgograd")],
        [InlineKeyboardButton("Пермь", callback_data="city_perm")],
        [InlineKeyboardButton("Ростов-на-Дону", callback_data="city_rostov")],
    ]
    await message.reply_text("📍 Выбери город:", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== ОБРАБОТЧИК КНОПОК ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Выбор города
    if data.startswith('city_'):
        city_map = {
            'city_moscow': 'Москва', 'city_spb': 'Санкт-Петербург', 'city_pskov': 'Псков',
            'city_petrozavodsk': 'Петрозаводск', 'city_novgorod': 'Великий Новгород',
            'city_nizhny_novgorod': 'Нижний Новгород', 'city_vladivostok': 'Владивосток',
            'city_krasnoyarsk': 'Красноярск', 'city_ekaterinburg': 'Екатеринбург',
            'city_yoshkar_ola': 'Йошкар-Ола', 'city_kazan': 'Казань', 'city_kaliningrad': 'Калининград',
            'city_sergiyev_posad': 'Сергиев Посад', 'city_yaroslavl': 'Ярославль', 'city_sochi': 'Сочи',
            'city_kolomna': 'Коломна', 'city_elista': 'Элиста', 'city_tobolsk': 'Тобольск',
            'city_vyborg': 'Выборг', 'city_derbent': 'Дербент', 'city_tambov': 'Тамбов',
            'city_novosibirsk': 'Новосибирск', 'city_ufa': 'Уфа', 'city_samara': 'Самара',
            'city_krasnodar': 'Краснодар', 'city_volgograd': 'Волгоград', 'city_perm': 'Пермь',
            'city_rostov': 'Ростов-на-Дону',
        }
        
        selected_city = city_map.get(data, 'Москва')
        user_cities[user_id] = selected_city
        clear_user_data(user_id)
        
        await query.message.reply_text(f"✅ Город: {selected_city}\nТеперь смотри товары /buy")
        return
    
    # Проверка города
    if user_id not in user_cities:
        await query.message.reply_text("❌ Сначала выбери город /city")
        return
    
    selected_city = user_cities[user_id]
    
    # Категории товаров
    if data == "cat_designer":
        await show_designer_products(query.message, selected_city)
        return
    elif data == "cat_euphoriants":
        await show_euphoriants_products(query.message, selected_city)
        return
    elif data == "cat_cannabis":
        await show_cannabis_products(query.message, selected_city)
        return
    elif data == "cat_pharmacy":
        await show_pharmacy_products(query.message, selected_city)
        return
    
    # Выбор товара
    if data in product_info:
        clear_user_data(user_id)
        
        product = product_info[data]
        is_postal = data in postal_products
        
        # Сохраняем выбор
        user_selections[user_id] = {
            "product_key": data,
            "product_name": product["name"],
            "price": product["price"],
            "unit": product["unit"],
            "is_postal": is_postal
        }
        
        # Если аптечный товар - запрашиваем ФИО
        if is_postal:
            user_temporary_data[user_id] = {"step": "awaiting_fio"}
            
            try:
                with open(product["file"], 'rb') as photo:
                    await query.message.reply_photo(
                        photo=InputFile(photo),
                        caption=f"💊 {product['name']} - {product['price']}₽/{product['unit']}\n\n📝 Введи ФИО для почты:\nПример: Иванов Иван Иванович"
                    )
            except:
                await query.message.reply_text(
                    f"💊 {product['name']} - {product['price']}₽/{product['unit']}\n\n📝 Введи ФИО для почты:\nПример: Иванов Иван Иванович"
                )
        
        else:
            # Обычный товар - показываем адреса
            addresses = generate_addresses(selected_city, data)
            
            keyboard = []
            for i, addr in enumerate(addresses):
                keyboard.append([InlineKeyboardButton(f"📍 Вариант {i+1}: {addr}", callback_data=f"addr_{i}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{'designer' if 'mefedron' in data or 'alpha' in data else 'euphoriants' if 'ecstasy' in data else 'cannabis'}")])
            
            try:
                with open(product["file"], 'rb') as photo:
                    await query.message.reply_photo(
                        photo=InputFile(photo),
                        caption=f"💊 {product['name']}\n💰 {product['price']}₽/{product['unit']}\n🏙️ {selected_city}\n\nВыбери адрес:",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            except:
                await query.message.reply_text(
                    f"💊 {product['name']}\n💰 {product['price']}₽/{product['unit']}\n🏙️ {selected_city}\n\nВыбери адрес:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        return
    
    # Выбор адреса
    if data.startswith('addr_'):
        idx = int(data.split('_')[1])
        selection = user_selections.get(user_id)
        
        if not selection:
            await query.message.reply_text("❌ Товар не выбран")
            return
        
        addresses = generate_addresses(selected_city, selection["product_key"])
        
        if idx < len(addresses):
            selection["address"] = addresses[idx]
            await query.message.reply_text(
                f"📍 Адрес: {addresses[idx]}\n\n"
                f"📦 Сколько {selection['unit']}? (от 1 до 20):"
            )
        return
    
    # Оплата
    if data.startswith('pay_'):
        order = user_pending_confirmations.get(user_id)
        if not order:
            await query.message.reply_text("❌ Нет заказа")
            return
        
        method = data.split('_')[1]
        
        if method == "crypto":
            usdt_rate = get_usdt_rate()
            amount_usdt = order["total_price"] / usdt_rate
            
            # Просто показываем реквизиты
            await query.message.reply_text(
                f"💎 Оплата USDT\n\n"
                f"💊 {order['product_name']}\n"
                f"📦 {order['quantity']}{order['unit']}\n"
                f"💰 {order['total_price']}₽ (~{amount_usdt:.2f} USDT)\n\n"
                f"📮 Кошелек: USDT TRC20\n"
                f"🔗 Адрес: TDJx7K2sUZfPqxxxxxxxxxxxx\n\n"
                f"📸 Сделай скриншот перевода!"
            )
            
        elif method == "sbp":
            final_price = order["total_price"] + random.randint(100, 500)
            await query.message.reply_text(
                f"📱 Оплата СБП\n\n"
                f"💊 {order['product_name']}\n"
                f"📦 {order['quantity']}{order['unit']}\n"
                f"💰 {final_price}₽\n\n"
                f"📞 Номер: +79610793180\n"
                f"💳 Сбербанк\n\n"
                f"📸 Отправь скриншот!"
            )
            
        elif method == "card":
            final_price = order["total_price"] + random.randint(100, 500)
            await query.message.reply_text(
                f"💳 Оплата картой\n\n"
                f"💊 {order['product_name']}\n"
                f"📦 {order['quantity']}{order['unit']}\n"
                f"💰 {final_price}₽\n\n"
                f"💳 Карта: 2202 2068 5979 7685\n"
                f"🏦 Сбербанк\n\n"
                f"📸 Отправь скриншот!"
            )
        
        # Очищаем данные после оплаты
        clear_user_data(user_id)
        return
    
    # Отмена
    if data == "cancel":
        clear_user_data(user_id)
        await query.message.reply_text("❌ Заказ отменен")

# ========== ФУНКЦИИ ПОКАЗА ТОВАРОВ ==========
async def show_designer_products(message, city):
    """Дизайнерские товары"""
    keyboard = [
        [InlineKeyboardButton("💊 Мефедрон (Мука) - 4200₽/гр", callback_data="product_mefedron_flour")],
        [InlineKeyboardButton("✨ Мефедрон (Кристаллы) - 4800₽/гр", callback_data="product_mefedron_crystals")],
        [InlineKeyboardButton("⚡ Альфа-ПвП (Мука) - 4500₽/гр", callback_data="product_alpha_pvp_flour")],
        [InlineKeyboardButton("❄️ Альфа-ПвП (Кристаллы) - 5000₽/гр", callback_data="product_alpha_pvp_crystals")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    await message.reply_text(
        f"💊 Дизайнерские\n🏙️ {city}\n\nВыбери товар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_euphoriants_products(message, city):
    """Эйфоретики"""
    keyboard = [
        [InlineKeyboardButton("🌈 Экстази (МДМА) - 2800₽/шт", callback_data="product_ecstasy")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    await message.reply_text(
        f"🌈 Эйфоретики\n🏙️ {city}\n\nВыбери товар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_cannabis_products(message, city):
    """Каннабис"""
    keyboard = [
        [InlineKeyboardButton("🍫 Гашиш ICE-O-LATOR - 3800₽/гр", callback_data="product_hashish")],
        [InlineKeyboardButton("🌿 Марихуана (Шишки) - 3500₽/гр", callback_data="product_marijuana")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    await message.reply_text(
        f"🌿 Каннабис\n🏙️ {city}\n\nВыбери товар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_pharmacy_products(message, city):
    """Аптечные товары"""
    keyboard = [
        [InlineKeyboardButton("💊 Трамадол 50мг - 3500₽/уп", callback_data="product_tramadol")],
        [InlineKeyboardButton("😴 Атаракс 25мг - 1800₽/уп", callback_data="product_atarax")],
        [InlineKeyboardButton("💊 Золомакс 1мг - 4200₽/уп", callback_data="product_zolomax")],
        [InlineKeyboardButton("💊 Феназепам 1мг - 3800₽/уп", callback_data="product_phenazepam")],
        [InlineKeyboardButton("⚡ Лирика 300мг - 4500₽/уп", callback_data="product_lyrica_300")],
        [InlineKeyboardButton("🔥 Лирика 600мг - 800₽/таб", callback_data="product_lyrica_600")],
        [InlineKeyboardButton("💊 Габапентин - 2800₽/уп", callback_data="product_gabapentin")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_categories")]
    ]
    await message.reply_text(
        f"💊 Аптека (почта)\n🏙️ {city}\n📝 Требует ФИО и индекс\n\nВыбери товар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== ОБРАБОТЧИК СООБЩЕНИЙ ==========
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Если ждем ФИО
    if user_id in user_temporary_data and user_temporary_data[user_id].get("step") == "awaiting_fio":
        if validate_fio(text):
            user_temporary_data[user_id] = {
                "step": "awaiting_zip",
                "fio": text
            }
            await update.message.reply_text(
                "✅ ФИО принято!\n\n"
                "📮 Теперь введи индекс (6 цифр):\n"
                "Пример: 101000"
            )
        else:
            await update.message.reply_text("❌ Неверное ФИО. Пример: Иванов Иван Иванович")
        return
    
    # Если ждем индекс
    if user_id in user_temporary_data and user_temporary_data[user_id].get("step") == "awaiting_zip":
        if validate_zip(text):
            user_temporary_data[user_id] = {
                "step": "awaiting_quantity",
                "fio": user_temporary_data[user_id]["fio"],
                "zip": text
            }
            
            selection = user_selections[user_id]
            await update.message.reply_text(
                f"💊 {selection['product_name']}\n"
                f"👤 {user_temporary_data[user_id]['fio']}\n"
                f"🏤 {text}\n\n"
                f"📦 Сколько {selection['unit']}? (от 1 до 20):"
            )
        else:
            await update.message.reply_text("❌ Неверный индекс. 6 цифр: 101000")
        return
    
    # Если ждем количество (для аптеки)
    if user_id in user_temporary_data and user_temporary_data[user_id].get("step") == "awaiting_quantity":
        await handle_quantity_input(update, user_id, text, is_postal=True)
        return
    
    # Если ждем количество (для обычного товара)
    if user_id in user_selections and "address" in user_selections[user_id]:
        await handle_quantity_input(update, user_id, text, is_postal=False)
        return
    
    # Прочие сообщения
    await update.message.reply_text("Используй кнопки или команды: /start /buy /help")

async def handle_quantity_input(update, user_id, text, is_postal):
    """Обрабатывает ввод количества"""
    try:
        quantity = float(text.replace(',', '.'))
        
        if not (1 <= quantity <= 20):
            await update.message.reply_text("❌ От 1 до 20!")
            return
        
        selection = user_selections[user_id]
        product = product_info[selection["product_key"]]
        total_price = product["price"] * quantity
        
        # Создаем заказ
        order_data = {
            "product_name": selection["product_name"],
            "quantity": quantity,
            "unit": selection["unit"],
            "total_price": total_price,
            "city": user_cities.get(user_id, ""),
            "is_postal": is_postal
        }
        
        if is_postal:
            order_data.update({
                "fio": user_temporary_data[user_id]["fio"],
                "zip": user_temporary_data[user_id]["zip"]
            })
            del user_temporary_data[user_id]
        else:
            order_data["address"] = selection["address"]
        
        user_pending_confirmations[user_id] = order_data
        del user_selections[user_id]
        
        # Показываем способы оплаты
        keyboard = [
            [InlineKeyboardButton("💎 CryptoBot USDT", callback_data="pay_crypto")],
            [InlineKeyboardButton("📱 СБП", callback_data="pay_sbp")],
            [InlineKeyboardButton("💳 Карта", callback_data="pay_card")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
        ]
        
        if is_postal:
            msg = (
                f"📮 Почтовый заказ\n\n"
                f"💊 {order_data['product_name']}\n"
                f"📦 {quantity}{order_data['unit']}\n"
                f"👤 {order_data['fio']}\n"
                f"🏤 {order_data['zip']}\n"
                f"💰 {total_price}₽\n\n"
                f"💳 Выбери оплату:"
            )
        else:
            msg = (
                f"🚚 Курьерский заказ\n\n"
                f"💊 {order_data['product_name']}\n"
                f"📦 {quantity}{order_data['unit']}\n"
                f"📍 {order_data['address']}\n"
                f"🏙️ {order_data['city']}\n"
                f"💰 {total_price}₽\n\n"
                f"💳 Выбери оплату:"
            )
        
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        
    except ValueError:
        await update.message.reply_text("❌ Введи число! Пример: 2 или 3.5")

# ========== ЗАПУСК БОТА ==========
def main():
    """Запускаем бота"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("city", city_command))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("support", support))
    
    # Кнопки и сообщения
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Обработчик ошибок
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"⚠️ Ошибка: {context.error}")
    
    app.add_error_handler(error_handler)
    
    print("="*50)
    print("🔥 БОТ ЗЕТА ЗАПУЩЕН!")
    print(f"💰 Наценка: 150%+")
    print(f"🏙️ Городов: {len(streets)}")
    print(f"💊 Товаров: {len(product_info)}")
    print(f"📮 Аптека: ФИО+индекс")
    print("="*50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
