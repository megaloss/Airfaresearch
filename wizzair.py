from classes import Airport
import requests

AIRPORTS_URL = 'https://be.wizzair.com/11.8.0/Api/asset/map'

class WizzairHandle:

    @staticmethod
    def read_airports():
        def get_city_name(text):
            if '(' in text and ')' in text:
                return text.split('(')[0]
            return text

        def get_airport_name(text):
            if '(' in text and ')' in text:
                return text.split('(')[1].split('(')[0].strip('()')
            return text.split(' ')[-1:][0]

        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36'
        }
        payload = {
            'languageCode': 'en - gb'
        }

        try:
            response = requests.get(AIRPORTS_URL, params=payload, headers=headers, timeout=3)
            airports = response.json()

        except Exception as e:
            print('Error: ', e)
            return False
        airport_dict = {}
        for airport in airports['cities']:
            airport_dict[airport['iata']] = Airport(airport['iata'], get_airport_name(airport['shortName']),
                                                    get_city_name(airport['shortName']), airport['countryCode'],
                                                    [airport['latitude'], airport['longitude']])
        return airport_dict
