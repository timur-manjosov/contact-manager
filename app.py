from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from address_book import AddressBook


class ContactApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.book = AddressBook()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "Number", "Email")
        for contact in self.book.contacts.values():
            table.add_row(contact.name, contact.number, contact.email)
        table.cursor_type = "row"


if __name__ == "__main__":
    app = ContactApp()
    app.run()
