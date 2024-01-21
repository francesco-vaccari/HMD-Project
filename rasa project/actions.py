from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import random
from datetime import datetime


def get_size_for_group(pizza_sizes, group):
    for size in pizza_sizes:
        if size[1] == group:
            return size[0]
    return "medium"

def get_amount_for_group(amounts, group):
    for amount in amounts:
        if amount[1] == group:
            return amount[0]
    return "1"

def get_amounts():
    return ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]

def get_sizes():
    return ["small", "medium", "large", "extra large"]

def get_menu():
    return ["margherita", "pepperoni", "funghi", "capricciosa", "hawaii", "vegetarian", "french fries", "marinara", "ham", "salami", "cheese", 
            "coke", "fanta", "sprite", "water", "tea", 
            "cheesecake", "tiramisu", "ice cream"]

def get_menu_pizzas():
    return ["margherita", "pepperoni", "funghi", "capricciosa", "hawaii", "vegetarian", "french fries", "marinara", "ham", "salami", "cheese"]

def get_menu_prices():
    return {"margherita": 5, "pepperoni": 6, "funghi": 6, "capricciosa": 7, "hawaii": 8, "vegetarian": 7, "french fries": 7, "marinara": 6, "ham": 1, "salami": 1, "cheese": 1,
            "coke": 2, "fanta": 2, "sprite": 2, "water": 1, "tea": 1,
            "cheesecake": 3, "tiramisu": 3, "ice cream": 2}

def get_total(order):
    total = 0
    menu_prices = get_menu_prices()
    for elem in order:
        if len(elem) == 3:
            extra = -1 if elem[1] == "small" else 1 if elem[1] == "large" else 2 if elem[1] == "family" else 0
            total += (menu_prices[elem[2]] + extra) * float(elem[0])
        else:
            total += menu_prices[elem[1]] * float(elem[0])

    return total

def parse_date(input_string):
    # Parse the input date string
    date_object = datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%S.%f%z")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Format the date components
    day_date = date_object.strftime("%d")
    month_name = date_object.strftime("%B")
    hour_date = date_object.strftime("%H")
    minute_date = date_object.strftime("%M")
    day_name = days[date_object.weekday()]

    # If first digit of day is 0, remove it
    if day_date[0] == "0":
        day_date = day_date[1:]
    
    # Turn hour into 12-hour format
    if int(hour_date) > 12:
        hour_date = str(int(hour_date) - 12)
        am_pm = "pm"
    else:
        am_pm = "am"

    # Create the output dictionary
    output_dict = {
        "day_name": day_name,
        "day_date": day_date,
        "month_name": month_name,
        "hour_date": hour_date,
        "minute_date": minute_date,
        "am/pm": am_pm
    }

    return output_dict

def save_new_order(method, order, total, time, n_people, address):
    file = open("orders.txt", "r")
    lines = file.readlines()
    lines_split = []
    for line in lines:
        lines_split.append(line.split("*/*"))
    file.close()

    id = 0
    for i in range(0, 100000):
        found = False
        for line in lines_split:
            if int(line[0]) == i:
                found = True
                break
        if not found:
            id = i
            break
    
    file = open("orders.txt", "a")
    file.write(str(id) + "*/*" + str(order) + "*/*" + str(total) + "*/*" + str(method) + "*/*" + str(time) + "*/*" + str(n_people) + "*/*" + str(address) + "\n")
    file.close()

    return id

def retrieve_order(id):
    file = open("orders.txt", "r")
    lines = file.readlines()
    orders = []
    for line in lines:
        orders.append(line.split("*/*"))
    file.close()

    for order in orders:
        if str(order[0]) == id:
            return order

    return None

def cancel_order(id):
    file = open("orders.txt", "r")
    lines = file.readlines()
    orders = []
    for line in lines:
        orders.append(line.split("*/*"))
    file.close()

    file = open("orders.txt", "w")
    for order in orders:
        if str(order[0]) != id:
            file.write("*/*".join(order))
    file.close()

