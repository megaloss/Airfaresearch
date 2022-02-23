import requests
import json
from classes import Airport, SingleFare, ReturnFare, Route
from datetime import datetime, timedelta, date
from os import path
import logging
import time





AIRPORTS_URL='https://www.easyjet.com/ejcms/cache2m/api/inspireme/getroutedata?CurrencyId=4&originIata=AMS&sc_lang=en'

FLIGHTS_URL="https://www.easyjet.com/ejavailability/api/v54/availability/query"


logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# URL0='https://www.easyjet.com/ejcms/cache15m/api/routedates/get/'
# #?destinationIata=AMS&language=nl-NL&originIata=RHO'
# URL = "https://www.easyjet.com/ejcms/cache15m/api/flights/search?AdminFeePerBooking=0&AllDestinations=true&AllOrigins=false&AssumedPassengersPerBooking=1&AssumedSectorsPerBooking=1&CreditCardFeePercent=0&CurrencyId=0&MaxResults=100&OriginIatas=AMS,BRU&PreferredOriginIatas=AMS"
# URL='https://www.easyjet.com/ejcms/cache15m/api/flights/search?AdminFeePerBooking=0&AllDestinations=false&AllOrigins=false&AssumedPassengersPerBooking=1&AssumedSectorsPerBooking=1&CreditCardFeePercent=0&CurrencyId=4&DestinationIatas=CFU,EFL,RHO,SKG,HER,MXP,KRK,FAO,LIS,OPO&MaxPrice=80&MaxResults=40&OriginIatas=AMS&PreferredOriginIatas=AMS'
URL='https://www.easyjet.com/ejcms/cache15m/api/flights/search'
# #?AdminFeePerBooking=0&AllDestinations=false&AllOrigins=false&AssumedPassengersPerBooking=2&AssumedSectorsPerBooking=1&CreditCardFeePercent=0&CurrencyId=4&DestinationIatas=BUD&EndDate=2022-07-27&MaxResults=1&OriginIatas=AMS&StartDate=2022-06-2'
# #URL1='https://www.easyjet.com/api/routepricing/v2/searchfares/GetLowestOutboundPrice?departureAirport=BSL&arrivalAirport=AGA&currency=GBP'
# URL1='https://www.easyjet.com/api/routepricing/v2/searchfares/GetLowestDailyFares?departureAirport=BSL&arrivalAirport=AGA&currency=GBP'
payload={

"AdminFeePerBooking": "0",
"AllDestinations": "false",
"AllOrigins": "false",
"AssumedPassengersPerBooking": "1",
"AssumedSectorsPerBooking": "1",
"CreditCardFeePercent": "0",
"CurrencyId": "4",
"DestinationIatas": "CFU,EFL,RHO,SKG,HER,MXP,KRK,FAO,LIS,OPO",
"StartDate": "2022-06-22",
"EndDate": "2022-07-27",
"MaxResults": "1",
"OriginIatas": "AMS",

"MaxPrice": "40",
"PreferredOriginIatas": "AMS",
}




headers={
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,nl;q=0.5",
"Cache-Control": "no-cache",
"Connection": "keep-alive",
"content-type": "application/json;charset=UTF-8",
"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
"DNT": "1",
"Host": "www.easyjet.com",
"Pragma": "no-cache",
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "none",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
}

