from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import random


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

def get_menu():
    return ["margherita", "pepperoni", "funghi", "coke", "fanta", "sprite", "water", "tea", "cheesecake", "tiramisu", "ice cream"]

def get_menu_prices():
    return {"margherita": 5, "pepperoni": 6, "funghi": 5.50, "coke": 2.50, "fanta": 2, "sprite": 2, "water": 1, "tea": 2, "cheesecake": 4, "tiramisu": 4.50, "ice cream": 3}

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

def save_new_order(method, order, total, time, n_people, address):
    file = open("orders.txt", "r")
    lines = file.readlines()
    orders = []
    for line in lines:
        orders.append(line.split("*/*"))
    file.close()

    id = 0
    for i in range(0, 100000):
        found = False
        for order in orders:
            if int(order[0]) == i:
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
            file.write(str(order[0]) + "*/*" + str(order[1]) + "*/*" + str(order[2]) + "*/*" + str(order[3]) + "*/*" + str(order[4]) + "*/*" + 
                str(order[5]) + "*/*" + str(order[6]) + "*/*" + str(order[7]))
    file.close()


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
                amounts.append((entity['value'], entity['group']))
            elif entity['entity'] == 'pizza_types':
                temp_pizza_types.append((entity['value'], entity['group']))
            elif entity['entity'] == 'pizza_sizes':
                pizza_sizes.append((entity['value'], entity['group']))
            elif entity['entity'] == 'other_item_types':
                temp_other_items_types.append((entity['value'], entity['group']))

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
        
        # general order, no specific item, like "i want to order a pizza"
        if len(pizza_types) == 0 and len(other_items_types) == 0:
            return [SlotSet("order", old_order), SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False), SlotSet("asking_change_order", False), FollowupAction(name = "action_repeat_last_message")]
        
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

        dispatcher.utter_message(text="I'm sorry, I misunderstood. Try rephrasing you order. What would you like to order?")
        return [SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False), SlotSet("last_message", "Sorry for my confusion, what would you like to order?")]


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
        
        dispatcher.utter_message(text="Do you wish to cancel an order made in a previous call/conversation?")
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
            id = tracker.get_slot("order_id")
            if id is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. What is the id of the order you want to cancel? Please insert only the id in your message.")
                return [SlotSet("last_message", "What is the id of the order you want to cancel? Please insert only the id in your message.")]
            dispatcher.utter_message(text="You inserted the id: <" + str(id) + ">.")

            ordination = retrieve_order(id)
            if ordination is None:
                dispatcher.utter_message(text="Sorry, I couldn't find any order with that id.")
                dispatcher.utter_message(text="What is the id of the order you want to cancel? Please insert only the id in your message.")
                return [SlotSet("last_message", "What is the id of the order you want to cancel? Please insert only the id in your message."), SlotSet("order_id", None)]
            
            order = eval(ordination[1])
            total = ordination[2]
            method = ordination[3]
            date = ordination[4]
            n_people = ordination[5]
            address = ordination[6]

            utter="The order you made consists of:\n"
            for elem in order:
                utter += "- "
                for value in elem:
                    utter += value + " "
                utter = utter[:-1] + "\n"
            utter = utter[:-1] + "\nThe total is "
            utter += total + "€.\n"
            if method == 'takeaway':
                utter += "You chose to do takeaway. The order will be ready at " + date + "."
            elif method == 'delivery':
                utter += "You chose to have the order delivered. The order will be delivered at " + date + " to " + address + "."
            else:
                utter += "You chose to make a reservation for " + n_people + " people for " + date + "."
            
            dispatcher.utter_message(text=utter)
            dispatcher.utter_message(text="Do you confirm you want to cancel this order?")

            return [SlotSet("asking_id", False), SlotSet("last_message", "Do you confirm you want to cancel this order?"), SlotSet("order_id", id), SlotSet("asking_cancel", True)]

        dispatcher.utter_message(text="First I need the order id you were given during checkout. Please tell me your order id?")

        return [SlotSet("change_order_procedure", True), SlotSet("asking_change_order", False), SlotSet("last_message", "What is the id of the order you want to change?"), SlotSet("asking_id", True)]


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
        
        allergies = tracker.get_slot("allergies")
        if allergies is not None:
            dispatcher.utter_message(text="Looks like you have asked us for " + allergies + " options but... (here goes the check)")

        dispatcher.utter_message(text="Your order has been confirmed.")
        
        order = tracker.get_slot("order")
        utter = "Your order consists of:\n"
        for elem in order:
            utter += "- "
            for value in elem:
                utter += value + " "
            utter = utter[:-1] + "\n"
        utter = utter[:-1] + "\nThe total is "
        utter += str(get_total(order)) + "€."
        dispatcher.utter_message(text=utter)

        dispatcher.utter_message(text="Would you like to do take away, have the order delivered to you or do you prefer to eat here?")
        return [SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", True), SlotSet("choosing_eating_place", True), SlotSet("last_message", "Would you like to do take away, have the order delivered to you or do you prefer to eat here?"), SlotSet("total", get_total(order))]


class ActionUtterMenu(Action):
    def name(self) -> Text:
        return "action_utter_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        menu = ["margherita", "pepperoni", "funghi"]

        utter = "We have "
        for pizza in menu:
            utter += pizza + ", "
        utter = utter[:-2] + "."

        recommendation = menu[random.randint(0, len(menu)-1)]
        utter += " Today we recommend " + recommendation + "."

        dispatcher.utter_message(text=utter)

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
            dispatcher.utter_message(text="Today/right now it's not usually crowded.")
        else:
            dispatcher.utter_message(text="On " + date + " it's not crowded.")
        
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterAllergies(Action):
    def name(self) -> Text:
        return "action_utter_allergies"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        allergies = tracker.get_slot("allergies")
        
        if allergies == "gluten":
            dispatcher.utter_message(text="Our gluten free options are...")
            return [FollowupAction(name = "action_repeat_last_message")]
        elif allergies == "lactose":
            dispatcher.utter_message(text="Our lactose free options are...")
            return [FollowupAction(name = "action_repeat_last_message")]
        elif allergies == "vegan":
            dispatcher.utter_message(text="Our vegan options are...")
            return [FollowupAction(name = "action_repeat_last_message")]
        elif allergies == "vegetarian":
            dispatcher.utter_message(text="Our vegetarian options are...")
            return [FollowupAction(name = "action_repeat_last_message")]

        menu = ["margherita", "pepperoni", "funghi"]
        utter = "Our menu is: "
        for pizza in menu:
            utter += pizza + ", "
        utter = utter[:-2] + "."
        dispatcher.utter_message(text=utter)

        dispatcher.utter_message(text="Our gluten free options are... Our lactose free options are...")
        dispatcher.utter_message(text="Our vegan options are... Our vegetarian options are...")
        
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
            dispatcher.utter_message(text="Ok. Your order will be ready at " + date + ".")
            return [SlotSet("asking_time_takeaway", False), SlotSet("time", date), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!"), FollowupAction(name = "action_save_order")]

        utter = "You have decided to do takeaway."
        utter += "\nOur address is Sommarive Street, 9, 38123 Povo TN."
        utter += "\nPayment will be done at takeaway."
        utter += "\nWhen would you like to pick up your order?"

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
            dispatcher.utter_message(text="Ok. Your order will be delivered at " + date + ".")
            dispatcher.utter_message(text="What is the address for the delivery?")
            return [SlotSet("asking_time_delivery", False), SlotSet("time", date), SlotSet("last_message", "What is the address for the delivery?"), SlotSet("asking_address", True)]

        if tracker.get_slot("asking_address"):
            if tracker.get_slot("address") is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. What is the address for the delivery?")
                return []
            dispatcher.utter_message(text="Ok. Your order will be delivered at " + tracker.get_slot("address") + ".")
            return [SlotSet("asking_address", False), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!"), FollowupAction(name = "action_save_order")]
        
        utter = "You have decided to have the order delivered."
        utter += "\nPayment will be done at delivery time."
        utter += "\nWhen would you like the order to be delivered?"
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
            dispatcher.utter_message(text="Ok. Your reservation is for " + date + ".")
            return [SlotSet("asking_time_table", False), SlotSet("time", date), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!"), FollowupAction(name = "action_save_order")]

        utter = "You have decided to make a reservation."
        utter += "\nI just need some more information.\nHow many people do you want to make the reservation for?"
        dispatcher.utter_message(text=utter)

        return [SlotSet("choosing_eating_place", False), SlotSet("asking_people", True), SlotSet("last_message", "How many people do you want to make the reservation for?")
                , SlotSet("method", "table")]


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
        dispatcher.utter_message(text="We are open from 18:00 to 23:00 on weekdays and from 11:00 to midnight on weekends.")
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

        dispatcher.utter_message(text="If you want to cancel your order in the future, please remember your order id: " + str(order_id) + ".")
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