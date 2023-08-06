# -*- coding: utf-8 -*-
"""
Yelp API v2.0 code sample.

This program demonstrates the capability of the Yelp API version 2.0
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Please refer to http://www.yelp.com/developers/documentation for the API documentation.

This program requires the Python oauth2 library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
import argparse
import json
import re
import sys
import urllib
import urllib2
import unicodedata

import oauth2


API_HOST = 'api.yelp.com'
DEFAULT_TERM = ''
DEFAULT_LOCATION = 'Philadelphia, PA'
SEARCH_LIMIT = 20
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = "jOkLJFVDtBLs_fnrFPAvzA"
CONSUMER_SECRET = "W1MkE_Ed19AC0KEvzbz3Y0saQn0"
TOKEN = "oR02u7IT98l5ZYcTdZh8Eyp2zlYQfaBB"
TOKEN_SECRET = "owO2DZ6TgKH7v1iAkBaSMUpTuuE"

CATS = {
    'Arcades': 2,
    'Art Galleries': 3,
    'Arts & Entertainment': 1,
    'Botanical Gardens': 4,
    'Cabaret': 5,
    'Casinos': 6,
    'Cinema': 7,
    'Country Clubs': 8,
    'Cultural Center': 9,
    'Festivals': 10,
    'Jazz & Blues': 11,
    'LAN Centers': 12,
    'Museums': 13,
    'Music Venues': 14,
    'Observatories': 15,
    'Opera & Ballet': 16,
    'Paint & Sip': 17,
    'Performing Arts': 18,
    'Planetarium': 19,
    'Professional Sports Teams': 20,
    'Psychics & Astrologers': 21,
    'Race Tracks': 22,
    'Social Clubs': 23,
    'Stadiums & Arenas': 24,
    'Ticket Sales': 25,
    'Wine Tasting Room': 27,
    'Wineries': 26,
    'Bingo Halls': 28,
}


def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response


def search(term, location, offset=0):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset': offset,
        'category_filter': 'arts',
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)


def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    import json

    received = 0
    total = 1
    output = []
    while (received < total):
        response = search(term, location, received)
        total = response.get('total')
        received += SEARCH_LIMIT
        businesses = response.get('businesses')

        for i in businesses:
            if i['is_closed']:
                continue
            coordinate = i['location'].get('coordinate', '')
            if coordinate:
                latlong = 'POINT(%s %s)' % (coordinate['longitude'], coordinate['latitude'])
            else:
                latlong = ''
            output.append({
                'fields': {
                    'name': i['name'],
                    'slug': slugify(i['name']),
                    'phone': i.get('phone', ''),
                    'venue_type': CATS[i['categories'][0][0]],
                    'address': "%s, %s, %s %s" % (
                        " ".join(i['location']['address']),
                        i['location']['city'], i['location']['state_code'], i['location'].get('postal_code', '')
                    ),
                    'special_instructions': '',
                    'website': '',
                    'latlong': latlong,
                },
                'model': 'eventcalendar.venue',
            })
    with open('venues.json', 'w') as f:
        f.write(json.dumps(output))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM, type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location', default=DEFAULT_LOCATION, type=str, help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except urllib2.HTTPError as error:
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))


if __name__ == '__main__':
    main()
