from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import wizzair
from ryanair import RyanairHandle
from transavia import TransaviaHandle
from wizzair import WizzairHandle
from datetime import datetime, timedelta, date
import pickle
from classes import Airport, Route, SingleFare, ReturnFare
from utils import encode_datetime
airports = {}

import pickle
app=FastAPI()


origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8000",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    "http://192.168.0.15:8000",
    "http://192.168.0.15",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

airports= pickle.load(open('airports.p', 'rb'))
my_handles = [TransaviaHandle(),RyanairHandle()]
origin = [airports['RTM'], airports['EIN'], airports['AMS'], airports['CRL'], airports['BRU']]
date_from = (datetime(2022, 2, 25),datetime(2022, 2, 28))
date_to = (datetime(2022, 3, 6),datetime(2022, 3, 8))

@app.get('/get_origin_airports/')
async def get_origin_airports():
    return origin

@app.get('/get_flights_from/{airport_id}')
async def get_flights_from(airport_id):
    my_route = Route(origin, airports[airport_id])
    flights = my_handle.get_return(my_route, date_from, date_to)
    return flights

@app.get('/get_all_flights_from/{airport_id}')
async def get_all_flights_from(airport_id, outbound_date_from=date_from[0],outbound_date_to=date_from[1], inbound_date_from=date_to[0],inbound_date_to=date_to[1]):
    airport_from = airports[airport_id]
    outbound_date_from = datetime.strptime(outbound_date_from,'%d-%m-%Y')
    outbound_date_to = datetime.strptime(outbound_date_to,'%d-%m-%Y')
    outbound_date=(outbound_date_from,outbound_date_to)
    inbound_date_from = datetime.strptime(inbound_date_from,'%d-%m-%Y')
    inbound_date_to = datetime.strptime(inbound_date_to,'%d-%m-%Y')
    inbound_date=(inbound_date_from,inbound_date_to)
    print (f'got request for {airport_id}, outbound_date = {(outbound_date_from, outbound_date_to)}, inbound_date= {(inbound_date_from, inbound_date_to)}')
    flights=[]
    for handle in my_handles:
        extras=handle.get_cheapest_return(airport_from, outbound_date, inbound_date, airports)
        if extras:
            flights.extend(extras)
    print (flights)
    return flights