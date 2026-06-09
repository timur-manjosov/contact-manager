import json

def show_contacts(contacts):
    if contacts: 
        for key, value in contacts.items():
            print(f"{key} -> {value}")
    else:
        print("There are currently no entries in contact. Please go forward by adding some contacts!")

def add_contact(contacts):
    name = input("Please continue with a name: ")
    number = input("Now give the name a telephon number: ")
    contacts[name] = number

def close_contacts(contacts):
    with open("contacts.json", "w") as datei:
        json.dump(contacts, datei)

    print("Bye")

try:
    with open("contacts.json", "r") as file:
        contacts = json.load(file)
        print("Contact list was loaded!")

except FileNotFoundError:
    print("Right now, there are no contacts. Please go forward with adding contacts!")
    contacts = {}
 

while True:
    decison = input("1) List contacts\n 2) Add a contact\n 3) Leave!\n Chosse an option from 1 to 3: ")

    if decison == "1":
        show_contacts(contacts)

    elif decison == "2":
        add_contact(contacts)

    elif decison == "3":
        close_contacts(contacts)
        break

    else:
        print("Please choose a number between 1 - 3")
