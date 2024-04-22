from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import status

from src.schemas.schemas import ContactModel
from src.database.models import Contact,User    

# Список контактів
async def get_contacts(skip: int, limit: int, user: User, db: Session) -> list[Contact]:
    """
    The get_contacts function returns a list of contacts.
        
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: Session: Pass in the database connection to the function
    :param current_user: User: Filter the contacts by user
    :return: A list of contact
    :doc-author: Trelent
    """

    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:

    """
    Retrieve a single contact by ID.

    :param contact_id: int: ID of the contact to retrieve.
    :param user: User: User object to filter contacts.
    :param db: Session: Database session object.
    :return: Contact: Retrieved contact object.
    """

    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      contact_number=body.contact_number,
                      birthday=body.birthday,
                      additional_information=body.additional_information,
                      user_id=user.id
                      )
    """
    Create a new contact.

    :param body: ContactModel: Contact data to create.
    :param user: User: User object to associate with the contact.
    :param db: Session: Database session object.
    :return: Contact: Created contact object.
    """

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:

    """
    Update an existing contact.

    :param contact_id: int: ID of the contact to update.
    :param body: ContactModel: Contact data to update.
    :param user: User: User object to authorize the update.
    :param db: Session: Database session object.
    :return: Contact | None: Updated contact object if successful, None if contact not found.
    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.contact_number = body.contact_number
        contact.birthday = body.birthday
        contact.additional_information = body.additional_information
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:

    """
    Remove a contact.

    :param contact_id: int: ID of the contact to remove.
    :param user: User: User object to authorize the removal.
    :param db: Session: Database session object.
    :return: Contact | None: Removed contact object if successful, None if contact not found.
    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

# Пошук контакту за ім'ям
async def find_contact_by_first_name(first_name: str, user: User, db: Session) -> list[Contact]:

    """
    Search contacts by first name.

    :param first_name: str: First name to search for.
    :param user: User: User object to filter contacts.
    :param db: Session: Database session object.
    :return: list[Contact]: List of contacts matching the first name.
    :raises: HTTPException: If no contacts are found matching the first name.
    """

    contact = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == user.id)).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact

# Пошук контакту за прізвищем
async def find_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> list[Contact]:

    """
    Search contacts by last name.

    :param contact_last_name: str: Last name to search for.
    :param user: User: User object to filter contacts.
    :param db: Session: Database session object.
    :return: list[Contact]: List of contacts matching the last name.
    :raises: HTTPException: If no contacts are found matching the last name.
    """

    contact = db.query(Contact).filter(and_(Contact.last_name == contact_last_name, Contact.user_id == user.id)).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact

# Пошук контакту за адресою електронної пошти
async def find_contact_by_email(contact_email: str, user: User, db: Session) -> list[Contact]:

    """
    Search contacts by email address.

    :param contact_email: str: Email address to search for.
    :param user: User: User object to filter contacts.
    :param db: Session: Database session object.
    :return: list[Contact]: List of contacts matching the email address.
    :raises: HTTPException: If no contacts are found matching the email address.
    """

    contact = db.query(Contact).filter(and_(Contact.email == contact_email, Contact.user_id == user.id)).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact

async def upcoming_birthdays(current_date, to_date, skip: int, limit: int, user: User, db: Session) -> list[Contact]:

    """
    Retrieve contacts with upcoming birthdays within a specified date range.

    :param current_date: datetime: Start date of the date range.
    :param to_date: datetime: End date of the date range.
    :param skip: int: Number of contacts to skip.
    :param limit: int: Maximum number of contacts to retrieve.
    :param user: User: User object to filter contacts.
    :param db: Session: Database session object.
    :return: list[Contact]: List of contacts with upcoming birthdays within the date range.
    """

    contacts = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

    upcoming = []

    # Пошук в контактах по дням народження
    for contact in contacts:

        contact_birthday = (contact.birthday.month, contact.birthday.day)
        current_date = (current_date.month, current_date.day)
        to_date = (to_date.month, to_date.day)

        if current_date < contact_birthday <= to_date:
            upcoming.append(contact)

    return upcoming