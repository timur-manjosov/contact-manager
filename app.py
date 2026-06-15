from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
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
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "Number", "Email")
        for contact in self.book.contacts.values():
            table.add_row(contact.name, contact.number, contact.email, key=contact.name)  # (2) ── key ergänzen
        table.cursor_type = "row"

    def action_delete_contact(self) -> None:
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        self.book.delete(row_key.value)
        self.book.save()
        table.remove_row(row_key)


if __name__ == "__main__":
    app = ContactApp()
    app.run()
