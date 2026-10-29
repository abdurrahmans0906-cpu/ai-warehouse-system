import os
import time
import random
import numpy as np
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ------------------ PATH RESOLUTION ------------------
def get_data_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(current_dir, "..", "..", "data", "inventory_final.csv"),
        os.path.join(os.getcwd(), "data", "inventory_final.csv"),
        os.path.join(os.getcwd(), "backend", "data", "inventory_final.csv"),
        "data/inventory_final.csv"
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    return os.path.abspath(candidates[0])

# ------------------ IN-MEMORY CACHES ------------------
_PRODUCT_FORECAST_CACHE = {}
_BENCHMARK_CACHE = None

# ------------------ LOAD DATA ------------------
def load_data():
    csv_path = get_data_path()
    df = pd.read_csv(csv_path)

    if "Store ID" in df.columns and "Product ID" in df.columns:
        df["Product Unique"] = df["Product ID"] + "_" + df["Store ID"].astype(str)
    else:
        df["Product Unique"] = df["Product ID"]

    return df

# ------------------ CLEAN DATA ------------------
def preprocess_data(df):
    df = df.dropna()
    df["Date"] = pd.to_datetime(df["Date"])
    return df

# ------------------ ASSIGN INVENTORY (DETERMINISTIC) ------------------
def assign_inventory_and_names(df):
    # Predefined category and product mappings if missing
    inventory_map = {
        "INV001": ["Samsung TV", "Dell Laptop", "iPhone", "HP Printer", "LG Monitor", "Sony Camera", "Asus Laptop", "Lenovo PC"],
        "INV002": ["Barbie Doll", "Hot Wheels", "Teddy Bear", "Lego Set", "Toy Car", "Puzzle Game", "Action Figure"],
        "INV003": ["Pen", "Pencil", "Eraser", "Sharpener", "Notebook", "Marker", "Highlighter"],
        "INV004": ["Smartwatch", "Headphones", "Power Bank", "Bluetooth Speaker", "Earbuds", "USB Drive"],
        "INV005": ["Office Chair", "Office Table", "Printer Machine", "Projector", "Conference Mic"],
        "INV006": ["Sofa", "Dining Table", "Bed", "Wardrobe", "Bookshelf"],
        "INV007": ["Football", "Cricket Bat", "Tennis Racket", "Basketball", "Gym Dumbbells"],
        "INV008": ["Handbag", "Watch", "Sunglasses", "Wallet", "Chain", "Ring"]
    }

    if "inventory_id" in df.columns and "Product Name" in df.columns:
        return df

    inventory_ids = list(inventory_map.keys())
    products = sorted(df["Product ID"].unique())

    mapping_inventory = {}
    mapping_name = {}

    for i, product in enumerate(products):
        inv_id = inventory_ids[i % len(inventory_ids)]
        mapping_inventory[product] = inv_id
        names = inventory_map[inv_id]
        mapping_name[product] = names[i % len(names)]

    if "inventory_id" not in df.columns:
        df["inventory_id"] = df["Product ID"].map(mapping_inventory)
    if "Product Name" not in df.columns:
        df["Product Name"] = df["Product ID"].map(mapping_name)

    return df

# ------------------ PRODUCT TIME SERIES ------------------
def prepare_time_series(df, product_id):
    df_product = df[df["Product ID"] == product_id].copy()

    if df_product.shape[0] < 10:
        raise ValueError(f"Not enough data for product {product_id}")

    df_product = df_product.sort_values("Date")

    # Aggregate by Date to have clean 1-row-per-day continuous demand
    df_ts = (
        df_product.groupby("Date", as_index=False)["Units Sold"]
        .sum()
        .rename(columns={"Date": "ds", "Units Sold": "y"})
    )
    df_ts["ds"] = pd.to_datetime(df_ts["ds"])
    df_ts = df_ts.sort_values("ds").reset_index(drop=True)

    return df_ts, df_product

