import pandas as pd
import numpy as np
import os
import common.pathUtils as pathutils

class Dataset:
    def __init__(self):
        self.load_dataset()
        self.companies = []

    def load_dataset(self):
        base_path = pathutils.get_data_path() + '/stock_market_datasp500'
        dfs = []
        self.companies = []
        for file in os.listdir(base_path):
            dfs.append(pd.read_csv(base_path + '/' + file))
            company = file[:-4]
            self.companies.append(company)
            dfs[-1].columns = dfs[-1].columns.str.lower()
            del dfs[-1]['open'], dfs[-1]['low'], dfs[-1]['high'], dfs[-1]['stock splits']
            for col in dfs[-1].columns:
                if col == 'date':
                    continue
                dfs[-1].rename(columns={col : company + '/' + col}, inplace=True)
            dfs[-1].loc[:, 'date'] = pd.to_datetime(dfs[-1].loc[:, 'date'])

        assert(len(dfs) > 0)
        self.df = dfs[0]
        for df_iter in dfs[1:]:
            self.df = self.df.merge(df_iter, how='outer', on=['date'])

        self.df.sort_values(by='date', inplace=True)
        self.df = self.df[(self.df['date'] >= pd.to_datetime('2000-01-01'))]
