"""Test dateandtime's base functions."""


import pytest
from mock import patch

from dateandtime import base
from dateandtime.base import MultiCalendar, be_a_clock, parse_args


@pytest.fixture
def defaults():
    """Get default settings."""

    return {
        "discordian": False,
        "eve_game": False,
        "eve_real": False,
    }


def test_no_args(defaults):
    """Basic use case."""

    assert parse_args(["dateandtime"]) == defaults


def test_literally_no_args(defaults):
    """This shouldn't be possible, but it shouldn't break anything."""

    assert parse_args() == defaults


def test_one_arg(defaults):
    """Simple use case."""

    defaults.update({"eve_game": True})
    assert parse_args(["dateandtime", "-e"]) == defaults


def test_two_args_the_same(defaults):
    """Shouldn't make a difference."""

    defaults.update({"discordian": True})
    assert parse_args(["dateandtime", "-d", "--discordian"]) == defaults


def test_two_different_args_raise():
    """Should raise SystemExit."""

    with pytest.raises(SystemExit):
        parse_args(["dateandtime", "-r", "-e"])


def test_three_raise_content():
    """Test the output of the sys exit being raised."""

    with pytest.raises(SystemExit) as error:
        parse_args(["dateandtime", "-r", "-e", "-d"])

    expected = (
        "Please limit yourself to a single calendar.\nI cannot display "
        "discordian, eve game and eve real at the same time :("
    )
    assert expected == error.value.args[0]


def test_two_raise_content():
    """Test the content of the sys exit being raised."""

    with pytest.raises(SystemExit) as error:
        parse_args(["dateandtime", "-r", "-d"])

    expected = (
        "Please limit yourself to a single calendar.\nI cannot display "
        "discordian and eve real at the same time :/"
    )
    assert expected == error.value.args[0]


def test_two_raise_content_two():
    """Test the ording of the sys exit being raised."""

    with pytest.raises(SystemExit) as error:
        parse_args(["dateandtime", "-r", "-e"])

    expected = (
        "Please limit yourself to a single calendar.\nI cannot display "
        "eve game and eve real at the same time :/"
    )
    assert expected == error.value.args[0]


def test_help_message():
    """Ensure the test message looks correct."""

    with pytest.raises(SystemExit) as error:
        parse_args(["dateandtime", "-h"])

    expected = (
         "Dateandtime usage:\n  dateandtime [calendar] [-h/--help]\n"
        "Alternate calendars (usage flags):\n  Discordian: [-d, --discord,"
        " --discordian, --discordianism]\n  Eve (game): [-e, --eve, --eve-"
        "game]\n  Eve (real): [-r, --eve-real, --eve-is-real]"
    )
    assert expected == error.value.args[0]


def test_be_a_clock_calls():
    """Ensure the be_a_clock function is calling out correctly."""

    with patch.object(base, "MultiCalendar") as patched_cal:
        with patch.object(MultiCalendar, "print_spaces") as patched_spaces:
            with patch.object(MultiCalendar, "print_calendar") as patched_pcal:
                be_a_clock(eve_real=True, test=True)
    patched_cal.assert_called_once_with(False, True, False)
    patched_spaces.assert_called_once()
    patched_pcal.assert_called_once()
