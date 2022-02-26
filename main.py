from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ryanair import RyanairHandler
from transavia import TransaviaHandler
from wizzair import WizzairHandler
from easyjet import EasyjetHandler
from datetime import datetime, timedelta, date
from classes import Airport, Route, SingleFare, ReturnFare
from utils import encode_datetime
from os import path



airports = {}

import pickle
app=FastAPI()
import logging
import requests

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
origins = [
    "http://0.0.0.0",
    "https://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://192.168.0.15",
    "http://flexifly.nl",
    "http://www.flexifly.nl",
    "https://www.flexifly.nl",
    "http://flexifly.nl",
    "https://flexifly.nl"

]

# try:
#     my_ip = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
#     my_ip = my_ip.text
#     origins.append('http://' + my_ip)
# except:
#     print ('Public ip not found')


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

airports_dict='airports.p'

my_handlers = [TransaviaHandler,RyanairHandler,EasyjetHandler]
#WizzairHandler, - removed
if not path.exists(airports_dict):
    airports={}
    for handler in my_handlers:
        data=handler.read_airports()
        #print (data)
        airports.update (data)
    print ('just loaded ', len(airports), 'airports')
    with open (airports_dict,'wb') as f:
        pickle.dump(airports,f)

#my_handlers = [TransaviaHandler,RyanairHandler,WizzairHandler]

airports= pickle.load(open('airports.p', 'rb'))


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
    print('working...')
    airport_from = airports.get(airport_id)
    if not airport_from:
        return []

    # if airport_id=='CRL':
    #     return 'Oh crap !'
    
    outbound_date_from = datetime.strptime(outbound_date_from,'%d-%m-%Y')
    outbound_date_to = datetime.strptime(outbound_date_to,'%d-%m-%Y')
    outbound_date=(outbound_date_from,outbound_date_to)
    inbound_date_from = datetime.strptime(inbound_date_from,'%d-%m-%Y')
    inbound_date_to = datetime.strptime(inbound_date_to,'%d-%m-%Y')
    inbound_date=(inbound_date_from,inbound_date_to)
    logging.debug (f'got request for {airport_id}, outbound_date = {(outbound_date_from, outbound_date_to)}, inbound_date= {(inbound_date_from, inbound_date_to)}')
    flights=[]
    
    for handler in my_handlers:
        if handler == WizzairHandler or handler == RyanairHandler:
            extras= await handler.get_cheapest_return(airport_from, outbound_date, inbound_date, airports)
        else:
            extras=handler.get_cheapest_return(airport_from, outbound_date, inbound_date, airports)
        if extras:
            logging.debug ('Got extras:',extras)
            flights.extend(extras)
        else: 
            logging.info (handler.__name__ + 'got empty array, skipping')
    if not flights:
        logging.info ("No flights found !")
        return []
    print ('Done !')
    return flights
