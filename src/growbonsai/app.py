import datetime
import pygame
import asyncio
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Button, Static, Label
from textual.containers import Horizontal, Container, Center, Middle

from _numbers import NUMBERS_DICT


class Clock(Static):
    DEFAULT_CSS = """
    #clock-wrapper {
        border: heavy yellow;
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    Static {
        width: auto
    }
    
    """

    def __init__(self, h_min, t_min, u_min, t_sec, u_sec, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h_min = Static(h_min)
        self.t_min = Static(t_min)
        self.u_min = Static(u_min)
        self.t_sec = Static(t_sec)
        self.u_sec = Static(u_sec)

    def compose(self):
        with Horizontal(id='clock-wrapper'):
            yield self.h_min
            yield Label(' ')
            yield self.t_min
            yield Label(' ')
            yield self.u_min
            yield Label(' ')
            yield Static(NUMBERS_DICT[':'])
            yield Label(' ')
            yield self.t_sec
            yield Label(' ')
            yield self.u_sec

    def update_clock(self, h_min, t_min, u_min, t_sec, u_sec):
        self.h_min.update(h_min)
        self.t_min.update(t_min)
        self.u_min.update(u_min)
        self.t_sec.update(t_sec)
        self.u_sec.update(u_sec)


class GrowBonsai(App):
    DEFAULT_CSS = """
    #body {
        border: heavy red;
        background: $surface;
        padding: 1 2;
    }
    """
    start_time = datetime.datetime.now()
    timer_widget = Clock(
        '',
        '',
        NUMBERS_DICT['0'],
        NUMBERS_DICT['0'],
        NUMBERS_DICT['0']
    )

    def on_mount(self):
        self.set_interval(1, self.update_time)

    def update_time(self):
        now = datetime.datetime.now()
        elapsed_time = now - self.start_time
        test_elapsed_time = elapsed_time + datetime.timedelta(minutes=0)
        minutes, seconds = divmod(test_elapsed_time.total_seconds(), 60)
        minutes_str = str(int(minutes)).zfill(2)
        seconds_str = str(int(seconds)).zfill(2)
        print(f"{minutes_str}:{seconds_str}")

        if int(minutes) >= 100:
            h_min = NUMBERS_DICT[minutes_str[-3]]
        else:
            h_min = ''

        if int(minutes) >= 10:
            t_min = NUMBERS_DICT[minutes_str[-2]]
        else:
            t_min = ''

        u_min = NUMBERS_DICT[minutes_str[-1]]
        t_sec = NUMBERS_DICT[seconds_str[-2]]
        u_sec = NUMBERS_DICT[seconds_str[-1]]

        self.timer_widget.update_clock(h_min, t_min,
                                       u_min, t_sec, u_sec)

    def compose(self):
        with Center(id='body'):
            yield self.timer_widget


if __name__ == "__main__":
    GrowBonsai().run()
