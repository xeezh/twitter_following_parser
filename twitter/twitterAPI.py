import requests
import secrets
import orjson
from copy import *
import twitter.operations as op


class API:
    def __init__(self, proxies, auth):
        self.__session = self.__init_session(
            proxies=proxies,
            auth=auth
        )
        self.__endpoint = 'https://twitter.com/i/api/graphql'

    def __gql(self, operation: tuple, variables: list[tuple]) -> dict:
        key, name = operation
        params = deepcopy(op.operations[name])
        for var in variables:
            params['variables'][var[0]] = var[1]
        query = self.__build_query(params)
        url = f"{self.__endpoint}/{key}/{name}?{query}"

        response = self.__session.get(
            url=url
        )
        return response.json()

    def user_tweets(self, rest_id: str, filter: bool) -> dict:
        response = self.__gql(
            operation=op.keys['UserTweets'],
            variables=[('userId', rest_id)]
        )
        tweets = response['data']['user']['result']['timeline_v2']['timeline']['instructions'][2]['entries']

        if filter:
            filtered = []
            for twt in tweets:
                if 'tweet-' + twt['entryId'].replace('tweet-', '') == twt['entryId']:
                    filtered.append(twt)
            tweets = filter

        return tweets

    def user_followings(self, rest_id, limit=15):
        response = self.__gql(
            operation=op.keys['Following'],
            variables=[('userId', rest_id)]
        )
        instr = response['data']['user']['result']['timeline']['timeline']['instructions']
        followings = []

        for i in instr:
            if i['type'] == "TimelineAddEntries":
                entries = i['entries']
                for e in entries:
                    if "user-" in e['entryId']:
                        username = e['content']['itemContent']['user_results']['result']['legacy']['screen_name']
                        followings.append(f"https://twitter.com/{username}")
                    if len(followings) == limit:
                        return followings
        return followings

    def user_by_screen_name(self, screen_name) -> dict:
        screen_name = screen_name[1:] if screen_name[0] == '@' else screen_name

        response = self.__gql(
            operation=op.keys['UserByScreenName'],
            variables=[('screen_name', screen_name)]
        )
        return response['data']['user']['result']

    @staticmethod
    def __build_query(params) -> str:
        return '&'.join(f'{k}={orjson.dumps(v).decode()}' for k, v in params.items())

    @staticmethod
    def __add_xcsrf_token(session) -> requests.Session:
        token = secrets.token_hex(16)
        session.cookies.set('ct0', token)
        return session

    @staticmethod
    def __add_guest_token(session) -> requests.Session:
        headers = {
            "authorization": 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            "content-type": "application/json",
            "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            "x-guest-token": session.cookies.get('guest_token'),
            "x-csrf-token": session.cookies.get("ct0"),
            "x-twitter-auth-type": '',
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": 'en',
        }
        r = session.post('https://api.twitter.com/1.1/guest/activate.json', headers=headers).json()
        session.cookies.set('gt', r['guest_token'])
        return session

    def __init_session(self, proxies, auth) -> requests.Session:
        sess = requests.Session()
        sess.proxies = proxies
        sess = self.__add_xcsrf_token(sess)
        sess = self.__add_guest_token(sess)
        cookie_list = []
        for c in sess.cookies:
            cookie_list.append((c.name, c.value))
        sess.headers = {
            "authorization": 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            "content-type": "application/json",
            "cookies": "; ".join(f"{k}={v}" for k, v in cookie_list),
            "x-guest-token": sess.cookies.get('gt'),
            "x-csrf-token": sess.cookies.get('ct0'),
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": 'en',
            "x-twitter-auth-type": "OAuth2Session",
        }
        sess.cookies['auth_token'] = auth
        return sess

#
# a = API(
#     proxies={
#         'https': 'http://Dgo324:k1VtZPlBFa@45.81.137.155:1050',
#         'http': 'http://Dgo324:k1VtZPlBFa@45.81.137.155:1050'
#     },
#     auth='8cc933a40a2c642059aeb17befee55fb28dbd217'
# )
# a.user_by_screen_name('FabrizioRomano')
# a.last_tweets('330262748')