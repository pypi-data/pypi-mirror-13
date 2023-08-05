from requests import Request
from requests import Session
from requests.compat import urljoin
from queue import Queue
from threading import Thread, Timer
import time


class Config(object):

    API_PATHS = {
        'get_summoner_objects_by_id': '/api/lol/{region}/v1.4/summoner/{summonerIds}',
        'get_summoner_objects_by_name': '/api/lol/{region}/v1.4/summoner/by-name/{summonerNames}',
        'get_masteries_by_id': '/api/lol/{region}/v1.4/summoner/{summonerIds}/masteries',
        'get_summoner_name_by_id': '/api/lol/{region}/v1.4/summoner/{summonerIds}/name',
        'get_runes_by_id': '/api/lol/{region}/v1.4/summoner/{summonerIds}/runes',
        'get_match_list_by_id': '/api/lol/{region}/v2.2/matchlist/by-summoner/{summonerId}',
        'get_match_by_id': '/api/lol/{region}/v2.2/match/{matchId}',
        'get_champion_list': '/api/lol/static-data/{region}/v1.2/champion',
        'get_champion_by_id': '/api/lol/static-data/{region}/v1.2/champion/{id}',
        'get_item_by_id': '/api/lol/static-data/{region}/v1.2/item/{id}'
        'get_language_strings'
    }

    REGIONAL_ENDPOINTS = {
        'BR':     'br.api.pvp.net',
        'EUNE':   'eune.api.pvp.net',
        'EUW':    'euw.api.pvp.net',
        'KR':     'kr.api.pvp.net',
        'LAN':    'lan.api.pvp.net',
        'LAS':    'las.api.pvp.net',
        'NA':     'na.api.pvp.net',
        'OCE':    'oce.api.pvp.net',
        'TR':     'tr.api.pvp.net',
        'RU':     'ru.api.pvp.net',
        'PBE':    'pbe.api.pvp.net',
        'Global': 'global.api.pvp.net',
    }

    def __init__(self, region):
        self.api_url = 'https://' + self.REGIONAL_ENDPOINTS[region]

    def __getitem__(self, key):
        prefix = self.api_url
        return urljoin(prefix, self.API_PATHS[key])


class RequestHandler(object):
    """
        Just change it so there is no request queue, might not even need the return queue
        maybe use a simpler time module implementation. However this still works so leave
        it for now. This follows the desired usage. its just weirdly complex. I guess it
        might allow for multi threaded usage of the handler? Unsure. Leave it for now. It
        might actually be great for multi threaded querying. Or do nothing idk.
    """

    def __init__(self):
        self.http = Session()
        self.queue = Queue()  # todo Put queue as part of Request Handler, Add Method that adds requests to queue
        self.return_queue = Queue()
        self.requester = Thread(target=self._request)

        self.request10s = 0
        self.request10m = 0

        self.limit10s = 10  # Max number of requests per 10 seconds.
        self.limit10m = 500  # Max number of requests per 10 minutes.

        self.requester.setDaemon(True)
        self.requester.start()
        self.reset10m()
        self.reset10s()

    def send_request(self, prepared_request):
        # print('Sending')
        response = self.http.send(prepared_request)  # todo rename response eventually
        if response.status_code == 429:  # todo try to tackle underlying problem?
            print('Limit Hit, retrying after %s seconds' % response.headers['retry-after'])
            time.sleep(int(response.headers['retry-after']))
            return self.send_request(prepared_request)
        else:
            # print('Returning')
            return response  # todo rework? might be far more complicated than necessary

    def _request(self):
        # print("Requesting")

        while True:
            if self.request10s < self.limit10s and self.request10m < self.limit10m:
                request = self.queue.get()
                prepared_request = self.http.prepare_request(request)
                response = self.send_request(prepared_request)
                self.queue.task_done()
                if '/lol/static-data' not in request.url:  # todo make it fancy dancy
                    self.request10s += 1
                    self.request10m += 1
                self.return_queue.put(response)

    def reset10s(self):
        Timer(10, self.reset10s).start()
        self.request10s = 0

    def reset10m(self):
        Timer(600, self.reset10m).start()
        self.request10m = 0

    def request(self, request, return_json=True):
        # print('Putting')  # Yeah, almost definitely too complicated
        self.queue.put(request)
        response = self.return_queue.get()
        if response.status_code == 400:
            raise KeyError('Bad Request, maybe incorrect parameters')
        elif response.status_code == 401:
            raise ValueError('Incorrect API Key, double check it')
        elif response.status_code == 404:
            raise IndexError('Not found, possibly does not exist')
        elif response.status_code == 429:
            raise Exception('This should not happen')
        elif response.status_code == 500:
            raise Exception('Unexpected condition, server at fault')
        elif response.status_code == 503:
            raise Exception('Service unavailable, retry later')
        else:
            if return_json:
                return response.json()
            else:
                return response


