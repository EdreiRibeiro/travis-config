import base64
import json
# import urllib
import requests
import types
import traceback
import datetime
from datetime import timedelta

import xmltodict

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from xml.etree.cElementTree import ElementTree, register_namespace, fromstring

from _xml2json import elem_to_internal, internal_to_elem, UsingPrefix

import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

class ConcurAPIError(Exception):
    """Raised if the Concur API returns an error."""
    pass


class ConcurClient(object):
    """OAuth client for the Concur API"""

    # app_auth_url = "Concur://app/authorize"
    # web_auth_uri = "https://www.concursolutions.com/net2/oauth2/Login.aspx"
    # token_url = "https://www.concursolutions.com/net2/oauth2/GetAccessToken.ashx"
    # api_url = "https://www.concursolutions.com/api"

    # api_url = "https://implementation.concursolutions.com/api"
    # web_auth_uri = "https://implementation.concursolutions.com/net2/oauth2/Login.aspx"
    # token_url = "https://implementation.concursolutions.com/net2/oauth2/GetAccessToken.ashx"

    # base_url = 'https://www.concursolutions.com/'

    #tokeninfo_url = "https://api.Concur-app.com/oauth/v1/tokeninfo"
    ##authentication_scheme = "Bearer"
    authentication_scheme = "OAuth"

    # def __init__(self, base_url=None, client_id=None, client_secret=None, access_token=None, use_app=False):
    def __init__(self, username=None, password=None, consumerKey=None, base_url='https://www.concursolutions.com/'):

        self.base_url = base_url if base_url is not None else self.base_url
        self.api_url = base_url+'api' if base_url[-1] == '/' else base_url+'/api'
        self.web_auth_uri = base_url + 'net2/oauth2/Login.aspx' if base_url[-1] == '/' else base_url + '/net2/oauth2/Login.aspx'
        self.token_url = base_url + 'net2/oauth2/GetAccessToken.ashx' if base_url[-1] == '/' else base_url + '/net2/oauth2/GetAccessToken.ashx'
        self.oauthUrl = base_url + 'net2/oauth2/accesstoken.ashx' if base_url[-1] == '/' else base_url + '/net2/oauth2/accesstoken.ashx'

        self.username = username
        self.password = password
        self.consumerKey = consumerKey

        # self.client_id = client_id
        # self.client_secret = client_secret
        self.access_token = None
        self.token_expiration_date = None
        self.refresh_token = None
        # self.auth_url = self.app_auth_url if use_app else self.web_auth_uri
        # self.use_app = use_app

    # def build_oauth_url(self, redirect_uri=None, scope="EXPRPT", state=None):
    #     params = {
    #         'client_id': self.client_id,
    #         'scope': scope
    #     }
    #
    #     if redirect_uri:
    #         params['redirect_uri'] = redirect_uri
    #
    #     if state:
    #         params['state'] = state
    #
    #     # Use '%20' instead of '+'.
    #     encoded = urllib.urlencode(params).replace('+', '%20')
    #     return "%s?%s" % (self.auth_url, encoded)
    #
    # def get_oauth_token(self, code, **kwargs):
    #
    #     params = {
    #         'client_id': self.client_id,
    #         'client_secret': self.client_secret,
    #         'code': code,
    #         #'grant_type': kwargs.get('grant_type', 'authorization_code')
    #     }
    #
    #     if 'redirect_uri' in kwargs:
    #         params['redirect_uri'] = kwargs['redirect_uri']
    #     # response = requests.post(self.token_url, params=params)
    #     response = requests.get(self.token_url, params=params)
    #     content_type, parsed = self.validate_response(response)
    #     if content_type == 'xml':
    #         # if root.tag != 'Access_Token':
    #         #     raise ConcurAPIError('unknown XML tag: %s' % root.tag)
    #         for item in 'Token', 'Expiration_date', 'Refresh_Token':
    #             print '\t%s:\t%s' % (item, root.find(item).text)
    #         return root.find('Token').text
    #     if content_type == 'json':
    #         try:
    #             return response['access_token']
    #         except:
    #             raise ConcurAPIError(response)

    def validate_response(self, response):

        #print 'response.headers:%s' % response.headers
        #print 'response.content:%s' % response.content
        # print 'response.url:%s' % response.url
        if 'content-type' in [r.lower() for r in response.headers.keys()]:
            content_type = response.headers['content-type']
            if 'xml' in content_type:
                # root = fromstring(response.content)
                # if root.tag.lower() == 'error':
                #     raise ConcurAPIError(root.find('Message').text)
                #return 'xml', elem_to_internal(root,canonize=UsingPrefix(default_namespace=root),)
                # return 'xml', xmltodict.parse(response.content)
                return 'xml', response.content
            if 'json' in content_type:
                return 'json', json.loads(response.content)
        else:
            return ('json', {'Response':'no-content'})

        raise ConcurAPIError('unknown content-type: %s' % content_type)

    def api(self, path, method='GET', **kwargs):

        params = kwargs['params'] if 'params' in kwargs else {}
        data = kwargs['data'] if 'data' in kwargs else {}
        headers = kwargs['headers'] if 'headers' in kwargs else {}
        stream = kwargs['stream'] if 'stream' in kwargs else False
        verify = kwargs['verify'] if 'verify' in kwargs else False

        if not self.access_token and 'access_token' not in params:
            self.getTokenGivenUsernamePasswordAndConsumerKey()
            # raise ConcurAPIError("You must provide a valid access token.")

        url = "%s/%s" % (self.api_url, path)

        if 'access_token' in params:
            access_token = params['access_token']
            del(params['access_token'])
        else:
            access_token = self.access_token

        headers['Authorization'] = '%s %s' % (self.authentication_scheme, access_token)

        # print 'Request headers Concur Class:', headers

        # proxies = {
        #     # 'http': 'http://159.122.223.55:4022',
        #     'http': 'http://9.66.75.64:4022',
        #     # 'https': 'http://159.122.223.55:4022',
        #     'https': 'http://9.66.75.64:4022',
        # }


        resp = requests.request(method, url,
                                params=params,
                                headers=headers,
                                data=data,
                                # proxies=proxies,
                                # verify=verify,
                                stream=stream,
                                )
        if str(resp.status_code)[0] not in ('2', '3'):
            print 'method =', method
            print 'url =', url
            print 'params =', params
            print 'headers =', headers
            print 'data =', data
            print
            # raise ConcurAPIError("Error returned via the API with status code (%s):" % resp.status_code, resp.text)
            raise ConcurAPIError(resp.text)
        return resp

    def get(self, path, **params):
        content_type, parsed = self.validate_response(
            self.api(path, 'GET', params=params))
        return parsed

    def post(self, path, **data):
        params = data.pop('_params', {})
        if '_xmlns' in data:
            headers = { 'content-type': 'application/xml' }
            elem = ElementTree(
                internal_to_elem(
                    data,
                    canonize=UsingPrefix(
                        default_namespace=data.pop('_xmlns'),
                        ),
                    ),
                )
            data = StringIO()
            elem.write(data)
            data = data.getvalue()
        else:
            headers = {}
        content_type, parsed = self.validate_response(
            self.api(path, 'POST',
                     params=params,
                     headers=headers,
                     data=data,
                     ))
        return parsed


    def __getattr__(self, name):
        '''\
        Turn method calls such as "Concur.foo_bar(...)" into
        "Concur.api('/foo/bar', 'GET', params={...})", and then parse the
        response.
        '''
        base_path = name.replace('_', '/')

        # Define a function that does what we want.
        def closure(*path, **params):
            'Accesses the /%s API endpoints.'
            path = list(path)
            path.insert(0, base_path)
            return self.parse_response(
                self.api('/'.join(path), 'GET', params=params)
                )

        # Clone a new method with the correct name and doc string.
        retval = types.FunctionType(
            closure.func_code,
            closure.func_globals,
            name,
            closure.func_defaults,
            closure.func_closure)
        retval.func_doc =  closure.func_doc % base_path

        # Cache it to avoid additional calls to __getattr__.
        setattr(self, name, retval)
        return retval

    def getbasic(self, user, password):
        # basic authentication (according to HTTP)
        return base64.encodestring(user + ':' + password)


    def getTokenGivenUsernamePasswordAndConsumerKey(self, username=None, password=None, consumerKey=None):

        now = datetime.datetime.now()
        if (self.token_expiration_date is None or now > self.token_expiration_date):
            print '**Expired**', 'now:', now, '- TOKEN_EXPIRATION_DT:', self.token_expiration_date

            if self.username is not None and self.password is not None and self.consumerKey is not None:
                username = self.username
                password = self.password
                consumerKey = self.consumerKey

            if username is not None and password is not None and consumerKey is not None:
                basic = 'Basic ' + self.getbasic(username, password)
                headers1 = {'Authorization': basic.rstrip(),
                            'X-ConsumerKey': consumerKey,
                            'Accept': 'application/json'}
                r = requests.get(self.oauthUrl, headers=headers1)
                access_token_full = json.loads(r.content)
                if access_token_full.has_key('Error'):
                    raise ConcurAPIError('Invalid Credentials. Please try again.')
                else:
                    self.setAccessToken(access_token_full['Access_Token']['Token'])
                    self.setRefreshToken(access_token_full['Access_Token']['Refresh_Token'])
                    expiration = access_token_full['Access_Token']['Expiration_date']
                    self.setTokenExpirationDate(datetime.datetime.strptime(expiration, "%m/%d/%Y %I:%M:%S %p"))
            else:
                raise ConcurAPIError("You must provide username, password and consumerKey.")

        else:
            print '**Not Expired**','now:',now,'- TOKEN_EXPIRATION_DT:',self.token_expiration_date



    def setAccessToken(self, access_token):
        self.access_token = access_token

    def getAccessToken(self):
        return self.access_token

    def setRefreshToken(self, refresh_token):
        self.refresh_token = refresh_token

    def getRefreshToken(self):
        return self.refresh_token

    def setTokenExpirationDate(self, token_expiration_date):
        self.token_expiration_date = token_expiration_date

    def getTokenExpirationDate(self):
        return self.token_expiration_date