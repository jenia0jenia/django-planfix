from .classes import PlanFixBase, PlanfixError
from .utils import print_parser
from xml.etree import ElementTree
from collections import OrderedDict

class PlanFix(PlanFixBase):

    """
    https://planfix.ru/docs/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D0%B9
    """

    def project_get_list(self, cur_page=1, target='all'):
        if not str(cur_page).isdigit():
            cur_page = 1
        self.method = 'project.getList'
        self.scheme = {'account', 'sid', 'pageCurrent', 'target'}
        params = {'account': self.account,
                  'sid': self.sid,
                  'pageCurrent': str(cur_page),
                  'target': target}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('projects')
            return [(item.find('id').text, item.find('title').text) for item in rt]
        except PlanfixError as e:
            return None

    def contact_get_list(self, cur_page=1, search=''):
        if not str(cur_page).isdigit():
            cur_page = 1
        self.method = 'contact.getList'
        self.scheme = {'account', 'sid', 'pageCurrent', 'pageSize', 'search'}
        params = {'account': self.account,
                  'sid': self.sid,
                  'pageCurrent': str(cur_page),
                  'pageSize': '100',
                  'search': search}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('contacts')
            total = rt.attrib['totalCount']
            return [(item.find('userid').text, item.find('email').text) for item in rt]
        except PlanfixError as e:
            return None

    def contact_get(self, **kwargs):
        self.method = 'contact.get'
        self.scheme = ['account',
                       'sid',
                       {'contact': ['id', 'general']}
                      ]
        try:
            response = ElementTree.fromstring(self.connect(**kwargs))
            return response.find('contact').find('userid').text
        except PlanfixError as e:
            return None

    def contact_add(self, **kwargs):
        self.method = 'contact.add'
        self.scheme = ['account',
                       'sid',
                       {'contact': ['template',
                                    'name',
                                    'lastName',
                                    'post',
                                    'email',
                                    'mobilePhone',
                                    'workPhone',
                                    'homePhone',
                                    'address',
                                    'description',
                                    'sex',
                                    'skype',
                                    'icq',
                                    'vk',
                                    'birthdate',
                                    'lang',
                                    'isCompany',
                                    'canBeWorker',
                                    'canBeClient'
                                    ]}
                       ]

        try:
            response = ElementTree.fromstring(self.connect(**kwargs))
            return response.find('contact').find('userid').text
        except PlanfixError as e:
            # E-mail, указанный для логина, не уникален
            if e.message == '8007':
                return self.contact_get_list(search=kwargs['email'])[0][0]

    def task_get_list(self, target='template'):
        self.method = 'task.getList'
        self.custom_scheme = []
        self.scheme = {'account', 'sid', 'target', 'pageCurrent'}
        params = {'account': self.account,
                  'sid': self.sid,
                  'pageCurrent': '1',
                  'target': target}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('tasks')
            return [(item.find('id').text, item.find('title').text) for item in rt]
        except PlanfixError as e:
            return None

    def task_get_list_of_status(self, *args, **kwargs):
        self.method = 'taskStatus.getListOfSet'
        self.custom_scheme = []
        self.scheme = ['account',
                       'sid',
                       {'taskStatusSet': ['id']}
                       ]
        params = {'account': self.account,
                  'sid': self.sid}
        params.update(kwargs)
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('taskStatuses')
            return [(item.find('id').text, item.find('name').text) for item in rt]
        except PlanfixError as e:
            return None

    def task_change_status(self, id, status):
        self.method = 'task.changeStatus'
        self.custom_scheme = []
        self.scheme = ['account',
                       'sid',
                       {'task': ['id', 'general']},
                       'status',
                       'dateTime',
                       ]
        params = {'account': self.account,
                  'sid': self.sid,
                  'id': id,
                  'status': status}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            return response.find('task').find('id').text
        except PlanfixError as e:
            return None

    def task_add(self, *args, **kwargs):
        self.method = "task.add"
        self.scheme = ['account',
                       'sid',
                       {'task': ['template',
                                 'title',
                                 'description',
                                 'importance',
                                 'status',
                                 {'owner': 'id'},
                                 'statusSet',
                                 'checkResult',
                                 {'project': 'id'},
                                 'startDateIsSet',
                                 'startDate',
                                 'startTimeIsSet',
                                 'startTime',
                                 'endDateIsSet',
                                 'endDate',
                                 'endTimeIsSet',
                                 'endTime',
                                 # {'customData': 'customValue'}
                                ]
                        }]

        try:
            response = ElementTree.fromstring(self.connect(**kwargs))
            return response.find('task').find("id").text
        except PlanfixError as e:
            return None

    # def task_add_v2(self, *args, **kwargs):
    #     self.method = "task.add"
    #     self.scheme = ['account',
    #                    'sid',
    #                    {'task': ['template',
    #                              'title',
    #                              'description',
    #                              'importance',
    #                              'status',
    #                              {'owner': 'id'},
    #                              'statusSet',
    #                              'checkResult',
    #                              {'project': 'id'},
    #                              'startDateIsSet',
    #                              'startDate',
    #                              'startTimeIsSet',
    #                              'startTime',
    #                              'endDateIsSet',
    #                              'endDate',
    #                              'endTimeIsSet',
    #                              'endTime',
    #                              {'customData': 'customValue'}]
    #                     }]

    #     try:
    #         response = ElementTree.fromstring(self.connect(**kwargs))
    #         return response.find('task').find("id").text
    #     except PlanfixError as e:
    #         return None

    def task_get(self, id, general=''):
        self.method = "task.get"
        self.scheme = ['account',
                       'sid',
                       {'task': ['id', 'general']}
                       ]
        params = {'account': self.account,
            'sid': self.sid,
            'id': id,
            'general': general}
        try:
            # response = ElementTree.fromstring(self.connect(**params))
            # return response.find('task').find("id").text
            response = self.connect(**params)
            return response
        except PlanfixError as e:
            return None

    def task_get_field_value(self, id, general='', custom_data_id=''):
        root = ElementTree.fromstring(self.task_get(id, general))
        custom_data = root.find('task').find('customData').findall('customValue')
        for custom_value in custom_data:
            if custom_data_id == custom_value.find('field').find('id').text:
                return [int(value.text) for value in custom_value.findall('value')]

    def task_update(self, *args, **kwargs):
        self.method = "task.update"
        self.scheme = ['account',
                       'sid',
                       {'task': ['id',
                                 'silent',
                                 'title',
                                 'general',
                                 'checkResult',
                                 'description',
                                 'importance',
                                 'status',
                                 {'owner': 'id'},
                                 'statusSet',
                                 'checkResult',
                                 {'project': 'id'},
                                 'startDateIsSet',
                                 'startDate',
                                 'startTimeIsSet',
                                 'startTime',
                                 'endDateIsSet',
                                 'endDate',
                                 'endTimeIsSet',
                                 'endTime',
                                 {'customData': 'customValue'}, # customValue = [id, value]
                                 ]}
                       ]
        try:
            response = ElementTree.fromstring(self.connect(**kwargs))
            return response.find('task').find("id").text
        except PlanfixError as e:
            return None

    def task_update_v2(self, *args, **kwargs):
        self.method = "task.update"
        xml_values = {}
        xml_values['@method'] = self.method
        xml_values['account'] = self.account
        xml_values['sid'] = self.sid
        xml_values['silent'] = "1"

        task = {}
        task['id'] = kwargs.get('taskId')
        task['customData'] = {}
        task['customData']['customValue'] = []

        for custom_data in kwargs.get('custom_data'):
            task['customData']['customValue'].append({
                'id': custom_data['id'],
                'value': custom_data['value'],
            })

        xml_values['task'] = task

        try:
            return self.connect_v2(xml_values, **kwargs)
            # response = ElementTree.fromstring(self.connect_v2(xml_values, **kwargs))
            # return response.find('task').find("id").text
        except PlanfixError as e:
            return None

    def handbook_get_group_list(self, *args, **kwargs):
        self.method = 'handbook.getGroupList'
        self.scheme = ['account', 'sid']
        params = {'account': self.account,
                  'sid': self.sid}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('handbookGroups')
            return [(group.find('id').text, group.find('name').text) for group in rt]
        except PlanfixError as e:
            return None

    def handbook_get_list(self, *args, **kwargs):
        self.method = 'handbook.getList'
        self.scheme = ['account',
                       'sid',
                       {'group': 'id'}]
        params = {'account': self.account,
                  'sid': self.sid}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('handbooks')
            return [(group.find('id').text, group.find('name').text) for group in rt]
        except PlanfixError as e:
            return None

    def handbook_get_records(self, handbook, *args, **kwargs):
        self.method = 'handbook.getRecords'
        self.scheme = ['account',
                       'sid',
                       {'handbook': 'id'},
                       'parentKey',
                       'pageCurrent',
                       'pageSize',
                       ]
        params = {'account': self.account,
                  'sid': self.sid,
                  'handbook': handbook,
                  }

        if "parentKey" in kwargs:
            params["parentKey"] = kwargs["parentKey"]

        if "pageCurrent" in kwargs:
            params["pageCurrent"] = kwargs["pageCurrent"]

        if "pageSize" in kwargs:
            params["pageSize"] = kwargs["pageSize"]

        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('records')
            result = dict()
            for record in rt:
                result[record.find('key').text] = \
                    record.find('customData').find('customValue').find('value').text 
            return result
        except PlanfixError as e:
            return None

    def analitic_get_group_list(self):
        self.method = 'analitic.getGroupList'
        self.scheme = {'account', 'sid'}
        params = {'account': self.account,
                  'sid': self.sid,}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('analiticGroups')
            count_groups = rt.attrib['count']
            total = rt.attrib['totalCount']

            return [(item.find('id').text, item.find('name').text) for item in rt]
        except PlanfixError as e:
            return None

    def analitic_get_list(self, groupId):
        self.method = 'analitic.getList'
        self.scheme = {'account', 'sid'}
        params = {'account': self.account,
                  'analiticGroup': groupId,
                  'sid': self.sid,}
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('analitics')
            count_groups = rt.attrib['count']
            total = rt.attrib['totalCount']

            return [(item.find('id').text, item.find('name').text) for item in rt]
        except PlanfixError as e:
            return None

    def action_add(self, *args, **kwargs):
        self.method = 'action.add'
        xml_values = {}
        xml_values['@method'] = self.method
        xml_values['account'] = self.account
        xml_values['sid'] = self.sid

        analitic = {}
        analitic['id'] = kwargs.get('analiticId')
        analitic['analiticData'] = {}
        analitic['analiticData']['itemData'] = []

        for a_data in kwargs.get('analitic_data'):
            analitic['analiticData']['itemData'].append({
                'fieldId': a_data['field_id'],
                'value': a_data['value']
            })

        xml_values['action'] = {
            'description': kwargs.get('description'),
            # 'task': {'general': kwargs.get('taskGeneral')},
            'task': {'id': kwargs.get('taskId')},
            # {'contact': 'general'},
            'taskNewStatus': kwargs.get('taskNewStatus'),
            'notifiedList': {'user': kwargs.get('userIdList')},
            # 'isHidden': kwargs.get('isHidden'),
            # 'owner': {'id': kwargs.get('ownerId')},
            # 'dateTime': kwargs.get('dateTime'),
            'analitics': {'analitic': analitic}
        }

        try:
            response = ElementTree.fromstring(self.connect_v2(xml_values, **kwargs))
            print(response)
            rt = response.find('action')
            return rt.find('id').text
        except PlanfixError as e:
            return None

    def action_get_list(self, _id):
        self.method = 'action.getList'
        xml_values = {}
        xml_values['@method'] = self.method
        xml_values['account'] = self.account
        xml_values['sid'] = self.sid

        xml_values['task'] = {'general': _id}

        try:
            response = ElementTree.fromstring(self.connect_v2(xml_values, **kwargs))
            rt = response.find('action')
            xml_string = self.connect(**params)
            res = xmltodict.parse(xml_string)
            return res
        except PlanfixError as e:
            return None

    def action_get(self, action_id):
        self.method = 'action.get'
        self.scheme = ['account',
                       {'action': 'id'},
                       'sid',
                      ]
        params = {'account': self.account,
                  'action': action_id,
                  'sid': self.sid,}
        try:
            xml_string = self.connect(**params)
            res = xmltodict.parse(xml_string)
            return res
        except PlanfixError as e:
            return None
