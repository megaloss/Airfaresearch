from classes import Airport, SingleFare, ReturnFare
import requests
from utils import encode_datetime


class RyanairHandle:

    @staticmethod
    def read_airports():
        airports_link = 'https://www.ryanair.com/api/booking/v4/en-gb/res/stations'
        response = requests.get(airports_link)
        airports = response.json()
        airport_dict = dict()
        for airport in airports:
            lat = int(airports[airport]['latitude'][:-1]) / 10000 if (
                    airports[airport]['latitude'][-1:] == 'N') else -int(airports[airport]['latitude'][:-1]) / 10000
            lon = int(airports[airport]['longitude'][:-1]) / 10000 if (
                    airports[airport]['longitude'][-1:] == 'E') else -int(airports[airport]['longitude'][:-1]) / 10000
            airport_dict[airport] = Airport(airport, airports[airport]['name'], airports[airport]['name'],
                                            airports[airport]['country'], [lat, lon])
        return airport_dict

    @staticmethod
    def get_fare(route, date):
        SINGLE_TRIP_API_URL = 'https://services-api.ryanair.com/farfnd/3/oneWayFares'
        date = date.strftime('%Y-%m-%d')
        language = 'en'
        limit = 16
        market = 'en-gb'
        offset = 0
        priceValueTo = 1000
        fares = []

        payload = {'departureAirportIataCode': route.from_airport.id,
                   'arrivalAirportIataCode': route.to_airport.id,
                   'language': language,
                   'limit': limit,
                   'market': market,
                   'offset': offset,
                   'outboundDepartureDateFrom': date,
                   'outboundDepartureDateTo': date,
                   'priceValueTo': priceValueTo}
        response = requests.get(SINGLE_TRIP_API_URL, params=payload)
        #print (response.url)
        #print (response.status_code)
        data = response.json()

        if data['total'] == 1:

            for item in data['fares']:
                departure_date = encode_datetime(item['outbound']['departureDate'])
                arrival_date = encode_datetime(item['outbound']['arrivalDate'])
                price = item['outbound']['price']['value']
                flight_number = item['outbound']['flightNumber']
                fares.append(SingleFare(route, departure_date, arrival_date, price, flight_number))
        else:
            return False
        return fares




    @staticmethod
    def get_return(route, date_outbound, date_inbound):
        ROUND_TRIP_API_URL = 'https://www.ryanair.com/api/farfnd/v4/roundTripFares'
        date_outbound = date_outbound.strftime('%Y-%m-%d')
        date_inbound = date_inbound.strftime('%Y-%m-%d')
        language = 'en'
        limit = 16
        market = 'en-gb'
        offset = 0
        price_max = 1000
        fares = []
        payload = {'departureAirportIataCode': route.from_airport.id,
                   'arrivalAirportIataCode': route.to_airport.id,
                   'inboundDepartureDateFrom': date_inbound,
                   'inboundDepartureDateTo': date_inbound,
                   'language': language,
                   'limit': limit,
                   'market': market,
                   'offset': offset,
                   'outboundDepartureDateFrom': date_outbound,
                   'outboundDepartureDateTo': date_outbound,
                   'priceValueTo': price_max}

        response = requests.get(ROUND_TRIP_API_URL, params=payload, timeout=0.1)
        # print (response.url)
        data = response.json()

        if len(data) >= 1:

            for item in data['fares']:
                departure_date = encode_datetime(item['outbound']['departureDate'])
                arrival_date = encode_datetime(item['outbound']['arrivalDate'])
                price = item['outbound']['price']['value']
                flight_number = item['outbound']['flightNumber']
                outbound = SingleFare(route, departure_date, arrival_date, price, flight_number)
                departure_date = encode_datetime(item['inbound']['departureDate'])
                arrival_date = encode_datetime(item['inbound']['arrivalDate'])
                price = item['inbound']['price']['value']
                flight_number = item['inbound']['flightNumber']
                inbound = SingleFare(route.invert(), departure_date, arrival_date, price, flight_number)
                fares.append(ReturnFare(outbound,inbound))
        else:
            return False
        return fares

