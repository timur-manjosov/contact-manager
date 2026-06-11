import json


class Contact:
    def __init__(self, name, number, email):
        self.name = name
        self.number = number
        self.email = email

    def show(self):
        print(f"Name: {self.name} | Number: {self.number} | Email: {self.email}")

    def to_dict(self):
        return {"name": self.name, "number": self.number, "email": self.email}

class AddressBook:
    def __init__(self):
        self.contacts = {}
        self.load()

    def load(self):
        try:
            with open("contacts.json", "r") as file:
                raw = json.load(file)        # rohe Mappen aus der Datei
            self.contacts = {}               # leeres Regal, das wir füllen
            for key, value in raw.items():
                self.contacts[key] = Contact(value["name"], value["number"], value["email"])   # <- DEINE Kernzeile
            print("Contact list was loaded!")
        except FileNotFoundError:
            print("Right now, there are no contacts. Please go forward with adding contacts!")
            self.contacts = {}

    def show_contacts(self):
        if self.contacts:
            for contact in self.contacts.values():
                contact.show()
        else:
            print("There are currently no entries in contact. Please go forward by adding some contacts!")

    def search_contact(self):
        name = input("Please continue with a name: ")
        if name in self.contacts:
            self.contacts[name].show()
        else:
            print("The user you want to find does not exist.")

    def add_contact(self):
        name = input("Please continue with a name: ")
        number = input("Now give the name a telephon number: ")
        email = input("Close this process by giving a email: ")
        self.contacts[name] = Contact(name, number, email)

    def delete_contact(self):
        name = input("Please continue with a name: ")
        if name in self.contacts:
            del self.contacts[name]
        else:
            print("This contact does not exist!")

    def save_contacts(self):
        data = {}
        for key, value in self.contacts.items():
            data[key] = value.to_dict()
        with open("contacts.json", "w") as datei:
            json.dump(data, datei)

        print("The contact list was saved!")


book = AddressBook()


while True:
    decison = input("1) List contacts\n 2) Search a contact\n 3) Add a contact\n 4) Delete a contact\n 5) Leave!\n Choose an option from 1 to 5: ")

    if decison == "1":
        book.show_contacts()
    elif decison == "2":
        book.search_contact()
    elif decison == "3":
        book.add_contact()
        book.save_contacts()
    elif decison == "4":
        book.delete_contact()
        book.save_contacts()
    elif decison == "5":
        print("Bye!")
        break
    else:
        print("Please choose a number between 1 - 5")
