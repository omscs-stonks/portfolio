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


def plot_daily_rets(**kwargs):
    """
    Loading the combined ticker data from yahoo finance unoffical API
    Using the adjusted close to get the daily close value for each ticker
    Dropping rows for Holidays/Weekends

    Input: string of space seperated stock tickers
    Output: Pandas Dataframe of adjusted closed values
    """
    df = kwargs["df"]
    fig = df.plot(title=kwargs["title"], template="simple_white",
              labels=dict(index=kwargs["idx"], value=kwargs["val"], variable=kwargs["var"]))
    fig.update_yaxes(tickprefix="%")
    fig.show()

    fig = px.line(df, x=kwargs["idx"], y=df.columns,
              hover_data={"date": "|%B %d, %Y"},
              title=kwargs["title"])
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y")
    fig.show()


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
    return cum_port_ret

def cumulative_tkr_rets(prices):
    """
    Calculating the cumulative daily returns of each ticker
    
    Input: Ticker Prices
    Output: Pandas Dataframe of daily returns by ticker
    """
    daily_ret = prices.drop(['AFRM'], axis=1).pct_change().fillna(0)
    cum_daily_ret = (daily_ret + 1).cumprod()
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

    return prices, weights

prices, weights = extact_data(FPATH)
cum_port_ret = cumulative_port_rets(prices, weights)
cum_port_ret.columns


cum_tkr_ret = cumulative_tkr_rets(prices)
cum_tkr_ret.reset_index(level=0, inplace=True)

fig = px.line(cum_tkr_ret, x="Date", y=cum_tkr_ret.columns ,
              hover_data={"Date": "|%B %d, %Y"},
              title='custom tick labels' )

fig.update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y")
fig.show()

fig.write_html("path/to/file.html")


if __name__ == '__main__':


    # plot_daily_rets(**{"df": daily_ret, "title": "Cumulative TICKER Daily Return",
    #                     "idx": "Date",  "val":"""% Return""", "var":"TICKER" })

    plot_daily_rets(**{"df": cum_port_ret, "title": "Cumulative Portfolio Daly Return",
                        "idx": "Date",  "val":"""% Return""", "var":"Portfolio" })