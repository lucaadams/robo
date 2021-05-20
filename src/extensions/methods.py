from datetime import datetime

def parse_timestamp(timestamp):
    # if timestamp is in ms, convert to seconds
    if len(str(timestamp)) > 10:
        timestamp = timestamp // 1000

    unformatted_datetime = str(datetime.fromtimestamp(timestamp))
    
    time = unformatted_datetime[11:15]
    date = unformatted_datetime[:10]

    day, month, year = date.split("-")

    # if the minutes value is less than 10, add a 0 in front (e.g. 10:5 -> 10:05)
    if int(time[3:]) < 10:
        time = f"{time[:2]}:0{time[3]}"

    return f"{time} {day}/{month}/{year}"
