import wizzair
from ryanair import RyanairHandle
from transavia import TransaviaHandle
from wizzair import WizzairHandle
from datetime import datetime, timedelta, date
import pickle
from classes import Airport, Route, SingleFare, ReturnFare
from utils import encode_datetime
airports = {}


def refresh_airports_dict():
    handles = [RyanairHandle(), TransaviaHandle(), WizzairHandle()]
    for handle in handles:
        data = handle.read_airports()
        if data:
            airports.update(data)
        else:
            print('Failed fo obtain data from ', handle)
    pickle.dump(airports, open('airports.p','wb'))

#refresh_airports_dict()
#exit(0)
#my_handle = RyanairHandle()
#my_handle = TransaviaHandle()
my_handle = WizzairHandle()
airports = pickle.load(open('airports.p', 'rb'))
'''
# create return flight from a list of 2 separate flights
my_flights = []

my_flights.append({'route': Route(airports['EIN'], airports['AGP']),
                   'date': datetime(2021, 12, 1, 12, 00)})
my_flights.append({'route': Route(airports['AGP'], airports['EIN']),
                   'date': datetime(2021, 12, 22, 12, 00)})
my_trip = []
for flight in my_flights:
    my_fares = my_handle.get_fare(flight['route'], flight['date'])
    if my_fares:
        for my_fare in my_fares:
            my_trip.append(my_fare)

trip = False
if len(my_trip) == 2:
    trip = ReturnFare(my_trip[0], my_trip[1])
print(trip)


print('-'*50)

# 2-nd way to create return flight
my_route = Route(airports['EIN'], airports['AGP'])
new_trip = my_handle.get_return(my_route, datetime(2021, 12, 15), datetime(2021, 12, 22))
for trip in new_trip:
    print(trip)

'''


'''
destinations = [airports['EIN'], airports['AMS']]

date_from = (datetime(2021, 12, 15),datetime(2021, 12, 20))
date_to = (datetime(2021, 12, 30),datetime(2022, 1, 7))
#fares=my_handle.get_cheapest_fare(destinations, date_from, airports)

fares=my_handle.get_cheapest_return(destinations, date_from, date_to, airports)

fares.sort(key=lambda x: x.price)
if fares:
    for fare in fares:
        print (fare)
else:
    print ('nothing found !')
'''
#airports = my_handle.read_airports()
origin = airports['EIN']
destination = airports['BUD']
my_route = Route (origin, destination)
date_from = (datetime(2022, 1, 23),datetime(2022, 1, 31))
date_to = (datetime(2022, 1, 25),datetime(2022, 2, 11))
flights=[]

# destinations = my_handle.get_destinations(origin, date_from)
# for airport in destinations:   
#     if airports[airport] == origin:
#         continue
    

#     my_route = Route(origin, airports[airport])

#     flight = my_handle.get_return(my_route, date_from, date_to)
#     if flight:
#         flights.append(flight)
#flights = my_handle.get_cheapest_return(origin, date_from, date_to, airports)
#print (flights[0].outbound.flight_number)
#response = my_handle.get_return(my_route, date_from, date_to)
#print (response)
destinations = (my_handle.get_destinations(origin, date_from))
count=0
for dest in destinations:
    destination = airports.get(dest)
    if destination:
        my_route=Route (origin,destination)
        fare = my_handle.get_return(my_route, date_from, date_to)
        if fare:
            print (fare)
            count+=1

print ("total fares found:", count)
