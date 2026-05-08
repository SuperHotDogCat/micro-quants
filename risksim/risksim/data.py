# Copyright (c) 2026 SuperHotDogCat

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# 全データにIndexでDate, ColumnsでClose, High, Low, Open, Volumeのdataがあることを保証するdfを返すようにする

import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

def load_yfinance_data(ticker_code: str, start: str, end: str) -> pd.DataFrame:
    r"""
    Load historical price data from Yahoo Finance and return
    a DataFrame.

    Args:
        ticker_code (str): e.g. "AAPL"
        start (str): "YYYY-MM-DD"
        end (str): "YYYY-MM-DD"

    Returns:
        pandas.DataFrame:
            columns = ["Close", "High", "Low", "Open", "Volume"]
    """
    # --- 型チェック ---
    if not isinstance(ticker_code, str):
        raise TypeError("ticker_code must be str")

    if not isinstance(start, str):
        raise TypeError("start must be str (YYYY-MM-DD)")

    if not isinstance(end, str):
        raise TypeError("end must be str (YYYY-MM-DD)")

    import yfinance as yf
    import concurrent.futures

    def fetch_finance_data():
        return yf.download(ticker_code, start=start, end=end)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(fetch_finance_data)
        df = future.result(timeout=10) # 10秒でtime out

    df = df.xs(ticker_code, axis=1, level=1) # ticker_codeで指定したdataを取り出す
    return df

def compute_return(df: pd.DataFrame, column: str, T: str, max_lag: str = None) -> pd.Series:
    r"""
    Compute time-based returns over a specified horizon using a datetime index.

    This function calculates returns between each timestamp t and the closest
    available past observation at (t - T). If no exact timestamp exists, the
    most recent available observation before (t - T) is used (forward-fill logic).

    Args:
        df (pd.DataFrame):
            Input DataFrame with a DatetimeIndex. Must contain the specified column.
            The index does not need to be equally spaced (e.g., trading days only).

        column (str):
            Column name used to compute returns (e.g., "Close", "Adj Close").

        T (str):
            Time horizon as a pandas-compatible timedelta string.
            Examples:
                - "5D"    : 5 calendar days
                - "1D"    : 1 day
                - "30min" : 30 minutes
                - "1H"    : 1 hour

        max_lag (str | None, optional):
            Maximum allowed deviation between the requested timestamp (t - T)
            and the actual matched timestamp used for return computation.

            If provided, observations where:
                actual_time < (t - T) - max_lag
            are discarded.

            Examples:
                - "1D": allow up to 1 day mismatch (e.g., weekends)
                - None: no filtering (default)

    Returns:
        pd.Series:
            Time-aligned return series with the same index as input df (after filtering).
            NaN values and invalid matches are removed.

    Notes:
        - Uses forward-fill (ffill) to select past observations, ensuring no future
          data leakage.
        - For financial time series with trading gaps (e.g., weekends),
          the actual lag may exceed T unless max_lag is enforced.
        - If strict business-day alignment is required, consider using index-based
          shifting (e.g., shift(N)) instead of time-based offsets.

    Raises:
        ValueError:
            If the specified column is not found in df.

        TypeError:
            If df.index is not a DatetimeIndex.

    Example:
        >> ret = compute_return(df, "Close", "5D", max_lag="1D")
        >> ret.head()

    """

    if column not in df.columns:
        raise ValueError(f"{column} not found")

    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("index must be DatetimeIndex")

    df = df.sort_index()

    T_delta = pd.Timedelta(T)
    target_index = df.index - T_delta

    past_price = df[column].reindex(target_index, method="ffill")

    # --- ズレ計算 ---
    actual_index = df.index.to_series().reindex(target_index, method="ffill").values
    lag = df.index - actual_index

    # --- フィルタ ---
    if max_lag is not None:
        max_lag_delta = pd.Timedelta(max_lag)
        mask = lag <= max_lag_delta
    else:
        mask = pd.Series(True, index=df.index)

    # --- リターン率 ---
    ret = df[column] / past_price.values - 1
    ret = pd.Series(ret, index=df.index)
    # Filtering
    ret = ret[mask]
    ret = ret.dropna()

    return ret

