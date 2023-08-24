import matplotlib.pyplot as plt

from dev.data import Dataset
from backtest.day_info import DayInfo
import pandas as pd
from common.colors import get_colorscheme
from copy import deepcopy

class Reporter:
    def __init__(self, date_from, date_to, compare_data):
        self.date_from = date_from
        self.date_to = date_to
        self.daily_datapoints = []

        if compare_data != None:
            self.compare_data = deepcopy(compare_data)
        else:
            self.compare_data = None

    def add(self, day_info):
        if (day_info.date >= self.date_from and day_info.date <= self.date_to):
            self.daily_datapoints.append(day_info)

    def normalize_compare_data(self):
        self.compare_data.df.index = self.compare_data.df.loc[:, 'date']
        self.compare_data.df = self.compare_data.df[((self.compare_data.df.index >= self.date_from)&(self.compare_data.df.index <= self.date_to))]
        self.compare_data.df.sort_index(inplace=True)
        initial_bankroll = self.daily_datapoints[0].current_bankroll
        for stock in self.compare_data.companies:
            self.compare_data.df.loc[:, stock + '/close'] /= self.compare_data.df.iloc[0].loc[stock + '/close']
            self.compare_data.df.loc[:, stock + '/close'] *= initial_bankroll

    def plot_compare_data(self, evo_ax):
        colors = get_colorscheme(len(self.compare_data.companies))
        for i, stock in enumerate(self.compare_data.companies):
            evo_ax.plot(self.compare_data.df.index, self.compare_data.df.loc[:, stock+'/close'], label=stock, color=colors[i])

    def report(self):
        daily_data_dfs = []
        for day_info in self.daily_datapoints:
            daily_data = pd.DataFrame([day_info.daily_data], index=[day_info.date])
            daily_data_dfs.append(daily_data)
        df_data = pd.concat(daily_data_dfs)

        position_dfs = []
        for day_info in self.daily_datapoints:
            daily_position = pd.DataFrame([day_info.current_positions], index=[day_info.date])
            position_dfs.append(daily_position)

        df_position = pd.concat(position_dfs)

        bankroll_dfs = []
        for day_info in self.daily_datapoints:
            daily_bankroll = pd.DataFrame([[day_info.current_bankroll, day_info.total_position_value]], index=[day_info.date], columns=['current_bankroll', 'total_position_value'])
            bankroll_dfs.append(daily_bankroll)
        df_bankroll = pd.concat(bankroll_dfs)
        df_bankroll['unallocated_bankroll'] = df_bankroll['current_bankroll'] - df_bankroll['total_position_value']

        fig = plt.figure()
        heights = [8, 1]
        grid_spec = fig.add_gridspec(nrows=2, ncols=2, height_ratios=heights)

        evo_ax = fig.add_subplot(grid_spec[0, :])
        evo_ax.plot(df_bankroll.index, df_bankroll.loc[:, 'current_bankroll'], color='blue', label='total_bankroll')
        evo_ax.plot(df_bankroll.index, df_bankroll.loc[:, 'total_position_value'], color='black', label='total_position_value')
        evo_ax.plot(df_bankroll.index, df_bankroll.loc[:, 'unallocated_bankroll'], color='orange', label='unallocated_bankroll')
        if self.compare_data != None:
            self.normalize_compare_data()
            self.plot_compare_data(evo_ax)
        evo_ax.legend()