# ------------------ INVENTORY LEVEL DATA ------------------
def prepare_inventory_data(df, inventory_id):
    df_inv = df[df["inventory_id"] == inventory_id].copy()

    if df_inv.empty:
        raise ValueError(f"No data for {inventory_id}")

    df_grouped = (
        df_inv.groupby("Date", as_index=False)["Units Sold"]
        .sum()
        .rename(columns={"Date": "ds", "Units Sold": "y"})
    )
    df_grouped["ds"] = pd.to_datetime(df_grouped["ds"])
    df_grouped = df_grouped.sort_values("ds").reset_index(drop=True)

    return df_grouped, df_inv

# ------------------ ML FEATURE ENGINEERING ------------------
def _create_ml_features(series):
    """
    Constructs autoregressive lag and rolling window features:
    - lag_1, lag_2, lag_3, lag_7
    - 7-day rolling mean and standard deviation
    - day of week (cyclical proxy)
    """
    X, y = [], []
    for i in range(7, len(series)):
        lags = [series[i - 1], series[i - 2], series[i - 3], series[i - 7]]
        rolling_mean = float(np.mean(series[i - 7:i]))
        rolling_std = float(np.std(series[i - 7:i]))
        day_of_week = float(i % 7)
        X.append(lags + [rolling_mean, rolling_std, day_of_week])
        y.append(series[i])
    return np.array(X), np.array(y)

def _recursive_ml_forecast(model, history_series, steps=7):
    """
    Generates multi-step ahead forecasts autoregressively.
    """
    current = list(history_series)
    preds = []
    for _ in range(steps):
        i = len(current)
        lags = [current[i - 1], current[i - 2], current[i - 3], current[i - 7]]
        rolling_mean = float(np.mean(current[i - 7:i]))
        rolling_std = float(np.std(current[i - 7:i]))
        day_of_week = float(i % 7)
        features = np.array([lags + [rolling_mean, rolling_std, day_of_week]])
        pred = float(model.predict(features)[0])
        pred = max(0.0, pred)
        preds.append(pred)
        current.append(pred)
    return np.array(preds)

