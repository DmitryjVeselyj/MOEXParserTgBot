from moex.options.option import Option
from .generic_dao import GenericDao
from .base_loader import BaseLoader
from itertools import chain


class OptionDataLoader(BaseLoader):
    def __init__(self, db_path) -> None:
        super().__init__(db_path)
        self._assets = ['SBER', 'GAZP', 'ALRS', 'MAGN', 'YNDX', 'LKOH', 'POLY', 'CHMF',
                        'TCSG', 'MOEX', 'VTBR', 'PLZL', 'NVTK', 'ROSN', 'FIVE', 'TATN',
                        'MTLR', 'POSI', 'SNGS', 'SMLT', 'SBERP', 'OZON', 'PIKK', 'ABIO',
                        'MTSS', 'IRAO']

    def get_assets_list(self):
        return self._assets

    def load_open_position_data(self, asset, date='today', option_type='C'):  # TODO dao one object
        option = Option(asset)
        dao = GenericDao(self._db_path)

        data = option.get_open_positions(date, option_type)
        if len(data) == 0 or len(data[1]['open_positions']) == 0:
            return

        open_positions = data[1]['open_positions']
        storing_open_positions_tradedates_fiz = dao.select('open_positions', columns=['tradedate, is_fiz'],
                                                           condition=f'asset=\'{asset}\' and option_type=\'{option_type}\' order by date(tradedate) desc limit 50')

        for open_position in open_positions:
            if (open_position['tradedate'], open_position['is_fiz']) not in storing_open_positions_tradedates_fiz:
                dao.insert('open_positions', open_position)
            else:
                dao.update('open_positions', open_position,
                           condition=f'tradedate=\'{open_position["tradedate"]}\' and is_fiz={open_position["is_fiz"]} and asset=\'{asset}\' and option_type=\'{option_type}\'')

    def load_turnovers_data(self, asset, series_type='W'):
        option = Option(asset)
        dao = GenericDao(self._db_path)

        data = option.get_turnovers(series_type)
        if len(data) == 0 or len(data[1]['asset_turnovers']) == 0:
            return

        turnovers = data[1]['asset_turnovers']
        storing_turn_tradedates = dao.select('turnovers', columns=['tradedate'],
                                             condition=f'asset=\'{asset}\' and series_type=\'{series_type}\' order by date(tradedate) desc limit 50')

        # [(date, ), (date, )] -> [date, date]
        storing_turn_tradedates_lst = list(chain(*storing_turn_tradedates))

        for turn in turnovers:
            if turn['tradedate'] not in storing_turn_tradedates_lst:
                turn['series_type'] = series_type
                dao.insert('turnovers', turn)
            else:
                turn['series_type'] = series_type
                dao.update('turnovers', turn,
                           condition=f'tradedate=\'{turn["tradedate"]}\' and asset=\'{asset}\' and series_type=\'{series_type}\'')
