from textual.app import App, ComposeResult
from textual.widgets import Header, Footer


class ContactApp(App):
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


if __name__ == "__main__":
    app = ContactApp()
    app.run()