# ------------------ MULTI-MODEL TRAINING & EVALUATION ------------------
def train_all_forecast_models(df_ts, forecast_days=7, eval_days=14, use_cache=True, cache_key=None):
    """
    Trains and evaluates 6 diverse forecasting models on retail inventory time series:
    1. Facebook Prophet (Additive Bayesian Time Series with weekly seasonality)
    2. ARIMA (AutoRegressive Integrated Moving Average)
    3. Exponential Smoothing (Holt-Winters State Space)
    4. XGBoost Regressor (Gradient Boosted Trees)
    5. Random Forest Regressor (Ensemble Bagging)
    6. Ridge Regression (L2 Regularized Linear Model)

    Computes:
    - MAE, RMSE, MAPE, Accuracy %, R², Execution Latency (ms)
    - Full 7-day future projections
    - Unified 37-point timeline (past 30 days + next 7 forecast days)
    """
    if use_cache and cache_key and cache_key in _PRODUCT_FORECAST_CACHE:
        return _PRODUCT_FORECAST_CACHE[cache_key]

    ts = df_ts.copy()
    ts = ts.sort_values("ds").reset_index(drop=True)
    full_y = ts["y"].values
    full_len = len(full_y)

    if full_len < 30:
        raise ValueError(f"Need at least 30 observations, found {full_len}")

    # -------- EVALUATION SPLIT --------
    split_idx = full_len - eval_days
    train_eval_df = ts.iloc[:split_idx]
    y_train_eval = train_eval_df["y"].values
    y_test_eval = ts["y"].iloc[split_idx:].values

    X_train_eval, y_train_eval_ml = _create_ml_features(y_train_eval)

    models_info = [
        {
            "id": "prophet",
            "name": "Prophet",
            "category": "Additive Decomposition",
            "description": "Decomposable additive time-series model with weekly seasonality & robust changepoint detection."
        },
        {
            "id": "arima",
            "name": "ARIMA",
            "category": "Autoregressive Integrated MA",
            "description": "Statistical ARIMA(1, 1, 1) model capturing autocorrelation, differenced stationary trend & noise shocks."
        },
        {
            "id": "exponential_smoothing",
            "name": "Exponential Smoothing",
            "category": "Holt-Winters State Space",
            "description": "Triple/double exponential smoothing assigning exponentially decreasing weights over past demand."
        },
        {
            "id": "xgboost",
            "name": "XGBoost",
            "category": "Gradient Boosted Trees",
            "description": "Second-order gradient boosted decision trees leveraging recursive 7-day lag and rolling statistics."
        },
        {
            "id": "random_forest",
            "name": "Random Forest",
            "category": "Ensemble Bagging Trees",
            "description": "Meta-estimator bagging multiple randomized decision trees to reduce variance on demand fluctuations."
        },
        {
            "id": "ridge",
            "name": "Ridge Regression",
            "category": "L2 Regularized Linear",
            "description": "L2-regularized linear baseline balancing lag features and preventing collinearity overfitting."
        }
    ]

    eval_predictions = {}
    execution_times = {}

    # 1. Prophet Eval
    t0 = time.time()
    try:
        mp_eval = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
        mp_eval.fit(train_eval_df)
        fut_eval = mp_eval.make_future_dataframe(periods=eval_days)
        eval_predictions["prophet"] = mp_eval.predict(fut_eval)["yhat"].iloc[-eval_days:].values
    except Exception:
        eval_predictions["prophet"] = np.full(eval_days, np.mean(y_train_eval))
    execution_times["prophet"] = round((time.time() - t0) * 1000, 1)

    # 2. ARIMA Eval
    t0 = time.time()
    try:
        ma_eval = ARIMA(y_train_eval, order=(1, 1, 1)).fit()
        eval_predictions["arima"] = ma_eval.forecast(steps=eval_days)
    except Exception:
        eval_predictions["arima"] = np.full(eval_days, np.mean(y_train_eval))
    execution_times["arima"] = round((time.time() - t0) * 1000, 1)

    # 3. Exponential Smoothing Eval
    t0 = time.time()
    try:
        mes_eval = ExponentialSmoothing(y_train_eval, trend="add").fit()
        eval_predictions["exponential_smoothing"] = mes_eval.forecast(steps=eval_days)
    except Exception:
        eval_predictions["exponential_smoothing"] = np.full(eval_days, np.mean(y_train_eval))
    execution_times["exponential_smoothing"] = round((time.time() - t0) * 1000, 1)

    # 4. XGBoost Eval
    t0 = time.time()
    try:
        m_xgb_eval = XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.05, random_state=42)
        m_xgb_eval.fit(X_train_eval, y_train_eval_ml)
        eval_predictions["xgboost"] = _recursive_ml_forecast(m_xgb_eval, y_train_eval, eval_days)
    except Exception:
        eval_predictions["xgboost"] = np.full(eval_days, np.mean(y_train_eval))
    execution_times["xgboost"] = round((time.time() - t0) * 1000, 1)

    # 5. Random Forest Eval
    t0 = time.time()
    try:
        m_rf_eval = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        m_rf_eval.fit(X_train_eval, y_train_eval_ml)
        eval_predictions["random_forest"] = _recursive_ml_forecast(m_rf_eval, y_train_eval, eval_days)
    except Exception:
        eval_predictions["random_forest"] = np.full(eval_days, np.mean(y_train_eval))
    execution_times["random_forest"] = round((time.time() - t0) * 1000, 1)

    # 6. Ridge Eval
    t0 = time.time()
    try:
        m_rd_eval = Ridge(alpha=1.0)
        m_rd_eval.fit(X_train_eval, y_train_eval_ml)
        eval_predictions["ridge"] = _recursive_ml_forecast(m_rd_eval, y_train_eval, eval_days)
    except Exception:
        eval_predictions["ridge"] = np.full(eval_days, np.mean(y_train_eval))
    execution_times["ridge"] = round((time.time() - t0) * 1000, 1)

    # Compute Evaluation Metrics
    accuracy_list = []
    y_test_sum = np.sum(y_test_eval) if np.sum(y_test_eval) > 0 else 1.0

    for info in models_info:
        m_id = info["id"]
        pred = np.maximum(0.0, np.array(eval_predictions[m_id]))
        mae = float(mean_absolute_error(y_test_eval, pred))
        rmse = float(np.sqrt(mean_squared_error(y_test_eval, pred)))
        mape = float(np.mean(np.abs((y_test_eval - pred) / np.maximum(y_test_eval, 1.0))) * 100.0)
        accuracy_pct = float(max(0.0, (1.0 - np.sum(np.abs(y_test_eval - pred)) / y_test_sum) * 100.0))
        r2 = float(r2_score(y_test_eval, pred))

        accuracy_list.append({
            "id": m_id,
            "name": info["name"],
            "category": info["category"],
            "description": info["description"],
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "accuracy": round(accuracy_pct, 2),
            "r2": round(r2, 3),
            "latency_ms": execution_times[m_id]
        })

    # Sort by Accuracy desc, MAE asc
    accuracy_list.sort(key=lambda x: (-x["accuracy"], x["mae"]))
    for rank, item in enumerate(accuracy_list, start=1):
        item["rank"] = rank
        item["is_best"] = (rank == 1)

    best_model_id = accuracy_list[0]["id"]
    best_model_name = accuracy_list[0]["name"]

    # -------- FUTURE FORECAST (FULL DATASET 7 DAYS) --------
    future_forecasts = {}
    X_full, y_full_ml = _create_ml_features(full_y)

    # 1. Full Prophet
    try:
        mp_full = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
        mp_full.fit(ts)
        fut_full = mp_full.make_future_dataframe(periods=forecast_days)
        future_forecasts["prophet"] = mp_full.predict(fut_full)["yhat"].iloc[-forecast_days:].values
    except Exception:
        future_forecasts["prophet"] = np.full(forecast_days, np.mean(full_y))

    # 2. Full ARIMA
    try:
        ma_full = ARIMA(full_y, order=(1, 1, 1)).fit()
        future_forecasts["arima"] = ma_full.forecast(steps=forecast_days)
    except Exception:
        future_forecasts["arima"] = np.full(forecast_days, np.mean(full_y))

    # 3. Full Exponential Smoothing
    try:
        mes_full = ExponentialSmoothing(full_y, trend="add").fit()
        future_forecasts["exponential_smoothing"] = mes_full.forecast(steps=forecast_days)
    except Exception:
        future_forecasts["exponential_smoothing"] = np.full(forecast_days, np.mean(full_y))

    # 4. Full XGBoost
    try:
        m_xgb_full = XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.05, random_state=42)
        m_xgb_full.fit(X_full, y_full_ml)
        future_forecasts["xgboost"] = _recursive_ml_forecast(m_xgb_full, full_y, forecast_days)
    except Exception:
        future_forecasts["xgboost"] = np.full(forecast_days, np.mean(full_y))

    # 5. Full Random Forest
    try:
        m_rf_full = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        m_rf_full.fit(X_full, y_full_ml)
        future_forecasts["random_forest"] = _recursive_ml_forecast(m_rf_full, full_y, forecast_days)
    except Exception:
        future_forecasts["random_forest"] = np.full(forecast_days, np.mean(full_y))

    # 6. Full Ridge
    try:
        m_rd_full = Ridge(alpha=1.0)
        m_rd_full.fit(X_full, y_full_ml)
        future_forecasts["ridge"] = _recursive_ml_forecast(m_rd_full, full_y, forecast_days)
    except Exception:
        future_forecasts["ridge"] = np.full(forecast_days, np.mean(full_y))

    # Build Unified 37-Point Timeline (Past 30 Days Actual + Next 7 Forecast Days)
    history_window = 30
    recent_ts = ts.iloc[-history_window:]
    last_date = ts["ds"].iloc[-1]

    graph_points = []

    # Historical segment (days -30 to -1)
    for _, row in recent_ts.iterrows():
        d_str = row["ds"].strftime("%Y-%m-%d") if hasattr(row["ds"], "strftime") else str(row["ds"])[:10]
        actual_val = round(float(row["y"]), 2)
        graph_points.append({
            "ds": d_str,
            "actual": actual_val,
            "prophet": None,
            "arima": None,
            "exponential_smoothing": None,
            "xgboost": None,
            "random_forest": None,
            "ridge": None,
            "best_forecast": None,
            "yhat": actual_val  # backward compatibility
        })

    # Bridge point: attach last actual point to forecast lines for continuity
    last_actual = graph_points[-1]["actual"]
    for key in ["prophet", "arima", "exponential_smoothing", "xgboost", "random_forest", "ridge", "best_forecast"]:
        graph_points[-1][key] = last_actual

    # Future forecast segment (days +1 to +7)
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_days + 1)]
    for i, fut_dt in enumerate(future_dates):
        d_str = fut_dt.strftime("%Y-%m-%d")
        p_val = round(float(max(0.0, future_forecasts["prophet"][i])), 2)
        a_val = round(float(max(0.0, future_forecasts["arima"][i])), 2)
        es_val = round(float(max(0.0, future_forecasts["exponential_smoothing"][i])), 2)
        xgb_val = round(float(max(0.0, future_forecasts["xgboost"][i])), 2)
        rf_val = round(float(max(0.0, future_forecasts["random_forest"][i])), 2)
        rd_val = round(float(max(0.0, future_forecasts["ridge"][i])), 2)

        best_val = {
            "prophet": p_val,
            "arima": a_val,
            "exponential_smoothing": es_val,
            "xgboost": xgb_val,
            "random_forest": rf_val,
            "ridge": rd_val
        }.get(best_model_id, p_val)

        graph_points.append({
            "ds": d_str,
            "actual": None,
            "prophet": p_val,
            "arima": a_val,
            "exponential_smoothing": es_val,
            "xgboost": xgb_val,
            "random_forest": rf_val,
            "ridge": rd_val,
            "best_forecast": best_val,
            "yhat": best_val
        })

    # Last 3 days summary
    last_3_points = graph_points[-3:]
    last_3_data = [
        {"date": p["ds"], "value": p["best_forecast"]}
        for p in last_3_points
    ]

    # Metrics comparison chart formatting
    metrics_comparison_chart = [
        {
            "model": item["name"],
            "accuracy": item["accuracy"],
            "mae": item["mae"],
            "rmse": item["rmse"],
            "mape": item["mape"],
            "latency": item["latency_ms"]
        }
        for item in accuracy_list
    ]

    result = {
        "models_accuracy": accuracy_list,
        "best_model": accuracy_list[0],
        "graph": graph_points,
        "last_3_days": last_3_data,
        "metrics_comparison_chart": metrics_comparison_chart,
        "future_demand_sum": float(sum(p["best_forecast"] for p in graph_points[-forecast_days:]))
    }

    if cache_key:
        _PRODUCT_FORECAST_CACHE[cache_key] = result

    return result

