from collections import UserDict
from datetime import datetime, timedelta
from typing import Dict, Callable


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Given value hasn't 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y").date())
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу

    def add_phone(self, value):
        for phone in self.phones:
            if phone.value == value:
                raise ValueError(f"Phone {value} is already in the list")
        self.phones.append(Phone(value))

    def edit_phone(self, old_phone, new_phone):
        if Phone(old_phone) and Phone(new_phone):  # additional checks for input data
            for phone in self.phones:
                if phone.value == old_phone:
                    phone.value = new_phone
                    return phone.value

    def find_phone(self, phone):
        if Phone(phone):  # additional validation for input data through Phone class
            for phone_item in self.phones:
                if phone_item.value == phone:
                    return phone_item.value

    def remove_phone(self, phone):
        if Phone(phone):
            for phone_item in self.phones:
                if phone_item.value == phone:
                    self.phones.remove(phone_item)

    def add_birthday(self, value):
        if Birthday(value):
            self.birthday = value

    def __str__(self):
        # older return version for Record __str__ below
        # return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

        # added self.birthdays to output which always shows birthday
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        # add new record data by the name value nested in record attribute
        self.data[record.name.value] = record

    def find(self, name):
        for name_item in self.data:
            if name_item == name:
                return self.data[name_item]
        return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays_list = []
        for user in self.data:
            name = self.data[user].name.value
            birthday = self.data[user].birthday
            formatted_birthday = datetime.strptime(birthday, "%d.%m.%Y").date()
            birthday_this_year = datetime(
                today.year, formatted_birthday.month, formatted_birthday.day
            ).date()

            if birthday_this_year < today:
                birthday_this_year = datetime(
                    today.year + 1, formatted_birthday.month, formatted_birthday.day
                ).date()
            days_diff = birthday_this_year - today

            if days_diff.days <= 7 and birthday_this_year.weekday() <= 4:
                upcoming_birthdays_list.append(
                    {
                        "name": name,
                        "congratulation_date": birthday_this_year.strftime("%d.%m.%Y"),
                    }
                )

            elif days_diff.days <= 7 and birthday_this_year.weekday() == 5:
                birthday_this_year += timedelta(days=2)
                upcoming_birthdays_list.append(
                    {
                        "name": name,
                        "congratulation_date": birthday_this_year.strftime("%d.%m.%Y"),
                    }
                )

            elif days_diff.days <= 7 and birthday_this_year.weekday() == 6:
                birthday_this_year += timedelta(days=1)
                upcoming_birthdays_list.append(
                    {
                        "name": name,
                        "congratulation_date": birthday_this_year.strftime("%d.%m.%Y"),
                    }
                )
        return upcoming_birthdays_list


def input_error(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Provide prompt in proper format please."
        except IndexError:
            return "Incorrect input."
        except KeyError:
            return "Contact not found."

    return inner


def parse_input(user_input: str) -> tuple:
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args: list, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args: list, book: AddressBook):
    name, phone, new_phone = args
    record = book.find(name)
    message = "Contact's phone changed."
    if record:
        record.edit_phone(phone, new_phone)
    if record is None:
        return f"Cannot find contact with the name: {name}"
    return message


def all_contacts(book: AddressBook) -> str:
    if len(book):
        return_str = ""
        for _, contact in book.items():
            return_str += f"{contact} \n"
        return return_str[:-2]  # remove redundant line split for return
    return "Contacts not found"


@input_error
def phone_contact(args: list, book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    phones_output = ""
    if record:
        phones = record.phones
        for phone in phones:
            phones_output += phone.value + " "
        return phones_output


@input_error
def add_birthday(args: list, book: AddressBook) -> str:
    name, date, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
        return f"Birthday {date} added to {name}"
    if record is None:
        return f"Contact {name} is not found"


@input_error
def show_birthday(args: list, book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)

    if record is None:
        return f"User {name} not found"
    if record.birthday is None:
        return f"User didn't add birthday"
    return record.birthday


@input_error
def birthdays(book: AddressBook) -> str:
    birthdays_data = book.get_upcoming_birthdays()
    if len(birthdays_data):
        birthdays_list = []
        for item in birthdays_data:
            birthdays_list.append(f"{item['name']:} {item['congratulation_date']}")
        output_str = "\n".join(birthdays_list)
        return output_str
    return "No upcoming birthdays for the week ahead"


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["exit", "close"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(phone_contact(args, book))
        elif command == "all":
            print(all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

# Command prompts for testing:

# ADD CONTACT: add Test 1234567890
# CHANGE CONTACT: change Test 1234567890 0987654321
# PHONE CONTACT: phone Test
# ADD BIRTHDAY: add-birthday Test 05.04.1999
# SHOW BIRTHDAY: show-birthday Test
# ALL UPCOMING BIRTHDAYS: birthdays
# ALL CONTACTS: all