def get_lactose_options():
    return ["marinara"]

def get_vegan_options():
    return ["marinara"]

def get_vegetarian_options():
    return ["margherita", "pepperoni", "funghi", "capricciosa", "hawaii", "vegetarian", "french fries", "marinara"]

def get_gluten_options():
    return []

class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        if tracker.get_slot("order_confirmed"):
            dispatcher.utter_message(text="I'm sorry but your order has already been confirmed.")
            return [FollowupAction(name = "action_repeat_last_message"), SlotSet("asking_change_order", False)]
        
        entities = tracker.latest_message['entities']
        amounts = []
        temp_pizza_types = []
        pizza_sizes = []
        temp_other_items_types = []

        old_order = [] if tracker.get_slot("order") is None else tracker.get_slot("order")
        temp_order = [] if tracker.get_slot("temp_order") is None else tracker.get_slot("temp_order")
        old_order += temp_order

        # extract from entities items, amounts and sizes the user has specified
        for entity in entities:
            if entity['entity'] == 'amounts':
                # if entity['group'] exists append value and group
                # else append value and -1
                if 'group' in entity:
                    if entity['value'] == 'a':
                        amounts.append(('1', entity['group']))
                    if str(entity['value']) in get_amounts():
                        amounts.append((str(entity['value']), entity['group']))
                else:
                    amounts.append((entity['value'], -1))
            elif entity['entity'] == 'pizza_types':
                if 'group' in entity:
                    temp_pizza_types.append((entity['value'], entity['group']))
                else:
                    temp_pizza_types.append((entity['value'], -1))
            elif entity['entity'] == 'pizza_sizes':
                if 'group' in entity:
                    if entity['value'] in get_sizes():
                        pizza_sizes.append((entity['value'], entity['group']))
                else:
                    pizza_sizes.append((entity['value'], -1))
            elif entity['entity'] == 'other_item_types':
                if 'group' in entity:
                    temp_other_items_types.append((entity['value'], entity['group']))
                else:
                    temp_other_items_types.append((entity['value'], -1))

        temp_order = []

        # check if the items the entities (types, sizes, amounts and other items) are in the menu
        menu = get_menu()
        pizza_types = []
        for pizza in temp_pizza_types:
            if pizza[0] in menu:
                pizza_types.append(pizza)
            else:
                dispatcher.utter_message(text="Sorry, we don't have " + pizza[0] + " in our menu.")
        other_items_types = []
        for item in temp_other_items_types:
            if item[0] in menu:
                other_items_types.append(item)
            else:
                dispatcher.utter_message(text="Sorry, we don't have " + item[0] + " in our menu.")
        
        if tracker.get_intent_of_latest_message() == "nothing_else":
            if len(old_order) == 0:
                dispatcher.utter_message(text="What would you like to order?")
                return [SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("order_confirmed", False), SlotSet("asking_change_order", False), SlotSet("last_message", "What would you like to order?")]
            else:
                return [FollowupAction(name = "action_confirm_order")]

        # general order, no specific item, like "i want to order a pizza"
        if len(pizza_types) == 0 and len(other_items_types) == 0:
            dispatcher.utter_message(text="What would you like to order?")
            return [SlotSet("order", old_order), SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False), SlotSet("asking_change_order", False), SlotSet("last_message", "What would you like to order?")]
        
        # try to match items with amounts and sizes
        for pizza in pizza_types:
            value = pizza[0]
            group = pizza[1]
            temp_order.append((get_amount_for_group(amounts, group), get_size_for_group(pizza_sizes, group), value))
        for item in other_items_types:
            value = item[0]
            group = item[1]
            temp_order.append((get_amount_for_group(amounts, group), value))
        
        utter = "Your order is: "
        for elem in temp_order + old_order:
            for value in elem:
                utter += value + " "
            utter = utter[:-1] + ", "
        utter = utter[:-2] + ". "
        dispatcher.utter_message(text=utter)

        allergies = tracker.get_slot("allergies")
        if allergies is not None:
            if allergies == "gluten":
                options = get_gluten_options()
                conflict = False
                for elem in temp_order:
                    if len(elem) == 3 and elem[2] not in options:
                        conflict = True
                        break
                if conflict:
                    dispatcher.utter_message(text="Looks like you asked for gluten free options but you also ordered something that contains gluten.")
            if allergies == "lactose":
                options = get_lactose_options()
                conflict = False
                for elem in temp_order:
                    if len(elem) == 3 and elem[2] not in options:
                        conflict = True
                        break
                if conflict:
                    dispatcher.utter_message(text="Looks like you asked for lactose free options but you also ordered something that contains lactose.")
            if allergies == "vegan":
                options = get_vegan_options()
                conflict = False
                for elem in temp_order:
                    if len(elem) == 3 and elem[2] not in options:
                        conflict = True
                        break
                if conflict:
                    dispatcher.utter_message(text="Looks like you asked for vegan options but you also ordered something that is not vegan.")
            if allergies == "vegetarian":
                options = get_vegetarian_options()
                conflict = False
                for elem in temp_order:
                    if len(elem) == 3 and elem[2] not in options:
                        conflict = True
                        break
                if conflict:
                    dispatcher.utter_message(text="Looks like you asked for vegetarian options but you also ordered something that is not vegetarian.")
            dispatcher.utter_message(text="Is your order correct?")
        else:
            dispatcher.utter_message(text="Is it correct?")

        return [SlotSet("order", old_order), SlotSet("temp_order", temp_order), SlotSet("asking_correct", True), SlotSet("asking_anything_else", False), SlotSet("order_confirmed", False), SlotSet("last_message", utter + "Is it correct?"), SlotSet("asking_change_order", False)]


