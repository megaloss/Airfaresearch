from classes import Airport, SingleFare, ReturnFare, Route
import requests
from utils import encode_datetime
from datetime import timedelta
import asyncio
import aiohttp
import json
import logging
import time
import pickle
import os.path
import socket

from aiocache import cached

timeout=aiohttp.ClientTimeout(60)

# Set up logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler('wizzair.log')
#log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s')

# file_handler.setFormatter(log_formatter)
# logger.addHandler(file_handler)


#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s')

AIRPORTS_URL = 'https://be.wizzair.com/12.2.0/Api/asset/map'
#TIMETABLE_URL = 'https://be.wizzair.com/11.17.2/Api/search/timetable'
TIMETABLE_URL = 'https://be.wizzair.com/12.2.0/Api/search/timetable'
#TIMETABLE_URL = 'https://be.wizzair.com/12.1.2/Api/search/timetable'
#TIMETABLE_URL = 'https://be.wizzair.com/11.17.0/Api/assets/timechart'
#timeout = 15


headers={
"accept": "application/json, text/plain, */*",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,nl;q=0.5",
"cache-control": "no-cache",
#"content-length": "260",
"content-type": "application/json;charset=UTF-8",
"dnt": "1",
"origin": "https://wizzair.com",
"pragma": "no-cache",
#"sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
#"sec-ch-ua-mobile": "?0",
#"sec-ch-ua-platform": "Linux",
#"sec-fetch-dest": "empty",
#"sec-fetch-mode": "cors",
#"sec-fetch-site": "same-site",
"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}
class WizzairHandler:

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

        # headers = {
        #     'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36'
        # }
        # payload = {
        #     'languageCode': 'en - gb'
        # }

        try:
            #print ('params=',params)
            response = requests.get(AIRPORTS_URL, headers=headers)
            airports = response.json()

        except Exception as e:
            logger.error('Error: ', e)
            return []
        airport_dict = {}
        for airport in airports['cities']:
            airport_dict[airport['iata']] = Airport(airport['iata'], get_airport_name(airport['shortName']),
                                                    get_city_name(airport['shortName']), airport['countryCode'],
                                                    [airport['latitude'], airport['longitude']])
        return airport_dict

    @staticmethod
    def get_destinations(origin, date=False,price_limit=1000):
        # if isinstance(date, tuple):
        #     outboundDepartureDateFrom, outboundDepartureDateTo = date[0].strftime('%Y-%m-%d'),date[1].strftime('%Y-%m-%d')
        # else:
        #     outboundDepartureDateFrom = outboundDepartureDateTo = date.strftime('%Y-%m-%d')

        # headers = {
        #     'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36'
        # }
        payload = {
            'languageCode': 'en - gb'
        }
        if not os.path.exists('wizz_flights.p'):
            try:
                response = requests.get(AIRPORTS_URL, headers=headers, timeout=20)
                if response.status_code !=200:
                    logger.error ("Got no destinations from api")
                    return []
                all_flights = response.json()
                if all_flights:
                    with open('wizz_flights.p', 'wb') as f:
                        pickle.dump(all_flights,f)

            except Exception as e:
                logger.error(e)
                return []
        else:
            with open('wizz_flights.p', 'rb') as f:
                    all_flights = pickle.load(f)
        connections =[]
        for city in all_flights['cities']:
            if city['iata'] != origin.id:
                continue
            
            for conn in city['connections']:
                #print (conn)
                connections.append(conn['iata'])
        if len(connections)>0:
            return connections
        return []
    

    @staticmethod
    def get_return(route, date_outbound, date_inbound, limit=1000):

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
        outbound= {"departureStation":route.from_airport.id,"arrivalStation":route.to_airport.id,"from":outboundDepartureDateFrom,"to":outboundDepartureDateTo}
        inbound = {"departureStation":route.to_airport.id,"arrivalStation":route.from_airport.id,"from":inboundDepartureDateFrom,"to":inboundDepartureDateTo}
        flights=[outbound,inbound]
        payload = {"flightList":flights,
                    "priceType":"regular", #'wds' = discounted pricing
                    "adultCount":1,
                    "childCount":0,
                    "infantCount":0,
                    }
        

        #print ("payload = ", payload)
        
        response = requests.post(TIMETABLE_URL, json=payload, headers=headers)
        #logger.debug (response.text)
        data = response.json()
        #logger.debug (data)
        if len (data['outboundFlights'])<1 or len (data["returnFlights"])<1:
            return []
        if data['outboundFlights'][0]['price']['currencyCode']!="EUR":
            logger.warning("Prices are not in EUR !!! ")

        inbounds=[]
        outbounds=[]


        for item in data['outboundFlights']:
            if item['priceType'] == "price":
                departure_date = encode_datetime(item["departureDates"][0])
                price = item['price']['amount']
                outbounds.append([departure_date,price])
            
        for item in data["returnFlights"]:
            if item['priceType'] == "price":
                departure_date = encode_datetime(item["departureDates"][0])
                price = item['price']['amount']
                inbounds.append([departure_date,price])


        best_outbound, best_inbound = WizzairHandler.get_best_pair(outbounds, inbounds)
        flight_number='WZ000'
        if best_outbound and best_inbound:
            outbound = SingleFare(route, best_outbound[0], best_outbound[0], best_outbound[1], flight_number)
            inbound = SingleFare(route.invert(), best_inbound[0], best_inbound[0], best_inbound[1], flight_number)
            return [ReturnFare(outbound,inbound)] # list is expected !
        return []

    @staticmethod
    def get_best_pair(outbounds, inbounds):
        outbounds_sorted=sorted(sorted(outbounds, reverse=False), key= lambda x: x[1])
        inbounds_sorted=sorted(sorted(inbounds, reverse=True), key= lambda x: x[1])

        while (outbounds_sorted and inbounds_sorted):
            if inbounds_sorted[0][0]-outbounds_sorted[0][0] > timedelta(days=1):
                return outbounds_sorted[0], inbounds_sorted[0]
            if len(outbounds_sorted)> len (inbounds_sorted):
                outbounds_sorted.pop(0)
            else:
                inbounds_sorted.pop(0)
        return False, False

    @staticmethod
    @cached(ttl=600)
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
        connector = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=connector) as session:
            for airport in destinations:
                outbound= {"departureStation":origin.id,"arrivalStation":airport.id,"from":outboundDepartureDateFrom,"to":outboundDepartureDateTo}
                inbound = {"departureStation":airport.id,"arrivalStation":origin.id,"from":inboundDepartureDateFrom,"to":inboundDepartureDateTo}
                flights=[outbound,inbound]
                payload = {"flightList":flights,
                            "priceType":"regular",
                            "adultCount":"1",
                            "childCount":"0",
                            "infantCount":"0"
                            }
                payload = json.dumps(payload).replace(' ','')
                logger.debug ('sent request for ' + airport.id)
                tasks.append(asyncio.create_task(session.post(TIMETABLE_URL, data=payload, headers=headers,verify_ssl=False)))

                await asyncio.sleep(0)
            responses = await asyncio.gather(*tasks)
        for response in responses:
            #logger.debug (response.status)
            if response.status !=200:
                logger.error(f"server returned {response}")
                return []
            #logger.debug (await response.text())
            data = await response.json()
            if len (data['outboundFlights'])<1 or len (data["returnFlights"])<1:
                continue
            if data['outboundFlights'][0]['price']['currencyCode']!="EUR":
                logger.warning("************WARNING***************** : Prices are not in EUR !!! ")

            inbounds=[]
            outbounds=[]
            origin=airports.get(data['outboundFlights'][0]['departureStation'])
            destination = airports.get(data['outboundFlights'][0]['arrivalStation'])
            if not origin or not destination:
                continue
            logger.debug (f'A flight from {origin.id} to {destination.id}')


            for item in data['outboundFlights']:
                if item['priceType'] == "price":
                    departure_date = encode_datetime(item["departureDates"][0])
                    price = item['price']['amount']
                    outbounds.append([departure_date,price])
                
            for item in data["returnFlights"]:
                if item['priceType'] == "price":
                    departure_date = encode_datetime(item["departureDates"][0])
                    price = item['price']['amount']
                    inbounds.append([departure_date,price])


                best_outbound, best_inbound = WizzairHandler.get_best_pair(outbounds, inbounds)
                flight_number='WZ000'
            if best_outbound and best_inbound:
                route=Route (origin,destination)
                outbound = SingleFare(route, best_outbound[0], best_outbound[0], best_outbound[1], flight_number)
                inbound = SingleFare(route.invert(), best_inbound[0], best_inbound[0], best_inbound[1], flight_number)
                fares.append(ReturnFare(outbound,inbound)) # list is expected !
            else:
                continue
        return fares


    
    @staticmethod
    @cached(ttl=600)
    async def get_cheapest_return(origin, date_outbound, date_inbound, airports, limit=1000):
        start = time.time()
        flights=[]
        destinations = WizzairHandler.get_destinations(origin, date_outbound)
        if not destinations:
            logger.debug('No destinations available')
            logger.info (f'Finished in {str(round(time.time()-start,2))} sec.')
            return []
        #logger.debug ('Destinations found :')
        #logger.debug (destinations)

        dest_airports=[]
        #tasks=[]
        for airport in destinations:
            destination_airport = airports.get(airport)
            if not destination_airport or destination_airport == origin:
                continue
            dest_airports.append(destination_airport)

        flights = await WizzairHandler.get_returns(origin, dest_airports, date_outbound, date_inbound, airports)
        #logger.debug (flights)

        if not flights:
            logger.debug('returning empty array...')
            logger.info (f'Finished in {str(round(time.time()-start,2))} sec.')
            return []
        logger.info (f'Finished in {str(round(time.time()-start,2))} sec.')
        return flights
        

'''
https://be.wizzair.com/11.17.0/Api/search/search

{"isFlightChange":false,"flightList":[{"departureStation":"EIN","arrivalStation":"BUD","departureDate":"2022-01-23"}],"adultCount":1,"childCount":0,"infantCount":0,"wdc":true}
this requires cookies :(
'''