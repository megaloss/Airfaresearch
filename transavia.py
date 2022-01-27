from classes import Airport, SingleFare, ReturnFare, Route
from utils import encode_datetime
import http.client, urllib.request, urllib.parse, urllib.error, json , os
import logging

# Set up logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
hdlr = logging.FileHandler('transavia.log')
fmt = logging.Formatter('%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s')

hdlr.setFormatter(fmt)
logger.addHandler(hdlr)

MY_KEY = os.getenv('TRANSAVIA_KEY')
if not MY_KEY:
    logger.error('No API key found !')
# logger.info('The Transavia key is ' + MY_KEY)

class TransaviaHandler:
    @staticmethod
    def convert_date(date):
        return date.strftime('%Y%m%d')

    @staticmethod
    def read_airports():
        headers = {
            # Request headers
            'apikey': MY_KEY,
        }

        params = urllib.parse.urlencode({
        })

        try:
            conn = http.client.HTTPSConnection('api.transavia.com')
            conn.request("GET", "/v2/airports/?%s" % params, "{body}", headers)
            response = conn.getresponse()
            response = response.read()
            airports = json.loads(response)

            conn.close()
        except Exception as e:
            print('Transavia retrieving data Error: ', e)
            return []
        airport_dict = {}
        for airport in airports:
            airport_dict[airport['id']] = Airport(airport['id'],airport['name'], airport['city'], airport['country']['code'], [airport['geoCoordinates']['latitude'], airport['geoCoordinates']['longitude']])
        return airport_dict

    @staticmethod
    def get_fare(route, date,  limit=1000):
        headers = {
            'apikey': MY_KEY,
        }

        if isinstance(date, tuple):
            originDepartureDate = TransaviaHandler.convert_date(date[0]) + '-' + \
                                  TransaviaHandler.convert_date(date[1])
        else:
            originDepartureDate = TransaviaHandler.convert_date(date)

        params = urllib.parse.urlencode({
            'origin':  route.from_airport.id,
            'destination': route.to_airport.id,
            'originDepartureDate': originDepartureDate,
            'limit': limit,

        })

        try:
            conn = http.client.HTTPSConnection('api.transavia.com')

            conn.request("GET", "/v1/flightoffers/?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            data = json.loads(data)
            conn.close()
        except Exception as e:
            logger.error("[ERROR: {0}]".format(e))
            return []
        if not data or not data.get('resultSet'):
            return []
        fares=[]
        for item in data['flightOffer']:
            departure_date = encode_datetime(item['outboundFlight']['departureDateTime'])
            arrival_date = encode_datetime(item['outboundFlight']['arrivalDateTime'])
            price = item['pricingInfoSum']['totalPriceOnePassenger']
            flight_number = item['outboundFlight']['flightNumber']
            fares.append(SingleFare(route, departure_date, arrival_date, price, flight_number))
        return fares

    @staticmethod
    def get_return(route, date_outbound, date_inbound, limit=1000):
        headers = {
            'apikey': MY_KEY,
        }
        if isinstance(date_outbound,  tuple):
            originDepartureDate = TransaviaHandler.convert_date(date_outbound[0])+'-'+ \
                                  TransaviaHandler.convert_date(date_outbound[1])
        else:
            originDepartureDate = TransaviaHandler.convert_date(date_outbound)
        if isinstance(date_inbound,tuple):
            destinationDepartureDate = TransaviaHandler.convert_date(date_inbound[0]) + '-' + \
                                  TransaviaHandler.convert_date(date_inbound[1])
        else:
            destinationDepartureDate = TransaviaHandler.convert_date(date_inbound)
        
        
            
        params = urllib.parse.urlencode({
            'origin': route.from_airport.id,
            'destination': route.to_airport.id,
            'originDepartureDate': originDepartureDate,
            'destinationDepartureDate': destinationDepartureDate,
            'lowestPricePerDestination': 'T',
            'limit': limit,

        })



        try:
            conn = http.client.HTTPSConnection('api.transavia.com')
            conn.request("GET", "/v1/flightoffers/?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            if data:
                data = json.loads(data)
            else:
                return []
            
        except Exception as e:
           logger.error("[ERROR: {0}]".format(e))
           return []

        if not data or not data.get('resultSet'):
            return []
        fares = []
        for item in data['flightOffer']:
            departure_date = encode_datetime(item['outboundFlight']['departureDateTime'])
            arrival_date = encode_datetime(item['outboundFlight']['arrivalDateTime'])
            price = item['outboundFlight']['pricingInfo']['totalPriceOnePassenger']
            flight_number = item['outboundFlight']['flightNumber']
            outbound = SingleFare(route, departure_date, arrival_date, price, flight_number)
            departure_date = encode_datetime(item['inboundFlight']['departureDateTime'])
            arrival_date = encode_datetime(item['inboundFlight']['arrivalDateTime'])
            price = item['inboundFlight']['pricingInfo']['totalPriceOnePassenger']
            flight_number = item['inboundFlight']['flightNumber']
            inbound=SingleFare(route.invert(), departure_date, arrival_date, price, flight_number)

            fares.append(ReturnFare(outbound, inbound))

        return fares

    @staticmethod
    def get_cheapest_fare(origin, date, airports, limit=1000):
        headers = {
            'apikey': MY_KEY,
        }
        if isinstance(origin,list):
            airport_list=''
            for location in origin:
                airport_list+=location.id+','
        else:
            airport_list = origin.id
        if isinstance(date, tuple):
            originDepartureDate = TransaviaHandler.convert_date(date[0]) + '-' + \
                                  TransaviaHandler.convert_date(date[1])
        else:
            originDepartureDate = TransaviaHandler.convert_date(date)

        params = urllib.parse.urlencode({
            'origin': airport_list,
            'originDepartureDate': originDepartureDate,
            'limit': limit,

        })

        try:
            conn = http.client.HTTPSConnection('api.transavia.com')

            conn.request("GET", "/v1/flightoffers/?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            data = json.loads(data)
            conn.close()
        except Exception as e:
            logger.error("[ERROR: {0}]".format(e))
            return []
        if not data or not data.get('resultSet'):
            return []
        fares = []
        for item in data['flightOffer']:
            departure_date = encode_datetime(item['outboundFlight']['departureDateTime'])
            arrival_date = encode_datetime(item['outboundFlight']['arrivalDateTime'])
            price = item['pricingInfoSum']['totalPriceOnePassenger']
            flight_number = item['outboundFlight']['flightNumber']
            flight_from = airports[item['outboundFlight']['departureAirport']['locationCode']]
            flight_to = airports[item['outboundFlight']['arrivalAirport']['locationCode']]
            fares.append(SingleFare(Route(flight_from,flight_to), departure_date, arrival_date, price, flight_number))
        return fares

    @staticmethod
    def get_cheapest_return(origin, date_outbound, date_inbound, airports, limit=1000):
        headers = {
            'apikey': MY_KEY,
        }
        if isinstance(origin,list):
            airport_list=''
            for location in origin:
                airport_list+=location.id+','
        else:
            airport_list = origin.id
        if isinstance(date_outbound,  tuple):
            originDepartureDate = TransaviaHandler.convert_date(date_outbound[0])+'-'+ \
                                  TransaviaHandler.convert_date(date_outbound[1])
        else:
            originDepartureDate = TransaviaHandler.convert_date(date_outbound)
        if isinstance(date_inbound,tuple):
            destinationDepartureDate = TransaviaHandler.convert_date(date_inbound[0]) + '-' + \
                                  TransaviaHandler.convert_date(date_inbound[1])
        else:
            destinationDepartureDate = TransaviaHandler.convert_date(date_inbound)



        params = urllib.parse.urlencode({
            'origin': airport_list,
            'originDepartureDate': originDepartureDate,
            'destinationDepartureDate': destinationDepartureDate,
            'lowestPricePerDestination': 'T',
            'limit': limit,

        })

        try:
            conn = http.client.HTTPSConnection('api.transavia.com')
            conn.request("GET", "/v1/flightoffers/?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            if not data:
                return []
            data = json.loads(data)
            conn.close()
        except Exception as e:
            logger.error("[ERROR: {0}]".format(e))
            return []

        if not data or not data.get('resultSet'):
            return []
        fares = []
        for item in data['flightOffer']:
            departure_date = encode_datetime(item['outboundFlight']['departureDateTime'])
            arrival_date = encode_datetime(item['outboundFlight']['arrivalDateTime'])
            price = item['outboundFlight']['pricingInfo']['totalPriceOnePassenger']
            flight_number = item['outboundFlight']['flightNumber']
            flight_from = airports[item['outboundFlight']['departureAirport']['locationCode']]
            flight_to = airports[item['outboundFlight']['arrivalAirport']['locationCode']]
            outbound = SingleFare(Route(flight_from,flight_to), departure_date, arrival_date, price, flight_number)
            departure_date = encode_datetime(item['inboundFlight']['departureDateTime'])
            arrival_date = encode_datetime(item['inboundFlight']['arrivalDateTime'])
            price = item['inboundFlight']['pricingInfo']['totalPriceOnePassenger']
            flight_number = item['inboundFlight']['flightNumber']
            flight_from = airports[item['inboundFlight']['departureAirport']['locationCode']]
            flight_to = airports[item['inboundFlight']['arrivalAirport']['locationCode']]
            inbound = SingleFare(Route(flight_from,flight_to), departure_date, arrival_date, price, flight_number)

            fares.append(ReturnFare(outbound, inbound))

        return fares


