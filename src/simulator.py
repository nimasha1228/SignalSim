import time
import pandas as pd
import numpy as np
from copy import deepcopy
from logger_config import logger, log_blank_line


     
def order_generator(signal, best_bid_price, best_ask_price, long_position, short_position, open_order_size=1):

    open_long_size = close_long_size = open_short_size = close_short_size = 0
    order_type = None
    sent_order_price = None

    net_position = long_position - short_position

    # --- BUY signal ---
    if signal == 1:
        sent_order_price = best_ask_price 
        if net_position >= 0:
            # add to existing longs
            open_long_size = open_order_size
            order_type = "open_long"
        else:
            # flip from shorts → longs
            close_short_size = short_position
            open_long_size = open_order_size
            order_type = "close_short and open_long"

    # --- SELL signal ---
    elif signal == -1:
        sent_order_price = best_bid_price
        if net_position <= 0:
            open_short_size = open_order_size
            order_type = "open_short"
        else:
            close_long_size = long_position
            open_short_size = open_order_size
            order_type = "close_long and open_short"

    # --- HOLD signal ---
    else:
        order_type = "hold"

    return {
        "open_long_size": open_long_size,
        "close_long_size": close_long_size,
        "open_short_size": open_short_size,
        "close_short_size": close_short_size,
        "order_type": order_type,
        "sent_order_price": sent_order_price,
    }



def simulation(trader_df, open_order_size, pnl_obj):

    log_blank_line()
    logger.info("-------- Trade Report --------")
    logger.info("==============================================")

    exchange_df = deepcopy(trader_df)

    # Convert to numpy arrays for efficient iteration
    timestamps = trader_df["timestamp"].to_numpy()
    bid_prices = trader_df["bid_price"].to_numpy()
    ask_prices = trader_df["ask_price"].to_numpy()
    signals = trader_df["action_int"].to_numpy()

    long_position = 0
    short_position = 0


    for ts, best_bid_price, best_ask_price, signal in zip(timestamps, bid_prices, ask_prices, signals):
        order_dict = order_generator(signal, best_bid_price, best_ask_price, long_position, short_position, open_order_size)

        send_order_time = ts

        open_long_size = order_dict["open_long_size"] 
        close_long_size = order_dict["close_long_size"]
        open_short_size = order_dict["open_short_size"]
        close_short_size = order_dict["close_short_size"]
        order_type = order_dict["order_type"]
        sent_order_price = order_dict["sent_order_price"]
        
        # Order send assumption: always send close orders first

        # EXCHANGE 


        exec_time = send_order_time + pd.Timedelta(seconds=1)
        matched_event = exchange_df.loc[exchange_df["timestamp"] == exec_time]

        filled_open_long_size = filled_close_long_size = filled_open_short_size = filled_close_short_size = 0


        if not matched_event.empty:

            market_ask_price = matched_event["ask_price"].iloc[0]
            market_bid_price = matched_event["bid_price"].iloc[0]
            available_ask_qty = matched_event["ask_qty"].iloc[0]
            available_bid_qty = matched_event["bid_qty"].iloc[0]
            if close_long_size>0: # ask
                if sent_order_price <= market_bid_price:

                    # Compute execution probability
                    price_aggressiveness = max((market_bid_price - sent_order_price) / market_bid_price, 0.01)
                    liquidity_factor = min(available_bid_qty / close_long_size, 1.0)
                    prob_exec = (0.5 * price_aggressiveness) + (0.5 * liquidity_factor)

                    if prob_exec >= 0.08 and available_bid_qty > 0:
                        filled_close_long_size = close_long_size if available_bid_qty >= close_long_size else available_bid_qty
                        available_bid_qty = available_bid_qty - filled_close_long_size


            if close_short_size>0: # bid
                if sent_order_price >= market_ask_price: 

                    # Compute execution probability
                    price_aggressiveness = max((sent_order_price - market_ask_price) / market_ask_price, 0.01)
                    liquidity_factor = min(available_ask_qty / close_short_size, 1.0)
                    prob_exec = (0.5 * price_aggressiveness) + (0.5 * liquidity_factor)

                    if prob_exec >= 0.08 and available_ask_qty > 0:
                        filled_close_short_size = close_short_size if available_ask_qty >= close_short_size else available_ask_qty
                        available_ask_qty = available_ask_qty - filled_close_short_size



            if open_short_size>0: # ask
                if sent_order_price <= market_bid_price:

                    # Compute execution probability
                    price_aggressiveness = max((market_bid_price - sent_order_price) / market_bid_price, 0.01)
                    liquidity_factor = min(available_bid_qty / open_short_size, 1.0)
                    prob_exec = (0.5 * price_aggressiveness) + (0.5 * liquidity_factor)

                    if prob_exec >= 0.08 and available_bid_qty > 0:
                        filled_open_short_size = open_short_size if available_bid_qty >= open_short_size else available_bid_qty
                        available_bid_qty = available_bid_qty - filled_open_short_size


            if open_long_size>0: # bid
                if sent_order_price >= market_ask_price: 

                    # Compute execution probability
                    price_aggressiveness = max((sent_order_price - market_ask_price) / market_ask_price, 0.01)
                    liquidity_factor = min(available_ask_qty / open_long_size, 1.0)
                    prob_exec = (0.5 * price_aggressiveness) + (0.5 * liquidity_factor)

                    if prob_exec >= 0.08 and available_ask_qty > 0:
                        filled_open_long_size = open_long_size if available_ask_qty >= open_long_size else available_ask_qty
                        available_ask_qty = available_ask_qty - filled_open_long_size            
                    

            pnl_and_pos_dict = pnl_obj.update_pnl(market_bid_price, market_ask_price, filled_open_long_size, filled_close_long_size, filled_open_short_size, filled_close_short_size)

            total_pnl = pnl_and_pos_dict['total_pnl']
            realized_pnl = pnl_and_pos_dict['realized_pnl']
            unrealized_pnl = pnl_and_pos_dict['unrealized_pnl']
            long_position = pnl_and_pos_dict['total_long_pos']
            short_position = pnl_and_pos_dict['total_short_pos']
            print(total_pnl)




        else: # hold
            pass



