'''
1. dates availability and cheapest fares
POST to https://web.flypgs.com/pegasus/cheapest-fare
JSON:
    {"viewType":"DAILY","currency":"GBP","flightSearch":{"departureDate":"2022-02-01","departurePort":"SAW","returnDate":"2022-02-01","arrivalPort":"EIN"},"finalMonth":false,"departureFlightTypeSelection":[],"departureFlightTimeSelection":[],"returnFlightTypeSelection":[],"returnFlightTimeSelection":[]}
headers:
    accept: application/json, text/plain, */*
    accept-encoding: gzip, deflate, br
    accept-language: en
    access-control-allow-origin: *
    cache-control: no-cache, no-store, must-revalidate
    content-length: 300
    content-type: application/json
    cookie: LANGUAGE=en; LOGGED_IN=false; BUNDLE-SELECTION=SUPER_ECO; CKP={"tgOne":false,"tgTwo":false}
    dnt: 1
    origin: https://web.flypgs.com
    pragma: no-cache
    sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Linux"
    sec-fetch-dest: empty
    sec-fetch-mode: cors
    sec-fetch-site: same-origin
    user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36
    x-platform: web
    x-version: 1.24.0

response:
    
    departureCheapestRoute -> monthlyCheapestList -> [1] -> dailyCheapestList -> []



2. flights availability
POST to https://web.flypgs.com/pegasus/availability
JSON:
    {"flightSearchList":[{"departurePort":"EIN","arrivalPort":"SAW","departureDate":"2022-01-30","returnDate":"2022-02-05"}],"adultCount":1,"childCount":0,"infantCount":0,"currency":"EUR","dateOption":1,"ffRedemption":false,"totalPoints":null,"personnelFlightSearch":false,"operationCode":"TK","affiliate":{"id":null},"bookingType":"BOOKING"}
headers:
    accept: application/json, text/plain, */*
    accept-encoding: gzip, deflate, br
    accept-language: en
    access-control-allow-origin: *
    cache-control: no-cache, no-store, must-revalidate
    content-length: 338
    content-type: application/json
    dnt: 1
    origin: https://web.flypgs.com
    pragma: no-cache
    sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Linux"
    sec-fetch-dest: empty
    sec-fetch-mode: cors
    sec-fetch-site: same-origin
    user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36
    x-platform: web
    x-version: 1.24.0
    cookie: LANGUAGE=en; LOGGED_IN=false


'''