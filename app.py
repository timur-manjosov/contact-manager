from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Button
from address_book import AddressBook

class ContactApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "delete_contact", "Delete")
    ]

    def __init__(self):
        super().__init__()
        self.book = AddressBook()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Input(placeholder="Name", id="name")
        yield Input(placeholder="Number", id="number")
        yield Input(placeholder="Email", id="email")
        yield Button("Add", id="add")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "Number", "Email")
        for contact in self.book.contacts.values():
            table.add_row(contact.name, contact.number, contact.email, key=contact.name)
        table.cursor_type = "row"

    def action_delete_contact(self) -> None:
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        self.book.delete(row_key.value)
        self.book.save()
        table.remove_row(row_key)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        name = self.query_one("#name", Input).value
        number = self.query_one("#number", Input).value
        email = self.query_one("#email", Input).value

        self.book.add(name, number, email)
        self.book.save()

        table = self.query_one(DataTable)
        table.add_row(name, number, email, key=name)

        for field in self.query(Input):
            field.value = ""


if __name__ == "__main__":
    app = ContactApp()
    app.run()
