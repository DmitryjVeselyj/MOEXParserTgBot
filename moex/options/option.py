from ..base import MoexObject
from ..request import Request

class Option(MoexObject):
    def __init__(self, option_name):
        super().__init__()
        self.request = Request()
        self._option_name = option_name

    def get_open_positions(self, date : str ='today'):
        params = {'iss.meta'   : 'off', 
                  'iss.json'   : 'extended',
                  'lang'       : 'ru',
                  'date'       : date,
                  'asset_type' : 'S'} 
        
        url = f'https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/{self._option_name}/openpositions.jsonp'
        return self.request.get(url, params=params).json()

    def get_turnovers(self):
        params = {'iss.meta'    : 'off', 
                  'iss.json'    : 'extended',
                  'lang'        : 'ru',
                  'series_type' : 'W'}
        url = f'https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/{self._option_name}/turnovers.jsonp' 

        return self.request.get(url, params=params).json()
