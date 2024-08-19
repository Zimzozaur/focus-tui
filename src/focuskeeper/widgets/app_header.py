from textual.widgets import Header
from textual.widgets._header import HeaderTitle


class AppHeader(Header):
    def compose(self):
        yield HeaderTitle()
