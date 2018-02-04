import csv
import os
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request, build_opener, HTTPErrorProcessor
from urllib.error import HTTPError

API_JSON_ENCODING = 'utf-8'
API_BASE_URL = 'http://api.meetup.com/'
EVENTS_URI = 'events'
GROUP_NAME = 'Kubernetes-London'

try:
    try:
        import cjson
        parse_json = lambda s: cjson.decode(s.decode(API_JSON_ENCODING), True)
    except ImportError:
        try:
            import json
            parse_json = lambda s: json.loads(s.decode(API_JSON_ENCODING))
        except ImportError:
            import simplejson
            parse_json = lambda s: simplejson.loads(s.decode(API_JSON_ENCODING))
except:
    print("Error - your system is missing support for a JSON parsing library.")

class MeetupHTTPErrorProcessor(HTTPErrorProcessor):
    def http_response(self, request, response):
        try:
            return HTTPErrorProcessor.http_response(self, request, response)
        except HTTPError as e:
            data = e.read()

            try:
                error_json = parse_json(data)
            except ValueError:
                print('Value error when trying to parse JSON from response data:\n%s' % response)
                raise

            if e.code == 401:
                raise UnauthorizedError(error_json)
            elif e.code in ( 400, 500 ):
                raise BadRequestError(error_json)
            else:
                raise ClientException(error_json)

class Meetup(object):
    opener = build_opener(MeetupHTTPErrorProcessor)
    # Act like a real browser or else CloudFlare protection
    # blocks the request as banned
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

    def __init__(self, api_key):
        """Initializes a new session with an api key that will be added
        to subsequent api calls"""
        self.api_key = api_key
        self.opener.addheaders = [('Accept-Charset', 'utf-8')]

    def args_str(self, url_args):
        if self.api_key:
            url_args['key'] = self.api_key
        return urlencode(url_args)

    def _fetch(self, uri, **url_args):
        args = self.args_str(url_args)
        url = API_BASE_URL + uri + '/' + "?" + args

        print("requesting %s" % (url))
        return parse_json(self.opener.open(url).read())

    def get_events(self, **params):
        uri = GROUP_NAME + '/' + EVENTS_URI
        return self._fetch(uri, **params)

if __name__ == '__main__':
    api_key = os.environ["MEETUP_API_KEY"]
    if api_key == '':
        raise ValueError("Meetup API key not found")
    # create Meetup api client
    client = Meetup(api_key)
    # fetch first 200 events in descending order
    events = client.get_events(sign=True, scroll='recent_past', desc=True)
    # we need to augment the data with rsvp_limit field in case
    # the event didnt have any RSVP limit set
    def rsvp_limit(event):
        if 'rsvp_limit' not in event:
            event['rsvp_limit'] = 0
        return event

    events = list(map(rsvp_limit, events))
    # pick the data and write them into CSV file
    # we need to convert 'created' time file into readable date time
    data = [(e['created'], e['local_date'], e['local_time'], e['venue']['name'], e['name'],
             e['rsvp_limit'], e['yes_rsvp_count'], e['waitlist_count']) for e in events]
    with open('events.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['announced', 'date', 'time', 'venue', 'name',
                          'rsvp_limit', 'rsvp_yes', 'waitlist'])
        for row in data:
            csv_out.writerow(row)

