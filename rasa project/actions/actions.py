from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
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


class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("order_confirmed"):
            dispatcher.utter_message(text="I'm sorry but your order has already been confirmed.")
            return []
        
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
            return [SlotSet("order", old_order), SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False)]
        
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
        utter = utter[:-2] + "."
        dispatcher.utter_message(text=utter)

        dispatcher.utter_message(text="Is it correct?")

        return [SlotSet("order", old_order), SlotSet("temp_order", temp_order), SlotSet("asking_correct", True), SlotSet("asking_anything_else", False), SlotSet("order_confirmed", False)]


class ActionOrderCorrect(Action):
    def name(self) -> Text:
        return "action_order_correct"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        old_order = [] if tracker.get_slot("order") is None else tracker.get_slot("order")

        order = tracker.get_slot("temp_order") + old_order
        dispatcher.utter_message(text="Ok, do you want anything else?")

        return [SlotSet("order", order), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("asking_anything_else", True), SlotSet("order_confirmed", False)]


class ActionOrderIncorrect(Action):
    def name(self) -> Text:
        return "action_order_incorrect"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        dispatcher.utter_message(text="Sorry, could you repeat your order? Try rephrasing it.")
        return [SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", False)]


class ActionChangeOrder(Action):
    def name(self) -> Text:
        return "action_change_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        if tracker.get_slot("order_confirmed"):
            dispatcher.utter_message(text="I'm sorry but your order has already been confirmed.")
            return []

        dispatcher.utter_message(text="Ok, let's start over. What would you like to order?")
        return [SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order", None), SlotSet("order_confirmed", False)]


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
        return [SlotSet("asking_anything_else", False), SlotSet("asking_correct", False), SlotSet("temp_order", None), SlotSet("order_confirmed", True), SlotSet("choosing_eating_place", True)]


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

        return []


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
        
        return []


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
        
        return []


class ActionTakeaway(Action):
    def name(self) -> Text:
        return "action_takeaway"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="takeaway action")
        return [SlotSet("choosing_eating_place", False)]


class ActionDelivery(Action):
    def name(self) -> Text:
        return "action_delivery"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="delivery action")
        return [SlotSet("choosing_eating_place", False)]


class ActionTable(Action):
    def name(self) -> Text:
        return "action_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="table action")
        return [SlotSet("choosing_eating_place", False)]