class EasyjetHandler:
    @staticmethod
    def read_airports():
        
        def read_from_web():
            payload = {
                'languageCode': 'en - gb'
            }

            try:
                response = requests.get(AIRPORTS_URL, headers=headers)
                airports = response.json()
            except Exception as e:
                return []
            with open ('easyjet_flights.json', 'w') as f:
                json.dump (airports,f, indent=4)
        def extract_airports():
            if not path.exists('easyjet_flights.json'):
                self.read_airports()
            with open ('easyjet_flights.json','r') as f:
                try:
                    data=json.load(f)
                    data=data['Airports']
                except Exception as e:
                    print (e)
                    return []
                    
            print (data[0])

            airport_dict = {}
            for airport in data:
                airport_dict[airport['AirportCode']] = Airport(airport['AirportCode'], airport['NameContent']['AirportName'],
                    airport['NameContent']['AirportName'], '', [airport['Latitude'], airport['Longitude']])
            return airport_dict

        airports = extract_airports()
        return airports


    @staticmethod
    def get_cheapest_return(origin, date_outbound, date_inbound, airports, limit=1000):

        def matchflights (outbounds, inbounds):

                result=[]
                outbound_flights={}
                inbound_flights={}
                for flight in outbounds:
                    outbound_flights[flight['DestinationIata']]={
                        'price':flight['Price'],
                        'DepartureDate': flight['DepartureDate']
                    }
                for flight in inbounds:
                    inbound_flights[flight['OriginIata']]={
                        'price':flight['Price'],
                        'DepartureDate': flight['DepartureDate']
                    }
                print (outbound_flights)
                print (inbound_flights)
                for key in outbound_flights:
                    match = inbound_flights.get(key)
                    if match:
                        #print (outbound_flights[key], match)
                        
                        result.append({ 'destination': key,
                                        'outbound': outbound_flights[key],
                                        'inbound':  match})
                return result if result else []

        if isinstance(date_outbound, tuple):
            outboundDepartureDateFrom, outboundDepartureDateTo = date_outbound[0].strftime('%Y-%m-%d'),date_outbound[1].strftime('%Y-%m-%d')
        else:
            outboundDepartureDateFrom = outboundDepartureDateTo = date_outbound.strftime('%Y-%m-%d')
            
        if isinstance(date_inbound, tuple):
            inboundDepartureDateFrom, inboundDepartureDateTo = date_inbound[0].strftime('%Y-%m-%d'),date_inbound[1].strftime('%Y-%m-%d')
        else:
            inboundDepartureDateFrom = inboundDepartureDateTo = date_inbound.strftime('%Y-%m-%d')


        payload_outbound={

        "AdminFeePerBooking": "0",
        "AllDestinations": "true",
        "AllOrigins": "false",
        "AssumedPassengersPerBooking": "1",
        "AssumedSectorsPerBooking": "1",
        "CreditCardFeePercent": "0",
        "StartDate": outboundDepartureDateFrom,
        "EndDate": outboundDepartureDateTo,
        "MaxResults": "50",
        "OriginIatas": "AMS",
        }

        payload_return={

        "AdminFeePerBooking": "0",
        "AllDestinations": "false",
        "AllOrigins": "true",
        "AssumedPassengersPerBooking": "1",
        "AssumedSectorsPerBooking": "1",
        "CreditCardFeePercent": "0",
        #"CurrencyId": "4",
        #"Currency":"EUR",
        "StartDate": inboundDepartureDateFrom,
        "EndDate": inboundDepartureDateTo,
        "MaxResults": "50",
        "DestinationIatas": "AMS",
        #"MaxPrice": "40",
        #"PreferredOriginIatas": "AMS",
        }

        session = requests.Session()

        resp1 = session.get(URL, headers=headers,  params=payload_outbound)
        print (resp1.status_code)
        if resp1.status_code !=200 :
            print ('no outbound flights found !')
            return[]
        flights_out=resp1.json()['Flights']

        resp2 = session.get(URL, headers=headers,  params=payload_return)
        print (resp2.status_code)
        if resp2.status_code !=200 :
            print ('no inbound flights found !')
            return[]
        flights_in=resp2.json()['Flights']
        session.close()
        flights = matchflights (flights_out,flights_in)
        fares=[]
        for flight in flights:
            destination=airports.get(flight['destination'])
            route=Route (origin,destination)
            flight_number='EASY'
            outbound = SingleFare(route, flight['outbound']['DepartureDate'], flight['outbound']['DepartureDate'], int(flight['outbound']['price']), flight_number)
            inbound = SingleFare(route.invert(), flight['inbound']['DepartureDate'], flight['inbound']['DepartureDate'], int(flight['inbound']['price']), flight_number)
            fares.append(ReturnFare(outbound,inbound)) # list is expected !
        
        return fares

