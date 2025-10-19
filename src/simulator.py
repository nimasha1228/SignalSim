import time
import pandas as pd
import numpy as np
from copy import deepcopy
from logger_config import logger, log_blank_line, log_once


     
def order_generator(signal, best_bid_price, best_ask_price, long_position, short_position, open_order_size=1):

    log_blank_line()

    log_once("=======> Generating Orders...")

    open_long_size = close_long_size = open_short_size = close_short_size = 0
    order_type = None
    sent_order_price = None

    net_position = long_position - short_position

    # Order send assumption: always send close orders first
    # --- BUY signal ---
    if signal == 1:
        logger.info("BUY signal detected.")
        sent_order_price = best_ask_price 
        if net_position >= 0:
            # add to existing longs
            open_long_size = open_order_size
            order_type = "open_long"
            logger.info(f"Placed {order_type} order: Buy {open_long_size} @ {sent_order_price:.2f}")
        else:
            # flip from shorts → longs
            close_short_size = short_position
            open_long_size = open_order_size
            order_type = "close_short and open_long"
            logger.info(f"Placed {close_short_size} close short(s) @{sent_order_price:.2f} and Placed {open_long_size} open long(s) @ {sent_order_price:.2f}")


    # --- SELL signal ---
    elif signal == -1:
        logger.info("SELL signal detected.")
        sent_order_price = best_bid_price
        if net_position <= 0:
            open_short_size = open_order_size
            order_type = "open_short"
            logger.info(f"Placed {order_type} order: Sell {open_short_size} @ {sent_order_price:.2f}")
        else:
            close_long_size = long_position
            open_short_size = open_order_size
            order_type = "close_long and open_short"
            
            logger.info(f"Placed {close_long_size} close long(s) @ {sent_order_price:.2f} and placed {open_short_size} open short(s) @ {sent_order_price:.2f}")

    # --- HOLD signal ---
    else:
        order_type = "hold"
        logger.info("Waiting for the next signal...")

    return {
        "signal":signal,
        "open_long_size": open_long_size,
        "close_long_size": close_long_size,
        "open_short_size": open_short_size,
        "close_short_size": close_short_size,
        "order_type": order_type,
        "sent_order_price": sent_order_price,
    }