class ActionOrderCorrect(Action):
    def name(self) -> Text:
        return "action_order_correct"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        old_order = [] if tracker.get_slot("order") is None else tracker.get_slot("order")

        order = tracker.get_slot("temp_order") + old_order
        dispatcher.utter_message(text="Ok, do you want anything else?")

        return [SlotSet("order", order), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("asking_anything_else", True), SlotSet("order_confirmed", False), SlotSet("last_message", "Do you want anything else?")]


class ActionOrderIncorrect(Action):
    def name(self) -> Text:
        return "action_order_incorrect"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        dispatcher.utter_message(text="I'm sorry, I misunderstood. Try rephrasing you order or saying one item at a time. What would you like to order?")
        return [SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False), SlotSet("last_message", "What would you like to order?")]


class ActionChangeOrder(Action):
    def name(self) -> Text:
        return "action_change_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        if tracker.get_slot("asking_correct"):
            return [FollowupAction(name = "action_order_incorrect")]
        if tracker.get_slot("asking_anything_else"):
            dispatcher.utter_message(text="I'm sorry, you cannot change an order once confirmed.")
            return [FollowupAction(name = "action_order")]

        if tracker.get_slot("order") is not None and len(tracker.get_slot("order")) > 0:
            dispatcher.utter_message(text="I'm sorry, you cannot change an order once confirmed.")
            return [FollowupAction(name = "action_repeat_last_message")]
        
        dispatcher.utter_message(text="Do you wish to cancel an order made in a previous call?")
        return [SlotSet("asking_change_order", True), SlotSet("last_message", "Do you wish to cancel an order made in a previous call/conversation?")]


