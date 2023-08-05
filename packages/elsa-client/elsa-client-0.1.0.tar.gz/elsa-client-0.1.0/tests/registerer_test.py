import unittest


class TestRegisterer(unittest.TestCase):

    def test_registration(self):

        from reg.registerer import ElsaClient as ec

        client = ec()
        res_code = client.register('http://192.168.99.100:8080/registration')
        self.assertIsNotNone(res_code)
        self.assertEqual(res_code, 200)

    def test_registration_defaults(self):

        from reg.registerer import ElsaClient as ec

        client = ec()
        res_code = client.register_with_defaults(
                'http://192.168.99.100:8080/registration',
                'test-service', 'http://localhost:3000/')
        self.assertIsNotNone(res_code)
        self.assertEqual(res_code, 200)
        print('defaults success.')
