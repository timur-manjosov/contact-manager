from address_book import AddressBook

book = AddressBook()


while True:
    decision = input("1) List contacts\n 2) Search a contact\n 3) Add a contact\n 4) Delete a contact\n 5) Leave!\n Choose an option from 1 to 5: ")
    
    if decision == "1":
        if book.contacts:
            for contact in book.contacts.values():
                print(contact)
        else:
            print("No contact: ")
    elif decision == "2":
        name = input("Name? : ")
        contact = book.find(name)
        if contact:
            print(contact)
        else:
            print("No contact was found")

    elif decision == "3":
        name = input("Name? : ")
        number = input("Number? : ")
        email = input("Email? : ")
        book.add(name, number, email)
        book.save()
    elif decision == "4":
        name = input("Name? : ")
        deleted = book.delete(name)
        if deleted:
            print(f"Deleted {name} from the list")
        else:
            print(f"{name} is not in the list")
        book.save()
    elif decision == "5":
        print("Bye!")
        break
    else:
        print("Please choose a number between 1 - 5")
