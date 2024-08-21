from textual import on
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Collapsible


class Accordion(Container):
    """Accordion class is a container for Collapsibles
    that turns them into Accordion.
    """

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize `_currently_expanded` variable."""
        super().__init__(*args, **kwargs)
        self._currently_expanded: Collapsible | None = None

    @on(Collapsible.Expanded)
    def collapse_other_expanded(self, event: Collapsible.Expanded) -> None:
        """Close last when new clicked."""
        if self._currently_expanded is event.collapsible:
            self._currently_expanded.collapsed = False
        elif self._currently_expanded is not None:
            self._currently_expanded.collapsed = True
        self._currently_expanded = event.collapsible
