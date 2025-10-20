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
        
        if self.current_peak_pnl != 0:
            current_drawdown = self.current_peak_pnl - self.net_pnl
        else:
            current_drawdown = self.max_drawdown

        if self.net_pnl > self.current_peak_pnl:
            self.current_peak_pnl = self.net_pnl

        if self.max_drawdown < current_drawdown:
            self.max_drawdown = current_drawdown

        print("net_pnl",self.net_pnl,"  current_peak_pnl",self.current_peak_pnl, self.max_drawdown,current_drawdown )


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
    



def get_max_drawdown(df, max_drawdown_col="max_drawdown", peak_pnl_col="peak_pnl"):
    """
    Calculate the maximum drawdown from the provided DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing simulation.
    max_drawdown_col : str, optional
        Column name containing drawdown values. Default is "max_drawdown".

    Returns
    -------
    float
        The final (maximum) drawdown value from the DataFrame.
    """
    max_drawdown = df[max_drawdown_col].iloc[-1] 
    peak_pnl = df[peak_pnl_col].iloc[-1] 
    max_drawdown_percentage = (max_drawdown/peak_pnl)*100
    return max_drawdown, max_drawdown_percentage

def get_total_num_of_trades(df, traded_count_col="num_of_trades"):
    """
    Calculate the total number of trades executed during the simulation.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing trade-level statistics.
    traded_count_col : str, optional
        Column name representing trade count per iteration. Default is "num_of_trades".

    Returns
    -------
    int
        The total number of trades across all simulation steps.
    """
    total_trade_count = df[traded_count_col].sum()
    return total_trade_count
    

def get_gross_and_net_pnl(df, gross_pnl_col="gross_pnl", net_pnl_col="net_pnl"):
    """
    Retrieve and display the final gross and net PnL values from the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing PnL-related columns.
    gross_pnl_col : str, optional
        Column name for gross PnL. Default is "gross_pnl".
    net_pnl_col : str, optional
        Column name for net PnL. Default is "net_pnl".

    Returns
    -------
    tuple of float
        (gross_pnl, net_pnl) — the final gross and net PnL values.
    """
    gross_pnl = df[gross_pnl_col].iloc[-1] 
    net_pnl =  df[net_pnl_col].iloc[-1]

    return float(gross_pnl), float(net_pnl)



def calculate_average_trade_pnl(df, realized_pnl_col="realized_pnl", traded_close_count_col = "num_of_closed_trades"):
    """
    Compute the average realized PnL per closed trade.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing realized PnL and trade count data.
    realized_pnl_col : str, optional
        Column name for realized PnL. Default is "realized_pnl".
    traded_close_count_col : str, optional
        Column name representing number of closed trades. Default is "num_of_closed_trades".

    Returns
    -------
    float
        The average realized PnL per closed trade.
    """
    total_realized_pnl = df[realized_pnl_col].iloc[-1]
    traded_close_count = df[traded_close_count_col].sum()
    avg_trade_pnl = total_realized_pnl/traded_close_count
    
    return float(avg_trade_pnl)


def calculate_average_slippage(df, slippage_col="slippage", traded_count_col="num_of_trades"):
    """
    Calculate the average slippage per executed trade.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing slippage and trade count data.
    slippage_col : str, optional
        Column name for slippage values. Default is "slippage".
    traded_count_col : str, optional
        Column name representing trade count per iteration. Default is "num_of_trades".

    Returns
    -------
    tuple
        (average_slippage, total_trade_count) — average slippage per trade and total number of executed trades.
    """

    executed = df[df[traded_count_col]>0]
    total_trade_count = df[traded_count_col].sum()
    if executed.empty:
        print("No executed trades found.")
        return 0.0, 0

    avg_slippage = executed[slippage_col].sum()/ total_trade_count

    return float(avg_slippage), total_trade_count