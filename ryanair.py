from classes import Airport, SingleFare, ReturnFare, Route
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
    def get_fare(route, date,price_limit=1000):
        SINGLE_TRIP_API_URL = 'https://services-api.ryanair.com/farfnd/3/oneWayFares'
        if isinstance(date, tuple):
            outboundDepartureDateFrom, outboundDepartureDateTo = date[0].strftime('%Y-%m-%d'),date[1].strftime('%Y-%m-%d')
        else:
            outboundDepartureDateFrom = outboundDepartureDateTo = date.strftime('%Y-%m-%d')
        language = 'en'
        limit = 16
        market = 'en-gb'
        offset = 0
        priceValueTo = limit
        fares = []

        payload = {'departureAirportIataCode': route.from_airport.id,
                   'arrivalAirportIataCode': route.to_airport.id,
                   'language': language,
                   'limit': limit,
                   'market': market,
                   'offset': offset,
                   'outboundDepartureDateFrom': outboundDepartureDateFrom,
                   'outboundDepartureDateTo': outboundDepartureDateTo,
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
    def get_destinations(origin, date,price_limit=1000):
        # SINGLE_TRIP_API_URL = 'https://services-api.ryanair.com/farfnd/3/oneWayFares'
        SINGLE_TRIP_API_URL ='https://www.ryanair.com/api/farfnd/v4/oneWayFares'
        if isinstance(date, tuple):
            outboundDepartureDateFrom, outboundDepartureDateTo = date[0].strftime('%Y-%m-%d'),date[1].strftime('%Y-%m-%d')
        else:
            outboundDepartureDateFrom = outboundDepartureDateTo = date.strftime('%Y-%m-%d')
        language = 'en'
        limit = 150
        market = 'en-gb'
        offset = 0
        priceValueTo = price_limit
        destinations = []

        payload = {'departureAirportIataCode': origin.id,
                   'language': language,
                   'limit': limit,
                   'market': market,
                   'offset': offset,
                   'adultPaxCount': 1,
                   'outboundDepartureDateFrom': outboundDepartureDateFrom,
                   'outboundDepartureDateTo': outboundDepartureDateTo,
                   'priceValueTo': priceValueTo}
        response = requests.get(SINGLE_TRIP_API_URL, params=payload)
        print (response.url)
        #print (response.status_code)
        data = response.json()
        #print (data)

        if data['size'] >= 1:

            for item in data['fares']:
                
                airport = item['outbound']['arrivalAirport']['iataCode']

                destinations.append(airport)
        else:
            return False
        return destinations


    @staticmethod
    def get_return(route, date_outbound, date_inbound, limit=1000):
        ROUND_TRIP_API_URL = 'https://www.ryanair.com/api/farfnd/v4/roundTripFares'
        if isinstance(date_outbound, tuple):
            outboundDepartureDateFrom, outboundDepartureDateTo = date_outbound[0].strftime('%Y-%m-%d'),date_outbound[1].strftime('%Y-%m-%d')
        else:
            outboundDepartureDateFrom = outboundDepartureDateTo = date_outbound.strftime('%Y-%m-%d')
        
        if isinstance(date_inbound, tuple):
            inboundDepartureDateFrom, inboundDepartureDateTo = date_inbound[0].strftime('%Y-%m-%d'),date_inbound[1].strftime('%Y-%m-%d')
        else:
            inboundDepartureDateFrom = inboundDepartureDateTo = date_inbound.strftime('%Y-%m-%d')
        language = 'en'
        market = 'en-gb'
        offset = 0
        price_max = limit
        fares = []
        payload = {'departureAirportIataCode': route.from_airport.id,
                   'arrivalAirportIataCode': route.to_airport.id,
                   'inboundDepartureDateFrom': inboundDepartureDateFrom,
                   'inboundDepartureDateTo': inboundDepartureDateTo,
                   'language': language,
                #    'limit': limit,
                   'market': market,
                   'offset': offset,
                   'outboundDepartureDateFrom': outboundDepartureDateFrom,
                   'outboundDepartureDateTo': outboundDepartureDateTo,
                   'priceValueTo': price_max}
        #print (payload)

        response = requests.get(ROUND_TRIP_API_URL, params=payload)
        #print (response.url)
        data = response.json()
        #print (data)

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

    @staticmethod
    def get_cheapest_return(origin, date_outbound, date_inbound, airports, limit=1000):

        flights=[]
        destinations = RyanairHandle.get_destinations(origin, date_outbound)
        if not destinations:
            return False
        print ('destinations available from ryanair are:', destinations)
        for airport in destinations:   
            if airports[airport] == origin:
                continue
        
            my_route = Route(origin, airports[airport])
            flight = RyanairHandle.get_return(my_route, date_outbound, date_inbound)
            if flight:
                flights.extend(flight)
        #print (flights)

        
        return flights

