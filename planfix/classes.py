# Planfix api - https://planfix.ru/docs/

import requests
from hashlib import md5
from xml.etree import ElementTree
from django.core.cache import cache

import xmltodict

# class Cache(object):
#     params = {}
#
#     def get(self,key):
#         if key in self.params:
#             return self.params[key]
#         else:
#             return None
#
#     def set(self,key,value,timeout):
#         self.params[key] = value
#
#
# cache = Cache()


class PlanfixError(Exception):
    """Exception raised for errors in the PLANFIX requests.

    Attributes:
        code -- planfix error code
        message -- explanation of the error
    """

    def __init__(self, code='', message=''):
        self.code = code
        self.message = message


class PlanFixBase(object):
    CACHE_TIMELIFE = 20
    request_templ = """<?xml version="1.0" encoding="UTF-8"?>
        <request method="{}">
          {}
          <signature>{}</signature>
        </request>
        """

    method = ''
    scheme = []
    sign = ''

    host = ""
    api_key = ""
    private_key = ""
    project_id = ""
    user = ""
    password = ""
    account = ""
    level = 0
    sid = None
    debug = None

    def __init__(self, *args, **kwargs):
        self.sid = cache.get('planfix_sid')
        attr_list = [i.__str__() for i in dir(self) if not i.startswith('__')]
        if kwargs:
            for item in kwargs.keys():
                if item in attr_list:
                    self.__setattr__(item, kwargs[item])
        if not self.sid:
            self.auth()

    def scheme_sort(self, a):
        if isinstance(a, dict):
            for i in a.keys():
                # a[i] = sorted(a[i], key=self.scheme_sort)
                return i
        else:
            return a

    def get_sign(self, **kwargs):
        params_list = self.method + \
            self.string_by_schemefileds(
                self.scheme, **kwargs) + self.private_key
        self.sign = md5(params_list.encode('utf-8')).hexdigest()

    def string_by_schemefileds(self, element, **kwargs):
        result_list = []
        element = list(element)
        element.sort(key=self.scheme_sort)

        for item in element:
            if not isinstance(item, dict):
                result_list.append(kwargs.get(item, ''))
            else:
                for key, val in item.items():
                    if not isinstance(val, list):
                        if val == 'id':
                            result_list.append(kwargs.get(key, ''))
                        elif val == 'customValue':
                            res = kwargs.get(key, '')
                            if not res == '' and isinstance(res, list):
                                result_list.append(str(res[0]) + str(res[1]))
                        else:
                            result_list.append(kwargs.get(val, ''))
                    else:
                        result_list.append(
                            self.string_by_schemefileds(val, **kwargs))
        return "".join(result_list)

    def create_xml_by_scheme(self, element, **kwargs):
        result = ""
        template = "<%s>%s</%s>"
        custom_data_template = "<id>%s</id><value>%s</value>"
        sub_result = ''
        for item in element:
            if not isinstance(item, dict):
                if not kwargs.get(item, None) is None:
                    result += template % (item, kwargs.get(item, ''), item)
            else:
                for key, val in item.items():
                    if not isinstance(val, list):
                        kw_val = kwargs.get(key)
                        if not kw_val is None:
                            if val == 'id':
                                sub_result = template % (val, kw_val, val)
                            elif val == 'customValue':
                                if isinstance(kw_val, list):
                                    sub_result = template % \
                                        (val, (custom_data_template % (kw_val[0], kw_val[1])), val)
                            else:
                                sub_result = template % (val, kw_val, val)
                    else:
                        sub_result = self.create_xml_by_scheme(val, **kwargs)
                    result += template % (key, sub_result, key)
        return result

    def connect(self, **kwargs):
        if not 'sid' in kwargs and self.sid:
            kwargs['sid'] = self.sid
        self.get_sign(**kwargs)
        body = self.create_xml_by_scheme(self.scheme, **kwargs)
        self.print_debug(body)
        data = self.request_templ.format(
            self.method, body, self.sign).encode('utf-8')
        r = requests.post(self.host, data=data, auth=(self.api_key, ""))
        content = r.content.decode()

        self.print_debug(content)

        if self.is_session_valid(content):
            return content
        elif self.method != 'auth.login':
            tmp_params = dict(method=self.method, scheme=self.scheme)
            self.auth(renew=True)
            self.scheme, self.method = tmp_params['scheme'], tmp_params['method']
            return self.connect(**kwargs)

    def is_session_valid(self, res):
        response = ElementTree.fromstring(res)
        if response.attrib['status'] == 'ok':
            return True
        else:
            if response.find('code').text == '0005':
                return False
            else:
                raise PlanfixError(response.find('code').text, response.find('message').text)

    def auth(self, renew=False):
        if renew or self.sid == None:
            self.method = 'auth.login'
            self.scheme = ['account', 'login', 'password']
            params = {'account': self.account, 'login': self.user, 'password': self.password}
            response = self.connect(**params)
            if self.is_session_valid(response):
                root = ElementTree.fromstring(response)
                res = root.find('sid')
                self.sid = res.text
                cache.set('planfix_sid', self.sid, self.CACHE_TIMELIFE*60)
            else:
                return False

    def print_debug(self, msg):
        if hasattr(self.debug, '__call__'):
            try:
                self.debug(msg)
            except TypeError as e:
                print(e)

    def connect_v2(self, xml_values, **kwargs):
        if not 'sid' in xml_values and self.sid:
            xml_values['sid'] = self.sid

        xml_request = {}
        xml_request['request'] = xml_values
        body = xmltodict.unparse(xml_request, pretty=True)
        data = body.encode('utf-8')
        self.print_debug(data)

        r = requests.post(self.host, data=data, auth=(self.api_key, ""))
        content = r.content.decode()
        self.print_debug(content)

        if self.is_session_valid(content):
            return content
        elif self.method != 'auth.login':
            self.auth(renew=True)
            return self.connect_v2(xml_values, **kwargs)
