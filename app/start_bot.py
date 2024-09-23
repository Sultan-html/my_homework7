from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand
import asyncio, logging, aiohttp, schedule, time

bot = Bot(token='7303652506:AAG-5DZmVByDrXuNhT0NEkAJdsmAl8ez1JU')
dp = Dispatcher()

monitoring = False  
chat_id = None
selected_crypto = None
logging.basicConfig(
    filename='crypto_monitoring.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

async def get_crypto_price(symbol):
    url = f'https://api.binance.com/api/v3/avgPrice?symbol={symbol}USDT'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json_response = await response.json()
                price = json_response.get('price')
                if price:
                    return f'Стоимость {symbol} на {time.ctime()}, {price}'
                else:
                    return f'Не удалось получить цену {symbol}'
    except Exception as e:
        logging.error(f'Ошибка при запросе {symbol}: {e}')
        return 'Ошибка запроса к Binance API'

async def monitor_crypto(eth_price, ltc_price, btc_price):
    logging.info(f"ETH: {eth_price}, LTC: {ltc_price}, BTC: {btc_price}")

async def get_btc_price():
    url = 'https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_response = await response.json()
            price = json_response.get('price')
            if price:
                return f'Стоимость биткоина на {time.ctime()}, {price}', price
            else:
                return f'Не удалось получить цену биткоина', None

async def get_ltc_price():
    url = 'https://api.binance.com/api/v3/avgPrice?symbol=LTCUSDT'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_response = await response.json()
            price = json_response.get('price')
            if price:
                return f'Стоимость литкойна на {time.ctime()}, {price}', price
            else:
                return f'Не удалось получить цену литкойна', None

async def get_eth_price():
    url = 'https://api.binance.com/api/v3/avgPrice?symbol=ETHUSDT'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_response = await response.json()
            price = json_response.get('price')
            if price:
                return f'Стоимость Ethereum на {time.ctime()}, {price}', price
            else:
                return f'Не удалось получить цену Ethereum', None

async def monitor_btc_price():
    global monitoring
    while monitoring:
        message, btc_price = await get_btc_price()
        eth_price = (await get_eth_price())[1]
        ltc_price = (await get_ltc_price())[1]
        await bot.send_message(chat_id, message)
        await monitor_crypto(eth_price, ltc_price, btc_price)
        await asyncio.sleep(3600)

async def monitor_ltc_price():
    global monitoring
    while monitoring:
        message, ltc_price = await get_ltc_price()
        eth_price = (await get_eth_price())[1]
        btc_price = (await get_btc_price())[1]
        await bot.send_message(chat_id, message)
        await monitor_crypto(eth_price, ltc_price, btc_price)
        await asyncio.sleep(3600)

async def monitor_eth_price():
    global monitoring
    while monitoring:
        message, eth_price = await get_eth_price()
        ltc_price = (await get_ltc_price())[1]
        btc_price = (await get_btc_price())[1]
        await bot.send_message(chat_id, message)
        await monitor_crypto(eth_price, ltc_price, btc_price)
        await asyncio.sleep(3600)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет {message.from_user.full_name}, напишите / для выведение всех команд бота')

@dp.message(Command('btc'))
async def btc(message: Message):
    global chat_id, monitoring
    chat_id = message.chat.id
    if not monitoring:
        monitoring = True
        await message.answer("Начало мониторинга BTC")
        asyncio.create_task(monitor_btc_price())
    else:
        await message.answer("Мониторинг уже запущен!")

@dp.message(Command('ltc'))
async def ltc(message: Message):
    global chat_id, monitoring
    chat_id = message.chat.id
    if not monitoring:
        monitoring = True
        await message.answer("Начало мониторинга LTC")
        asyncio.create_task(monitor_ltc_price())
    else:
        await message.answer("Мониторинг уже запущен!")

@dp.message(Command('eth'))
async def eth(message: Message):
    global chat_id, monitoring
    chat_id = message.chat.id
    if not monitoring:
        monitoring = True
        await message.answer("Начало мониторинга ETH")
        asyncio.create_task(monitor_eth_price())
    else:
        await message.answer("Мониторинг уже запущен!")

@dp.message(Command('stop'))
async def stop(message: Message):
    global monitoring
    if monitoring:
        monitoring = False
        await message.answer("Мониторинг остановлен")
    else:
        await message.answer("Мониторинг уже остановлен")

async def on_startup():
    await bot.set_my_commands([
        BotCommand(command="/start", description='Запустить бота'),
        BotCommand(command="/btc", description='Начать мониторинг BTC'),
        BotCommand(command='/ltc', description='Начать мониторинг LTC'),
        BotCommand(command='/eth', description='Начать мониторинг ETH'),
        BotCommand(command="/stop", description='Остановить мониторинг')
    ])
    logging.info("БОТ ЗАПУЩЕН")

async def periodic_report():
    if selected_crypto:
        message = await get_crypto_price(selected_crypto)
        await bot.send_message(chat_id, f'Периодический отчет: {message}')

async def scheduler():
    schedule.every(10).minutes.do(periodic_report)
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    await on_startup()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
