from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy
import json
from datamodel import Order, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any
import pandas as pd

data = pd.read_csv('C:/Users/shelb/Trading-Algorithm/prices_round_4_day_3.csv')

berries = data[data[data.columns[0]].str.contains('BERRIES')]
bananas = data[data[data.columns[0]].str.contains('BANANAS')]

berries = berries.iloc[-1500:, :]
bananas = bananas.iloc[-1500:, :]

columns = data.columns[0].split(";")
berriesdata = pd.DataFrame(columns=columns)
bananasdata = pd.DataFrame(columns=columns)

for i in range(1500):
    row = berries.iloc[i][0].split(";")
    berriesdata.loc[i] = row

    row = bananas.iloc[i][0].split(";")
    bananasdata.loc[i] = row

berriesdata = berriesdata['mid_price']
bananasdata = bananasdata['mid_price']


class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": self.compress_state(state),
            "orders": self.compress_orders(orders),
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

    def compress_state(self, state: TradingState) -> dict[str, Any]:
        listings = []
        for listing in state.listings.values():
            listings.append([listing["symbol"], listing["product"], listing["denomination"]])

        order_depths = {}
        for symbol, order_depth in state.order_depths.items():
            order_depths[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return {
            "t": state.timestamp,
            "l": listings,
            "od": order_depths,
            "ot": self.compress_trades(state.own_trades),
            "mt": self.compress_trades(state.market_trades),
            "p": state.position,
            "o": state.observations,
        }

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.buyer,
                    trade.seller,
                    trade.price,
                    trade.quantity,
                    trade.timestamp,
                ])

        return compressed

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

logger = Logger()

