"""Tests for dateandtime's multicalendar object."""


import sys
import pytest
import datetime
from mock import patch

from ddate.base import DDate
from dateandtime import multicalendar


@pytest.fixture(
    params=[
        multicalendar.MultiCalendar(),
        multicalendar.MultiCalendar(discordian=True),
        multicalendar.MultiCalendar(eve_game=True),
        multicalendar.MultiCalendar(eve_real=True),
    ],
    ids=["normal", "discordian", "eve_game", "eve_real"]
)
def cal(request):
    """Fixture to run tests with all four supported calendar types."""

    return request.param


def test_discordian_settings():
    """Verify settings for using Discordian calendar."""

    with patch.object(multicalendar, "discordian_calendar") as patched_cal:
        disco = multicalendar.MultiCalendar(discordian=True)
    patched_cal.assert_called_once_with(disco.date)
    assert disco.discordian
    assert disco.max_width == 14
    assert isinstance(disco.date, DDate)
    assert disco.month == disco.date.SEASONS[disco.date.season]
    assert disco.ending_days == ["70", "71", "72", "73"]
    assert disco.day_of_month == disco.date.day_of_season
    assert disco.weekday_abbrs == [d[:2].title() for d in disco.date.WEEKDAYS]
    assert not disco.eve_real
    assert not disco.eve_game
    assert disco.year == disco.date.year


def test_normal_settings():
    """Verify settings for normal calendar."""

    patchcal = patch.object(multicalendar.calendar.TextCalendar, "formatmonth")
    with patchcal as patched_cal:
        normal = multicalendar.MultiCalendar()
    patched_cal.assert_called_once_with(normal.date.year, normal.date.month)
    assert isinstance(normal.date, datetime.datetime)
    assert normal.max_width == 20
    assert normal.month == normal.date.strftime("%B")
    assert normal.ending_days == ["28", "29", "30", "31"]
    assert normal.day_of_month == normal.date.strftime("%d")
    assert normal.weekday_abbrs == ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    assert not normal.discordian
    assert not normal.eve_real
    assert not normal.eve_game
    assert normal.year == normal.date.year


def test_eve_game_settings():
    """Verify settings for using the in game eve time."""

    evegame = multicalendar.MultiCalendar(eve_game=True)
    assert isinstance(evegame.date, datetime.datetime)
    assert not evegame.discordian
    assert not evegame.eve_real
    assert evegame.eve_game
    assert evegame.year == "YC {0}".format(evegame.date.year - 1898)


def test_eve_real_settings():
    """Verify settings for using eve game time like it was real."""

    evereal = multicalendar.MultiCalendar(eve_real=True)
    assert isinstance(evereal.date, datetime.datetime)
    assert not evereal.discordian
    assert evereal.eve_real
    assert not evereal.eve_game
    assert evereal.year == 23236 + (evereal.date.year - 1898)


def test_print_calendar(cal, capfd):
    """Ensure we are printing the calendar correctly."""

    cal.print_calendar()
    out, _ = capfd.readouterr()
    for line in out.splitlines():
        for setting in ["TODAY", "PAST", "OTHERMONTH", "END"]:
            line = line.replace(getattr(multicalendar.ANSI, setting), "")
        if not line:
            continue
        assert len(line) == cal.max_width

    assert out.splitlines()[-1] == multicalendar.ANSI.END, "should be ANSI.END"
    assert " ".join(cal.weekday_abbrs) in out.splitlines()[1]
    tag_should_be = "{0} {1}".format(cal.month, cal.year)
    if len(tag_should_be) > cal.max_width:
        tag_should_be = "{0} {1}".format(cal.month[:3], cal.year)
    assert tag_should_be in out.splitlines()[0]


def test_long_tag_line(cal, capfd):
    """Ensure we are shortening the tag line in print_calendar."""

    cal.month = "Something Really Long and Fake"
    cal.year = 1234
    cal.print_calendar()
    out, _ = capfd.readouterr()
    expected = "{0} {1}".format(
        cal.month[:cal.max_width - len(str(cal.year)) - 1],
        cal.year,
    )
    assert expected in out


def test_print_spaces(cal, capfd):
    """Ensure we print blank spaces."""

    cal.print_spaces()
    out, _ = capfd.readouterr()
    for line in out.splitlines():
        assert len(line) == cal.max_width
    assert len(out.splitlines()) == 420


@pytest.mark.format_line
def test_full_line(cal):
    """Ensure full lines are passed back."""

    preformat = [int(x) for x in range(len(cal.weekday_abbrs), 1)]
    assert cal.format_line(preformat) == " ".join(preformat)


@pytest.mark.format_line
def test_calling_last_days(cal):
    """Ensure we call the function to get the last days of last month."""

    preformat = [int(x) for x in range(len(cal.weekday_abbrs) - 1, 1)]
    with patch.object(cal, "get_last_days_of_last_month") as patch_last:
        cal.format_line(preformat)
    patch_last.assert_called_once_with(preformat)


@pytest.mark.format_line
def test_calling_next_days(cal):
    """Ensure we call the function to get the next days of next month."""

    preformat = cal.ending_days[-2:]
    with patch.object(cal, "get_next_days_of_next_month") as patch_next:
        cal.format_line(preformat)
    patch_next.assert_called_once_with(preformat)


@pytest.mark.format_line
def test_parse_out_ansi_end(cal):
    """Ensure we've accounted for the ANSI.END sequence."""

    preformat = ["5", "6", "7", "{0}{1}".format(
        cal.ending_days[-1], multicalendar.ANSI.END)]
    with patch.object(cal, "get_next_days_of_next_month") as patch_next:
        cal.format_line(preformat)
    patch_next.assert_called_once_with(preformat)


def test_print_time(cal, capfd):
    """Ensure we're printing the time correctly."""

    now = datetime.datetime.now()
    cal.print_time(now)
    out, _ = capfd.readouterr()
    time_should_be = "{0}:{1} {2}".format(
        int(now.strftime("%I")),
        now.strftime("%M"),
        now.strftime("%p").lower(),
    )
    assert time_should_be in out
    if sys.version_info < (3, ):
        assert out[0] == "\r"
    assert len(out) == cal.max_width + 1  # len() +1 for the carrage return
    assert out[-1] == " "  # don't end with a newline...


def test_getting_last_days():
    """We should try from 31 down to get the last days of last month."""

    def _ansi_wrapped(day):
        return "{0}{1}{2}".format(
            multicalendar.ANSI.OTHERMONTH,
            day,
            multicalendar.ANSI.END,
        )

    cal = multicalendar.MultiCalendar(date=datetime.datetime(2014, 3, 1))
    fake_line = ["1", "2", "3"]
    returned = cal.get_last_days_of_last_month(fake_line)
    expected = [
        _ansi_wrapped(25),
        _ansi_wrapped(26),
        _ansi_wrapped(27),
        _ansi_wrapped(28),
        "1",
        "2",
        "3",
    ]
    assert returned == expected
