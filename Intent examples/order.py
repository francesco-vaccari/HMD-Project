
pizzas = [
    "margherita", "margheritas", "margarita", "margaritas", 
    "pepperoni", "pepperonis", "pepper",
    "funghi", "funghis", "mushroom", "mushrooms", "fungi", "fungis",
    "capricciosa", "capricciosas", "capriccios", "capriccio", "capri", "Capri",
    "hawaii", "hawaiis", "hawaiian", "hawaiians", "Hawaii", "Hawaiian", "Hawaiians",
    "vegetarian", "without meat", "meatless", "vegetarians", "veggie",
    "french fries", "chips", "fries", "French fries", 
    "marinara", "marinaras",
    "ham", "prosciutto",
    "salami", "salamis",
    "cheese", "cheeses"
    ]

sizes = ["small", "medium", "large", "extra large"]

other_items = [
    "coke", "coca cola", "cola", "cokes", "colas", "Coca-Cola",
    "fanta", "fantas", "Fanta",
    "sprite", "sprites",
    "water", "waters",
    "tea", "teas",
    "cheesecake", "cheesecakes",
    "tiramisu", "tiramisus",
    "ice cream", "ice creams", "gelato"
    ]

amounts = ["a", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
           "11", "12", "13", "14", "15", "16", "17",
           "18", "19", "20"]

prefixes = [
    "i want to order ",
    "i would like to order ",
    "i want ",
    "i would like ",
    "i'd like ",
    "can i have ",
    "can i get ",
    ""
]

import random

file = open("order.txt", "w")

for i in range(30000):
    sentence = random.choice(prefixes)

    len_order = random.randint(1, 4)

    for group in range(len_order):
        group = str(group+1)
        
        amount_or_nothing = random.randint(0, 2)
        if amount_or_nothing != 0:
            sentence += "[" + random.choice(amounts) + ']{"entity": "amounts", "group": "' + group + '"} '
        pizza_or_other = random.randint(0, 2)
        if pizza_or_other == 0:
            size_or_nothing = random.randint(0, 3)
            if size_or_nothing == 0:
                sentence += "[" + random.choice(pizzas) + ']{"entity": "pizza_types", "group": "' + group + '"} '
            else:
                sentence += "[" + random.choice(sizes) + ']{"entity": "pizza_sizes", "group": "' + group + '"} '
                sentence += "[" + random.choice(pizzas) + ']{"entity": "pizza_types", "group": "' + group + '"} '
        else:
            sentence += "[" + random.choice(other_items) + ']{"entity": "other_item_types", "group": "' + group + '"} '
        
        add_and = random.randint(0, 1)
        if add_and == 0 and str(group) != str(len_order):
            sentence += "and "
    
    file.write("- " + sentence + "\n")

file.close()


# now open the file and remove duplicates

file = open("order.txt", "r")
lines = file.readlines()
file.close()

file = open("order.txt", "w")
set_lines = set(lines)
for line in set_lines:
    file.write(line)
file.close()

print("duplicate lines removed: " + str(len(lines) - len(set_lines)) + " out of " + str(len(lines)) + " lines")