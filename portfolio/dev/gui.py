import numpy as np
import pandas as pd
import matplotlib .pyplot as plt
from matplotlib.widgets import TextBox
import matplotlib.colors
import xml.etree.ElementTree as ET


class ExploGUI:
    def __init__(self, ds, confPath):
        print(ds.df.columns)
        self.ds = ds

        self.fig = plt.figure()
        heights = [10, 5, 5, 5, 4]
        self.grid_spec = self.fig.add_gridspec(ncols=4, nrows=5, height_ratios=heights)
        self.plots_axes = []
        for i in range(4):
            self.plots_axes.append(self.fig.add_subplot(self.grid_spec[i, :]))
        self.plots_axes.append(self.fig.add_subplot(self.grid_spec[4, 0:2]))
        self.plots_axes.append(self.fig.add_subplot(self.grid_spec[4, 2:4]))

        self.plotted_features = []
        self.filters = []
        self.xname = ''
        self.mean_wcom = -1
        self.std_wcom = -1
        self.corr_wcom = -1
        self.ignorena_rolling_aggregates = 0
        config = self.parse_config(confPath)

        self.draw_plots()
        plt.show()

    def parse_config(self, confPath):
        tree = ET.parse(confPath)
        root = tree.getroot()
        self.xname = root.find('xname').text
        for feature in root.findall('features/feature'):
            self.plotted_features.append(feature[0].text)
            self.filters.append(feature[1].text)

        self.detrend = int(root.find('detrend').text)

        rolling_aggregates = root.find('rolling_aggregates')
        self.ignorena_rolling_aggregates = rolling_aggregates.find('ignorena').text

        rolling_mean = root.find('rolling_aggregates/rolling_mean')
        self.mean_wcom = float(rolling_mean.find('wcom').text)

        rolling_std = root.find('rolling_aggregates/rolling_std')
        self.std_wcom = float(rolling_std.find('wcom').text)

        rolling_corr = root.find('rolling_aggregates/rolling_correlation')
        self.corr_wcom = float(rolling_corr.find('wcom').text)

    def get_colorscheme(self, num_features):
        hsv = plt.get_cmap('hsv')
        offset = 0
        color_step = 255 // num_features
        colors = []
        for i in range(num_features):
            colors.append(matplotlib.colors.to_hex(hsv(i * color_step + offset)))
        return colors

    def draw_plots(self):
        assert(len(self.plotted_features) <= 10)
        df = self.ds.df[[self.xname] + self.plotted_features]
        for i, plotted_feature in enumerate(self.plotted_features):
            if self.filters[i] != None:
                df.loc[:, plotted_feature] = df.query(self.filters[i]).loc[:, plotted_feature]

        detrended_features = []
        for i in range(len(self.plotted_features)):
            if self.detrend:
                df.loc[:, 'rolling_mean(' + self.plotted_features[i] + ')'] = df.loc[:, self.plotted_features[i]].ewm(com=self.mean_wcom,
                                                                                                  ignore_na=self.ignorena_rolling_aggregates,
                                                                                                  min_periods=self.mean_wcom,
                                                                                                  adjust=True).mean()
            else:
                df.loc[:, 'rolling_mean(' + self.plotted_features[i] + ')'] = 0
            detrended_features.append(self.plotted_features[i] + '-rolling_mean(' + self.plotted_features[i] + ')')
            df.loc[:, detrended_features[i]] = df[self.plotted_features[i]] - df['rolling_mean(' + self.plotted_features[i] + ')']

            df.loc[:, 'rolling_std(' + detrended_features[i] + ')'] = df[detrended_features[i]].ewm(com=self.std_wcom,
                                                                                       ignore_na=self.ignorena_rolling_aggregates,
                                                                                       min_periods=self.std_wcom,
                                                                                       adjust=True).std()

        df_corr = df[detrended_features].ewm(com=self.corr_wcom, ignore_na=self.ignorena_rolling_aggregates,
                                             min_periods=self.corr_wcom, adjust=True).corr().unstack()



        colors_features = self.get_colorscheme(2 * len(self.plotted_features))
        for i in range(len(self.plotted_features)):
            self.plots_axes[0].plot(df[self.xname], df[self.plotted_features[i]], color = colors_features[2*i], label = self.plotted_features[i])

        for i, plotted_feature in enumerate(self.plotted_features):
            self.plots_axes[0].plot(df[self.xname], df['rolling_mean(' + self.plotted_features[i] + ')'],
                                    color=colors_features[2 * i + 1],
                                    label='rolling_mean(' + self.plotted_features[i] + ')' )
        self.plots_axes[0].legend()

        for i, feature in enumerate(detrended_features):
            self.plots_axes[1].plot(df[self.xname], df[feature], color=colors_features[2*i], label=feature)
        self.plots_axes[1].legend()

        for i, feature in enumerate(detrended_features):
            self.plots_axes[2].plot(df[self.xname], df['rolling_std('+feature+')'], color=colors_features[2*i], label='rolling_std('+feature+')')
        self.plots_axes[2].legend()

        colors_corr = self.get_colorscheme((len(self.plotted_features) * (len(self.plotted_features) - 1)) // 2)
        idx = 0
        for i in range(len(detrended_features)):
            for j in range(i + 1, len(detrended_features)):
                name = 'corr(' + detrended_features[i] + ', ' + detrended_features[j] + ')'
                self.plots_axes[3].plot(df[self.xname], df_corr.loc[:, (detrended_features[i], detrended_features[j])], color=colors_corr[idx], label=name)
                idx += 1
        self.plots_axes[3].legend()

        boxplot_data = [df.loc[:, feature].dropna() for feature in self.plotted_features]
        bp = self.plots_axes[4].boxplot(boxplot_data, sym='+', patch_artist=True)
        self.plots_axes[4].set_xticks(list(range(1, len(self.plotted_features) + 1)))
        self.plots_axes[4].set_xticklabels(self.plotted_features)
        for patch, color in zip(bp['boxes'], colors_features[0:len(colors_features):2]):
            patch.set(facecolor=color)



