import unittest
from httmock import HTTMock, all_requests
from api import Api
from report import Report
from report_manager import ReportManager

"""
class ContactManagerTest(unittest.TestCase):
    def setUp(self):
        gan_token = 'h027MapNNujPH0gV+sXAdmzZTDffHOpJEHaBtrD3NXtNqI4dT3NLXhyTwiZr7PUOGZJNSGv/b9xVyaguX0nDrONGhudPkxtl5EoXrM4SOZHswebpSy2ehh0edrGVF7dVJVZLIlRwgViY3n3/2hMQ5Njp9JFywnOy7gMeaoKw0hYLRbd+wVqvl2oOnspXwGTTcZ9Y+cdP8jIhUUoXOieXst0IXVclAHXa+K1d15gKLcpmXzK+jx14wGEmb4t8MSU'
        self.api = Api(token=gan_token)
        self.report_manager = ReportManager(self.api)
        self.start_path = '/v3'

    @all_requests
    def get_existing_report_mock(self, url, request):
        self.assertEqual(url.path, self.start_path + '/attributes/attribute/')
        status_code = 200
        content = '{"url":"https://api.getanewsletter.com/v3/attributes/attribute/","name":"attribute","code":"attribute","usage_count":0}'
        return {'status_code': status_code,
                'content': content}

    def test_get_existing_report(self):
        #with HTTMock(self.get_existing_attribute_mock):
        report = self.report_manager.get('1')
        self.assertTrue(isinstance(report, Report))
        #self.assertEqual(report.name, 'attribute')
        self.assertTrue(isinstance(report.sent_to_lists, list()))
        """