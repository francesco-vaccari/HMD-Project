file = open("ask_affluence.txt", "w")

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "mondays", "tuesdays", "wednesdays", "thursdays", "fridays", "saturdays", "sundays"]

hours = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
         "11", "12"]

ampm = ["a.m.", "p.m."]

sentences = [
    "how busy is it on {day} at {hour} {ampm}",
    "how crowded is it on {day}",
    "is it crowded on {day} at {hour} {ampm}",
    "is it crowded on {day}",
    "are there many people on {day} at {hour} {ampm}",
    "are there many people on {day}",
    "is it full on {day} at {hour} {ampm}",
    "is it full on {day}",
    "is it busy on {day} at {hour} {ampm}",
    "is it busy on {day}",
]

additional = [
    "is it busy", "is it crowded", "is it full", "are there many people",
    "how busy is it", "how crowded is it", "how full is it", "how many people are there",
    "is it busy today", "is it crowded today", "is it full today", "are there many people today",
    "how busy is it today", "how crowded is it today", "how full is it today", "how many people are there today",
    "is it busy right now", "is it crowded right now", "is it full right now", "are there many people right now",
    "how busy is it right now", "how crowded is it right now", "how full is it right now", "how many people are there right now",
    "is it busy tomorrow", "is it crowded tomorrow", "is it full tomorrow", "are there many people tomorrow",
    "how busy is it tomorrow", "how crowded is it tomorrow", "how full is it tomorrow", "how many people are there tomorrow",
]

for sentence in sentences:
    for day in days:
        for hour in hours:
            for am in ampm:
                file.write("- " + sentence.format(day=day, hour=hour, ampm=am) + "\n")

for sentence in additional:
    file.write("- " + sentence + "\n")