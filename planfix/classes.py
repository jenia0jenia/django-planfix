import requests
from hashlib import md5
from xml.etree import ElementTree
from django.core.cache import cache
from functools import cmp_to_key
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
        print('scheme_sort')
        if isinstance(a, dict):
            for i in a.keys():
                a[i] = sorted(a[i], key=self.scheme_sort)
                return i
        else:
            return a

    def get_sign(self, **kwargs):
        params_list = self.method + \
            self.string_by_schemefileds(
                self.scheme, **kwargs) + self.private_key
        self.sign = md5(params_list.encode('utf-8')).hexdigest()

    def string_by_schemefileds(self, element, **kwargs):
        print('string_by_schemefileds')
        result_list = []
        element = list(element)
        element.sort(key=self.scheme_sort)

        for item in element:
            if not isinstance(item, dict):
                result_list.append(kwargs.get(item, ''))
            else:
                for tmp_key in item.keys():
                    tmp_val = item[tmp_key]
                    if not isinstance(tmp_val, list):
                        if tmp_val == 'id':
                            result_list.append(kwargs.get(tmp_key, ''))
                        elif tmp_val == 'customValue':
                            res = kwargs.get(tmp_key, '')
                            if not res == '' and isinstance(res, list):
                                result_list.append(
                                    "".join(["".join([str(i[0]), str(i[1])]) for i in res]))
                        else:
                            result_list.append(kwargs.get(tmp_val, ''))
                    else:
                        result_list.append(
                            self.string_by_schemefileds(tmp_val, **kwargs))
        return "".join(result_list)

    def create_xml_by_scheme(self, element, **kwargs):
        result = ""
        template = "<%s>%s</%s>"
        custom_data_template = "<id>%s</id><value>%s</value>"
        for item in element:
            if not isinstance(item, dict):
                result += template % (item, kwargs.get(item, ''), item)
            else:
                for tmp_key in item.keys():
                    tmp_val = item[tmp_key]
                    if not isinstance(tmp_val, list):
                        if tmp_val == 'id':
                            sub_result = template % (tmp_val, kwargs.get(tmp_key, ''), tmp_val)
                        elif tmp_val == 'customValue':
                            res = kwargs.get(tmp_key, '')
                            if not res == '' and isinstance(res, list):
                                sub_result = "".join(
                                    [template % (tmp_val, (custom_data_template % i), tmp_val) for i in res])
                        else:
                            sub_result = template % (
                                tmp_val, kwargs.get(tmp_key, ''), tmp_val)
                    else:
                        sub_result = self.create_xml_by_scheme(tmp_val, **kwargs)
                    result += template % (tmp_key, sub_result, tmp_key)
        return result

    def connect(self, **kwargs):
        print('connect')
        if not 'sid' in kwargs and self.sid:
            kwargs['sid'] = self.sid
        self.get_sign(**kwargs)
        body = self.create_xml_by_scheme(self.scheme, **kwargs)
        self.print_debug(body)
        data = self.request_templ.format(
            self.method, body.encode('utf-8'), self.sign)
        r = requests.post(self.host, data=data, auth=(self.api_key, ""))
        if self.method != 'auth.login':
            if self.is_session_valid(r.content):
                self.print_debug(r.content)
                return r.content
            else:
                tmp_params = dict(method=self.method, scheme=self.scheme)
                self.auth(renew=True)
                self.scheme, self.method = tmp_params['scheme'], tmp_params['method']
                return self.connect(**kwargs)
        else:
            return r.content

    def is_session_valid(self, res):
        response = ElementTree.fromstring(res)
        if response.attrib['status'] == 'ok':
            return True
        else:
            if response.find('code').text == '0005':
                return False
            else:
                raise AttributeError(response.find('code').text)

    def auth(self, renew=False):
        if renew or self.sid == None:
            self.method = 'auth.login'
            self.scheme = ['account', 'login', 'password']
            params = {'account': self.account, 'login': self.user, 'password': self.password}
            response = ElementTree.fromstring(self.connect(**params))
            res = response.find('sid')
            self.sid = res.text
            cache.set('planfix_sid', self.sid, self.CACHE_TIMELIFE*60)

    def print_debug(self, msg):
        if hasattr(self.debug, '__call__'):
            try:
                self.debug(msg)
            except TypeError as e:
                print(e)
