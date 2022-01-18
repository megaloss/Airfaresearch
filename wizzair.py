from classes import Airport, SingleFare, ReturnFare, Route
import requests
from utils import encode_datetime
from datetime import timedelta

AIRPORTS_URL = 'https://be.wizzair.com/11.17.0/Api/asset/map'
TIMETABLE_URL = 'https://be.wizzair.com/11.17.0/Api/search/timetable'
#TIMETABLE_URL = 'https://be.wizzair.com/11.17.0/Api/assets/timechart'
headers={"accept": "application/json, text/plain, */*",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,nl;q=0.5",
"cache-control": "no-cache",
"content-length": "260",
"content-type": "application/json;charset=UTF-8",
"dnt": "1",
"origin": "https://wizzair.com",
"pragma": "no-cache",
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Linux",
"sec-fetch-dest": "empty",
"sec-fetch-mode": "cors",
"sec-fetch-site": "same-site",
"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
}
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
            response = requests.get(AIRPORTS_URL, params=payload, headers=headers)
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

    @staticmethod
    def get_destinations(origin, date,price_limit=1000):
        # if isinstance(date, tuple):
        #     outboundDepartureDateFrom, outboundDepartureDateTo = date[0].strftime('%Y-%m-%d'),date[1].strftime('%Y-%m-%d')
        # else:
        #     outboundDepartureDateFrom = outboundDepartureDateTo = date.strftime('%Y-%m-%d')

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
        connections =[]
        for city in airports['cities']:
            if city['iata'] != origin.id:
                continue
            
            for conn in city['connections']:
                #print (conn)
                connections.append(conn['iata'])
        if len(connections)>0:
            return connections
        return False
    

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
        #print (response.text)
        data = response.json()
        #print (data)
        if len (data['outboundFlights'])<1 or len (data["returnFlights"])<1:
            return False
        if data['outboundFlights'][0]['price']['currencyCode']!="EUR":
            print ("************WARNING***************** : Prices are not in EUR !!! ")

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


        best_outbound, best_inbound = WizzairHandle.get_best_pair(outbounds, inbounds)
        flight_number='WZ000'
        if best_outbound and best_inbound:
            outbound = SingleFare(route, best_outbound[0], best_outbound[0], best_outbound[1], flight_number)
            inbound = SingleFare(route.invert(), best_inbound[0], best_inbound[0], best_inbound[1], flight_number)
            return [ReturnFare(outbound,inbound)] # list is expected !
        return False

    @staticmethod
    def get_best_pair(outbounds, inbounds):
        outbounds_sorted=sorted(sorted(outbounds, reverse=False), key= lambda x: x[1])
        inbounds_sorted=sorted(sorted(inbounds, reverse=True), key= lambda x: x[1])

        while (outbounds_sorted and inbounds_sorted):
            if inbounds_sorted[0][0]-outbounds_sorted[0][0] > timedelta(days=1):
                # print ("the best option is: ", outbounds_sorted[0], "-->", inbounds_sorted[0])
                # print ("stay duration is: ", inbounds_sorted[0][0]-outbounds_sorted[0][0])
                # print ("price is: ",inbounds_sorted[0][1]+outbounds_sorted[0][1])
                return outbounds_sorted[0], inbounds_sorted[0]
            #print ('Next attempt... outbounds:')
            # for item in outbounds_sorted:
            #     print (item)
            # print ("returns:")
            # for item in inbounds_sorted:
            #     print (item)
            if len(outbounds_sorted)> len (inbounds_sorted):
                outbounds_sorted.pop(0)
            else:
                inbounds_sorted.pop(0)
        return False, False

    @staticmethod
    def get_cheapest_return(origin, date_outbound, date_inbound, airports, limit=1000):


        flights=[]
        destinations = WizzairHandle.get_destinations(origin, date_outbound)
        if not destinations:
            return False
        print ('destinations available from Wizzair are:', destinations)
        # print ('for debugging purpose slicing to 5 items...')
        # destinations=destinations[:5]
        # print ('destinations available from Wizzair are:', destinations)
        for airport in destinations:
            destination_airport = airports.get(airport)
            if not destination_airport or destination_airport == origin:
                continue
            
            my_route = Route(origin, destination_airport)
            flight = WizzairHandle.get_return(my_route, date_outbound, date_inbound)
            print ('requesting flights from ',origin,' to ', destination_airport )
            if flight:
                flights.extend(flight)
        #print (flights)

        
        return flights
        

'''
https://be.wizzair.com/11.17.0/Api/search/search

{"isFlightChange":false,"flightList":[{"departureStation":"EIN","arrivalStation":"BUD","departureDate":"2022-01-23"}],"adultCount":1,"childCount":0,"infantCount":0,"wdc":true}
this requires cookies :(
'''