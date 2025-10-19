import numpy as np

class RealTimePnL:
    def __init__(self, commision_per_trade):

        self.commision_per_trade = commision_per_trade
        self.total_running_commision = 0

        self.total_long_spent_value = 0.0
        self.total_long_position_size = 0.0
        self.average_long_entry_price = 0.0
        self.realized_long_pnl = 0.0
        self.unrealized_long_pnl = 0.0
        self.total_long_pnl = 0.0
        
        self.total_short_spent_value = 0.0
        self.total_short_position_size = 0.0
        self.average_short_entry_price = 0.0
        self.realized_short_pnl = 0.0
        self.unrealized_short_pnl = 0.0
        self.total_short_pnl = 0.0

        self.max_drawdown = 0.0
        self.current_peak_pnl = 0.0
        self.gross_pnl = 0.0
        self.net_pnl = 0.0

    def update_pnl(self, best_bid_price: float, best_ask_price: float, 
                   opened_long_position_size: float, closed_long_position_size: float, 
                   opened_short_position_size: float, closed_short_position_size: float):
        """
        Updates the PnL state based on new trade activity and current market prices.
        
        NOTE: This function updates the class's internal state (self.variables) directly.
        """
        
        # --- 1. HANDLE LONG POSITIONS ---
        
        # A. Open Long Positions (Entry at Ask Price)
        if opened_long_position_size > 0:
            current_long_spent = opened_long_position_size * best_ask_price
            
            new_long_spent = self.total_long_spent_value + current_long_spent
            new_long_size = self.total_long_position_size + opened_long_position_size
            
            self.average_long_entry_price = new_long_spent / new_long_size
            self.total_long_spent_value = new_long_spent
            self.total_long_position_size = new_long_size
            
        # B. Close Long Positions (Exit at Bid Price)
        if closed_long_position_size > 0:
            
            closed_size = np.minimum(closed_long_position_size, self.total_long_position_size)
            
            # Calculate realized PnL for the closed amount
            spent_for_closed_amount = closed_size * self.average_long_entry_price
            returned_after_close = closed_size * best_bid_price
            delta_pnl = returned_after_close - spent_for_closed_amount # Long PnL: Sell - Buy
            
            # Update state
            self.realized_long_pnl += delta_pnl
            self.total_long_spent_value -= spent_for_closed_amount
            self.total_long_position_size -= closed_size
            
            # Reset average entry price if position is flat
            if self.total_long_position_size < 0:
                self.average_long_entry_price = 0.0
        
        
        # --- 2. HANDLE SHORT POSITIONS ---
        
        # A. Open Short Positions (Entry at Bid Price)
        if opened_short_position_size > 0:
            current_short_spent = opened_short_position_size * best_bid_price
            
            new_short_spent = self.total_short_spent_value + current_short_spent
            new_short_size = self.total_short_position_size + opened_short_position_size
            
            self.average_short_entry_price = new_short_spent / new_short_size
            self.total_short_spent_value = new_short_spent
            self.total_short_position_size = new_short_size
            
        # B. Close Short Positions (Exit at Ask Price to cover)
        if closed_short_position_size > 0:
            
            closed_size = np.minimum(closed_short_position_size, self.total_short_position_size)

            # Calculate realized PnL for the closed amount
            spent_for_closed_amount = closed_size * self.average_short_entry_price
            cost_to_cover = closed_size * best_ask_price
            delta_pnl = spent_for_closed_amount - cost_to_cover # Short PnL: Initial Value - Cost to Cover
            
            # Update state
            self.realized_short_pnl += delta_pnl
            self.total_short_spent_value -= spent_for_closed_amount
            self.total_short_position_size -= closed_size

            # Reset average entry price if position is flat
            if self.total_short_position_size < 0:
                self.average_short_entry_price = 0.0


        # --- 3. CALCULATE UNREALIZED & TOTAL PNL (Mark-to-Market) ---
        
        # Long Unrealized PnL (Marking to best BID price)
        self.unrealized_long_pnl = (self.total_long_position_size * best_bid_price) - self.total_long_spent_value
        self.total_long_pnl = self.realized_long_pnl + self.unrealized_long_pnl
        
        # Short Unrealized PnL (Marking to best ASK price)
        # Note: total_short_spent_value is the money initially received
        self.unrealized_short_pnl = self.total_short_spent_value - (self.total_short_position_size * best_ask_price)
        self.total_short_pnl = self.realized_short_pnl + self.unrealized_short_pnl
        
        # Global Total PnL
        self.gross_pnl = self.total_long_pnl + self.total_short_pnl

        num_of_trades = int(opened_long_position_size > 0) + int(opened_short_position_size > 0) + int(closed_long_position_size > 0) + int(closed_short_position_size > 0)
        num_of_opened_trades = int(opened_long_position_size > 0) + int(opened_short_position_size > 0) 
        num_of_closed_trades =  int(closed_long_position_size > 0) + int(closed_short_position_size > 0)

        current_commision = num_of_trades * self.commision_per_trade
        self.total_running_commision = self.total_running_commision + current_commision
        self.net_pnl = self.gross_pnl - self.total_running_commision
        
        current_drawdown = (self.current_peak_pnl - self.net_pnl)/self.current_peak_pnl
        if self.max_drawdown < current_drawdown:
            self.max_drawdown = current_drawdown
        if self.net_pnl > self.current_peak_pnl:
            self.current_peak_pnl = self.net_pnl



        # You would typically return a dictionary of the updated state for logging, 
        # or simply rely on the class's state being updated.
        return {
            'gross_pnl': self.gross_pnl,
            'net_pnl': self.net_pnl,
            'max_drawdown':self.max_drawdown,
            'peak_pnl':self.current_peak_pnl,
            'num_of_trades':num_of_trades,
            'num_of_opened_trades':num_of_opened_trades,
            'num_of_closed_trades':num_of_closed_trades,
            'realized_pnl': self.realized_long_pnl + self.realized_short_pnl,
            'unrealized_pnl': self.unrealized_long_pnl + self.unrealized_short_pnl,
            'total_long_pos':self.total_long_position_size,
            'total_short_pos':self.total_short_position_size,
            'net_position': self.total_long_position_size - self.total_short_position_size
        }
    