class ActionChangeOrderConfirmed(Action):
    def name(self) -> Text:
        return "action_change_order_confirmed"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("asking_cancel"):
            if tracker.latest_message['intent']['name'] == 'confirm':
                id = tracker.get_slot("order_id")
                cancel_order(id)
                dispatcher.utter_message(text="Ok, your order has been cancelled.")
                return [SlotSet("asking_cancel", False), SlotSet("last_message", "What would you like to order?"), SlotSet("order_id", None), SlotSet("order_confirmed", False), SlotSet("order", None), SlotSet("temp_order", None), SlotSet("change_order_procedure", False), SlotSet("asking_change_order", False)]
            else: 
                dispatcher.utter_message(text="Ok, your order has not been cancelled.")
                return [SlotSet("asking_cancel", False), SlotSet("last_message", "What would you like to order?"), SlotSet("order_id", None), SlotSet("order_confirmed", False), SlotSet("order", None), SlotSet("temp_order", None), SlotSet("change_order_procedure", False), SlotSet("asking_change_order", False)]


        if tracker.get_slot("asking_id"):
            id = []
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == "number":
                    id.append(str(entity['value']))
            if len(id) == 0:
                id = None
            else:
                id = "".join(id)
            if id is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. What is the order number of the order you want to cancel?")
                return [SlotSet("last_message", "What is the order number of the order you want to cancel?")]
            dispatcher.utter_message(text="Retrieving information for order number " + str(id) + ".")

            ordination = retrieve_order(id)
            if ordination is None:
                dispatcher.utter_message(text="Sorry, I couldn't find any order with that order number.")
                dispatcher.utter_message(text="What is the order number of the order you want to cancel?")
                return [SlotSet("last_message", "What is the order number of the order you want to cancel?"), SlotSet("order_id", None)]
            
            order = eval(ordination[1])
            total = ordination[2]
            method = ordination[3]
            date = ordination[4]
            n_people = ordination[5]
            address = ordination[6]

            utter="The order you made consists of: "
            for elem in order:
                for value in elem:
                    utter += value + " "
                utter = utter[:-1] + " "
            utter = utter[:-1] + ". The total is "
            utter += total + "€. "
            if method == 'takeaway':
                parsed_date = parse_date(date)
                date_utter = parsed_date['hour_date'] + ":" + parsed_date['minute_date'] + " " + parsed_date['am/pm']
                utter += "You chose to do takeaway. The order will be ready at " + date_utter + "."
            elif method == 'delivery':
                parsed_date = parse_date(date)
                date_utter = parsed_date['hour_date'] + ":" + parsed_date['minute_date'] + " " + parsed_date['am/pm']
                utter += "You chose to have the order delivered. The order will be delivered at " + date_utter + " to " + address + "."
            else:
                parsed_date = parse_date(date)
                date_utter = parsed_date['day_name'] + " " + parsed_date['day_date'] + " " + parsed_date['month_name'] + " at " + parsed_date['hour_date'] + ":" + parsed_date['minute_date'] + " " + parsed_date['am/pm']
                utter += "You chose to make a reservation for " + n_people + " people for " + date_utter + "."
            
            dispatcher.utter_message(text=utter)
            dispatcher.utter_message(text="Do you confirm you want to cancel this order?")

            return [SlotSet("asking_id", False), SlotSet("last_message", "Do you confirm you want to cancel this order?"), SlotSet("order_id", id), SlotSet("asking_cancel", True)]

        dispatcher.utter_message(text="First I need the order number you were given during checkout. Please tell me your order number?")

        return [SlotSet("change_order_procedure", True), SlotSet("asking_change_order", False), SlotSet("last_message", "What is the order number of the order you want to change?"), SlotSet("asking_id", True)]


class ActionChangeOrderNotConfirmed(Action):
    def name(self) -> Text:
        return "action_change_order_not_confirmed"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="Ok, so what would you like to order?")

        return [SlotSet("asking_change_order", False), SlotSet("last_message", "What would you like to order?")]


