import unittest
from creatio_tests.page import CreatioAuthPage
from creatio_tests.models.config import CheckContext
from creatio_tests.fields.factory import FieldFactory
from creatio_tests.field_types import FieldType


class ContactsCardFreedomUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = CreatioAuthPage(
            base_url="https://crm-bundle.creatio.com/",
            username="Administrator",
            password="Administrator",
            test_url="0/Shell/?autoOpenIdLogin=true#Card/Contacts_FormPage/edit/bb912869-4e0d-4111-af8f-477c772ba7da",
            headless=True,
            wait_timeout_sec=180,
            debug=False,
        )
        cls.client.login()
        cls.client.load_page()
        cls.client.build_fields_index()
        cls.ctx = CheckContext(driver=cls.client.driver, wait_timeout_sec=30, debug=True, prefix="[tests]")

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_text_recipient_name(self):
        el = self.client.fields.get("Dear")
        self.assertIsNotNone(el, "field 'Dear' not found in index")
        field = FieldFactory.create(
            field_type=FieldType.TEXT,
            code="Dear",
            title="Recipient's name",
            readonly=True,
            strict_title=True,
            context=self.ctx,
        )
        result = field.check(el)
        self.assertTrue(result.ok, msg=result.message)

    def test_datetime_created_on_readonly(self):
        el = self.client.fields.get("DateTimePicker_iniisf1")
        self.assertIsNotNone(el, "field 'DateTimePicker_iniisf1' not found in index")
        field = FieldFactory.create(
            field_type=FieldType.DATETIME,
            code="DateTimePicker_iniisf1",
            title="Created on",
            readonly=True,
            strict_title=True,
            context=self.ctx,
        )
        result = field.check(el)
        self.assertTrue(result.ok, msg=result.message)

    def test_lookup_type_value(self):
        el = self.client.fields.get("Type")
        self.assertIsNotNone(el, "field 'Type' not found in index")
        field = FieldFactory.create(
            field_type=FieldType.LOOKUP,
            code="Type",
            title="Type",
            readonly=False,
            strict_title=True,
            context=self.ctx,
            lookup_values=["Contact person", "Customer", "Employee", "Supplier"],
        )
        result = field.check(el)
        self.assertTrue(result.ok, msg=result.message)

if __name__ == "__main__":
    unittest.main(verbosity=2)
