from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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
        pizza_types = []
        pizza_sizes = []
        order = []

        for e in entities:
            if e['entity'] == 'pizza_amounts':
                pizza_amounts.append((e['value'], e['group']))
            elif e['entity'] == 'pizza_types':
                pizza_types.append((e['value'], e['group']))
            elif e['entity'] == 'pizza_sizes':
                pizza_sizes.append((e['value'], e['group']))
        
        # dispatcher.utter_message(text="amounts: " + str(pizza_amounts))
        # dispatcher.utter_message(text="types: " + str(pizza_types))
        # dispatcher.utter_message(text="sizes: " + str(pizza_sizes))

        if len(pizza_amounts) == 0:
            if len(pizza_types) == 0:
                dispatcher.utter_message(text="What would you like to order?")
                return []
        else:
            if len(pizza_amounts) == len(pizza_types):
                for i in range(len(pizza_amounts)):
                    order.append((get_amount_for_group(pizza_amounts, pizza_types[i][1]), pizza_types[i][0], get_size_for_group(pizza_sizes, pizza_types[i][1])))
            if len(pizza_amounts) > 0 and len(pizza_types) == 0:
                dispatcher.utter_message(text="What would you like to order?")
                return []
        if order == []:
            for i in range(len(pizza_types)):
                order.append((get_amount_for_group(pizza_amounts, pizza_types[i][1]), pizza_types[i][0], get_size_for_group(pizza_sizes, pizza_types[i][1])))

        utter = "Your order is: "
        if new:
            utter = "Your new order is: "
        for pizza in order:
            utter += pizza[0] + " " + pizza[2] + " " + pizza[1] + ", "
        utter = utter[:-2]
        utter += ". Is it correct?"
        dispatcher.utter_message(text=utter)

        return [SlotSet("order", None), SlotSet("temp_order", order), SlotSet("temp_order_set", True)]


class ActionOrderConfirmed(Action):
    def name(self) -> Text:
        return "action_order_confirmed"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
    
        order = tracker.get_slot("temp_order")
        dispatcher.utter_message(text="Your order has been confirmed.")

        return [SlotSet("order", order), SlotSet("temp_order", None), SlotSet("temp_order_set", False)]

class ActionOrderNotConfirmed(Action):
    def name(self) -> Text:
        return "action_order_not_confirmed"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        
        dispatcher.utter_message(text="I'm sorry. Could you repeat you order? Please try rephrasing it.")
        return [SlotSet("temp_order", None), SlotSet("temp_order_set", False)]