def simulation(trader_df, open_order_size, pnl_obj, spread_penalty_factor, cb, ca, min_price_aggressiveness, min_exec_prob_threshold):

    exchange_df = deepcopy(trader_df)

    # Convert to numpy arrays for efficient iteration
    timestamps = trader_df["timestamp"].to_numpy()
    bid_prices = trader_df["bid_price"].to_numpy()
    ask_prices = trader_df["ask_price"].to_numpy()
    signals = trader_df["action_int"].to_numpy()

    long_position = 0
    short_position = 0
    log_records = []

    # data_end_time = timestamps.max() 
    num_of_trades = 0
    buy_signal_count = (trader_df["action_int"] == 1).sum()
    sell_signal_count = (trader_df["action_int"] == -1).sum()
    total_received_signal_count = buy_signal_count + sell_signal_count

    for ts, best_bid_price, best_ask_price, signal in zip(timestamps, bid_prices, ask_prices, signals):

        order_dict = order_generator(signal, best_bid_price, best_ask_price, long_position, short_position, open_order_size)
        order_sent_time = ts

        open_long_size = order_dict["open_long_size"] 
        close_long_size = order_dict["close_long_size"]
        open_short_size = order_dict["open_short_size"]
        close_short_size = order_dict["close_short_size"]
        sent_order_price = order_dict["sent_order_price"]
        signal = order_dict["signal"]
        

        
        # ====================== EXCHANGE ===============================================================

        # Checking whether any orders have been received
        order_generated = open_long_size>0 or close_long_size>0 or open_short_size>0 or close_short_size>0

        exec_time = order_sent_time + np.timedelta64(1, "s") 
        matched_event = exchange_df.loc[exchange_df["timestamp"] == exec_time]

        # If we want match with clostset data point instead of just cancelling
        # while order_generated and matched_event.empty:
        #     logger.info(f"waiting for matching")
        #     exec_time = exec_time + np.timedelta64(1, "s")
        #     matched_event = exchange_df.loc[exchange_df["timestamp"] == exec_time]
        #     if exec_time>=data_end_time:
        #         break

        if not matched_event.empty:

            filled_open_long_size = filled_close_long_size = filled_open_short_size = filled_close_short_size = 0

            close_long_sent_price = 0.0
            close_long_fill_price = 0.0
            close_short_sent_price = 0.0
            close_short_fill_price = 0.0
            open_short_sent_price = 0.0
            open_short_fill_price = 0.0
            open_long_sent_price = 0.0
            open_long_fill_price = 0.0

            prob_exec = 0.0
            price_aggressiveness = 0.0

            market_ask_price = matched_event["ask_price"].iloc[0]
            market_bid_price = matched_event["bid_price"].iloc[0]
            available_ask_qty = matched_event["ask_qty"].iloc[0]
            available_bid_qty = matched_event["bid_qty"].iloc[0]
            spread_flag = matched_event["spread_flag"].iloc[0]
            
            traded = 0
            slippage = 0.0 

            if order_generated:

                if close_long_size>0: # ask
                    if sent_order_price <= market_bid_price:

                        logger.info(f"Exchange received close_long order: {close_long_size} unit(s) @{sent_order_price:.2f}.")
                
                        # --- Mid-price and slippage ---
                        mid_price = (market_bid_price + market_ask_price) / 2

                        # Compute execution probability
                        price_aggressiveness = (((1-min_price_aggressiveness)*(sent_order_price))+(market_bid_price*((min_price_aggressiveness*cb)-1)))/(market_bid_price*(cb-1))
                        price_aggressiveness = np.clip(price_aggressiveness, 0, 1.0)
                        penalty = spread_penalty_factor if spread_flag == 1 else 1.0
                        prob_exec = penalty * price_aggressiveness

                        # if prob_exec >= min_exec_prob_threshold and available_bid_qty > 0:
                        rand_val = np.random.random()
                        if rand_val < prob_exec and available_bid_qty > 0:

                            logger.info(f"close_long order FILLED: {close_long_size} unit(s) @{market_bid_price:.2f} ")

                            filled_close_long_size = close_long_size if available_bid_qty >= close_long_size else available_bid_qty
                            available_bid_qty = available_bid_qty - filled_close_long_size
                            close_long_sent_price = sent_order_price
                            close_long_fill_price = market_bid_price

                            slippage =  close_long_fill_price - close_long_sent_price # Sell side

                            traded = 1
                            
                        else:
                            logger.info(f"close_long order NOT FILLED: (exec_prob={prob_exec:.2f}, available_qty={available_bid_qty}).")   
                    else:
                        logger.info(f"close_long order NOT FILLED: sent_order_price({sent_order_price}) > market_bid_price({market_bid_price})")


                if close_short_size>0: # bid
                    if sent_order_price >= market_ask_price: 

                        logger.info(f"Exchange received close_short order: {close_short_size} unit(s) @ {sent_order_price:.2f}")

                        # --- Mid-price and slippage ---
                        mid_price = (market_bid_price + market_ask_price) / 2

                        # Compute execution probability
                        price_aggressiveness = (((1 - min_price_aggressiveness) * sent_order_price) + (market_ask_price * ((min_price_aggressiveness * ca) - 1)))/(market_ask_price * (ca - 1))
                        price_aggressiveness = np.clip(price_aggressiveness, 0, 1.0)
                        penalty = spread_penalty_factor if spread_flag == 1 else 1.0
                        prob_exec = penalty * price_aggressiveness

                        # if prob_exec >= min_exec_prob_threshold and available_ask_qty > 0:
                        rand_val = np.random.random()
                        if rand_val < prob_exec and available_ask_qty > 0:

                            logger.info(f"close_short order FILLED: {close_short_size} unit(s) @{market_ask_price:.2f}")

                            filled_close_short_size = close_short_size if available_ask_qty >= close_short_size else available_ask_qty
                            available_ask_qty = available_ask_qty - filled_close_short_size
                            close_short_sent_price = sent_order_price
                            close_short_fill_price = market_ask_price

                            slippage = close_short_sent_price - close_short_fill_price # Buy side

                            traded = 1

                        else:    
                            logger.info(f"close_short order NOT FILLED: (exec_prob={prob_exec:.2f}, available_qty={available_ask_qty}).")
                    else:
                        logger.info(f"close_long order NOT FILLED: sent_order_price({sent_order_price}) < market_ask_price({market_ask_price})")


                
                if open_short_size>0: # ask
                    if sent_order_price <= market_bid_price:

                        logger.info(f"Exchange received open_short order: {open_short_size} unit(s) @ {sent_order_price:.2f}")

                        # --- Mid-price and slippage ---
                        mid_price = (market_bid_price + market_ask_price) / 2

                        # Compute execution probability
                        price_aggressiveness = (((1-min_price_aggressiveness)*(sent_order_price))+(market_bid_price*((min_price_aggressiveness*cb)-1)))/(market_bid_price*(cb-1))
                        price_aggressiveness = np.clip(price_aggressiveness, 0, 1.0)
                        penalty = spread_penalty_factor if spread_flag == 1 else 1.0
                        prob_exec = penalty * price_aggressiveness


                        # if prob_exec >= min_exec_prob_threshold and available_bid_qty > 0:
                        rand_val = np.random.random()
                        if rand_val < prob_exec and available_bid_qty > 0:

                            logger.info(f"open_short order FILLED: {open_short_size} unit(s) @ {market_bid_price:.2f}")

                            filled_open_short_size = open_short_size if available_bid_qty >= open_short_size else available_bid_qty
                            available_bid_qty = available_bid_qty - filled_open_short_size
                            open_short_sent_price = sent_order_price
                            open_short_fill_price = market_bid_price

                            slippage = open_short_fill_price - open_short_sent_price # Sell side

                            traded = 1

                        else:
                            logger.info(f"open_short order NOT FILLED: (exec_prob={prob_exec:.2f}, available_qty={available_bid_qty}).")
                    else:
                        logger.info(f"close_long order NOT FILLED: sent_order_price({sent_order_price}) > market_bid_price({market_bid_price})")



                if open_long_size>0: # bid
                    if sent_order_price >= market_ask_price: 

                        logger.info(f"Exchange received open_long order: {open_long_size} unit(s) @ {sent_order_price:.2f}")

                        # --- Mid-price and slippage ---
                        mid_price = (market_bid_price + market_ask_price) / 2

                        # Compute execution probability
                        price_aggressiveness = (((1 - min_price_aggressiveness) * sent_order_price) + (market_ask_price * ((min_price_aggressiveness * ca) - 1)))/(market_ask_price * (ca - 1))
                        price_aggressiveness = np.clip(price_aggressiveness, 0, 1.0)
                        penalty = spread_penalty_factor if spread_flag == 1 else 1.0
                        prob_exec = penalty * price_aggressiveness

                        # if prob_exec >= min_exec_prob_threshold and available_ask_qty > 0:
                        rand_val = np.random.random()
                        if rand_val < prob_exec and available_ask_qty > 0:

                            logger.info(f"open_long order FILLED: {open_long_size} unit(s) @ {market_ask_price:.2f}")

                            filled_open_long_size = open_long_size if available_ask_qty >= open_long_size else available_ask_qty
                            available_ask_qty = available_ask_qty - filled_open_long_size
                            open_long_sent_price = sent_order_price
                            open_long_fill_price = market_ask_price

                            traded = 1

                            slippage = open_long_sent_price - open_long_fill_price # Sell side
                                    
                        else:
                            logger.info(f"open_long order NOT FILLED: (exec_prob={prob_exec:.2f}, available_qty={available_ask_qty}).")
                    else:
                        logger.info(f"close_long order NOT FILLED: sent_order_price({sent_order_price}) < market_ask_price({market_ask_price})")

            else:
                logger.info(f"No new orders received...")
                mid_price = (best_bid_price + best_ask_price) / 2
                   


            pnl_and_pos_dict = pnl_obj.update_pnl(market_bid_price, market_ask_price, filled_open_long_size, filled_close_long_size, filled_open_short_size, filled_close_short_size)

            gross_pnl_per_trade = pnl_and_pos_dict['total_pnl'] # Gross PnL
            realized_pnl = pnl_and_pos_dict['realized_pnl']
            unrealized_pnl = pnl_and_pos_dict['unrealized_pnl']
            long_position = pnl_and_pos_dict['total_long_pos']
            short_position = pnl_and_pos_dict['total_short_pos']


            if traded:
                num_of_trades = num_of_trades + 1

            
            # Add records
            log_records.append({
                "signal":signal,
                "exchange_time": exec_time,    
                "order_sent_time": order_sent_time if order_generated else None,    
                "mid_price":mid_price,
                "slippage":slippage,
                "gross_pnl_per_trade": gross_pnl_per_trade,
                "realized_pnl": realized_pnl,
                "unrealized_pnl": unrealized_pnl,
                "long_position": long_position,
                "short_position": short_position,
                "close_long_sent_price": close_long_sent_price,
                "close_long_fill_price": close_long_fill_price,
                "close_short_sent_price": close_short_sent_price,
                "close_short_fill_price": close_short_fill_price,
                "open_short_sent_price": open_short_sent_price,
                "open_short_fill_price": open_short_fill_price,
                "open_long_sent_price": open_long_sent_price,
                "open_long_fill_price": open_long_fill_price,
                "filled_close_long_size": filled_close_long_size,
                "filled_close_short_size": filled_close_short_size,
                "filled_open_short_size": filled_open_short_size,
                "filled_open_long_size": filled_open_long_size,
                "prob_exec":prob_exec,
                "price_aggressiveness":price_aggressiveness,
                "traded_or_not":traded,
                "spread_flag":spread_flag
                })
            

        else: 
            logger.info(f"Order Cancelled!!! --> No Matched events. ")

        # Convert to DataFrame
        results_df = pd.DataFrame(log_records)


    return results_df, num_of_trades, total_received_signal_count


