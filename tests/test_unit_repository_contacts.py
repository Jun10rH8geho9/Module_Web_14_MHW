import unittest
from datetime import date, timedelta

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Contact, User

from src.schemas.schemas import ContactModel

from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
    find_contact_by_first_name,
    find_contact_by_last_name,
    find_contact_by_email,
    upcoming_birthdays,
)

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name='test_first_name_1',
                last_name='test_last_name_1',
                email="test@test.com",
                contact_number="111-111-1111",
                birthday=date(2000, 3, 15),
                user=self.user
            ),
            Contact(
                id=2,
                first_name='test_first_name_2',
                last_name='test_last_name_2',
                email="test@test.com",
                contact_number="222-222-2222",
                birthday=date(2000, 4, 15),
                user=self.user
            )
        ]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(limit, offset, self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user
        )
        self.session.query().filter().first.return_value = contact
        result = await get_contact(1, self.user, self.session)
        self.assertEqual(result, contact)
    
    async def test_create_contact(self):
        body = ContactModel(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user)
        result = await create_contact(body, self.user, self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.contact_number, body.contact_number)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact(self):
        body = ContactModel(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user
        )
        mocked_contact = Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user
        )
        self.session.query().filter().first.return_value = mocked_contact
        result = await update_contact(1, body, self.user, self.session)
        self.assertIsInstance(result, Contact)

    async def test_remove_contact(self):
        contact = Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user
        )

        self.session.query().filter().first.return_value = contact


        result = await remove_contact(1, self.user, self.session)
        self.assertIsInstance(result, Contact)

    async def test_find_contact_by_first_name(self):
        contacts = [Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        self.session.query().filter().all.return_value = contacts

        result = await find_contact_by_first_name('test_first_name', self.user, self.session)
        self.assertEqual(result, contacts)
    
    async def test_find_contact_by_last_name(self):
        contacts = [Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user), ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        self.session.query().filter().all.return_value = contacts

        result = await find_contact_by_last_name('test_last_name', self.user, self.session)
        self.assertEqual(result, contacts)


    async def test_find_contact_by_email(self):
        contact = Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email="test@test.com",
            contact_number="111-111-1111",
            birthday=date(2000, 4, 15),
            user=self.user
        )
        # Mocking the db.query(...).filter(...).first() call to return the contact object directly
        self.session.query().filter().first.return_value = contact

        # Calling the function under test
        result = await find_contact_by_email('test@test.com', self.user, self.session)

        # Asserting the result
        self.assertEqual(result, contact)

    async def test_upcoming_birthdays(self):
        current_date = date.today()
        to_date = current_date + timedelta(days=7)
        skip = 0
        limit = 10
        expected_result = []

        print(f"CURRENT DATE: {current_date}")
        print(f"TO DATE: {to_date}")

        contacts = [Contact(
            id=1,
            first_name='test_first_name_1',
            last_name='test_last_name_1',
            email="test@test.com",
            contact_number="111-111-1111",
                            birthday=date(2000, 4, 16),
                            user_id=self.user),
                    Contact(id=2,
            first_name='test_first_name_2',
            last_name='test_last_name_2',
            email="test@test.com",
            contact_number="222-222-2222",
            birthday=date(2000, 4, 14),
            user_id=self.user)]

        for contact in contacts:

            contact_birthday_month_day = (contact.birthday.month, contact.birthday.day)
            current_date_month_day = (current_date.month, current_date.day)
            to_date_month_day = (to_date.month, to_date.day)

            if current_date_month_day < contact_birthday_month_day <= to_date_month_day:
                expected_result.append(contact)

        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await upcoming_birthdays(current_date, to_date, skip, limit, self.user, self.session)

        self.assertCountEqual(result, expected_result)