def get_max_drawdown(df, max_drawdown_col="max_drawdown"):
    max_drawdown = df[max_drawdown_col].iloc[-1] 
    return max_drawdown

def get_total_num_of_trades(df, traded_count_col="num_of_trades"):
    total_trade_count = df[traded_count_col].sum()
    return total_trade_count
    

def get_gross_and_net_pnl(df, gross_pnl_col="gross_pnl", net_pnl_col="net_pnl"):
    gross_pnl = df[gross_pnl_col].iloc[-1] 
    net_pnl =  df[net_pnl_col].iloc[-1]

    print(f"Gross PnL: {gross_pnl:.6f}")
    print(f"Net PnL: {net_pnl:.6f}")

    return float(gross_pnl), float(net_pnl)



def calculate_average_trade_pnl(df, realized_pnl_col="realized_pnl", traded_close_count_col = "num_of_closed_trades"):
    total_realized_pnl = df[realized_pnl_col].iloc[-1]
    traded_close_count = df[traded_close_count_col].sum()
    avg_trade_pnl = total_realized_pnl/traded_close_count
    print(f"Average Trade PnL: {avg_trade_pnl:.6f}")
    return float(avg_trade_pnl)


def calculate_average_slippage(df, slippage_col="slippage", traded_count_col="num_of_trades"):
    executed = df[df[traded_count_col]>0]
    total_trade_count = df[traded_count_col].sum()
    if executed.empty:
        print("No executed trades found.")
        return 0.0, 0

    avg_slippage = executed[slippage_col].sum()/ total_trade_count

    print(f"Executed Trades: {total_trade_count}")
    print(f"Average Slippage per Trade: {avg_slippage:.6f}")
    return float(avg_slippage)