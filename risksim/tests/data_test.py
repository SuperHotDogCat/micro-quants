import pandas as pd
import risksim.data as fdata # finance data

def test_load_yfinance_data():
    df = fdata.load_yfinance_data("AAPL", "2023-01-01", "2023-02-01")
    print(df)
    print(df.index)
    print(type(df.index))
    print(df.index.dtype)
    # 空じゃない
    assert not df.empty

def test_compute_return():
    df = fdata.load_yfinance_data("AAPL", "2023-01-01", "2023-02-01")
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
    df = fdata.load_yfinance_data("AAPL", "2023-01-01", "2023-02-01")
    ret = fdata.compute_return(df, "Close", "1D", max_lag="1D")
    # 2023-01-20時点のVaR（それ以前だけ）
    var = fdata.compute_var_at_time(ret, "2023-01-20", 0.95)
    
