from data import Dataset
from gui import ExploGUI
from stock_normalisation import StockNormalisationModel
from pca import MarketPca
from strategy.pca_strategy import PcaStrategy
import pandas as pd
from backtest.backtest import Backtest
from backtest.reporter import Reporter
from backtest.logger import Logger
import matplotlib.pyplot as plt
from common.pathUtils import get_data_path
from backtest.run_backtest import run_backtest

if __name__ == '__main__':
    path = get_data_path() + '/sector_funds'
    date_from = pd.Timestamp('2000-01-01')
    backtest_date_from = pd.Timestamp('2007-01-01')
    date_to = pd.Timestamp('2020-01-01')
    data = Dataset(path)
    initial_bankroll = 10000

    strategy_config = '../config/pcaStrategyConfig.xml'
    strategy = PcaStrategy(data.companies, strategy_config)

    run_backtest(data, date_from, backtest_date_from, date_to, 10000, strategy)

    plt.show()