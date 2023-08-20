import numpy as np
import pandas as pd

from backtest.day_info import DayInfo
import xml.etree.ElementTree as ET
from dev.stock_normalisation import StockNormalisationModel
from dev.pca import MarketPca

import matplotlib.pyplot as plt
from common.colors import get_colorscheme

class PcaStrategy:
    def parse_config(self, conf_path):
        tree = ET.parse(conf_path)
        root = tree.getroot()

        stock_normalisation_config = root.find('stock_normalisation')
        self.norm_ignorena = int(stock_normalisation_config.find('ignorena').text)
        self.norm_trend_ewma_com = int(stock_normalisation_config.find('trend_ewma_com').text)
        self.norm_std_ewma_com = int(stock_normalisation_config.find('std_ewma_com').text)

        self.window = int(root.find('window').text)
        self.report_pca_model = int(root.find('report_pca_model').text)
        self.report_recalibration_config = int(root.find('report_recalibration').text)
        self.decision_frequency = int(root.find('decision_frequency').text)

    def __init__(self, stocks, conf_path):
        self.stocks = stocks
        self.parse_config(conf_path)
        self.normalisation_model = StockNormalisationModel(self.norm_trend_ewma_com, self.norm_std_ewma_com, self.norm_ignorena)
        self.daily_datapoints = []

    def report_recalibration(self, last_day_volatility, start_date, end_date):
        fig = plt.figure()
        fig.suptitle('Pca recalibration report : ' + str(start_date) + ' - ' + str(end_date))
        heights = [1, 1, 1]
        grid_spec = fig.add_gridspec(ncols=2, nrows=3, height_ratios=heights)

        colors = get_colorscheme(len(last_day_volatility))
        ax0 = fig.add_subplot(grid_spec[0, :])
        ax0.set_title('first pca component')
        ax0.bar(list(range(1, len(self.first_pca_component) + 1)), self.first_pca_component.to_numpy(), tick_label=self.first_pca_component.index, color=colors)

        ax1 = fig.add_subplot(grid_spec[1, :])
        ax1.set_title('last_day_volatility_feature')
        ax1.bar(list(range(1, len(last_day_volatility) + 1)), last_day_volatility.to_numpy(), tick_label=last_day_volatility.index, color=colors)

        ax2 = fig.add_subplot(grid_spec[2, :])
        ax2.set_title('recalibrated ratios')
        ax2.bar(list(range(1, len(self.ratios) + 1)), self.ratios.to_numpy(), tick_label=self.ratios.index, color=colors)


    def recalibrate_ratios(self):
        day_info_dfs = []
        for day_info in self.daily_datapoints:
            day_info_df = pd.DataFrame([day_info.daily_data], index=[day_info.date])
            day_info_dfs.append(day_info_df)
        df = pd.concat(day_info_dfs)
        df.sort_index(inplace=True)
        end_date = df.index[-1]
        start_date = end_date + pd.Timedelta(days=-self.window)

        feature_subset = []
        for stock in self.stocks:
            feature_subset.append(stock + '/close')

        df_features = self.normalisation_model.fit(df, feature_subset)
        for stock in self.stocks:
            df_features[stock + '/Pca_feature'] = df_features[stock + '/close_log_ewmadiv'] / df_features[
                stock + '/close_log_ewmadiv_std_ewma']

        feature_subset_pca = []
        for stock in self.stocks:
            feature_subset_pca.append(stock + '/Pca_feature')

        df_features = df_features[((df_features.index >= start_date)&(df_features.index <= end_date))]
        df_features['date'] = df_features.index
        df_features.reset_index(drop=True, inplace=True)

        self.df_features = df_features #change later

        market_pca = MarketPca(start_date, end_date, df_features, feature_subset_pca, 1)
        market_pca.fit()

        if(self.report_pca_model):
            market_pca.report([])

        ### now first pca component describes how much volatility I want to buy
        first_pca_component_np = np.zeros(shape=(len(self.stocks)))
        for i, stock in enumerate(self.stocks):
            first_pca_component_np[i] = market_pca.pca_components.iloc[0].loc[stock + '/Pca_feature']

        self.first_pca_component = pd.Series(first_pca_component_np, index=self.stocks)

        ratios_adjusted_for_volatility_np = np.zeros(shape=(len(self.stocks)))
        for i, stock in enumerate(self.stocks):
            ratios_adjusted_for_volatility_np[i] = self.first_pca_component[stock] / df_features.iloc[-1].loc[stock + '/close_log_ewmadiv_std_ewma']
        ratios_adjusted_for_volatility = pd.Series(ratios_adjusted_for_volatility_np, index=self.stocks)

        self.ratios = ratios_adjusted_for_volatility / ratios_adjusted_for_volatility.sum()

        if(self.report_recalibration_config):
            vol_features = [stock + '/close_log_ewmadiv_std_ewma' for stock in self.stocks]
            self.report_recalibration(df_features.iloc[-1].loc[vol_features], start_date, end_date)



    # it's expected that data is given in sorted order and without gaps
    def add_daily_data(self, day_info):
        self.daily_datapoints.append(day_info)


    def get_positions(self, day_info):
        pass



