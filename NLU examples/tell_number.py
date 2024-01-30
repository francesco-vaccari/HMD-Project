entity_values = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
           "11", "12", "13", "14", "15", "16", "17",
           "18", "19", "20"]

entity_name = "amounts"

sentences= [
    "i want a table for %s people",
    "i want a table for %s",
    "i want to make a reservation for %s people",
    "i want to make a reservation for %s",
    "i want to book a table for %s people",
    "i want to book a table for %s",
    "i would like to make a reservation for %s people",
    "i would like to make a reservation for %s",
    "i would like to book a table for %s people",
    "i would like to book a table for %s",
    "i want to reserve a table for %s people",
    "i want to reserve a table for %s",
    "i would like to reserve a table for %s people",
    "%s people",
    "%s",
    "for %s people",
    "for %s",
    "reservation for %s people",
    "reservation for %s",
    "a table for %s people",
    "a table for %s",
    "table for %s people",
    "table for %s",
    "book a table for %s people",
    "book a table for %s",
    "book for %s people",
    "book for %s",
    "reserve a table for %s people",
    "reserve a table for %s",
]

file = open("tell_number.txt", "w")
for sentence in sentences:
    for value in entity_values:
        entity = f"[{value}]({entity_name})"
        file.write("- " + sentence.replace("%s", entity) + "\n")