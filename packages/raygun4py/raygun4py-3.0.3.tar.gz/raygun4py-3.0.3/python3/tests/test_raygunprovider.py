import unittest, sys
from raygun4py import raygunprovider
from raygun4py import utilities

class TestRaygunSender(unittest.TestCase):

    def setUp(self):
        self.sender = raygunprovider.RaygunSender('invalidapikey')
        self.handler = raygunprovider.RaygunHandler('testkey', 'v1.0')

    def test_apikey(self):
        self.assertEqual(self.sender.apiKey, 'invalidapikey')

    def test_handler_apikey(self):
        self.assertEqual(self.handler.sender.apiKey, 'testkey')

    def test_handler_version(self):
        self.assertEqual(self.handler.version, 'v1.0')

    def test_sending_403_with_invalid_key(self):
        try:
            raise Exception('test')
        except Exception as e:
            info = sys.exc_info()
            http_result = self.sender.send_exception(exc_info=info)
            self.assertEqual(http_result[0], 403)

    def test_ignore_exceptions(self):
        ex = ['Exception']
        self.sender.ignore_exceptions(ex)

        self.assertEqual(self.sender.ignoredExceptions, ex)

    def test_filter_keys_set(self):
        keys = ['credit_card']
        self.sender.filter_keys(keys)

        self.assertEqual(self.sender.filteredKeys, keys)

    def test_filter_keys_filters_error(self):
        keys = ['identifier']
        self.sender.filter_keys(keys)

        self.sender.set_user({ 'identifier': 'foo' })

        self.assertEqual(utilities.filter_keys(keys, self.sender.user)['identifier'], '<filtered>')

    def test_set_transmitLocalVariables(self):
        self.sender = raygunprovider.RaygunSender('foo', config={ 'transmitLocalVariables': False })

        self.assertFalse(self.sender.transmitLocalVariables)

    def test_default_transmitLocalVariables(self):
        self.sender = raygunprovider.RaygunSender('foo')

        self.assertTrue(self.sender.transmitLocalVariables)

def main():
    unittest.main()

if __name__ == '__main__':
    main()