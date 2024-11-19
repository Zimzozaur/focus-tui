from typing import TYPE_CHECKING, Literal

from textual import on
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Input

from focustui.composite_widgets import ClockDisplay
from focustui.constants import MIN_SESSION_LEN, MINUTE
from focustui.modals import ConfirmPopup
from focustui.utils import session_len_parser
from focustui.widgets import SessionLenInput

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager
    from focustui.db import DatabaseManager
    from focustui.sound_manager import SoundManager


ACTIONS_NOT_ALLOWED_ON_IDLE = (
    "play_ambient",
    "stop_ambient",
    "toggle_hours",
    "toggle_seconds",
)


class FocusScreen(Screen):
    _ambient_silent = reactive(True, bindings=True)
    _input_mode = reactive("PLACEHOLDER", bindings=True)

    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("ctrl+s", "open_settings", "Settings"),
        ("ctrl+a", "play_ambient", "Play Ambient"),
        ("ctrl+a", "stop_ambient", "Stop Ambient"),
        ("ctrl+e", "toggle_hours", "Toggle Hours"),
        ("ctrl+r", "toggle_seconds", "Toggle Seconds"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_open_settings(self) -> None:
        """Open settings screen."""
        self.app.open_settings()

    def action_play_ambient(self):
        self._ambient_silent = False
        self._sm.toggle_ambient(
            self._ambient_silent,
            self._cm.config.ambient.volume,
        )

    def action_stop_ambient(self):
        self._ambient_silent = True
        self._sm.toggle_ambient(
            self._ambient_silent,
            self._cm.config.ambient.volume,
        )

    def action_toggle_hours(self):
        self._cm.toggle_clock_display_hours()

    def action_toggle_seconds(self):
        self._cm.toggle_clock_display_seconds()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:  # noqa: PLR0911
        """If clock is active allow to toggle ambient and hide rest."""
        if self._active_session and action not in ACTIONS_NOT_ALLOWED_ON_IDLE:
            return False

        if action in ("play_ambient", "stop_ambient") and not self._active_session:
            return False
        if action == "play_ambient" and self._ambient_silent:
            return True
        if action == "stop_ambient" and not self._ambient_silent:
            return True

        if action in ("toggle_hours", "toggle_seconds") and not self._active_session:
            return False
        if action in ("toggle_hours", "toggle_seconds"):
            return True

        return not self._active_session

    def __init__(
        self,
        cm: "ConfigManager",
        db: "DatabaseManager",
        sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._cm = cm
        self._db = db
        self._sm = sm
        self._session_len_input = SessionLenInput(cm=self._cm)
        self._clock_display = ClockDisplay(cm=self._cm)
        self._focus_button = Button("Focus", variant="success", id="focus-bt")
        self._active_session = False
        self._session_len: int = session_len_parser(self._cm.get_session_length())
        self._remaining_session: int = 0
        self._cancel_session_remaining: int = MINUTE
        self._intervals = []
        self._mode: Literal["stopwatch", "timer"] | None = None
        self._min_length: int = MIN_SESSION_LEN * MINUTE
        self._input_mode = self._cm.get_time_input_mode()

    def compose(self):
        with Horizontal(id="clock-wrapper"):
            yield self._clock_display
        with Vertical(id="focus-wrapper"):
            yield self._session_len_input
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, "#focus-bt")
    def _focus_button_clicked(self) -> None:
        """Start, Cancel, Kill session."""
        if self._focus_button.variant == "success":
            self._start_session()
        elif self._focus_button.variant == "warning":
            self._reset_timer()
        elif self._mode == "timer" or self._session_len < self._min_length:
            popup = ConfirmPopup(message="Do you want to kill the session?")
            self.app.push_screen(popup, self._not_successful_session)
        else:
            self._successful_session()

    @on(Input.Changed, "#session-duration")
    def _is_valid_session_length(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        is_valid: bool = event.input.is_valid
        self._focus_button.disabled = not is_valid
        if is_valid:
            self._cm.update_session_length(
                self._session_len_input.value,
            )

    def _start_session(self) -> None:
        """Start a Timer session."""
        self._active_session = True
        self._session_len_input.visible = False
        self._session_len = self._session_len_input.to_int() * MINUTE
        self._mode = "stopwatch" if self._session_len == 0 else "timer"
        if self._mode == "timer":
            self._remaining_session = self._session_len
            update_clock = self.set_interval(1, self._timer_display_update)
        else:
            update_clock = self.set_interval(1, self._stopwatch_display_update)

        cancel_session = self.set_interval(1, self._cancel_session)
        self._intervals.extend([update_clock, cancel_session])
        self._focus_button.variant = "warning"
        self._sm.play_ambient_in_background(
            ambient_name=self._cm.config.ambient.name,
        )
        self.app.refresh_bindings()  # Deactivates Bindings

    def _timer_display_update(self) -> None:
        """Update variable used by timer, update displayed time and
        call `TimerScreen._successful_session()` when self._remaining_session == 0.
        """
        self._remaining_session -= 1
        if self._remaining_session == 0:
            self._successful_session()
        else:
            minutes, seconds = divmod(self._remaining_session, 60)
            minutes_str = str(minutes).zfill(1)
            seconds_str = str(seconds).zfill(2)
            self._clock_display.update_time(minutes_str, seconds_str)

    def _stopwatch_display_update(self) -> None:
        """Update variable used by timer and update displayed time."""
        self._session_len += 1
        minutes, seconds = divmod(self._session_len, 60)
        minutes_str = str(minutes).zfill(1)
        seconds_str = str(seconds).zfill(2)
        self._clock_display.update_time(minutes_str, seconds_str)

    def _successful_session(self) -> None:
        """Play song, add successful session to DB and reset clock."""
        # self._db.create_session_entry(self._session_len // 60, 1)  # noqa: ERA001
        self._reset_timer()
        alarm = self._cm.config.alarm
        self._sm.play_sound(
            sound_name=alarm.name,
            sound_volume=alarm.volume,
        )

    def _not_successful_session(self, should_kill: bool) -> None:
        """Add killed session to DB and reset clock."""
        if not should_kill:
            return

        focused_for = (self._session_len - self._remaining_session) // MINUTE  # noqa: F841
        # self._db.create_session_entry(focused_for, 0)  # noqa: ERA001
        self._reset_timer()

    def _reset_timer(self) -> None:
        """Set all clock properties to default."""
        self._active_session = False
        self._session_len_input.visible = True
        self._session_len = self._cm.get_session_length()
        self._cancel_session_remaining = MINUTE
        for interval in self._intervals:
            interval.stop()
        self._intervals.clear()
        self._clock_display.update_time("0", "00")
        self._focus_button.variant = "success"
        self._focus_button.label = "Focus"
        self._ambient_silent = True
        self._sm.stop_ambient()
        self.app.refresh_bindings()

    def _cancel_session(self) -> None:
        """Allow user to cancel timer in first
        `self._cancel_timer_counter_default` seconds.
        """
        self._cancel_session_remaining -= 1
        if self._cancel_session_remaining > 0:
            self._focus_button.label = f"Cancel ({self._cancel_session_remaining})"
        elif self._mode == "timer" or (
                self._mode == "stopwatch" and self._session_len < self._min_length
        ):
            self._focus_button.label = "Kill"
            self._focus_button.variant = "error"
        else:
            self._focus_button.label = "End"
            self._focus_button.variant = "error"
