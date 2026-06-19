import json


class Contact:
    def __init__(self, name, number, email):
        self.name = name
        self.number = number
        self.email = email

    def __str__(self):
        return f"Name: {self.name} | Number: {self.number} | Email: {self.email}"

    def to_dict(self):
        return {"name": self.name, "number": self.number, "email": self.email}


class AddressBook:
    def __init__(self):
        self.contacts = {}
        self.load()

    def load(self):
        try:
            with open("contacts.json") as file:
                raw = json.load(file)
            self.contacts = {
                name: Contact(entry["name"], entry["number"], entry["email"])
                for name, entry in raw.items()
            }
        # A missing or corrupt file just means we start with an empty book.
        except (FileNotFoundError, json.JSONDecodeError):
            self.contacts = {}

    def find(self, name):
        return self.contacts.get(name)

    def add(self, name, number, email):
        self.contacts[name] = Contact(name, number, email)

    def delete(self, name):
        if name in self.contacts:
            del self.contacts[name]
            return True
        return False

    def save(self):
        data = {name: contact.to_dict() for name, contact in self.contacts.items()}
        with open("contacts.json", "w") as file:
            json.dump(data, file)

