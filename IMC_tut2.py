import json
from typing import Dict, List
from datamodel import Order, TradingState, Trade, OrderDepth
from json import JSONEncoder

Time = int
Symbol = str
Product = str
Position = int
UserId = str
Observation = int


class Trader:
    def run(self, state: TradingState) -> Dict[str, Order]:
        result = {}
        for product in state.listings:
            if product not in state.position:
                state.position[product] = 0
            
            # Calculate the midpoint price between the best bid and ask prices
            best_bid = max(state.order_depths[product].buy_orders.keys())
            best_ask = min(state.order_depths[product].sell_orders.keys())
            midpoint_price = (best_bid + best_ask) / 2
            
            # Calculate the order book depth at the midpoint price
            buy_depth = state.order_depths[product].buy_orders.get(best_bid, 0)
            sell_depth = state.order_depths[product].sell_orders.get(best_ask, 0)
            book_depth = min(buy_depth, abs(sell_depth))
            
            # Calculate the volatility of the market
            market_trades = state.market_trades[product]
            last_price = market_trades[-1].price
            prices = [trade.price for trade in market_trades[:-1]]
            volatility = sum(abs(price - last_price) for price in prices) / len(prices) if prices else 0
            
            # Determine the trend of the market
            if prices:
                market_direction = "up" if last_price > prices[-1] else "down"
            else:
                market_direction = "none"
            
            # Determine whether to buy or sell
            if market_direction == "up":
                if book_depth > 0:
                    price = best_ask + 1
                    quantity = min(book_depth, 10)
                    order_side = OrderDepth.SELL
                    order = Order(product, price, quantity, order_side)
                    result[product] = order
            elif market_direction == "down":
                if book_depth > 0:
                    price = best_bid - 1
                    quantity = min(book_depth, 10)
                    order_side = OrderDepth.BUY
                    order = Order(product, price, quantity, order_side)
                    result[product] = order
            
            # Limit position to maximum position limit
            if state.position[product] > 20:
                price
