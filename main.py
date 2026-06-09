import json

def show_contacts(contacts):
    if contacts: 
        for key, value in contacts.items():
            print(f"{key} -> {value}")
    else:
        print("There are currently no entries in contact. Please go forward by adding some contacts!")

def search_contact(contacts):
    name = input("Please continue with a name: ")
    if name in contacts:
        number = contacts[name]
        print(f"The contact {name} does have the phone number: {number}")
    else:
        print("The user you want to find does not exist.")

def add_contact(contacts):
    name = input("Please continue with a name: ")
    number = input("Now give the name a telephon number: ")
    contacts[name] = number

def delete_contact(contacts):
    name = input("Please continue with a name: ")
    if name in contacts:
        del contacts[name]
    else:
        print("This contact does not exist!")

def save_contacts(contacts):
    with open("contacts.json", "w") as datei:
        json.dump(contacts, datei)

    print("The contact list was saved!")

try:
    with open("contacts.json", "r") as file:
        contacts = json.load(file)
        print("Contact list was loaded!")

except FileNotFoundError:
    print("Right now, there are no contacts. Please go forward with adding contacts!")
    contacts = {}

while True:
    decison = input("1) List contacts\n 2) Search a contact\n 3) Add a contact\n 4) Delete a contact\n 5) Leave!\n Choose an option from 1 to 5: ")

    if decison == "1":
        show_contacts(contacts)
    elif decison == "2":
        search_contact(contacts)
    elif decison == "3":
        add_contact(contacts)
        save_contacts(contacts)
    elif decison == "4":
        delete_contact(contacts)
        save_contacts(contacts)
    elif decison == "5":
        print("Bye!")
        break
    else:
        print("Please choose a number between 1 - 5")
