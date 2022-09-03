import json
import yfinance as yf
import pandas as pd 
import plotly.express as px
import matplotlib.pyplot as plt
pd.options.plotting.backend = "plotly"

FPATH = 'portfolio\portfolio.json'

def _load_portfolio_data(fpath):
    """
    Loading the json object of holdings 
    Input: relative file path to .json
    Output: Space seperated string, dictionary object of holdings
    """
    with open(fpath) as js:
        pf = json.load(js)
    stocks = ' '.join(pf.keys())

    return stocks, pf

def _loading_ticker_data(stocks):
    """
    Loading the combined ticker data from yahoo finance unoffical API
    Using the adjusted close to get the daily close value for each ticker
    Dropping rows for Holidays/Weekends

    Input: string of space seperated stock tickers
    Output: Pandas Dataframe of adjusted closed values
    """

    data = yf.download(tickers=stocks, period='ytd', interval='1d')
    df_adj = data['Adj Close']
    df_adj = df_adj.dropna(how='any',axis=0) 

    return df_adj


def cumulative_port_rets(prices, weights):
    """
    Input: string of space seperated stock tickers
    Output: Pandas Dataframe of adjusted closed values
    """

    daily_ret = prices.drop(['AFRM'], axis=1).pct_change().fillna(0)
    # check that columns are same 
    daily_ret = daily_ret[weights.columns]
    port_ret  = pd.DataFrame(daily_ret.values * weights.values, columns=daily_ret.columns, index=daily_ret.index)
    port_ret = port_ret.sum(axis = 1)
    cum_port_ret = (port_ret + 1).cumprod()
    cum_port_ret = cum_port_ret.to_frame()
    cum_port_ret.reset_index(level=0, inplace=True)
    cum_port_ret.columns = ['Date', 'Return']

    return cum_port_ret

def cumulative_tkr_rets(prices):
    """
    Calculating the cumulative daily returns of each ticker
    
    Input: Ticker Prices
    Output: Pandas Dataframe of daily returns by ticker
    """
    daily_ret = prices.drop(['AFRM'], axis=1).pct_change().fillna(0)
    cum_daily_ret = (daily_ret + 1.0 ).cumprod()
    return cum_daily_ret

def extact_data(fpath):
    """
    Loading data via helper functions
    As of 9/1, excluding short poritions 
    Input: string relative path to portfolio .json
    Output: Pandas Dataframe of ticker prices, weights of stocks 
    """
    stocks, pf = _load_portfolio_data(fpath)
    prices = _loading_ticker_data(stocks=stocks)
    shares = pd.DataFrame(pf).drop('Start_Date').drop(['AFRM'], axis=1)
    weights = shares.div(shares.sum(axis=1), axis=0)
    weights = weights.astype(float)

    return prices, weights

def plot_tickers(tkr_df):
    fig = tkr_df.plot(title="Pandas Backend Example", template="simple_white",
                labels=dict(index="time", value="Return", variable="Ticker"))
    fig.update_yaxes(tickprefix="%")
    fig.write_html("ticker-daily.html")

def plot_portfolio(port_df):
    fig = px.line(port_df, x="Date", y="Return")
    fig.write_html("portfolio-daily.html")

if __name__ == '__main__':

    prices, weights = extact_data(FPATH)
    cum_port_ret = cumulative_port_rets(prices, weights)
    cum_tkr_ret = cumulative_tkr_rets(prices)
    plot_tickers(cum_tkr_ret)
    plot_portfolio(cum_port_ret)
