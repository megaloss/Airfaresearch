from classes import Airport
import http.client, urllib.request, urllib.parse, urllib.error, json , os
MY_KEY = os.getenv('TRANSAVIA_KEY')


class TransaviaHandle:

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
            return False
        airport_dict = {}
        for airport in airports:
            airport_dict[airport['id']] = Airport(airport['id'],airport['name'], airport['city'], airport['country']['code'], [airport['geoCoordinates']['latitude'], airport['geoCoordinates']['longitude']])
        return airport_dict
