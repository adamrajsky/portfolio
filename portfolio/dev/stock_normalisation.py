from data import Dataset
import matplotlib.pyplot as plt
import numpy as np

# computes log(p_i / ewma(p_i ... ))
class StockNormalisationModel:
    def __init__(self, trend_ewma_com, std_ewma_com, ignorena):
        self.trend_ewma_com = trend_ewma_com
        self.std_ewma_com = std_ewma_com
        self.ignorena = ignorena
        pass

    def fit(self, df, feature_subset):
        df_temp = df[feature_subset]
        for feature in feature_subset:
            df_temp[feature+'_ewma'] =df_temp[feature].ewm(com=self.trend_ewma_com, ignore_na = self.ignorena, min_periods=self.trend_ewma_com, adjust=True).mean()
            df_temp[feature+'_log_ewmadiv'] = np.log(df_temp[feature] / df_temp[feature+'_ewma'])
            df_temp[feature+'_log_ewmadiv_std_ewma'] = df_temp[feature+'_log_ewmadiv'].ewm(com=self.std_ewma_com, ignore_na = self.ignorena, min_periods=self.std_ewma_com, adjust=True).std()
            del df_temp[feature]
        return df_temp









