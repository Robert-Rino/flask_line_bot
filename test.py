import unittest
from unittest import mock
from app import app

class MyTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config.from_object('test')
        print(app.config['SECRET_KEY'])
        self.app = app.test_client()

    # def test_secretkey(self):
    #     assert app.config['SECRET_KEY'] == 'rino-test'

if __name__ == '__main__':
    unittest.main()
