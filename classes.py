class Airport:
    airports={}

    @staticmethod
    def get_airport(airport):
        return Airport.airports[airport]


    def __init__(self, id_code, name, city, country, location):
        self.id = id_code
        self.name = name
        self.city = city
        self.country = country
        self.location = dict()
        self.location['latitude'] = location[0]
        self.location['longitude'] = location[1]
        Airport.airports[id_code] = self

    def __repr__(self):
        return f" is an airport called {self.name} in the city of {self.city} in {self.country}. Its coordinates are :{self.location}\n"


class Route:
    def __init__(self, from_airport: Airport , to_airport: Airport):
        self.from_airport = from_airport
        self.to_airport = to_airport

    def __repr__(self):
        return f" is a route from {self.from_airport} to {self.to_airport}"

    def invert(self):
        return Route(self.to_airport, self.from_airport)

    def distance(self):
        from math import sin, cos, sqrt, atan2, radians

        R = 6373.0 # Earth radius in km

        lat1 = radians(self.from_airport.location['latitude'])
        lon1 = radians(self.from_airport.location['longitude'])
        lat2 = radians(self.to_airport.location['latitude'])
        lon2 = radians(self.to_airport.location['longitude'])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c


class SingleFare:
    def __init__(self, route, departure_date, arrival_date, price, flight_number):
        self.route = route
        self.departure_date = departure_date
        self.arrival_date = arrival_date
        self.price = price
        self.flight_number = flight_number

    def __repr__(self):
        return f'Flight from {self.route.from_airport.name} to {self.route.to_airport.name} on {self.departure_date} costs {self.price} EUR'


class ReturnFare:
    def __init__(self, outbound, inbound):
        if outbound.route.to_airport != inbound.route.from_airport or outbound.route.from_airport != inbound.route.to_airport :
            print ("That is not a return flight !!!")
            return
        self.outbound = outbound
        self.inbound = inbound
        self.price = self.outbound.price + self.inbound.price

    def __repr__(self):
        return f'Flight from {self.outbound.route.from_airport.name} to {self.outbound.route.to_airport.name} on {self.outbound.departure_date}\n' \
               f'Return on {self.inbound.departure_date}. Total price is {self.price:.2f}. Total distance {self.distance()} km. That is {self.price/self.distance()} EUR/km \n'\
               f'You stay at your destination for {self.stay_period()}'

    def distance(self):
        return self.outbound.route.distance() + self.inbound.route.distance()

    def stay_period(self):
        return self.inbound.departure_date - self.outbound.arrival_date