class ActionConfirmOrder(Action):
    def name(self) -> Text:
        return "action_confirm_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        dispatcher.utter_message(text="Your order has been confirmed.")
        
        order = tracker.get_slot("order")
        utter = "Your order consists of: "
        for elem in order:
            for value in elem:
                utter += value + " "
            utter = utter[:-1] + " "
        utter = utter[:-1] + ". The total is "
        utter += str(get_total(order)) + "€. "
        dispatcher.utter_message(text=utter)

        dispatcher.utter_message(text="Would you like to do take away, have the order delivered to you or do you prefer to eat here?")
        return [SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", True), SlotSet("choosing_eating_place", True), SlotSet("last_message", "Would you like to do take away, have the order delivered to you or do you prefer to eat here?"), SlotSet("total", get_total(order))]


class ActionUtterMenu(Action):
    def name(self) -> Text:
        return "action_utter_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        menu = get_menu()

        utter = "We have "
        for pizza in menu:
            utter += pizza + ", "
        utter = utter[:-2] + "."

        recommendation = menu[random.randint(0, 10)]
        utter += " Today we recommend " + recommendation + "."

        dispatcher.utter_message(text=utter)

        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterCost(Action):
    def name(self) -> Text:
        return "action_utter_cost"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        order = tracker.get_slot("order")
        if order is None or len(order) == 0:
            dispatcher.utter_message(text="You haven't ordered anything yet.")
            return [FollowupAction(name = "action_repeat_last_message")]
        total = get_total(order)
        dispatcher.utter_message(text="The total is " + str(total) + "€. ")

        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterFunctions(Action):
    def name(self) -> Text:
        return "action_utter_functions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        dispatcher.utter_message(text="I'm here to handle you ordination or to cancel a previous order. Ask for the menu or options for intolerances if you'd like.")

        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterAffluence(Action):
    def name(self) -> Text:
        return "action_utter_affluence"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        date = None
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'time':
                date = entity['value']
        
        if date is None:
            dispatcher.utter_message(text="Today it's not usually crowded.")
        else:
            parsed_date = parse_date(date)
            date_utter = parsed_date['day_name'] + "s"
            dispatcher.utter_message(text="On " + date_utter + " it's usually not crowded.")
        
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterAllergies(Action):
    def name(self) -> Text:
        return "action_utter_allergies"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        allergies = tracker.get_slot("allergies")
        
        if allergies == "gluten":
            options = get_gluten_options()
            if len(options) == 0:
                dispatcher.utter_message(text="Sorry. We don't have gluten free options.")
            if len(options) == 1:
                dispatcher.utter_message(text="Our only gluten free option is " + options[0] + ".")
            else:
                utter = "Our gluten free options are "
                for option in options:
                    utter += option + ", "
                utter = utter[:-2] + "."
                dispatcher.utter_message(text=utter)
            return [FollowupAction(name = "action_repeat_last_message")]
        elif allergies == "lactose":
            options = get_lactose_options()
            if len(options) == 0:
                dispatcher.utter_message(text="Sorry. We don't have lactose free options.")
            if len(options) == 1:
                dispatcher.utter_message(text="Our only lactose free option is " + options[0] + ".")
            else:
                utter = "Our lactose free options are "
                for option in options:
                    utter += option + ", "
                utter = utter[:-2] + "."
                dispatcher.utter_message(text=utter)
            return [FollowupAction(name = "action_repeat_last_message")]
        elif allergies == "vegan":
            options = get_vegan_options()
            if len(options) == 0:
                dispatcher.utter_message(text="Sorry. We don't have vegan options.")
            if len(options) == 1:
                dispatcher.utter_message(text="Our only vegan option is " + options[0] + ".")
            else:
                utter = "Our vegan options are "
                for option in options:
                    utter += option + ", "
                utter = utter[:-2] + "."
                dispatcher.utter_message(text=utter)
            return [FollowupAction(name = "action_repeat_last_message")]
        elif allergies == "vegetarian":
            options = get_vegetarian_options()
            if len(options) == 0:
                dispatcher.utter_message(text="Sorry. We don't have vegetarian options.")
            if len(options) == 1:
                dispatcher.utter_message(text="Our only vegetarian option is " + options[0] + ".")
            else:
                utter = "Our vegetarian options are "
                for option in options:
                    utter += option + ", "
                utter = utter[:-2] + "."
                dispatcher.utter_message(text=utter)
            return [FollowupAction(name = "action_repeat_last_message")]

        menu = get_menu()
        utter = "Our menu is: "
        for pizza in menu:
            utter += pizza + ", "
        utter = utter[:-2] + "."
        dispatcher.utter_message(text=utter)

        options = get_gluten_options()
        if len(options) == 0:
            dispatcher.utter_message(text="Sorry. We don't have gluten free options.")
        if len(options) == 1:
            dispatcher.utter_message(text="Our only gluten free option is " + options[0] + ".")
        else:
            utter = "Our gluten free options are "
            for option in options:
                utter += option + ", "
            utter = utter[:-2] + "."
            dispatcher.utter_message(text=utter)

        options = get_lactose_options()
        if len(options) == 0:
            dispatcher.utter_message(text="Sorry. We don't have lactose free options.")
        if len(options) == 1:
            dispatcher.utter_message(text="Our only lactose free option is " + options[0] + ".")
        else:
            utter = "Our lactose free options are "
            for option in options:
                utter += option + ", "
            utter = utter[:-2] + "."
            dispatcher.utter_message(text=utter)

        options = get_vegan_options()
        if len(options) == 0:
            dispatcher.utter_message(text="Sorry. We don't have vegan options.")
        if len(options) == 1:
            dispatcher.utter_message(text="Our only vegan option is " + options[0] + ".")
        else:
            utter = "Our vegan options are "
            for option in options:
                utter += option + ", "
            utter = utter[:-2] + "."
            dispatcher.utter_message(text=utter)
            
        options = get_vegetarian_options()
        if len(options) == 0:
            dispatcher.utter_message(text="Sorry. We don't have vegetarian options.")
        if len(options) == 1:
            dispatcher.utter_message(text="Our only vegetarian option is " + options[0] + ".")
        else:
            utter = "Our vegetarian options are "
            for option in options:
                utter += option + ", "
            utter = utter[:-2] + "."
            dispatcher.utter_message(text=utter)
        
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionTakeaway(Action):
    def name(self) -> Text:
        return "action_takeaway"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("asking_time_takeaway"):
            date = None
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'time':
                    date = entity['value']
            if date is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. When would you like to pick up your order?")
                return []
            
            parsed_date = parse_date(date)
            date_utter = parsed_date['hour_date'] + ":" + parsed_date['minute_date'] + " " + parsed_date['am/pm']
            dispatcher.utter_message(text="Ok. Your order will be ready at " + date_utter + ".")
            return [SlotSet("asking_time_takeaway", False), SlotSet("time", date), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!"), FollowupAction(name = "action_save_order")]

        utter = "You have decided to do takeaway."
        utter += " Our address is Sommarive Street, 9, 38123 Povo TN."
        utter += " Payment will be done at takeaway."
        utter += " When would you like to pick up your order?"

        dispatcher.utter_message(text=utter)

        return [SlotSet("choosing_eating_place", False), SlotSet("last_message", "When would you like to pick up your order?"), SlotSet("asking_time_takeaway", True), SlotSet("method", "takeaway")]


class ActionDelivery(Action):
    def name(self) -> Text:
        return "action_delivery"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("asking_time_delivery"):
            date = None
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'time':
                    date = entity['value']
            if date is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. When would you like the order to be delivered?")
                return []
            
            parsed_date = parse_date(date)
            date_utter = parsed_date['hour_date'] + ":" + parsed_date['minute_date'] + " " + parsed_date['am/pm']
            dispatcher.utter_message(text="Ok. Your order will be delivered at " + date_utter + ".")
            dispatcher.utter_message(text="What is the address for the delivery?")
            return [SlotSet("asking_time_delivery", False), SlotSet("time", date), SlotSet("last_message", "What is the address for the delivery?"), SlotSet("asking_address", True)]

        if tracker.get_slot("asking_address"):
            if tracker.get_slot("address") is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. What is the address for the delivery?")
                return []
            dispatcher.utter_message(text="Ok. Your order will be delivered at " + tracker.get_slot("address") + ".")
            return [SlotSet("asking_address", False), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!"), FollowupAction(name = "action_save_order")]
        
        utter = "You have decided to have the order delivered."
        utter += " Payment will be done at delivery time."
        utter += " When would you like the order to be delivered?"
        dispatcher.utter_message(text=utter)

        return [SlotSet("choosing_eating_place", False), SlotSet("last_message", "When would you like the order to be delivered?"), SlotSet("asking_time_delivery", True), SlotSet("method", "delivery")]


class ActionTable(Action):
    def name(self) -> Text:
        return "action_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("asking_people"):
            entities = tracker.latest_message['entities']
            amounts = []
            for entity in entities:
                if entity['entity'] == 'amounts':
                    amounts.append(entity['value'])
                if entity['entity'] == 'number':
                    amounts.append(str(entity['value']))
            if len(amounts) == 0:
                dispatcher.utter_message(text="Sorry, I didn't get that. How many people do you want to make the reservation for?")
                return []
            dispatcher.utter_message(text="Ok. Your reservation is for " + amounts[0] + " people.")
            dispatcher.utter_message(text="For what day and time do you want to make the reservation for?")
            return [SlotSet("asking_people", False), SlotSet("last_message", "For what day and time do you want to make the reservation for?"), SlotSet("asking_time_table", True), SlotSet("n_people", amounts[0])]

        if tracker.get_slot("asking_time_table"):
            date = None
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'time':
                    date = entity['value']
            if date is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. For what day and time do you want to make the reservation for?")
                return [SlotSet("time", None)]
            
            parsed_date = parse_date(date)
            date_utter = parsed_date['day_name'] + " " + parsed_date['day_date'] + " " + parsed_date['month_name'] + " at " + parsed_date['hour_date'] + ":" + parsed_date['minute_date'] + " " + parsed_date['am/pm']
            dispatcher.utter_message(text="Ok. Your reservation is for " + date_utter + ".")
            return [SlotSet("asking_time_table", False), SlotSet("time", date), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!"), FollowupAction(name = "action_save_order")]

        utter = "You have decided to make a reservation."
        utter += " I just need some more information. How many people do you want to make the reservation for?"
        dispatcher.utter_message(text=utter)

        return [SlotSet("choosing_eating_place", False), SlotSet("asking_people", True), SlotSet("last_message", "How many people do you want to make the reservation for?"), SlotSet("method", "table")]


class ActionRepeatLastMessage(Action):
    def name(self) -> Text:
        return "action_repeat_last_message"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        last_message = tracker.get_slot("last_message")
        if last_message is not None:
            dispatcher.utter_message(text=last_message)

        return [FollowupAction(name = "action_listen")]


class ActionUtterImABot(Action):
    def name(self) -> Text:
        return "action_utter_imabot"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="I am PizzaBot, a bot powered by Rasa to handle your order.")
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterOutOfScope(Action):
    def name(self) -> Text:
        return "action_utter_out_of_scope"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="Sorry, I cannot answer that.")
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterGreet(Action):
    def name(self) -> Text:
        return "action_utter_greet"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="Hello, I am PizzaBot, here to handle you order.")
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterAddress(Action):
    def name(self) -> Text:
        return "action_utter_address"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="Our address is Sommarive Street, 9, 38123 Povo TN.")
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterOpeningHours(Action):
    def name(self) -> Text:
        return "action_utter_opening_hours"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="We are open from 6 p.m. to 11 p.m. on weekdays and from 11 a.m. to midnight on weekends.")
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionSaveOrder(Action):
    def name(self) -> Text:
        return "action_save_order"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        method = tracker.get_slot("method")
        order = tracker.get_slot("order")
        total = tracker.get_slot("total")
        time = tracker.get_slot("time")
        n_people = tracker.get_slot("n_people")
        address = tracker.get_slot("address")

        order_id = save_new_order(method, order, total, time, n_people, address)

        dispatcher.utter_message(text="If you want to cancel your order in the future, please remember your order number: " + str(order_id) + ".")
        dispatcher.utter_message(text="The procedure is complete! Thank you for using PizzaBot. Goodbye!")

        return []


class ActionYouAreWelcome(Action):
    def name(self) -> Text:
        return "action_you_are_welcome"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="You are welcome!")
        return [FollowupAction(name = "action_repeat_last_message")]