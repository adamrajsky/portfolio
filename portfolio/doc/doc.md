## Project goal 
    Given n input contracts, the aim is to explore the portfolio created from first PCA component.
    First pca component is such linear combination, which allows you to compress input contracts into one number, while explaining the most 
    amount of variance. Most of the time, all values within this first component are positive (assuming good choice of input contracts). 
    I expect such linear combination might be a good choice to hedge equity portfolios with (long equity portfolio, short market) and should be a fairly robust.


## Additional details of specification 
    1. Existing programs solving the project goal : I don't know of any. Usually equity portfolios are hedged using S&P derivatives. (based on John Hull - Futures Options and other Derivatives)
    2. The components / steps agreed upon are as follows 
        a. Component making sure Data is easily accessible
        b. Exploration gui for picking the right features
        c. Normalization component creating features to be used in pca
        d. Pca itself incl. reporting
        e. Strategy component calibrating ratios OOS and computing positions given bankroll
        f. Backtest allowing evaluation of performance compared to some benchmark
        g. Picking equities
        

## Software documentation
### Usage
    The way to use it is running dev/main.py. Python interpreter is the only thing needed. Before that :
        1. Take a look in dev/main.py how paths are passed to Dataset object and how the data folders look - make sure the paths are set correctly for your system

    2. Given you can load data, you can use ExploGui (configured in config/explorationConfig.xml), to look at the features. 
       It shows the time series data, along with moving average (the trend of the time series) and moving variance / correlations between the series. If detrend configuration is on, 
       moving average is then subtracted from the time series and variance / correlations are calculated from these series 'detrended' series. Additionally, there should be a boxplot showing the range of values for the series.

       Look at the ExploGui interface in dev/gui.py and pass appropriate Dataset object and path to configuration (config/explorationConfig.xml). In explorationConfig you can configure which features should be included and 
       additional dataframe filters. 

    3. There is the pca_strategy.py and backtest, allowing you to measure OOS performace of these portfolios. Backtest dates and data paths are straightforwardly configured in dev/main.py. 
       Pca_strategy - the component calculating the ratios of input contracts and dicrete positions corresponding to the ratios is configured in config/pcaStrategyConfig.xml. Pca strategy uses the normalisation component (configured in the same config)
       and pca component. Window is the parameter describing the lookback used in Pca. Reporting flags are used to describe with parts should be reported. Decision frequency is the parameter describing how frequently should the portfolio be rebalanced. (in days). 
       Normalization params will be described in later section. (Software details)

### Software details
    There are multiple components : 
        a.) Dataset class
                Loads all csv files within a directory, which should be named based on the contract they represent and creates a dataframe with these features + holds a list of names of files.
        b.) ExploGui 
                Functionality described above. Loads  configuration from an xml file and then uses matplotlib and it's low level gridspec api to plot plots. 
        c.) Stock normalisation 
                StockNormalisationModel creates features which are meaningful when plugged into pca. More concretely, it computes ln(close_i / ema(close prices with com=trend_ewma_com in configuration)) 
                and the rolling variance of this feature (com specified in configuration). 
        d.) Pca itself
                Computes pca from specified features in a specified date window. Reports the evolution of the component in time (compress a set of features for a given day into n_components numbers and plot their evolution), 
                reconstruction error for various features, explained variance... 
        e.) Strategy
                Implements rebalacing : Uses normalisation and pca to bring it together and compute desired contract ratios. Uses greedy algo to compute discrete positions (you can only buy whole number of some contracts). Reports computed positions, 
                error compared to desired ratios.
                
                Implements interaction with backtest. Each day, it's given dayInfo object from backtest which it stores and then uses to compute ratios / positions.
                
                There are 2 interesting parts here : - the pca feature used (usually I used ln(close_i / ema(close prices with com=trend_ewma_com in configuration))/stdEma of feature above
                                                     - the algo creating discrete positions. Lets define Error(positions, desiredRatios) = sum over contracts ((pos_i / bankroll) - desiredRatio_i)**2
                                                            Then the algo starts with 0 positions and always buys a contract that maximizes the error decrease. 


        f. ) Backtest
                Given dataset, it produces dayInfo object each day which is passed into the strategy and contains information such as position value, bankroll, positions held by strategy, current prices, number of trades ... 
                Then the strategy decides on new positions. It then validates the acquired position (do I have enough money to buy what is passed in?), computes new value of the position the next day, reads new prices and again generates the object. 
                
                Additionally, it takes in a logger class, which each day takes the dayInfo object, serializes it into a json and writes it into a log file at the end of the backtest. If you want to use it, passing path to log is straightforward in backtest/run_backtest.py. 
                Additionally, it takes in a reporter class, which is each day passed the dayInfo object, it then aggregates the results and plots the evolution of the portfolio created by the strategy in time. 
                    Reporter also compares the evolution with a benchmark.

                run_backtest uses the backtest class, takes in desired datespans, data to use for backtest, data to use to compare with benchmark, bankroll and runs the backtest.

        It is implemented in such a way that it's modular. It is easy to create a new strategy to replace Pca strategy that has add_daily_data and get_new_positions in it's interface and can parse day_info objects and it will work as desired.