class BaseLoL(object):

    class Params(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)  # todo delete later
            for k, v in dict(*args, **kwargs).items():
                if v is not None:
                    self[k] = v  # todo Might have to set a special case for empty dunno yet

    def __init__(self):
        self.region = 'oce'
        self.config = Config('OCE')
        self.handler = RequestHandler()  # Handler takes a Request object
        self.api_key = '006851ab-d1d6-47c3-99db-46359cf26d48'

    @staticmethod
    def comma_separate(input_list):
        if type(input_list) == list:
            return ','.join(str(x).lower().replace(" ", "") for x in input_list)
        elif type(input_list) == str:
            return input_list.lower().replace(" ", "")
        elif type(input_list) == int:
            return str(input_list)
        elif input_list is None:
            return None
        else:
            raise TypeError('Only accepts lists and strings')

    def create_request(self, key, params=None, **kwargs):
        url = self.config[key].format(region=self.region, **kwargs)
        url = urljoin(url, '?api_key=' + self.api_key)
        request = Request('GET', url, params=params)
        return request


class SummonerMixin(BaseLoL):

    def get_summoner_object(self, name=None, summoner_id=None):
        if name is not None and summoner_id is not None:
            raise ValueError('Only accepts either names or summoner ids')
        elif name is not None:
            name = self.comma_separate(name)
            request = self.create_request('get_summoner_objects_by_name', summonerNames=name)
            return self.handler.request(request)
        elif summoner_id is not None:
            summoner_id = self.comma_separate(summoner_id)
            request = self.create_request('get_summoner_objects_by_id', summonerIds=summoner_id)
            return self.handler.request(request)
        else:
            raise ValueError('Requires either names or summoner ids')

    def get_masteries(self, summoner_id):
        summoner_id = self.comma_separate(summoner_id)
        request = self.create_request('get_masteries_by_id', summonerIds=summoner_id)
        return self.handler.request(request)

    def get_summoner_name(self, summoner_id):
        summoner_id = self.comma_separate(summoner_id)
        request = self.create_request('get_summoner_name_by_id', summonerIds=summoner_id)
        return self.handler.request(request)

    def get_runes(self, summoner_id):
        summoner_id = self.comma_separate(summoner_id)
        request = self.create_request('get_runes_by_id', summonerIds=summoner_id)
        return self.handler.request(request)


class MatchListMixin(BaseLoL):

    def get_match_list(self, summoner_id, champion_ids=None, ranked_queues=None,
                       season=None, begin_time=None, end_time=None,
                       begin_index=None, end_index=None):
        champion_ids = self.comma_separate(champion_ids)
        params = self.Params({
            ('championIds', champion_ids),
            ('rankedQueues', ranked_queues),
            ('season', season),
            ('beginTime', begin_time),
            ('endTime', end_time),
            ('beginIndex', begin_index),
            ('endIndex', end_index),
        })
        request = self.create_request('get_match_list_by_id', summonerId=summoner_id, params=params)
        return self.handler.request(request)


class MatchMixin(BaseLoL):

    def get_match_by_id(self, match_id, include_timeline=False):
        params = self.Params({('includeTimeline', include_timeline)})
        request = self.create_request('get_match_by_id', matchId=match_id, params=params)
        return self.handler.request(request)


class LoLStaticDataMixin(BaseLoL):

    def get_champion_list(self, locale=None, version=None, data_by_id=False, champ_data=None):
        params = self.Params({
            ('locale', locale),
            ('version', version),
            ('dataById', data_by_id),
            ('champData', champ_data),
        })
        request = self.create_request('get_champion_list', params=params)
        return self.handler.request(request)

    def get_champion(self, champion_id, locale=None, version=None, champ_data=None):
        params = self.Params({
            ('locale', locale),
            ('versions', version),
            ('champData', champ_data),
        })
        request = self.create_request('get_champion_by_id', id=champion_id, params=params)
        return self.handler.request(request)

    def get_item_list(self, locale=None, version=None, item_list_data=None):
        params = self.Params({
            ('locale', locale),
            ('versions', version),
            ('itemListData', item_list_data),
        })
        request = self.create_request('get_champion_list', params=params)
        return self.handler.request(request)

    def get_item(self, item_id, locale=None, version=None, item_data=None):
        params = self.Params({
            ('locale', locale),
            ('version', version),
            ('itemData', item_data),
        })
        request = self.create_request('get_item_by_id', id=item_id, params=params)
        return self.handler.request(request)


class LeagueOfLegends(SummonerMixin, MatchListMixin, LoLStaticDataMixin):
    a = 1
"""
    How RequestHandler works:
    1. Takes a Request object in self.request
    2. This goes into a Queue
    3. The Request is pulled from the Queue by a thread running self._request
    4. The thread prepares the Request and passes it to self.send_request
    5. This sends the request and returns the response (unless its 429 then it loops)
    6. The response is returned by self._request in a Queue (self.response_queue)
    7. self.request returns the response from the Queue
"""

# todo Detection of incorrect query parameters
