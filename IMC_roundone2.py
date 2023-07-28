from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
import json

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: Dict[Symbol, List[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

logger = Logger()

class Trader:

    def run(self, state: TradingState) -> Dict[Symbol, List[Order]]:
        """
        Trading algorithm that uses order book depth, market trends, and volatility to make trading decisions
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: List[Order] = []

                for bid in order_depth.buy_orders.keys():
                    if bid >= 10000:
                        orders.append(Order(product, bid, order_depth.buy_orders[bid]))

                for ask in order_depth.sell_orders.keys():
                    if ask <= 10000:
                        orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                result[product] = orders


            elif product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                bids = order_depth.buy_orders.keys()
                asks = order_depth.sell_orders.keys()

                med_value = (min(bids) + max(asks))/2

                if abs(max(bids) - min(asks)) < 5:
                    if max(bids) > med_value:
                        orders.append(Order(product, max(bids), order_depth.buy_orders[max(bids)]))
                    if min(asks) < med_value:
                        orders.append(Order(product, min(asks), -order_depth.sell_orders[min(asks)]))

                result[product] = orders


        logger.flush(state, result)
        return result

    # Return the method output dict