import pandas as pd
import risksim.data as fdata # finance data

def test_load_yfinance_data():
    df = fdata.load_yfinance_data("AAPL", "2023-01-01", "2026-02-01")
    print(df)
    print(df.index)
    print(type(df.index))
    print(df.index.dtype)
    # 空じゃない
    assert not df.empty

def test_compute_return():
    # 固定データ
    df = pd.DataFrame({
        "Close": [100, 101, 102],
        "High": [100, 101, 102],
        "Low": [100, 101, 102],
        "Open": [100, 101, 102],
        "Volume": [100, 101, 102]
    }, index=pd.date_range("2023-01-01", periods=3, freq="D"))
    ret = fdata.compute_return(df, "Close", "1D", max_lag="1D")
    # インデックスをSeriesに
    idx = ret.index.to_series()
    # 前日との差をチェック
    prev_day = idx - pd.Timedelta("1D")
    # 元データに前日が存在するか
    has_prev = prev_day.isin(df.index)
    # 全てTrueであることを確認
    assert has_prev.all(), "Return includes entries without exact 1D previous data"

def test_compute_var():
    # 固定データ
    df = pd.DataFrame({
        "Close": [100, 101, 102],
        "High": [100, 101, 102],
        "Low": [100, 101, 102],
        "Open": [100, 101, 102],
        "Volume": [100, 101, 102]
    }, index=pd.date_range("2023-01-01", periods=3, freq="D"))
    ret = fdata.compute_return(df, "Close", "1D", max_lag="1D")
    var = fdata.compute_var_at_time(ret, "2026-02-01", 0.95)
    print(var)

def test_plot_return_dist():
    # 固定データ
    df = pd.DataFrame({
        "Close": [100, 101, 102],
        "High": [100, 101, 102],
        "Low": [100, 101, 102],
        "Open": [100, 101, 102],
        "Volume": [100, 101, 102]
    }, index=pd.date_range("2023-01-01", periods=3, freq="D"))
    ret = fdata.compute_return(df, "Close", "1D", max_lag="1D")
    fdata.plot_return_dist(ret, confidence=0.95, ticker_symbol="AAPL")

def test_compute_portfolio_var():
    # Synthetic returns for 2 assets with fixed weights
    data = {
        "asset_1": [0.01, -0.02, 0.015, -0.005, 0.002],
        "asset_2": [0.005, -0.01, 0.02, -0.01, 0.003],
    }
    df = pd.DataFrame(data, index=pd.date_range("2024-01-01", periods=5, freq="D"))
    weights = [0.6, 0.4]

    var = fdata.compute_portfolio_var_at_time(df, weights, confidence=0.95)
    print(var)
    assert isinstance(var, float)
    assert var >= 0.0
    assert var > 0.0
