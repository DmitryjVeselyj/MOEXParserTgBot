import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from os import makedirs
from time import sleep
from analysis.option_analyzer import OptionAnalyzer
from etl.option_loader import OptionDataLoader
import logging

logging.basicConfig(filename='./tmp/bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

DB = "moex.db"
TOKEN = ""
bot = Bot(token=TOKEN)
dp = Dispatcher()


def option_load_data(asset):
    option_data_loader = OptionDataLoader(DB)
    option_data_loader.load_turnovers_data(asset, series_type="W")
    option_data_loader.load_open_position_data(asset, option_type='C')
    option_data_loader.load_open_position_data(asset, option_type='P')


# TODO refactor
def option_build_images(asset):
    option_analyzer = OptionAnalyzer(DB)

    makedirs(f"analysis/data/{asset}/", exist_ok=True)
    option_analyzer.build_open_positions_image(asset, f"analysis/data/{asset}/", option_type='C')
    option_analyzer.build_open_positions_image(asset, f"analysis/data/{asset}/", option_type='P')
    option_analyzer.build_turnovers_image(asset, f"analysis/data/{asset}/", series_type="W")


async def option_send_images(asset, chat_id=):
    await bot.send_message(chat_id, f"ASSET : {asset}")

    open_positions_last_day_table_call = FSInputFile(
        f"analysis/data/{asset}/table_open_pos_{asset}_C.png"
    )
    await bot.send_photo(chat_id, open_positions_last_day_table_call)

    open_positions_last_day_table_put = FSInputFile(
        f"analysis/data/{asset}/table_open_pos_{asset}_P.png"
    )
    await bot.send_photo(chat_id, open_positions_last_day_table_put)

    turnovers_photo_week = FSInputFile(
        f"analysis/data/{asset}/option_turnovers_{asset}_W.png"
    )
    await bot.send_photo(chat_id, turnovers_photo_week)



@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Starting mailing")
    option_data_loader = OptionDataLoader(DB)

    while True:
        for asset in option_data_loader.get_assets_list():
            option_load_data(asset)
            option_build_images(asset)
            await option_send_images(asset)

        sleep(60 * 60 * 5)


async def run_bot():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