def compute_var_at_time(
    return_series: pd.Series,
    t,
    confidence: float = 0.95,
    window: int | None = None,
):
    """
    Compute VaR using only data up to time t

    Args:
        return_series: pd.Series with DatetimeIndex
        t: timestamp (str or pd.Timestamp)
        confidence: confidence level
        window: number of past observations to use (None = all history)

    Returns:
        VaR (positive float): VaR is the maximum expected loss over a given horizon at a given confidence level.
    """

    if not isinstance(return_series.index, pd.DatetimeIndex):
        raise TypeError("return_series must have DatetimeIndex")

    t = pd.to_datetime(t)

    # --- t以前だけ ---
    hist = return_series.loc[:t]

    if hist.empty:
        raise ValueError("No data before given time")

    # --- window指定 ---
    if window is not None:
        hist = hist.tail(window)

    # --- VaR ---
    var = -np.percentile(hist, (1 - confidence) * 100)
    return var

def plot_return_dist(
    df: pd.Series,
    savename: str = "output.png",
    bins: int = 50,
    ticker_symbol: str = "",
    confidence: float | None = None,  # ← 追加
):
    data = df.dropna().values

    # 日付範囲
    from_date = df.index.min()
    to_date = df.index.max()

    # 平均と標準偏差
    mu = np.mean(data)
    sigma = np.std(data)

    # ヒストグラム
    plt.hist(data, bins=bins, density=True, alpha=0.6, label="Empirical")

    # 正規分布
    x = np.linspace(data.min(), data.max(), 1000)
    pdf = sp.stats.norm.pdf(x, mu, sigma)
    plt.plot(x, pdf, label=f"Normal (μ={mu:.4f}, σ={sigma:.4f})")

    # --- VaR 可視化 ---
    if confidence is not None:
        q = (1 - confidence) * 100
        var_threshold = np.percentile(data, q)  # 負の値になるはず
        var_value = -var_threshold              # VaR（正）

        # 縦線
        plt.axvline(var_threshold, linestyle="--",
                    label=f"VaR {int(confidence*100)}% = {var_value:.4f}")

        # 横軸に値表示（ちょい下にテキスト）
        plt.text(
            var_threshold,
            plt.ylim()[1] * 0.8,
            f"{var_threshold:.4f}",
            rotation=90,
            verticalalignment="center"
        )

    plt.legend()

    if ticker_symbol:
        plt.title(f"{ticker_symbol}: {from_date.date()} - {to_date.date()}")
    else:
        plt.title(f"{from_date.date()} - {to_date.date()}")

    plt.xlabel("Return")
    plt.ylabel("Density")
    plt.savefig(savename)
    plt.close()

def compute_portfolio_var_at_time(
    return_df: pd.DataFrame,
    weights,
    confidence: float = 0.95,
    window: int | None = None,
):
    """
    Compute portfolio VaR parametrically using a normal approximation.

    Args:
        return_df: pd.DataFrame with DatetimeIndex and numeric asset returns in each column.
        weights: sequence of portfolio weights matching return_df columns.
        confidence: confidence level (e.g. 0.95 for 95% VaR).
        window: number of most recent observations to use (None = all history).

    Returns:
        VaR as a non-negative float.

    Notes:
        Uses the formula VaR = -(mu_p + z * sigma_p), where
        z = sqrt(2) * erfinv(2*confidence - 1).
    """
    if not isinstance(return_df, pd.DataFrame):
        raise TypeError("return_df must be pandas DataFrame")

    if not isinstance(return_df.index, pd.DatetimeIndex):
        raise TypeError("return_df must have DatetimeIndex")

    returns = return_df.copy()
    weights = np.asarray(weights, dtype=float)

    if returns.empty:
        raise ValueError("return_df is empty")

    if len(weights) != returns.shape[1]:
        raise ValueError("weights length must equal number of assets")

    if window is not None:
        returns = returns.tail(window)

    returns = returns.dropna(how="any")
    if returns.empty:
        raise ValueError("No valid return data after dropping NaNs")

    mean_returns = returns.mean().to_numpy()
    cov_matrix = returns.cov().to_numpy()

    portfolio_mean = float(np.dot(weights, mean_returns))
    portfolio_variance = float(np.dot(weights, cov_matrix.dot(weights)))
    if portfolio_variance < 0:
        raise ValueError("Computed portfolio variance is negative")

    portfolio_std = np.sqrt(portfolio_variance)
    z_score = np.sqrt(2.0) * sp.special.erfinv(2.0 * confidence - 1.0) # Inverse CDF of standard distributions
    var = z_score * portfolio_std - portfolio_mean # Var = Upper 95% point
    return float(max(0.0, var))
