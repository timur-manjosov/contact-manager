from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Button
from textual.containers import Horizontal
from address_book import AddressBook

class ContactApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Contacts"
    SUB_TITLE = "AddressBook v1"

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
        with Horizontal(id="add-bar"):
            yield Input(placeholder="Name", id="name")
            yield Input(placeholder="Number", id="number")
            yield Input(placeholder="Email", id="email")
            yield Button("Add", id="add")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("Name", width=28)
        table.add_column("Number", width=22)
        table.add_column("Email", width=36)
        for contact in self.book.contacts.values():
            table.add_row(contact.name, contact.number, contact.email, key=contact.name)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.border_title = "◆ CONTACTS"
        self.query_one("#add-bar").border_title = "◆ NEW ENTRY"
        self.styles.opacity = 0.0
        self.styles.animate("opacity", value=1.0, duration=0.5)

    def action_delete_contact(self) -> None:
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        name = row_key.value
        self.book.delete(name)
        self.book.save()
        table.remove_row(row_key)
        self.notify(f"Removed {name}", severity="warning")

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

        self.notify(f"Added {name}", severity="information")


def main():
    ContactApp().run()

if __name__ == "__main__":
    main()
