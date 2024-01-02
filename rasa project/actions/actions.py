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

def get_amount_for_group(pizza_amounts, group):
    for amount in pizza_amounts:
        if amount[1] == group:
            return amount[0]
    return "1"


class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        new = False
        if tracker.get_slot("order") is not None and tracker.get_slot("temp_order") is None:
            order_set = True
            dispatcher.utter_message(text="You already made an order. I'm going to cancel your old order.")
            new = True

        entities = tracker.latest_message['entities']
        pizza_amounts = []
        pizza_types_temp = []
        pizza_sizes = []
        order = []

        for e in entities:
            if e['entity'] == 'pizza_amounts':
                pizza_amounts.append((e['value'], e['group']))
            elif e['entity'] == 'pizza_types':
                pizza_types_temp.append((e['value'], e['group']))
            elif e['entity'] == 'pizza_sizes':
                pizza_sizes.append((e['value'], e['group']))
        
        menu = ["margherita", "pepperoni", "funghi"]
        pizza_types = []
        for type in pizza_types_temp:
            for line in menu:
                if type[0] in line:
                    pizza_types.append(type)

        if len(pizza_amounts) == 0:
            if len(pizza_types) == 0:
                dispatcher.utter_message(text="What would you like to order?")
                return [SlotSet("order", None), SlotSet("order_set", False)]
        else:
            if len(pizza_amounts) == len(pizza_types):
                for i in range(len(pizza_amounts)):
                    order.append((get_amount_for_group(pizza_amounts, pizza_types[i][1]), pizza_types[i][0], get_size_for_group(pizza_sizes, pizza_types[i][1])))
            if len(pizza_amounts) > 0 and len(pizza_types) == 0:
                dispatcher.utter_message(text="What would you like to order?")
                return [SlotSet("order", None), SlotSet("order_set", False)]
        if order == []:
            for i in range(len(pizza_types)):
                order.append((get_amount_for_group(pizza_amounts, pizza_types[i][1]), pizza_types[i][0], get_size_for_group(pizza_sizes, pizza_types[i][1])))

        allergies = tracker.get_slot("allergies")
        if allergies == "gluten":
            # check if order contains gluten, if it does, warn the user and the proceed
            dispatcher.utter_message(text="Looks like you have asked us for gluten free options but...")
        elif allergies == "lactose":
            # check if order contains gluten, if it does, warn the user and the proceed
            dispatcher.utter_message(text="Looks like you have asked us for lactose free options but...")
        elif allergies == "vegan":
            # check if order contains gluten, if it does, warn the user and the proceed
            dispatcher.utter_message(text="Looks like you have asked us for " + allergies + " options but...")
        elif allergies == "vegetarian":
            # check if order contains gluten, if it does, warn the user and the proceed
            dispatcher.utter_message(text="Looks like you have asked us for " + allergies + " options but...")

        utter = "Your order is: "
        if new:
            utter = "Your new order is: "
        for pizza in order:
            utter += pizza[0] + " " + pizza[2] + " " + pizza[1] + ", "
        utter = utter[:-2]
        utter += ". Do you confirm?"
        dispatcher.utter_message(text=utter)

        return [SlotSet("order", None), SlotSet("order_set", False), SlotSet("temp_order", order), SlotSet("temp_order_set", True)]


class ActionOrderConfirmed(Action):
    def name(self) -> Text:
        return "action_order_confirmed"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
    
        order = tracker.get_slot("temp_order")
        dispatcher.utter_message(text="Your order has been confirmed.")

        return [SlotSet("order", order), SlotSet("order_set", True), SlotSet("temp_order", None), SlotSet("temp_order_set", False)]


class ActionOrderNotConfirmed(Action):
    def name(self) -> Text:
        return "action_order_not_confirmed"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="I'm sorry. Could you repeat you order? Please try rephrasing it.")
        return [SlotSet("temp_order", None), SlotSet("temp_order_set", False)]


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