from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors


def get_colorscheme(num_features):
    hsv = plt.get_cmap('hsv')
    offset = 0
    color_step = 255 // num_features
    colors = []
    for i in range(num_features):
        colors.append(matplotlib.colors.to_hex(hsv(i * color_step + offset)))
    return colors

class MarketPca:
    def __init__(self, date_from, date_to, df, feature_subset, n_components):
        self.date_from = date_from
        self.date_to = date_to
        self.df = df
        self.feature_subset = feature_subset
        self.n_components = n_components

    def fit(self):
        self.df_filtered = self.df[((self.df['date'] >= self.date_from) & (self.df['date'] <= self.date_to))]
        self.df_filtered = self.df_filtered[self.feature_subset]
        self.df_filtered.dropna(axis=1, inplace=True)
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(self.df_filtered)
        self.pca_components = pd.DataFrame(self.pca.components_, index=[i for i in range(self.n_components)], columns=self.df_filtered.columns)
        self.transformed_df_filtered = self.pca.transform(self.df_filtered)
        self.itransformed_df_filtered = self.pca.inverse_transform(self.transformed_df_filtered)

        columns = ['PC'+str(i) for i in range(self.n_components)]
        self.transformed_df_filtered = pd.DataFrame(self.transformed_df_filtered, columns=columns, index=self.df_filtered.index)
        self.transformed_df_filtered['date'] = self.df['date']

        self.itransformed_df_filtered = pd.DataFrame(self.itransformed_df_filtered, columns=self.df_filtered.columns, index=self.df_filtered.index)
        self.itransformed_df_filtered['date'] = self.df['date']

        self.df_filtered['date'] = self.df['date']

    def report(self, features_to_plot):
        self.fig = plt.figure()
        heights = [4, 4, 4, 4]
        self.grid_spec = self.fig.add_gridspec(ncols=4, nrows=4, height_ratios=heights)
        self.plots_axes = []
        for i in range(4):
            self.plots_axes.append(self.fig.add_subplot(self.grid_spec[i, :]))

        colors = get_colorscheme(self.n_components)

        for i in range(self.n_components):
            self.plots_axes[0].plot(self.transformed_df_filtered['date'], self.transformed_df_filtered[f'PC{i}'], color=colors[i], label=f'PC{i}')
        self.plots_axes[0].legend()

        columns = ['PC' + str(i) for i in range(self.n_components)]
        self.plots_axes[1].bar(list(range(1, self.n_components + 1)), self.pca.explained_variance_ratio_, color=colors, label=columns)
        self.plots_axes[1].legend()
        self.plots_axes[1].set_title("Explained variance ratio")

        df_diff_sq = (self.df_filtered.drop(columns=['date']) - self.itransformed_df_filtered.drop(columns=['date']))**2
        time_reconstruction_error = df_diff_sq.sum(axis=1)
        self.plots_axes[2].plot(self.transformed_df_filtered['date'], time_reconstruction_error.to_numpy(), label='reconstruction_error', color=colors[0])
        self.plots_axes[2].legend()

        feature_reconstruction_error = df_diff_sq.sum(axis=0)
        colors_many = get_colorscheme(min(250, len(self.feature_subset)))
        colors_bar = []
        for i in range(len(df_diff_sq.columns)):
            colors_bar.append(colors_many[i % len(colors_many)])
        self.plots_axes[3].bar(list(range(1, len(df_diff_sq.columns) + 1)), feature_reconstruction_error.to_numpy(), tick_label=df_diff_sq.columns, color=colors_bar)
        self.plots_axes[3].legend()
        self.plots_axes[3].set_title("Reconstruction error by feature")