# ------------------ LEGACY WRAPPER FOR BACKWARD COMPATIBILITY ------------------
def train_forecast_model(df_ts):
    """
    Backward-compatible method returning a Prophet-like forecast dataframe.
    """
    model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
    model.fit(df_ts)
    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)
    return forecast

# ------------------ INVENTORY DECISION ------------------
def calculate_inventory(df_product, forecast_or_val):
    current_stock = float(df_product["Inventory Level"].iloc[-1])

    avg_demand = float(df_product["Units Sold"].mean())
    std_demand = float(df_product["Units Sold"].std())

    lead_time = 3
    safety_stock = std_demand * 2
    rop = (avg_demand * lead_time) + safety_stock

    if isinstance(forecast_or_val, dict) and "future_demand_sum" in forecast_or_val:
        future_demand = forecast_or_val["future_demand_sum"]
    elif isinstance(forecast_or_val, pd.DataFrame) and "yhat" in forecast_or_val.columns:
        future_demand = float(forecast_or_val["yhat"].tail(7).sum())
    elif isinstance(forecast_or_val, (int, float)):
        future_demand = float(forecast_or_val)
    else:
        future_demand = avg_demand * 7

    if current_stock <= rop:
        decision = "REORDER"
        reorder_qty = int(future_demand)
    else:
        decision = "NO ACTION"
        reorder_qty = 0

    return {
        "current_stock": int(current_stock),
        "rop": int(rop),
        "decision": decision,
        "reorder_quantity": reorder_qty
    }

