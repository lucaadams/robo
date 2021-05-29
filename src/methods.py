"""
general methods to be used anywhere
"""

from datetime import datetime


def parse_timestamp(timestamp):
    timestamp = int(round(timestamp, 0))

    # if timestamp is in ms, convert to seconds
    if len(str(timestamp)) > 10:
        timestamp = round(timestamp / 1000, 0)

    unformatted_datetime = str(datetime.fromtimestamp(timestamp))

    time = unformatted_datetime[11:]
    date = unformatted_datetime[:10]

    hours, minutes, _ = time.split(":")
    year, month, day = date.split("-")

    return f"{hours}:{minutes} {day}/{month}/{year}"


def wrap(text, max_chars_per_line):
    text = text.strip(" ")
    text_split = text.split(" ")
    chars_on_this_line = 0

    wrapped_text = ""

    for word in text_split:
        wrapped_text += word + " "
        chars_on_this_line += len(word)
        if chars_on_this_line >= max_chars_per_line:
            if len(wrapped_text) < len(text):
                wrapped_text += "\n"
                chars_on_this_line = 0

    wrapped_text = wrapped_text.strip(" ")

    return wrapped_text
