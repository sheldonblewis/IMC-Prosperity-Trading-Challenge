from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, Symbol, ProsperityEncoder
import numpy as np
import pandas as pd
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

#make that we dont buy/sell on the entire period of short/up trend
NumberOfIterations_Colada = 0

EMA_Berries = 0
QUEUE_Berries = []
EMA_YESTERDAY_Berries = 0
BEST_EVER_Beries_Spread = 0

Last_Short = 0
Last_Upwards = 0

Shortam = 0
Upwards = 0

pearls_q = []
bananas_q = []
coconuts_q = []

EMA_20_Colada_yesterday = []
EMA_20_Colada_today = 0

EMA_100_Colada_yesterday = []
EMA_100_Colada_today = 0

Signals_Colada = []

EMA_yesterday_coconuts = 0
EMA_yesterday_coconuts5 = 0
EMA_yesterday_coconuts18 = 0
EMA_yesterday_coconuts40 = 0

EMA_yesterday_bananas = 5000
EMA_yesterday_pearls = 10000

trend_calculator_q = []
trend_calculator_algo = []

best_ever_banana_deal_spread = 0.001

EMA_small_coconut = 0
EMA_big_coconut = 0
EMA_DAYS_SMALL = 5
EMA_DAYS_BIG = 15
last_coco_trend = -1
last_deal_price_coco = 0


def ema_calc_coco(close_today, n):
    global EMA_small_coconut
    global EMA_big_coconut
    if n == EMA_DAYS_SMALL:
        yesterday_EMA = EMA_small_coconut
    elif n == EMA_DAYS_BIG:
        yesterday_EMA = EMA_big_coconut
    else:
        return -1
    EMA_today = (close_today * (2 / (n + 1))) + (yesterday_EMA * (1 - (2 / (n + 1))))
    return EMA_today


def ema_calc(close_today, n):
    global EMA_yesterday_bananas
    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_bananas * (1 - (2 / (n + 1))))
    EMA_yesterday_bananas = EMA_today
    return EMA_today


def ema_calc_colada(close_today, n):
    global EMA_yesterday_coconuts
    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_coconuts * (1 - (2 / (n + 1))))
    EMA_yesterday_coconuts = EMA_today
def ema_calc_colada5(close_today, n):
    global EMA_yesterday_coconuts5

    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_coconuts5 * (1 - (2 / (n + 1))))
    EMA_yesterday_coconuts5 = EMA_today
    return EMA_today

def ema_calc_colada18(close_today, n):
    global EMA_yesterday_coconuts18

    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_coconuts18 * (1 - (2 / (n + 1))))
    EMA_yesterday_coconuts18 = EMA_today
    return EMA_today

def ema_calc_colada40(close_today, n):
    global EMA_yesterday_coconuts40

    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_coconuts40 * (1 - (2 / (n + 1))))
    EMA_yesterday_coconuts40 = EMA_today
    return EMA_today


# def trend_calculator(average, allTimeAverage):
#     global trend_calculator_q
#     global trend_calculator_algo
#     sume = 0
#     if len(trend_calculator_q) < 10:
#         trend_calculator_q.append(average)
#     else:
#         trend_calculator_q.pop()
#     for el in trend_calculator_q:
#         sume += el
#
#     avg = sume / len(trend_calculator_q)
#     trend_calculator_algo.append(avg)
#     if len(trend_calculator_algo) > 10:
#         trend_calculator_algo.pop()
#
#     avgAns = avg
#
#     return allTimeAverage - avgAns
#

