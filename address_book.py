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
            with open("contacts.json", "r") as file:
                raw = json.load(file)
            self.contacts = {}
            for key, value in raw.items():
                self.contacts[key] = Contact(value["name"], value["number"], value["email"])
        except FileNotFoundError:
            self.contacts = {} 

    def find(self, name):
        return self.contacts.get(name)

    def add(self, name, number, email):
        self.contacts[name] = Contact(name, number, email)

    def delete(self, name):
        if name in self.contacts:
            del self.contacts[name]

    def save(self):
        data = {}
        for key, value in self.contacts.items():
            data[key] = value.to_dict()
        with open("contacts.json", "w") as datei:
            json.dump(data, datei)

