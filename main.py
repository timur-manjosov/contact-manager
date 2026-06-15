from address_book import AddressBook

book = AddressBook()


while True:
    decision = input("1) List contacts\n 2) Search a contact\n 3) Add a contact\n 4) Delete a contact\n 5) Leave!\n Choose an option from 1 to 5: ")
    
    if decision == "1":
        for contact in book.contacts.values():
            print(contact)
    elif decision == "2":
        name = input("Name? : ")
        contact = book.find(name)
        if contact:
            print(contact)

    elif decision == "3":
        name = input("Name? : ")
        number = input("Number? : ")
        email = input("Email? : ")
        book.add(name, number, email)
        book.save()
    elif decision == "4":
        name = input("Name? : ")
        book.delete(name)
        book.save()
    elif decision == "5":
        print("Bye!")
        break
    else:
        print("Please choose a number between 1 - 5")
