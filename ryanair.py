from classes import Airport, SingleFare, ReturnFare, Route
import requests
from utils import encode_datetime
import logging
import asyncio
import aiohttp
import json
import time


ROUND_TRIP_API_URL = 'https://www.ryanair.com/api/farfnd/v4/roundTripFares'
SINGLE_TRIP_API_URL ='https://www.ryanair.com/api/farfnd/v4/oneWayFares'



# # Set up logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# file_handler = logging.FileHandler('ryanair.log')
# log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s')

# file_handler.setFormatter(log_formatter)
# my_logger.addHandler(file_handler)


class RyanairHandler:

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
        # SINGLE_TRIP_API_URL = 'https://services-api.ryanair.com/farfnd/3/oneWayFares'
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
        #my_logger.debug (response.url)
        #my_logger.debug (response.status_code)
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
        # SINGLE_TRIP_API_URL ='https://www.ryanair.com/api/farfnd/v4/oneWayFares'
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
                   'priceValueTo': priceValueTo,}
        response = requests.get(SINGLE_TRIP_API_URL, params=payload)
        
        # my_logger.debug (response.url) -- somehow it does not work !
        # my_logger.debug ('response code =' + str(response.status_code))
        data = response.json()
        #my_logger.debug (data)

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
        #my_logger.debug (payload)

        response = requests.get(ROUND_TRIP_API_URL, params=payload)
        #my_logger.debug (response.url)
        data = response.json()
        #my_logger.debug (data)

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
    async def get_returns(origin, destinations, date_outbound, date_inbound, airports):

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
        fares = []
        tasks=[]
        async with aiohttp.ClientSession() as session:
            for airport in destinations:
                outbound= {"departureStation":origin.id,"arrivalStation":airport.id,"from":outboundDepartureDateFrom,"to":outboundDepartureDateTo}
                inbound = {"departureStation":airport.id,"arrivalStation":origin.id,"from":inboundDepartureDateFrom,"to":inboundDepartureDateTo}
                flights=[outbound,inbound]
                payload = {'departureAirportIataCode': origin.id,
                   'arrivalAirportIataCode': airport.id,
                   'inboundDepartureDateFrom': inboundDepartureDateFrom,
                   'inboundDepartureDateTo': inboundDepartureDateTo,
                   'language': language,
                #    'limit': limit,
                   'market': market,
                   'offset': offset,
                   'outboundDepartureDateFrom': outboundDepartureDateFrom,
                   'outboundDepartureDateTo': outboundDepartureDateTo,
                #    'priceValueTo': price_max
                   }

                tasks.append(asyncio.create_task(session.get(ROUND_TRIP_API_URL, params=payload)))
                

            responses = await asyncio.gather(*tasks)
        for response in responses:
            logger.debug (response.status)
            if response.status !=200:
                logger.error(f"server returned {response}")
                return []
            logger.debug (await response.text())
            data = await response.json()

            if len(data) < 1 or not data['fares']:
                continue
            origin = airports.get(data['fares'][0]['outbound']['departureAirport']['iataCode'])
            destination = airports.get(data['fares'][0]['outbound']['arrivalAirport']['iataCode'])
            if not origin or not destination:
                logger.warning ('something went wrong with the airport code')
                continue
            
            route = Route (origin, destination)
            
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

        
        return fares


    @staticmethod
    async def get_cheapest_return(origin, date_outbound, date_inbound, airports, limit=1000):
        start = time.time()


        flights=[]
        destinations = RyanairHandler.get_destinations(origin, date_outbound)
        if not destinations:
            logger.debug('No destinations available')
            logger.info (f'Finished in {str(round(time.time()-start,2))} sec.')
            return []
        logger.debug ('Destinations found :')
        logger.debug (destinations)
        logger.debug (f'checking {len(destinations)} destinations')
        dest_airports=[]
        for airport in destinations:
            destination_airport = airports.get(airport)
            if not destination_airport or destination_airport == origin:
                continue
            dest_airports.append(destination_airport)

        flights = await RyanairHandler.get_returns(origin, dest_airports, date_outbound, date_inbound, airports)
        logger.debug (flights)

        if not flights:
            logger.debug('returning empty array...')
            logger.info (f'Finished in {str(round(time.time()-start,2))} sec.')
            return []
        logger.info (f'Finished in {str(round(time.time()-start,2))} sec.')
        return flights
        