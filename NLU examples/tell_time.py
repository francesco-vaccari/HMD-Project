# When would you like to pick up you order?
# When would you like the order to be delivered?
# For what day and time do you want to make the reservation for?
import random
file = open("tell_time.txt", "w")

days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", ""]
days_numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", 
                "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", 
                "29", "30", "31", "1st", "second", "3rd", "4th", "5th", "6th", "7th", "8th","9th", 
                "10th", "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", 
                "20th", "21st", "20 second", "23rd", "24th", "25th", "26th", "27th", "28th", "29th", 
                "30th", "31st", ""]
months_names = ["January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December", ""]
hours_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
minutes_names = ["5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", ":00"]
am_pm = ["a.m.", "p.m."]



sentence = "- i would like to pick up the order at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")


sentence = "- i want to pick up the order at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")


sentence = "- i will come at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")


sentence = "- i will be there at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")


sentence = "- deliver the order at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")


sentence = "- deliver at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")

sentence = "- "
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")

sentence = "- at"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")

sentence = "- for around"
for i in range(50):
    hour = random.choice(hours_names)
    minute = random.choice(minutes_names)
    am = random.choice(am_pm)
    if minute == ":00":
        file.write(sentence + " " + hour + "" + minute + " " + am + "\n")
    else:
        file.write(sentence + " " + hour + " " + minute + " " + am + "\n")
    am = random.choice(am_pm)
    file.write(sentence + " " + hour + " " + am + "\n")
    if random.choice([True, False, False, False]):
        file.write(sentence + " half past " + hour + " " + am + "\n")

# exit()

sentence = ["- i want to make the reservation ", "- for ", "- at ", "- on ", "- next "]
import random
for i in range(300):
    day = random.choice(days_names)
    number = random.choice(days_numbers)
    month = random.choice(months_names)
    file.write(random.choice(sentence) + day + " " + number + " of " + month + "\n")
    file.write(random.choice(sentence) + number + " of " + month + "\n")
    file.write(random.choice(sentence) + day + " " + number + " " + month + "\n")
    file.write(random.choice(sentence) + number + " " + month + "\n")
    day = random.choice(days_names)
    number = random.choice(days_numbers)
    file.write(random.choice(sentence) + day + " " + number + "\n")
    file.write(random.choice(sentence) + number + "\n")
    
    day = random.choice(days_names)
    month = random.choice(months_names)
    file.write(random.choice(sentence) + day + " " + month + "\n")
    file.write(random.choice(sentence) + month + "\n")
    
    day = random.choice(days_names)
    file.write(random.choice(sentence) + day + "\n")

    day = random.choice(days_names)
    number = random.choice(days_numbers)
    month = random.choice(months_names)
    for j in range(20):
        hour = random.choice(hours_names)
        minute = random.choice(minutes_names)
        am = random.choice(am_pm)
        if minute == ":00":
            file.write(random.choice(sentence) + hour + "" + minute + " " + am + "\n")
        else:
            file.write(random.choice(sentence) + " " + hour + " " + minute + " " + am + "\n")
        am = random.choice(am_pm)
        file.write(random.choice(sentence) + hour + " " + am + "\n")
        if random.choice([True, False, False, False]):
            file.write(random.choice(sentence) + "half past " + hour + " " + am + "\n")

file.close()


file = open("tell_time.txt", "r")
lines = file.readlines()
file.close()

# say how many out of all sentences are duplicates
print(len(lines))
print(len(set(lines)))
print(len(lines) - len(set(lines)))

# remove duplicates
file = open("tell_time.txt", "w")
file.writelines(set(lines))
file.close()

