import json

class DayInfo:
    def __init__(self, date, current_bankroll, current_positions, daily_data, total_position_value, transactions_so_far, traded_lots_so_far):
        self.date = date
        self.current_bankroll = current_bankroll
        self.current_positions = current_positions
        self.daily_data = daily_data
        self.total_position_value = total_position_value
        self.transactions_so_far = transactions_so_far
        self.traded_lots_so_far = traded_lots_so_far

    def to_json_serializable_dict(self):
        dict = {
            'date' : str(self.date),
            'current_bankroll' : self.current_bankroll,
            'current_positions' : self.current_positions.to_dict(),
            'daily_data' : self.daily_data.to_dict(),
            'total_position_value' : self.total_position_value,
            'transactions_so_far' : self.transactions_so_far,
            'traded_lots_so_far' : self.traded_lots_so_far
        }
        return dict