# ------------------ TREND ------------------
def detect_trend(forecast_obj):
    if isinstance(forecast_obj, list):
        if len(forecast_obj) >= 6:
            first_avg = np.mean([p.get("best_forecast") or p.get("yhat") or 0 for p in forecast_obj[:3]])
            last_avg = np.mean([p.get("best_forecast") or p.get("yhat") or 0 for p in forecast_obj[-3:]])
        else:
            return "Stable"
    elif isinstance(forecast_obj, pd.DataFrame) and "yhat" in forecast_obj.columns:
        first_avg = forecast_obj["yhat"].head(3).mean()
        last_avg = forecast_obj["yhat"].tail(3).mean()
    else:
        return "Stable"

    diff_pct = (last_avg - first_avg) / (first_avg + 1e-5) * 100
    if diff_pct > 2.0:
        return "Increasing"
    elif diff_pct < -2.0:
        return "Decreasing"
    else:
        return "Stable"

# ------------------ INVENTORY SUMMARY & TOP PRODUCTS ------------------
def get_inventory_summary(df_inv):
    total_products = df_inv["Product Unique"].nunique()
    total_sales = df_inv["Units Sold"].sum()
    return total_products, total_sales

def get_top_products(df_inv):
    top = (
        df_inv.groupby(["Product ID", "Product Name"])["Units Sold"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    return top.to_dict(orient="records")

# ------------------ DATASET-WIDE MODEL BENCHMARK ------------------
def benchmark_all_models(sample_size=6, force_refresh=False):
    """
    Computes global multi-model benchmark metrics across representative
    products from the retail inventory dataset.
    """
    global _BENCHMARK_CACHE
    if _BENCHMARK_CACHE is not None and not force_refresh:
        return _BENCHMARK_CACHE

    df = load_data()
    df = preprocess_data(df)
    df = assign_inventory_and_names(df)

    product_ids = sorted(df["Product ID"].unique())[:sample_size]
    aggregated_metrics = {}

    for pid in product_ids:
        try:
            df_ts, _ = prepare_time_series(df, pid)
            model_res = train_all_forecast_models(df_ts, forecast_days=7, eval_days=14, use_cache=True, cache_key=pid)
            for m in model_res["models_accuracy"]:
                m_id = m["id"]
                if m_id not in aggregated_metrics:
                    aggregated_metrics[m_id] = {
                        "id": m_id,
                        "name": m["name"],
                        "category": m["category"],
                        "description": m["description"],
                        "mae_list": [],
                        "rmse_list": [],
                        "mape_list": [],
                        "accuracy_list": [],
                        "r2_list": [],
                        "latency_list": []
                    }
                aggregated_metrics[m_id]["mae_list"].append(m["mae"])
                aggregated_metrics[m_id]["rmse_list"].append(m["rmse"])
                aggregated_metrics[m_id]["mape_list"].append(m["mape"])
                aggregated_metrics[m_id]["accuracy_list"].append(m["accuracy"])
                aggregated_metrics[m_id]["r2_list"].append(m["r2"])
                aggregated_metrics[m_id]["latency_list"].append(m["latency_ms"])
        except Exception as e:
            print(f"Error benchmarking product {pid}: {e}")

    summary_list = []
    for m_id, vals in aggregated_metrics.items():
        summary_list.append({
            "id": m_id,
            "name": vals["name"],
            "category": vals["category"],
            "description": vals["description"],
            "mae": round(float(np.mean(vals["mae_list"])), 2),
            "rmse": round(float(np.mean(vals["rmse_list"])), 2),
            "mape": round(float(np.mean(vals["mape_list"])), 2),
            "accuracy": round(float(np.mean(vals["accuracy_list"])), 2),
            "r2": round(float(np.mean(vals["r2_list"])), 3),
            "latency_ms": round(float(np.mean(vals["latency_list"])), 1)
        })

    summary_list.sort(key=lambda x: (-x["accuracy"], x["mae"]))
    for rank, item in enumerate(summary_list, start=1):
        item["rank"] = rank
        item["is_best"] = (rank == 1)

    chart_data = [
        {
            "model": item["name"],
            "accuracy": item["accuracy"],
            "mae": item["mae"],
            "rmse": item["rmse"],
            "mape": item["mape"],
            "latency": item["latency_ms"]
        }
        for item in summary_list
    ]

    _BENCHMARK_CACHE = {
        "dataset": "Retail Inventory Dataset (inventory_final.csv)",
        "sample_size": len(product_ids),
        "total_models": len(summary_list),
        "models": summary_list,
        "best_overall": summary_list[0] if summary_list else None,
        "chart_data": chart_data
    }

    return _BENCHMARK_CACHE
