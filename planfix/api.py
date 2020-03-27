from .classes import PlanFixBase, PlanfixError
from xml.etree import ElementTree
from collections import OrderedDict

class PlanFix(PlanFixBase):
    def task_add(self, *args, **kwargs):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_task.add
        """
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
                                 {'customData': 'customValue'}]
                        }]

        try:
            response = ElementTree.fromstring(self.connect(**kwargs))
            return response.find('task').find("id").text
        except PlanfixError as e:
            return None

    def project_get_list(self, cur_page=1, target='all'):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_project.getList
        """
        result = []
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
            for item in rt:
                result.append((item.find('id').text, item.find('title').text))
            return result
        except PlanfixError as e:
            return None

    def contact_get_list(self, cur_page=1, search=''):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_contact.getList
        """
        result = []
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
            for item in rt:
                result.append((item.find('userid').text,
                               item.find('email').text))
            return result
        except PlanfixError as e:
            return None

    def contact_get(self, **kwargs):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_contact.get
        """
        result = []
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
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_contact.add
        """
        result = []
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
                # print(e.message)
                # print(e.code)
                return self.contact_get_list(search=kwargs['email'])[0][0]

    def task_get_list(self, target='template'):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_task.getList
        """
        result = []
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
            for item in rt:
                result.append((item.find('id').text, item.find('title').text))
            return result
        except PlanfixError as e:
            return None

    def task_get_list_of_status(self, *args, **kwargs):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_taskStatus.getListOfSet
        """
        result = []
        self.method = 'taskStatus.getListOfSet'
        self.custom_scheme = []
        self.scheme = ['account',
                       'sid',
                       {'taskStatusSet': ['id']}
                       ]
        params = {'account': self.account,
                  'sid': self.sid}
        params.update(kwargs)
        # print(params)
        try:
            response = ElementTree.fromstring(self.connect(**params))
            rt = response.find('taskStatuses')
            for item in rt:
                result.append((item.find('id').text, item.find('name').text))
            return result
        except PlanfixError as e:
            return None

    def task_change_status(self, id, status):
        """
        https://planfix.ru/docs/%D0%9F%D0%BB%D0%B0%D0%BD%D0%A4%D0%B8%D0%BA%D1%81_API_task.changeStatus
        """
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
                  'status': status
                  }
        try:
            response = ElementTree.fromstring(self.connect(**params))
            return response.find('task').find('id').text
        except PlanfixError as e:
            return None
