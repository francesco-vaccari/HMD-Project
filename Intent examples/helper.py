# read file and return a list of lines
file = open("tell_time.txt", "r")
lines = file.readlines()
file.close()

for i, line in enumerate(lines):
    if "-" not in list(line):
        print(line)
        print(i)