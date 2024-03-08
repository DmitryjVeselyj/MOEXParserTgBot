from .base_analyzer import BaseAnalyzer
from etl.generic_dao import GenericDao
from matplotlib import pyplot as plt
from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont

plt.rcParams.update({'figure.max_open_warning': 0})


class OptionAnalyzer(BaseAnalyzer):
    def build_turnovers_image(self, asset, path, series_type='W'):
        dao = GenericDao(self._db_path)
        turnovers = dao.select('turnovers',
                               condition=f'asset=\'{asset}\' and series_type=\'{series_type}\' order by date(tradedate) desc limit 30')[
                    ::-1]

        volume = []
        open_contracts = []
        tradedates = []
        for turnover in turnovers:
            volume.append(turnover[3])
            open_contracts.append(turnover[4])
            tradedates.append(turnover[2])

        fig, ax1 = plt.subplots()
        fig.set_size_inches(18, 10)

        ax1.set_title(f'{asset} : {series_type}')
        ax1.bar([i for i in range(len(volume))], volume)
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Объём, контракты', color='tab:blue')
        ax1.set_xticks([i for i in range(len(tradedates))], tradedates, rotation=60)
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('ОИ, контракты', rotation=270, labelpad=15)
        ax2.plot([i for i in range(len(open_contracts))], open_contracts, color='0.3', marker='o')

        fig.tight_layout()
        plt.savefig(path + f'option_turnovers_{asset}_{series_type}', dpi=100)

    def build_open_positions_image(self, asset, path, option_type='C'):
        dao = GenericDao(self._db_path)
        columns_indx = {key: value for value, key in enumerate(['tradedate',
                                                                'persons_long',
                                                                'persons_short',
                                                                'open_position_long',
                                                                'open_position_short',
                                                                'oichange_long',
                                                                'oichange_short'])}

        open_positions_fiz = dao.select('open_positions', columns=list(columns_indx.keys()),
                                        condition=f'asset=\'{asset}\' and is_fiz=1 and option_type=\'{option_type}\' order by date(tradedate) desc limit 1')[
                             ::-1]
        open_positions_no_fiz = dao.select('open_positions', columns=list(columns_indx.keys()),
                                           condition=f'asset=\'{asset}\' and is_fiz=0 and option_type=\'{option_type}\' order by date(tradedate) desc limit 1')[
                                ::-1]
        # no need for loop
        for position_no_fiz, position_fiz in zip(open_positions_no_fiz, open_positions_fiz):
            table = PrettyTable()
            table.title = f'{asset}: {position_no_fiz[columns_indx["tradedate"]]}_{option_type}'

            table.field_names = [' ', 'Физические лица, длинные', 'Физические лица, короткие',
                                 'Юридические лица, длинные', 'Юридические лица, короткие']
            # change places because Moscow Exchange
            table.add_row(['Открытые позиции', position_fiz[columns_indx['open_position_short']],
                           position_fiz[columns_indx['open_position_long']],
                           position_no_fiz[columns_indx['open_position_short']],
                           position_no_fiz[columns_indx['open_position_long']]])
            table.add_row(
                ['Изменение', position_fiz[columns_indx['oichange_short']], position_fiz[columns_indx['oichange_long']],
                 position_no_fiz[columns_indx['oichange_short']], position_no_fiz[columns_indx['oichange_long']]])
            table.add_row(['Количество лиц', position_fiz[columns_indx['persons_short']],
                           position_fiz[columns_indx['persons_long']], position_no_fiz[columns_indx['persons_short']],
                           position_no_fiz[columns_indx['persons_long']]])

            im = Image.new("RGB", (810, 160), "white")
            draw = ImageDraw.Draw(im)
            unicode_font = ImageFont.truetype("DejaVuSansMono.ttf", 10)
            draw.text((10, 10), table.get_string(), fill="black", font=unicode_font)

            # im.save(path + f'table_open_pos_{asset}_{tradedate}.png')
            im.save(path + f'table_open_pos_{asset}_{option_type}.png')

        # tradedate = []
        #
        # persons_long = []
        # persons_short = []
        #
        # open_position_long = []
        # open_position_short = []
        #
        # oichange_long = []
        # oichange_short = []
        #
        # for position in open_positions_no_fiz:
        #     tradedate.append(position[columns_indx['tradedate']])
        #
        #     persons_long.append(position[columns_indx['persons_long']])
        #     persons_short.append(position[columns_indx['persons_short']])
        #
        #     open_position_long.append(position[columns_indx['open_position_long']])
        #     open_position_short.append(position[columns_indx['open_position_short']])
        #
        #     oichange_long.append(position[columns_indx['oichange_long']])
        #     oichange_short.append(position[columns_indx['oichange_short']])
        #
        # plt.figure(figsize=(18, 10))
        # width = 0.2
        #
        # for x, y in enumerate(open_position_long):
        #     plt.annotate(y, (x, y), xytext=(0, 7),
        #                  textcoords="offset points", ha='center', va='bottom')
        # plt.bar([i for i in range(len(open_position_long))], open_position_long, width,
        #         label='Юридические лица, длинные')
        #
        # for x, y in enumerate(open_position_short):
        #     plt.annotate(y, (x + width, y), xytext=(0, 7),
        #                  textcoords="offset points", ha='center', va='bottom')
        # plt.bar([i + width for i in range(len(open_position_short))], open_position_short, width,
        #         label='Юридические лица, короткие')
        #
        # persons_long = []
        # persons_short = []
        #
        # open_position_long = []
        # open_position_short = []
        #
        # oichange_long = []
        # oichange_short = []
        #
        # for position in open_positions_fiz:
        #     persons_long.append(position[columns_indx['persons_long']])
        #     persons_short.append(position[columns_indx['persons_short']])
        #
        #     open_position_long.append(position[columns_indx['open_position_long']])
        #     open_position_short.append(position[columns_indx['open_position_short']])
        #
        #     oichange_long.append(position[columns_indx['oichange_long']])
        #     oichange_short.append(position[columns_indx['oichange_short']])
        #
        # for x, y in enumerate(open_position_long):
        #     plt.annotate(y, (x + width * 2, y), xytext=(0, 7),
        #                  textcoords="offset points", ha='center', va='bottom')
        #
        # plt.bar([i + width * 2 for i in range(len(open_position_long))], open_position_long, width,
        #         label='Физические лица, длинные')
        #
        # for x, y in enumerate(open_position_short):
        #     plt.annotate(y, (x + width * 3, y), xytext=(0, 7),
        #                  textcoords="offset points", ha='center', va='bottom')
        # plt.bar([i + width * 3 for i in range(len(open_position_short))], open_position_short, width,
        #         label='Физические лица, короткие',
        #         color='tab:purple')
        #
        # plt.legend()
        # plt.xlabel('Дата')
        # plt.ylabel('Открытые позиции')
        # plt.title(asset)
        # plt.xticks([i + width * 1.5 for i in range(len(tradedate))], tradedate)
        # plt.savefig(path + f'open_positions_{asset}', dpi=100)
        # plt.close()
