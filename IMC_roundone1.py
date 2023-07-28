from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
import numpy as np
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
                orders: list[Order] = []

                # Compute the weighted average price of the best bid and ask in the order book
                # This provides an estimate of the fair value of the asset
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                fair_value = (best_bid + best_ask) / 2.0

                # Compute the total volume of the best bid and ask in the order book
                # This provides an estimate of the liquidity of the market
                best_bid_volume = order_depth.buy_orders[best_bid]
                best_ask_volume = order_depth.sell_orders[best_ask]
                total_volume = abs(best_bid_volume) + abs(best_ask_volume)

                # Compute the bid-ask spread and the mid-price volatility
                # This provides an estimate of the market conditions and risks
                spread = best_ask - best_bid
                mid_price_volatility = np.std(list(order_depth.buy_orders.keys()) + list(order_depth.sell_orders.keys()))

                # Decide on the trading strategy based on the market conditions and risks
                if spread < 2 * mid_price_volatility and total_volume > 10:

                    # If the bid-ask spread is narrow and the liquidity is high,
                    # and the mid-price volatility is low,
                    # we can execute a market-making strategy by placing orders around the fair value
                    orders.append(Order(product, fair_value - 0.5, 1))
                    orders.append(Order(product, fair_value - 1, 1))
                    orders.append(Order(product, fair_value - 1.5, 1))
                    orders.append(Order(product, fair_value + 0.5, -1))
                    orders.append(Order(product, fair_value + 1, -1))
                    orders.append(Order(product, fair_value + 1.5, -1))

                elif spread > 2 * mid_price_volatility:

                    # If the bid-ask spread is wide, we can execute a trend-following strategy
                    # by placing orders in the direction of the market trend
                    if best_ask < fair_value:
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    if best_bid > fair_value:
                        orders.append(Order(product, best_bid, -best_bid_volume))

                else:

                    # If the market conditions are uncertain, we can execute a contrarian strategy
                    # by placing orders against the market trend
                    if best_ask < fair_value:
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    if best_bid > fair_value:
                        orders.append(Order(product, best_bid, -best_bid_volume))
                        orders.append(Order(product, fair_value - 0.5 , -1))
                        orders.append(Order(product, fair_value + 0.5, 1))
                    # Add the list of Orders to the method output dict with the key being the product name
                #result[product] = orders

            elif product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                fair_value = (best_bid + best_ask) / 2.0

                best_bid_volume = order_depth.buy_orders[best_bid]
                best_ask_volume = order_depth.sell_orders[best_ask]
                total_volume = abs(best_bid_volume) + abs(best_ask_volume)

                spread = best_ask - best_bid
                mid_price_volatility = np.std(list(order_depth.buy_orders.keys()) + list(order_depth.sell_orders.keys()))

                if spread < 2 * mid_price_volatility and total_volume > 10:
                    orders.append(Order(product, fair_value - 0.5, 1))
                    orders.append(Order(product, fair_value - 1, 1))
                    orders.append(Order(product, fair_value - 1.5, 1))
                    orders.append(Order(product, fair_value + 0.5, -1))
                    orders.append(Order(product, fair_value + 1, -1))
                    orders.append(Order(product, fair_value + 1.5, -1))

                elif spread > 2 * mid_price_volatility:
                    if best_ask < fair_value:
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    if best_bid > fair_value:
                        orders.append(Order(product, best_bid, -best_bid_volume))

                else:
                    if best_ask < fair_value:
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    if best_bid > fair_value:
                        orders.append(Order(product, best_bid, -best_bid_volume))
                        orders.append(Order(product, fair_value - 0.5 , -1))
                        orders.append(Order(product, fair_value + 0.5, 1))

                #result[product] = orders

        logger.flush(state, result)
        return result

    # Return the method output dict
