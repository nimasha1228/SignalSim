import numpy as np

class RealTimePnL:
    def __init__(self):
        # Initialize state variables to zero
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
        
        self.total_pnl = 0.0
        self.epsilon = 1e-6
        


    def update_pnl(self, best_bid_price: float, best_ask_price: float, 
                   opened_long_position_size: float, closed_long_position_size: float, 
                   opened_short_position_size: float, closed_short_position_size: float):
        """
        Updates the PnL state based on new trade activity and current market prices.
        
        NOTE: This function updates the class's internal state (self.variables) directly.
        """
        
        # --- 1. HANDLE LONG POSITIONS ---
        
        # A. Open Long Positions (Entry at Ask Price)
        if opened_long_position_size > self.epsilon:
            current_long_spent = opened_long_position_size * best_ask_price
            
            new_long_spent = self.total_long_spent_value + current_long_spent
            new_long_size = self.total_long_position_size + opened_long_position_size
            
            self.average_long_entry_price = new_long_spent / new_long_size
            self.total_long_spent_value = new_long_spent
            self.total_long_position_size = new_long_size
            
        # B. Close Long Positions (Exit at Bid Price)
        if closed_long_position_size > self.epsilon:
            
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
            if self.total_long_position_size < self.epsilon:
                self.average_long_entry_price = 0.0
        
        
        # --- 2. HANDLE SHORT POSITIONS ---
        
        # A. Open Short Positions (Entry at Bid Price)
        if opened_short_position_size > self.epsilon:
            current_short_spent = opened_short_position_size * best_bid_price
            
            new_short_spent = self.total_short_spent_value + current_short_spent
            new_short_size = self.total_short_position_size + opened_short_position_size
            
            self.average_short_entry_price = new_short_spent / new_short_size
            self.total_short_spent_value = new_short_spent
            self.total_short_position_size = new_short_size
            
        # B. Close Short Positions (Exit at Ask Price to cover)
        if closed_short_position_size > self.epsilon:
            
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
            if self.total_short_position_size < self.epsilon:
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
        self.total_pnl = self.total_long_pnl + self.total_short_pnl

        # You would typically return a dictionary of the updated state for logging, 
        # or simply rely on the class's state being updated.
        return {
            'total_pnl': self.total_pnl,
            'realized_pnl': self.realized_long_pnl + self.realized_short_pnl,
            'unrealized_pnl': self.unrealized_long_pnl + self.unrealized_short_pnl,
            'total_long_pos':self.total_long_position_size,
            'total_short_pos':self.total_short_position_size,
            'net_position': self.total_long_position_size - self.total_short_position_size
        }
    



def calculate_max_drawdown(df, gross_pnl_col="gross_pnl_per_trade", slippage_col="slippage"):
    net_pnl = df[gross_pnl_col].to_numpy(dtype=float) - np.abs(df[slippage_col].to_numpy(dtype=float))
    cum_pnl = np.cumsum(net_pnl)

    running_max = np.maximum.accumulate(cum_pnl)
    drawdown = cum_pnl - running_max

    max_drawdown = drawdown.min()

    return float(max_drawdown)



def compute_gross_and_net_pnl(df, pnl_col="total_pnl", slippage_col="slippage"):
    """
    Compute Gross and Net PnL over the entire simulation period (including holding times).
    """

    # --- Gross PnL: total profit over time ---
    gross_pnl = df[pnl_col].iloc[-1] - df[pnl_col].iloc[0]

    # --- Total slippage cost: only for executed trades ---
    total_slippage_cost = df.loc[df["traded_or_not"] == 1, slippage_col].abs().sum()

    # --- Net PnL: gross minus total slippage ---
    net_pnl = gross_pnl - total_slippage_cost

    print(f"💰 Gross PnL (including holds): {gross_pnl:.6f}")
    print(f"📉 Total Slippage Cost (executed only): {total_slippage_cost:.6f}")
    print(f"✅ Net PnL after Slippage: {net_pnl:.6f}")

    return float(gross_pnl), float(net_pnl)



def calculate_average_trade_pnl(df, realized_pnl_col="realized_pnl", trade_flag_col="traded_or_not"):
    """
    Calculate average realized PnL per executed trade.
    """
    executed = df[df[trade_flag_col] == 1]
    if executed.empty:
        print("⚠️ No executed trades found.")
        return 0.0, 0

    avg_trade_pnl = executed[realized_pnl_col].mean()
    trade_count = len(executed)

    print(f"📊 Executed Trades: {trade_count}")
    print(f"💰 Average Trade PnL: {avg_trade_pnl:.6f}")

    return float(avg_trade_pnl), trade_count


def calculate_average_slippage(df, slippage_col="slippage", trade_flag_col="traded_or_not"):
    """
    Calculate average slippage per executed trade.
    """
    executed = df[df[trade_flag_col] == 1]
    if executed.empty:
        print("⚠️ No executed trades found.")
        return 0.0, 0

    avg_slippage = executed[slippage_col].abs().mean()

    print(f"📊 Executed Trades: {trade_count}")
    print(f"📉 Average Slippage per Trade: {avg_slippage:.6f}")

    return float(avg_slippage)