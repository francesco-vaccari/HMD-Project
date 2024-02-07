import random


prefixes = ['i am at ', 'my address is ', 'i live in ', 'i am in ', '', "it's "]

file = open("usa.txt", "r")
usa_addresses = file.readlines()
file.close()

usa_addresses = usa_addresses[:250]

# read from csv file
file = open("italy.csv", "r")
lines = file.readlines()
file.close()

lines = lines[1:251]

# split each line by comma
addresses = []
for line in lines:
    line = line.split(',')
    address = line[3].strip() + " " + line[2].strip() + " " + line[5].strip() + " " + line[6].strip()
    addresses.append(address)

# make just one lowercase string
addresses = [address.lower() for address in addresses]
usa_addresses = [address.lower() for address in usa_addresses]

combined_addresses = addresses + usa_addresses

# remove any \n
combined_addresses = [address.replace("\n", "") for address in combined_addresses]
# remove spaces at the end
combined_addresses = [address.strip() for address in combined_addresses]


file = open("tell_address.txt", "w")

for address in combined_addresses:
    prefix = random.choice(prefixes)
    file.write("- " + prefix + "[" + address + "]" + "(address)\n")
