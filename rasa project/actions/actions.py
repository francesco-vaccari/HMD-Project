from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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


class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("order_confirmed"):
            dispatcher.utter_message(text="I'm sorry but your order has already been confirmed.")
            return [FollowupAction(name = "action_repeat_last_message")]
        
        entities = tracker.latest_message['entities']
        amounts = []
        pizza_types = []
        pizza_sizes = []
        other_items_types = []

        old_order = [] if tracker.get_slot("order") is None else tracker.get_slot("order")
        temp_order = [] if tracker.get_slot("temp_order") is None else tracker.get_slot("temp_order")
        old_order += temp_order

        # extract from entities items, amounts and sizes the user has specified
        for entity in entities:
            if entity['entity'] == 'amounts':
                amounts.append((entity['value'], entity['group']))
            elif entity['entity'] == 'pizza_types':
                pizza_types.append((entity['value'], entity['group']))
            elif entity['entity'] == 'pizza_sizes':
                pizza_sizes.append((entity['value'], entity['group']))
            elif entity['entity'] == 'other_item_types':
                other_items_types.append((entity['value'], entity['group']))

        # general order, no specific item, like "i want to order a pizza"
        if len(pizza_types) == 0 and len(other_items_types) == 0:
            dispatcher.utter_message(text="What would you like to order?")
            return [SlotSet("order", old_order), SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False), SlotSet("last_message", "What would you like to order?")]
        
        temp_order = []

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

        return [SlotSet("order", old_order), SlotSet("temp_order", temp_order), SlotSet("asking_correct", True), SlotSet("asking_anything_else", False), SlotSet("order_confirmed", False), SlotSet("last_message", utter + "Is it correct?")]


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
        
        if tracker.get_slot("order_confirmed"):
            dispatcher.utter_message(text="I'm sorry but your order has already been confirmed.")
            return [FollowupAction(name = "action_repeat_last_message")]

        dispatcher.utter_message(text="Ok, let's start over. What would you like to order?")
        return [SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order", None), SlotSet("order_confirmed", False), SlotSet("last_message", "What would you like to order?")]


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
        dispatcher.utter_message(text="Would you like to do take away, have the order delivered to you or do you prefer to eat here?")
        return [SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", True), SlotSet("choosing_eating_place", True), SlotSet("last_message", "Would you like to do take away, have the order delivered to you or do you prefer to eat here?")]


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
        
        day = tracker.get_slot("day")

        if day is None:
            dispatcher.utter_message(text="Today it's not crowded.")
        else:
            if day == "today": dispatcher.utter_message(text="Today it's not crowded.")
            elif day == "tomorrow": dispatcher.utter_message(text="Tomorrow it's usually not crowded.")
            else: dispatcher.utter_message(text="On " + day + " it's usually not crowded.")
        
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
            return []
        elif allergies == "lactose":
            dispatcher.utter_message(text="Our lactose free options are...")
            return []
        elif allergies == "vegan":
            dispatcher.utter_message(text="Our vegan options are...")
            return []
        elif allergies == "vegetarian":
            dispatcher.utter_message(text="Our vegetarian options are...")
            return []

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
            if tracker.get_slot("time") is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. When would you like to pick up your order?")
                return []
            dispatcher.utter_message(text="Ok. Your order will be ready at " + tracker.get_slot("time") + ".")
            dispatcher.utter_message(text="The procedure is complete! Thank you for using PizzaBot. Goodbye!")
            return [SlotSet("asking_time_takeaway", False), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!")]
        
        order = tracker.get_slot("order")

        utter = "Your order consists of:\n"
        for elem in order:
            utter += "- "
            for value in elem:
                utter += value + " "
            utter = utter[:-1] + "\n"
        utter = utter[:-1] + "\nThe total is "
        
        utter += str(get_total(order)) + "€.\nPayment will be done at takeaway."

        utter += "\nOur address is Via Sommarive, 9, 38123 Povo TN."
        utter += "\nWhen would you like to pick up your order?"

        dispatcher.utter_message(text=utter)

        return [SlotSet("choosing_eating_place", False), SlotSet("last_message", "When would you like to pick up your order?"), SlotSet("asking_time_takeaway", True)]


class ActionDelivery(Action):
    def name(self) -> Text:
        return "action_delivery"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("asking_time_delivery"):
            if tracker.get_slot("time") is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. When would you like the order to be delivered?")
                return []
            dispatcher.utter_message(text="Ok. Your order will be delivered at " + tracker.get_slot("time") + ".")
            dispatcher.utter_message(text="What is the address for the delivery?")
            return [SlotSet("asking_time_delivery", False), SlotSet("last_message", "What is the address for the delivery?"), SlotSet("asking_address", True)]

        if tracker.get_slot("asking_address"):
            if tracker.get_slot("address") is None:
                dispatcher.utter_message(text="Sorry, I didn't get that. What is the address for the delivery?")
                return []
            dispatcher.utter_message(text="Ok. Your order will be delivered at " + tracker.get_slot("address") + ".")
            dispatcher.utter_message(text="The procedure is complete! Thank you for using PizzaBot. Goodbye!")
            return [SlotSet("asking_address", False), SlotSet("last_message", "The procedure is complete. Thank you for using PizzaBot! Goodbye!")]
        
        order = tracker.get_slot("order")
        
        utter = "Your order consists of:\n"
        for elem in order:
            utter += "- "
            for value in elem:
                utter += value + " "
            utter = utter[:-1] + "\n"
        utter = utter[:-1] + "\nThe total is "
        
        utter += str(get_total(order)) + "€.\nPayment will be done at delivery time."
        utter += "\nWhen would you like the order to be delivered?"

        dispatcher.utter_message(text=utter)

        return [SlotSet("choosing_eating_place", False), SlotSet("last_message", "When would you like the order to be delivered?"), SlotSet("asking_time_delivery", True)]


class ActionTable(Action):
    def name(self) -> Text:
        return "action_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="table action")

        # maybe also add confirmation when asking address and time in takeaway and delivery

        # say price for current menu
        # ask how many people for table reservation
        # ask time and day for table reservation
        # say goodbye

        return [SlotSet("choosing_eating_place", False)]


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
        dispatcher.utter_message(text="Our address is Via Sommarive, 9, 38123 Povo TN.")
        return [FollowupAction(name = "action_repeat_last_message")]


class ActionUtterOpeningHours(Action):
    def name(self) -> Text:
        return "action_utter_opening_hours"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        dispatcher.utter_message(text="We are open from 18:00 to 23:00 on weekdays and from 11:00 to midnight on weekends.")
        return [FollowupAction(name = "action_repeat_last_message")]
