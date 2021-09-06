import wizzair
from ryanair import RyanairHandle
from transavia import TransaviaHandle
from wizzair import WizzairHandle
from datetime import datetime, timedelta, date
import pickle
from classes import Airport, Route, SingleFare, ReturnFare

airports = {}


def refresh_airports_dict():
    handles = [RyanairHandle(), TransaviaHandle(), WizzairHandle()]
    for handle in handles:
        data = handle.read_airports()
        if data:
            airports.update(data)
        else:
            print('Failed fo obtain data from ', handle)
    pickle.dump(airports, open('airports_test.p','wb'))


my_handle = RyanairHandle()
airports = pickle.load(open('airports.p', 'rb'))

# create return flight from a list of 2 separate flights
my_flights = []

my_flights.append({'route': Route(airports['BRU'], airports['LCA']),
                   'date': datetime(2021, 10, 15, 12, 00)})
my_flights.append({'route': Route(airports['LCA'], airports['BRU']),
                   'date': datetime(2021, 10, 25, 12, 00)})
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
my_route = Route(airports['BRU'], airports['LCA'])
new_trip = my_handle.get_return(my_route, datetime(2021, 10, 18), datetime(2021, 10, 25))
for trip in new_trip:
    print(trip)

