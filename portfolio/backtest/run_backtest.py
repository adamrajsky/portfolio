import pandas as pd
import numpy as np
from backtest.logger import Logger
from backtest.reporter import Reporter
from backtest.backtest import Backtest
from strategy.pca_strategy import PcaStrategy

from dev.data import Dataset

def run_backtest(data, data_date_from, backtest_date_from, date_to, initial_bankroll, strategy):
    logger = Logger("")
    reporter = Reporter(backtest_date_from, date_to)
    backtest = Backtest(data, data.companies, data_date_from, date_to, initial_bankroll, reporter, logger)

    while (not backtest.is_backtest_finished()):
        day_info = backtest.get_info()
        strategy.add_daily_data(day_info)
        date = day_info.date
        if(date >= backtest_date_from):
            positions = strategy.get_positions()
            backtest.set_new_positions(positions)
        else:
            zero_positions = day_info.current_positions
            backtest.set_new_positions(zero_positions)

    logger.push()
    reporter.report()