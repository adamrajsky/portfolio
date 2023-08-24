import copy

import pandas as pd
import numpy as np
from backtest.day_info import DayInfo
from backtest.reporter import Reporter
from copy import deepcopy


class Backtest:
    def __init__(self, data, stocks, date_from, date_to, initial_bankroll, reporter, logger):
        self.bankroll = initial_bankroll
        self.idx = 0
        self.stocks = stocks
        self.data = copy.deepcopy(data)
        self.data.df = self.data.df[((self.data.df['date'] >= date_from)&(self.data.df['date'] <= date_to))]
        self.data.df.index = self.data.df.date
        self.data.df.drop(columns=['date'], inplace=True)
        self.dates = list(self.data.df.index)
        self.total_position_value = 0
        self.transactions_so_far = 0
        self.traded_lots_so_far = 0

        self.current_porfolio = pd.DataFrame(np.zeros(shape=(len(self.dates), len(self.stocks))), index=self.dates, columns=stocks)

        self.reporter = reporter
        self.reporter.add(self.get_info())

        self.logger = logger
        self.logger.log(self.get_info())

    def get_info(self):
        date = self.dates[self.idx]
        res = DayInfo(date,
                      self.bankroll,
                      self.current_porfolio.loc[date, :],
                      self.data.df.loc[date, :],
                      self.total_position_value,
                      self.transactions_so_far,
                      self.traded_lots_so_far)

        return res

    def is_backtest_finished(self):
        return (self.idx == len(self.dates) - 1)

    def set_new_positions(self, new_positions):
        self.idx += 1
        pdate = self.dates[self.idx - 1]
        date = self.dates[self.idx]
        new_positions_cost = 0
        for stock in self.stocks:
            new_positions_cost += new_positions.loc[stock] * self.data.df.loc[pdate, stock+'/close']

        if new_positions_cost > self.bankroll:
            print("On date = ", date, " strategy tried to acquire invalid position [bankroll, new_positions_cost] = ", [self.bankroll, new_positions_cost])
            exit(0)

        self.current_porfolio.loc[date, :] = new_positions
        change = self.current_porfolio.loc[date, :] - self.current_porfolio.loc[self.dates[self.idx - 1]]
        self.traded_lots_so_far += abs(change).sum()
        self.transactions_so_far += abs(change).clip(0, 1).sum()

        new_positions_cost_next_day = 0
        for stock in self.stocks:
            new_positions_cost_next_day += new_positions.loc[stock] * self.data.df.loc[date, stock + '/close']
        self.total_position_value = new_positions_cost_next_day

        self.bankroll = self.bankroll - new_positions_cost + new_positions_cost_next_day
        self.logger.log(self.get_info())
        self.reporter.add(self.get_info())