class Trader:
    
    
    def __init__(self):
        self.bananas_sum = 0
        self.pearls_sum = 0
        self.b_num = 0
        self.p_num = 0
        
        self.coco_ask = self.coco_bid = self.pina_ask = self.pina_bid = 0
        
        self.bd = []
        self.bl = []
        self.last_buy = 0
        
        
        self.last_berries = 1000000

    
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        def get_best_orders(book: OrderDepth):
            return (max(book.buy_orders.keys()), min(book.sell_orders.keys()))
                
        
        k = 20
        
        print(state.position)
        

        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        LIMIT = 20

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            position = state.position.get(product, 0)


            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                
                    
                

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                if(order_depth.sell_orders != {} and order_depth.buy_orders != {}):
                    mid_price = (min(order_depth.sell_orders.keys()) + max(order_depth.buy_orders.keys()))/2
                    self.pearls_sum += mid_price
                    self.p_num += 1
                    
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                
                acceptable_price = 10000
                if(self.p_num > 10):  #Start using the average price when have enough data (10 samples?)
                    acceptable_price = self.pearls_sum / self.p_num #comment this line out to go back to old version

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask] #This will be a negative number

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price and position < LIMIT:
                        best_ask_volume = max(best_ask_volume, position - LIMIT)
                        print("BUY", str(-best_ask_volume) + "x", best_ask, product)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid] #this will be positive volume
                    
                    
                    if best_bid > acceptable_price and position > -LIMIT:
                        best_bid_volume = min(best_bid_volume, LIMIT + position)
                        print("SELL", str(best_bid_volume) + "x", best_bid, product)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
                

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'BANANAS':
                
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                mid_price = (max(order_depth.sell_orders.keys()) + min(order_depth.buy_orders.keys()))/2
                new_row = {'mid_price': mid_price}
                bananasdata = bananasdata.concat(new_row, ignore_index=True)

                bids = order_depth.buy_orders.keys()
                asks = order_depth.sell_orders.keys()

                # Set MACD parameters
                fast_period = 12*30
                slow_period = 26*30
                signal_period = 9*30

                # Set EMA period
                ema_period = 50*30

                # Set take profit and stop loss levels
                take_profit = 0.02 # 2%
                stop_loss = 0.01 # 1%

                # Calculate MACD and signal line
                exp1 = bananasdata['mid_price'].ewm(span=fast_period, adjust=False).mean()
                exp2 = bananasdata['mid_price'].ewm(span=slow_period, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=signal_period, adjust=False).mean()

                # Calculate EMA
                ema = bananasdata['mid_price'].ewm(span=ema_period, adjust=False).mean()

                # Initialize position and account balance
                position = 0
                balance = 100

                # Loop through the data
                #for i in range(len(bananasdata)):

                # Check for MACD crossover
                if macd[i] > signal[i] and macd[i-1] <= signal[i-1]:

                    # Buy
                    if position == 0:
                        position = balance / bananasdata['mid_price'][i]
                        balance = 0
                        for bid in bids:
                            orders.append(Order(product, bid, order_depth.buy_orders[bid]))

                # Check for MACD crossunder
                elif macd[i] < signal[i] and macd[i-1] >= signal[i-1]:

                    # Sell
                    if position > 0:
                        balance = position * bananasdata['mid_price'][i]
                        position = 0
                        for ask in asks:
                            orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                # Check for take profit or stop loss
                elif position > 0:
                    if bananasdata['mid_price'][i] >= ema[i] * (1 + take_profit):
                        balance = position * bananasdata['mid_price'][i]
                        position = 0
                        for bid in bids:
                            orders.append(Order(product, bid, order_depth.buy_orders[bid]))
                        
                    if bananasdata['mid_price'][i] <= ema[i] * (1 - stop_loss):
                        balance = position * bananasdata['mid_price'][i]
                        position = 0
                        for ask in asks:
                            orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                # Update EMA
                ema[i] = bananasdata['mid_price'].ewm(span=ema_period, adjust=False).mean()

                # Calculate final balance
                if position > 0:
                    balance = position * bananasdata['mid_price'][i]

                result[product] = orders


            if product == 'BERRIES':

                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                mid_price = (max(order_depth.sell_orders.keys()) + min(order_depth.buy_orders.keys()))/2
                new_row = {'mid_price': mid_price}
                berriesdata = berriesdata.concat(new_row, ignore_index=True)

                bids = order_depth.buy_orders.keys()
                asks = order_depth.sell_orders.keys()

                # Set MACD parameters
                fast_period = 12*30
                slow_period = 26*30
                signal_period = 9*30

                # Set EMA period
                ema_period = 50*30

                # Set take profit and stop loss levels
                take_profit = 0.02 # 2%
                stop_loss = 0.01 # 1%

                # Calculate MACD and signal line
                exp1 = berriesdata['mid_price'].ewm(span=fast_period, adjust=False).mean()
                exp2 = berriesdata['mid_price'].ewm(span=slow_period, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=signal_period, adjust=False).mean()

                # Calculate EMA
                ema = berriesdata['mid_price'].ewm(span=ema_period, adjust=False).mean()

                # Initialize position and account balance
                position = 0
                balance = 100

                # Loop through the data
                #for i in range(len(berriesdata)):

                # Check for MACD crossover
                if macd[i] > signal[i] and macd[i-1] <= signal[i-1]:

                    # Buy
                    if position == 0:
                        position = balance / berriesdata['mid_price'][i]
                        balance = 0
                        for bid in bids:
                            orders.append(Order(product, bid, order_depth.buy_orders[bid]))

                # Check for MACD crossunder
                elif macd[i] < signal[i] and macd[i-1] >= signal[i-1]:

                    # Sell
                    if position > 0:
                        balance = position * berriesdata['mid_price'][i]
                        position = 0
                        for ask in asks:
                            orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                # Check for take profit or stop loss
                elif position > 0:
                    if berriesdata['mid_price'][i] >= ema[i] * (1 + take_profit):
                        balance = position * berriesdata['mid_price'][i]
                        position = 0
                        for bid in bids:
                            orders.append(Order(product, bid, order_depth.buy_orders[bid]))
                        
                    if berriesdata['mid_price'][i] <= ema[i] * (1 - stop_loss):
                        balance = position * berriesdata['mid_price'][i]
                        position = 0
                        for ask in asks:
                            orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                # Update EMA
                ema[i] = berriesdata['mid_price'].ewm(span=ema_period, adjust=False).mean()

                # Calculate final balance
                if position > 0:
                    balance = position * berriesdata['mid_price'][i]

                result[product] = orders


            #if product == 'DIVING_GEAR':
                #do this
                    
        CUTOFF = 2 #choose some value
        mean_ratio = 15000/8000 #we could use empirical mean instead of given prices
        
        coco_book: OrderDepth = state.order_depths["COCONUTS"]
        pina_book: OrderDepth = state.order_depths["PINA_COLADAS"]
        
        coco_best_ask = min(coco_book.sell_orders.keys())
        pina_best_buy = max(pina_book.buy_orders.keys())
        
        pina_best_ask = min(pina_book.sell_orders.keys())
        coco_best_buy = max(coco_book.buy_orders.keys())
        
        cutoff_1 = cutoff_2 = CUTOFF
        coco_pos = state.position.get("COCONUTS",0)
        pina_pos = state.position.get("PINA_COLADAS",0)
        if(pina_pos > 0 and coco_pos < 0):
            cutoff_1 *= 5 #harder to buy pinas sell coconuts
        if(pina_pos < 0 and coco_pos > 0):
            cutoff_2 *= 5 #harder to sell pinas buy coconuts
        
        diff1 = coco_best_buy * mean_ratio - pina_best_ask
        if (diff1) > cutoff_1:
            pina_vol = - pina_book.sell_orders[pina_best_ask]
            coco_vol = coco_book.buy_orders[coco_best_buy]
            trade_vol = min(pina_vol, coco_vol//2, diff1//cutoff_1)
            result["PINA_COLADAS"] = [Order("PINA_COLADAS", pina_best_ask, trade_vol)]
            result["COCONUTS"] = [Order("COCONUTS", coco_best_buy, -trade_vol * 2)] #negative trade_vol since its a sell

        diff2 = pina_best_buy - coco_best_ask * mean_ratio
        if (diff2) > cutoff_2:
            pina_vol = pina_book.buy_orders[pina_best_buy]
            coco_vol = - coco_book.sell_orders[coco_best_ask]
            trade_vol = min(pina_vol, coco_vol//2, diff2//cutoff_2)
            result["PINA_COLADAS"] = [Order("PINA_COLADAS", pina_best_buy, -trade_vol)]
            result["COCONUTS"] = [Order("COCONUTS", coco_best_ask, trade_vol * 2)] #negative trade_vol since its a sell

        picnic_book: OrderDepth = state.order_depths["PICNIC_BASKET"]
        dip_book: OrderDepth = state.order_depths["DIP"]
        bread_book: OrderDepth = state.order_depths["BAGUETTE"]
        uk_book: OrderDepth = state.order_depths["UKULELE"]
        
        result["DIP"] = []
        result["BAGUETTE"] = []
        result["UKULELE"] = []
        result["PICNIC_BASKET"] = []
        
        
        picnic_bid, picnic_ask = get_best_orders(picnic_book)
        
        if type(position) != dict:
            print("Error: position is not a dictionary")
            

        
        for i in range(5):
            try: 
                buy_cost = 0
                dips = 0
                breads = 0
                
                temp_orders = {"BAGUETTE":[], "DIP":[], "UKULELE":[]}
                
                while(dips < 4):
                    dip_sell = get_best_orders(dip_book)[1]
                    qty = min(4-dips, -dip_book.sell_orders[dip_sell]) 
                    dips += qty
                    
                    del dip_book.sell_orders[dip_sell] 
                    
                    buy_cost += dip_sell * qty
                    temp_orders["DIP"].append(Order("DIP", dip_sell, qty)) #buy
                
                while(breads < 2):
                    bread_sell = get_best_orders(bread_book)[1]
                    qty = min(2-breads, -bread_book.sell_orders[bread_sell]) 
                    breads += qty
                    
                    del bread_book.sell_orders[bread_sell] 
                    
                    buy_cost += bread_sell * qty
                    temp_orders["BAGUETTE"].append(Order("BAGUETTE", bread_sell, qty)) #buy
                    
                    
                uk_sell = get_best_orders(uk_book)[1]
                qty = 1
            
                buy_cost += uk_sell * qty
                temp_orders["UKULELE"].append(Order("UKULELE", uk_sell, qty)) #buy
            
                print(buy_cost, picnic_bid, "a")
                if(buy_cost < picnic_bid):
                    result["PICNIC_BASKET"].append(Order("PICNIC_BASKET", picnic_bid, -1)) #sell basket
                    result["DIP"].extend(temp_orders["DIP"]) #buy the rest
                    result["UKULELE"].extend(temp_orders["UKULELE"])
                    result["BAGUETTE"].extend(temp_orders["BAGUETTE"])
            except:
                pass        
                
            try:  
                sell_cost = 0
                
                
                dips = 0
                breads = 0
                
                temp_orders = {"BAGUETTE":[], "DIP":[], "UKULELE":[]}
                
                while(dips < 4):
                    #find best sell order that we will use to buy
                    dip_buy = get_best_orders(dip_book)[0]
                    qty = min(4-dips, dip_book.buy_orders[dip_buy]) 
                    dips += qty
                    del dip_book.buy_orders[dip_buy] 
                    sell_cost += dip_buy * qty
                    temp_orders["DIP"].append(Order("DIP", dip_buy, -qty)) #sell
                
                while(breads < 2):
                    bread_buy = get_best_orders(bread_book)[0]
                    qty = min(2-breads, bread_book.buy_orders[bread_buy]) 
                    breads += qty
                    del bread_book.buy_orders[bread_buy] 
                    
                    sell_cost += bread_buy * qty
                    temp_orders["BAGUETTE"].append(Order("BAGUETTE", bread_buy, -qty)) #sell
                    
                uk_buy = get_best_orders(uk_book)[0]
                qty = 1
                sell_cost += uk_buy * qty
                temp_orders["UKULELE"].append(Order("UKULELE", uk_buy, -qty)) #sell
                print(sell_cost, picnic_ask, "b")
                if(sell_cost > picnic_ask):
                    result["PICNIC_BASKET"].append(Order("PICNIC_BASKET", picnic_ask, 1)) #buy basket
                    result["DIP"].extend(temp_orders["DIP"]) #sell the rest
                    result["UKULELE"].extend(temp_orders["UKULELE"])
                    result["BAGUETTE"].extend(temp_orders["BAGUETTE"])
            except:
                pass     
            
        if state.timestamp > 45000 and state.timestamp < 55000:
            
            pass
        
        logger.flush(state, result)
        return result