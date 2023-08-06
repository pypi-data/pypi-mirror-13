#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import os.path as path
import pytest

import fizzbotz


def get_test_file(filename, extension):
    file_path = path.join(path.dirname(__file__), 'test_files', '{}.{}'.format(filename, extension))
    with codecs.open(file_path, 'r', 'utf-8') as test_file:
        return test_file.read()[:-1]  # strip \n from end of file


@pytest.mark.asyncio
@pytest.mark.parametrize('filename, message_function', [
                            ('bestoftwitchchat', fizzbotz.TwitchChat().get_bestoftwitchchat_pasta),
                            ('twitchquotes', fizzbotz.TwitchChat().get_twitchquotes_pasta),
                            ('twitchquotes_emotes', fizzbotz.TwitchChat().get_twitchquotes_pasta),
                            ('twitchquotes_text_art', fizzbotz.TwitchChat().get_twitchquotes_pasta),
                            ('twitchquotes_unicode', fizzbotz.TwitchChat().get_twitchquotes_pasta),
                            ('joke_oneliner', fizzbotz.Joke().get_oneliner),
                            ('joke_oneliner_quote', fizzbotz.Joke().get_oneliner),
                            ('insult', fizzbotz.Insult().get)
                        ])
async def test_messages(filename, message_function):
    raw_html = get_test_file(filename, 'html')
    message = await message_function(from_html=raw_html)

    expected_message = get_test_file(filename, 'txt')
    if message != expected_message:
        pytest.fail("Didn't get expected result.\n\nExpected:\n{}\n\nReceived:\n{}".format(expected_message, message))


@pytest.mark.asyncio
@pytest.mark.parametrize('callback', [
                            fizzbotz.Imgur(2).get,
                            fizzbotz.Joke().get,
                            fizzbotz.TwitchChat().get
                        ])
async def test_command_get(callback):
    await callback() is not None


@pytest.mark.asyncio
async def test_square():
    square_message = await fizzbotz.Square().get('ggsnipes/sgak')
    assert square_message == "```\n" \
                             "G G S N I P E S / S G A K\n" \
                             "G S N I P E S / S G A K A\n" \
                             "S N I P E S / S G A K A G\n" \
                             "N I P E S / S G A K A G S\n" \
                             "I P E S / S G A K A G S /\n" \
                             "P E S / S G A K A G S / S\n" \
                             "E S / S G A K A G S / S E\n" \
                             "S / S G A K A G S / S E P\n" \
                             "/ S G A K A G S / S E P I\n" \
                             "S G A K A G S / S E P I N\n" \
                             "G A K A G S / S E P I N S\n" \
                             "A K A G S / S E P I N S G\n" \
                             "K A G S / S E P I N S G G\n" \
                             "```"


@pytest.mark.asyncio
@pytest.mark.parametrize('string_literal, exception', [
                            ('', fizzbotz.EmptyStringError),
                            ('This string is longer than the max allowed.', fizzbotz.StringLengthError)
                        ])
async def test_square_exceptions(string_literal, exception):
    with pytest.raises(exception):
        await fizzbotz.Square().get(string_literal)


@pytest.mark.asyncio
@pytest.mark.parametrize('dice', ['3d10', '3D10', '12', ''])
async def test_roll(dice):
    await fizzbotz.Roll().get(dice) is not None


@pytest.mark.asyncio
@pytest.mark.parametrize('dice', ['d10', '10d', '0', 'foo'])
async def test_roll_exception(dice):
    with pytest.raises(ValueError):
        await fizzbotz.Roll().get(dice)
