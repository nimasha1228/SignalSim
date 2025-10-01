
     
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
        "open_long": open_long_size,
        "close_long": close_long_size,
        "open_short": open_short_size,
        "close_short": close_short_size,
        "order_type": order_type,
        "sent_order_price": sent_order_price,
    }