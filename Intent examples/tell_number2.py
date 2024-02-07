singles = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
teens = ["10 "]
hundred = "hundred"


sentences= [
    "- order number is %s",
    "- my number is %s",
    "- my order number is %s",
    "- %s"
]

file = open("tell_number2.txt", "w")

for sentence in sentences:
    for i in range(1000):
        number = str(i)
        if i == 10:
            number = str(i) + " "
        file.write(sentence.replace("%s", number) + "\n")
    

file.close()
