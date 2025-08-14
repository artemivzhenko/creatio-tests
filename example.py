import unittest
from creatio_tests.utils.auth_loader import load_auth
from creatio_tests.utils.page_loader import load_page_config


class ContactsCardFreedomUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = load_auth("m.auth.json")
        cls.client.login()
        cls.client.load_page()
        cls.client.build_fields_index()
        cls.page = load_page_config(cls.client, "m.page.json")

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_all_fields_immediate(self):
        ok, results = self.page.check_all()
        self.assertTrue(ok, msg="some fields failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