class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                global EMA_yesterday_pearls
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                # print("bb ", best_bid, "ba", best_ask)

                mid_price = (best_ask + best_bid) / 2
                # print("midPrice: ", mid_price)
                pearls_q.append(mid_price)
                if len(pearls_q) > 100:
                    pearls_q.pop()

                average = 0
                for val in pearls_q:
                    average += val
                average /= len(pearls_q)
                # Define a fair value for the PEARLS.
                acceptable_price = int(average)
                # print("fair price (average): ", acceptable_price)
                position = state.position.get(product, 0)

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < acceptable_price:
                            # print("Possible buy deal found: ", volume, "@", price)
                            asks_lower_than_acceptable_price.append((price, volume))
                    asks_lower_than_acceptable_price.sort()
                    for price, volume in asks_lower_than_acceptable_price:
                        new_volume = min(-volume, 20 - position)
                        print("BUY ", new_volume, "@", price)
                        orders.append(Order(product, price, new_volume))
                        position += new_volume

                if len(order_depth.buy_orders) != 0:
                    bids_higher_than_acceptable_price = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > acceptable_price:
                            bids_higher_than_acceptable_price.append((price, volume))
                            # print("Possible sell deal found: ", volume, "@", price)
                    bids_higher_than_acceptable_price.sort(reverse=True)
                    for price, volume in bids_higher_than_acceptable_price:
                        new_volume = min(volume, 20 + position)
                        print("SELL ", -new_volume, "@", price)
                        orders.append(Order(product, price, -new_volume))
                        position -= new_volume

                # Add all the above the orders to the result dict
                result[product] = orders

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':
                global EMA_yesterday_bananas
                global sumAllTime
                global timestamp
                global best_ever_banana_deal_spread
                best_ever_banana_deal_spread *= 0.8
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                bananas_q.append(mid_price)
                if len(bananas_q) > 100:
                    bananas_q.pop()
                if EMA_yesterday_bananas == 0:
                    EMA_yesterday_bananas = mid_price

                average = 0
                for val in bananas_q:
                    average += val
                average /= len(bananas_q)

                Close_today = mid_price
                EMA100_Banane = ema_calc(Close_today, 100)
                EMA5_Banane = ema_calc(Close_today, 25)
                # EMA50_Banane = ema_calc(Close_today, 50)
                # EMA25_Banane = ema_calc(Close_today, 25)
                # EMA10_Banane = ema_calc(Close_today, 10)

                if len(bananas_q) < 15:
                    acceptable_price = average
                else:
                    # acceptable_price = EMA5_Banane
                    acceptable_price = EMA5_Banane
                    # acceptable_price = EMA25_Banane

                position = state.position.get(product, 0)
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < acceptable_price:
                            # print("Possible buy deal found: ", volume, "@", price)
                            asks_lower_than_acceptable_price.append((price, volume))
                            if acceptable_price - price > best_ever_banana_deal_spread:
                                best_ever_banana_deal_spread = acceptable_price - price
                    asks_lower_than_acceptable_price.sort()
                    theoretical_max_position = min(
                        20 / (best_ever_banana_deal_spread / 4) * (acceptable_price - best_ask), 20)
                    theoretical_max_position = 20

                    for price, volume in asks_lower_than_acceptable_price:
                        new_volume = min(-volume, theoretical_max_position - position)
                        print("BUY ", new_volume, "@", price)
                        orders.append(Order(product, price, new_volume))
                        position += new_volume

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    bids_higher_than_acceptable_price = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > acceptable_price:
                            bids_higher_than_acceptable_price.append((price, volume))
                            # print("Possible sell deal found: ", volume, "@", price)
                            if price - acceptable_price > best_ever_banana_deal_spread:
                                best_ever_banana_deal_spread = price - acceptable_price
                    bids_higher_than_acceptable_price.sort(reverse=True)
                    # print("best_ever_banana_deal_spread: ", best_ever_banana_deal_spread)
                    theoretical_max_position = min(
                        20 / (best_ever_banana_deal_spread / 4) * (best_bid - acceptable_price), 20)

                    theoretical_max_position = 20
                    for price, volume in bids_higher_than_acceptable_price:
                        new_volume = min(volume, theoretical_max_position + position)
                        print("SELL ", -new_volume, "@", price)
                        orders.append(Order(product, price, -new_volume))
                        position -= new_volume
                # Add all the above the orders to the result dict
                result[product] = orders

            if product == "COCONUTS":
                global EMA_small_coconut
                global EMA_big_coconut
                global last_coco_trend
                global last_deal_price_coco
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                position = state.position.get(product, 0)

                if EMA_small_coconut == 0:
                    EMA_small_coconut = mid_price
                    EMA_big_coconut = mid_price
                    last_deal_price_coco = mid_price
                EMA_big_coconut = ema_calc_coco(mid_price, EMA_DAYS_BIG)
                EMA_small_coconut = ema_calc_coco(mid_price, EMA_DAYS_SMALL)
                current_trend = last_coco_trend
                # current_trend = 1 if (EMA_small_coconut - EMA_big_coconut) > 1 else -1
                if (EMA_small_coconut - EMA_big_coconut) > 0.2:
                    current_trend = 1
                elif (EMA_small_coconut - EMA_big_coconut) < -0.2:
                    current_trend = -1

                if current_trend == last_coco_trend:
                    # place orders as maker
                    print("sEMA ", EMA_small_coconut, "        BEMA ", EMA_big_coconut, " --> ", current_trend)
                elif current_trend == 1:
                    print("# take buy order")
                    oportunity = (last_deal_price_coco - mid_price) / 30
                    position_allowance = 600 - position
                    wanted_volume = oportunity * position_allowance
                    if len(order_depth.sell_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_ask = min(order_depth.sell_orders.keys())
                        print("bb ", best_bid, "ba", best_ask)
                        asks_lower_than_acceptable_price = []
                        for price, volume in order_depth.sell_orders.items():
                            asks_lower_than_acceptable_price.append((price, volume))
                        # Sort all the available sell orders by their price
                        asks_lower_than_acceptable_price.sort()
                        for price, volume in asks_lower_than_acceptable_price:
                            new_volume = min(-volume, wanted_volume)
                            print("BUY ", new_volume, "@", price)
                            orders.append(Order(product, price, new_volume))
                            last_deal_price_coco = price
                            wanted_volume -= new_volume
                            if wanted_volume == 0:
                                break
                            else:
                                print("inca un buy")

                else:
                    print("# take sell order")
                    oportunity = -(last_deal_price_coco - mid_price) / 30
                    position_allowance = 600 + position
                    wanted_volume = oportunity * position_allowance
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_ask = min(order_depth.sell_orders.keys())
                        print("bb ", best_bid, "ba", best_ask)
                        bids_higher_than_acceptable_price = []
                        for price, volume in order_depth.buy_orders.items():
                            bids_higher_than_acceptable_price.append((price, volume))
                        # Sort all the available sell orders by their price
                        bids_higher_than_acceptable_price.sort(reverse=True)
                        for price, volume in bids_higher_than_acceptable_price:
                            new_volume = min(volume, wanted_volume)
                            print("SELL ", -new_volume, "@", price)
                            orders.append(Order(product, price, -new_volume))
                            last_deal_price_coco = price
                            wanted_volume -= new_volume
                            if wanted_volume == 0:
                                break
                            else:
                                print("inca un sell")
                last_coco_trend = current_trend
                # Add all the above the orders to the result dict
                result[product] = orders

            if product == 'PINA_COLADAS':

                global EMA_yesterday_coconuts5
                global EMA_yesterday_coconuts18
                global EMA_yesterday_coconuts40
                global EMA_yesterday_coconuts
                global AllTimesAverage_q

                global Signals_Colada

                global EMA_20_Colada_yesterday
                global EMA_20_Colada_today

                global EMA_100_Colada_yesterday
                global EMA_100_Colada_today

                global coconuts_q

                global Last_Short
                global Last_Upwards

                global Shortam
                global Upwards

                global NumberOfIterations_Colada
                # global highestBananas_value
                # global lowestBananas_value

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                best_bid2 = max(order_depth.buy_orders.keys())
                best_ask2 = min(order_depth.sell_orders.keys())

                mid_price = (best_ask2 + best_bid2) / 2

                # AverageAllTime = sumAllTime / impart

                # SOS = trend_calculator(mid_price, AverageAllTime)
                # letsSee = trend_calculator(mid_price, AverageAllTime)
                # # print("TREND CALCULATOR : ",letsSee)

                # print("midPrice: ", mid_price)
                coconuts_q.append(mid_price)
                if EMA_yesterday_coconuts == 0:
                    EMA_yesterday_coconuts = mid_price
                if EMA_yesterday_coconuts5 == 0:
                    EMA_yesterday_coconuts5 = mid_price
                if EMA_yesterday_coconuts18 == 0:
                    EMA_yesterday_coconuts18 = mid_price
                if EMA_yesterday_coconuts40 == 0:
                    EMA_yesterday_coconuts40 = mid_price

                if len(coconuts_q) > 100:
                    coconuts_q.pop()

                average = 0
                for val in coconuts_q:
                    average += val

                average /= len(coconuts_q)

                Close_today = mid_price

                average_ema = ema_calc_colada5(Close_today, 15)

                acceptable_price = average_ema

                EMA_20_Colada_yesterday.append(ema_calc_colada(Close_today, 20))
                EMA_100_Colada_yesterday.append(ema_calc_colada(Close_today, 100))




                if ema_calc_colada18(Close_today,20) > ema_calc_colada40(Close_today,50):
                    Signals_Colada.append(1)

                else:
                    Signals_Colada.append(-1)

                Shortam = 0
                Upwards = 0

                # for i , element in enumerate(Signals_Colada):
                #     if len(Signals_Colada) > 1:
                #         next_element = Signals_Colada[i+1] if i < len(Signals_Colada)-1 else None
                #         # print("Curent element ",element)
                #         # print("Next element ", next_element)
                #         if element == -1 and next_element == 1:
                #
                #             Upwards = 1
                #         elif element == 1 and next_element == -1:
                #             Shortam = -1

                if (len(Signals_Colada) > 2):
                    if (Signals_Colada[len(Signals_Colada) - 2] == -1 and Signals_Colada[len(Signals_Colada) - 1] == 1):
                        Upwards = 1
                    elif (Signals_Colada[len(Signals_Colada) - 2] == 1 and Signals_Colada[len(Signals_Colada) - 1] == -1):
                        Shortam = -1

                print("SHORTU LOCAL--  ", Shortam, "UPU LOCAL--  ", Upwards)

                if (Upwards == 1 and Shortam == 0):
                    Last_Upwards = 1
                    Last_Short = 0

                if (Upwards == 0 and Shortam == -1):
                    Last_Short = -1
                    Last_Upwards = 0

                # if(Shortam == 0 and Upwards == 1 and Last_Upwards ==1 and Last_Short == 0):
                #     Last_Upwards = 1
                #
                # if (Shortam == -1 and Upwards == 0 and Last_Upwards == 0 and Last_Short == -1):
                #     Last_Short = -1
                #
                # if (Shortam == -1 and Upwards == 0 and Last_Upwards == 1 and Last_Short == 0):
                #     Last_Short = -1

                # if(Last_Short == -1 and Shortam == 0):
                #     Last_Short = 0
                # elif(Last_Short == 0 and Shortam == -1):
                #     Last_Short = -1
                # elif(Last_Short == -1 and Shortam == -1):
                #     Last_Short = -1
                #
                #
                # if(Last_Upwards == 1 and Upwards == 0):
                #     Last_Upwards = 0
                # elif(Last_Upwards == 0 and Upwards ==1):
                #     Last_Upwards = 1
                # elif(Last_Upwards == 1 and Upwards ==1):
                #     Last_Upwards = 1

                print(Last_Short, "  -LAST SHORT-  ", Last_Upwards, "  -LAST UP-  ")

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    bestAsks2 = []
                    # asta inca nu i folosita
                    for key, value in order_depth.buy_orders.items():
                        if key < acceptable_price:
                            bestAsks2.append((key, value))

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if Last_Short == -1 :
                        if best_ask < acceptable_price:
                            print("NU CUMPARAM PE SHORT")
                            #orders.append(Order(product, best_ask, -best_ask_volume))
                            # NumberOfIterations_Colada+=1
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                            print("BUY", best_ask_volume , "x", best_ask)

                        # for key,value in bestAsks2:
                        #     orders.append(Order(product, key, -value))
                    elif Last_Upwards == 1:
                        if best_ask < acceptable_price:
                            NumberOfIterations_Colada += 1
                            for key, value in bestAsks2:
                                orders.append(Order(product, key, -value))
                                print("BUY", value , "x", key)


                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]

                    # asta inca nu i folosita
                    bestAsks = []
                    for key, value in order_depth.buy_orders.items():
                        if key > acceptable_price:
                            bestAsks.append((key, value))

                    if best_bid > acceptable_price and Last_Short == -1 :
                        NumberOfIterations_Colada += 1

                        # acCompute = trend_calculator(mid_price, AverageAllTime)
                        # print("Algo Compute", acCompute)
                        #
                        for key, value in bestAsks:
                            orders.append(Order(product, key, -value))

                        # orders.append(Order(product, best_bid, -best_bid_volume))
                    elif best_bid > acceptable_price and Last_Upwards == 1:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))
                        for key,value in bestAsks:
                            orders.append(Order(product,key,-value))
                            print("SELL", value, "x", key)
                        #orders.append(Order(product, best_bid, -best_bid_volume))


                # Add all the above the orders to the result dict
                result[product] = orders
            if product == 'BERRIES':
                global QUEUE_Berries

                global sumAllTime
                global timestamp

                global BEST_EVER_Beries_Spread
                global EMA_Berries
                global EMA_YESTERDAY_Berries

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                QUEUE_Berries.append(mid_price)
                if len(QUEUE_Berries) > 100:
                    QUEUE_Berries.pop()
                if EMA_YESTERDAY_Berries == 0:
                    EMA_YESTERDAY_Berries = mid_price

                average = 0
                for val in QUEUE_Berries:
                    average += val
                average /= len(QUEUE_Berries)

                Close_today = mid_price
                EMA_Berries = ema_calc(Close_today,30)
                # EMA50_Banane = ema_calc(Close_today, 50)
                # EMA25_Banane = ema_calc(Close_today, 25)
                # EMA10_Banane = ema_calc(Close_today, 10)

                if len(QUEUE_Berries) < 15:
                    acceptable_price = average
                else:
                    # acceptable_price = EMA5_Banane
                    acceptable_price = EMA_Berries
                    # acceptable_price = EMA25_Banane

                position = state.position.get(product, 0)
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < 3960:
                            # print("Possible buy deal found: ", volume, "@", price)
                            asks_lower_than_acceptable_price.append((price, volume))


                    for price, volume in asks_lower_than_acceptable_price:
                        print("BUY ", new_volume, "@", price)
                        orders.append(Order(product, price, new_volume))
                        position += new_volume

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    bids_higher_than_acceptable_price = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > 3985:
                            bids_higher_than_acceptable_price.append((price, -volume))




                    for price, volume in bids_higher_than_acceptable_price:

                        print("SELL ", -new_volume, "@", price)
                        orders.append(Order(product, price, -volume))

                # Add all the above the orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        logger.flush(state, result)
        return result