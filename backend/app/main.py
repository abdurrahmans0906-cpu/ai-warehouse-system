from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from app.services.forecast_service import (
    load_data,
    preprocess_data,
    prepare_time_series,
    train_all_forecast_models,
    train_forecast_model,
    calculate_inventory,
    detect_trend,
    assign_inventory_and_names,
    benchmark_all_models
)

# ------------------ APP INIT ------------------
app = FastAPI(
    title="AI Warehouse Multi-Model Demand Forecasting System",
    description="Multi-model time-series forecasting & software metrics evaluation engine using Retail Inventory Dataset",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ ROOT ------------------
@app.get("/")
def root():
    return {
        "message": "AI Warehouse Multi-Model Forecasting System Running",
        "models": ["Prophet", "ARIMA", "Exponential Smoothing", "XGBoost", "Random Forest", "Ridge Regression"],
        "dataset": "Retail Inventory Dataset (inventory_final.csv)"
    }


# ------------------ PRODUCTS LIST ------------------
@app.get("/products")
def get_products():
    try:
        df = load_data()
        df = preprocess_data(df)
        df = assign_inventory_and_names(df)

        products = (
            df[["Product ID", "Product Name", "inventory_id"]]
            .drop_duplicates()
            .sort_values("Product ID")
            .to_dict(orient="records")
        )

        return {
            "products": [p["Product ID"] for p in products],
            "product_details": products
        }
    except Exception as e:
        return {"error": str(e)}


# ------------------ MODEL LIST ------------------
@app.get("/models/list")
def list_models():
    return {
        "models": [
            {
                "id": "exponential_smoothing",
                "name": "Exponential Smoothing (Holt-Winters)",
                "type": "Statistical State Space",
                "family": "Smoothing Models",
                "strengths": "Fast, optimal for continuous local trend, low latency",
                "hyperparameters": "trend='add', seasonal=None"
            },
            {
                "id": "prophet",
                "name": "Facebook Prophet",
                "type": "Additive Decomposition",
                "family": "Bayesian Generalized Additive",
                "strengths": "Weekly & seasonal decomposition, robust to missing dates and shifts",
                "hyperparameters": "weekly_seasonality=True, changepoint_prior_scale=0.05"
            },
            {
                "id": "arima",
                "name": "ARIMA(1, 1, 1)",
                "type": "Autoregressive Integrated Moving Average",
                "family": "Box-Jenkins Classical Time Series",
                "strengths": "Captures first-order lag autocorrelation and moving average noise shocks",
                "hyperparameters": "p=1, d=1, q=1"
            },
            {
                "id": "xgboost",
                "name": "XGBoost Regressor",
                "type": "Gradient Boosted Decision Trees",
                "family": "Ensemble Boosting",
                "strengths": "Captures non-linear feature interactions, 7-day lags and rolling statistics",
                "hyperparameters": "n_estimators=50, max_depth=3, lr=0.05"
            },
            {
                "id": "random_forest",
                "name": "Random Forest Regressor",
                "type": "Bagging Ensemble Trees",
                "family": "Bootstrap Aggregation",
                "strengths": "Non-linear regression, robust to individual outlier noise",
                "hyperparameters": "n_estimators=50, max_depth=5"
            },
            {
                "id": "ridge",
                "name": "Ridge Regression",
                "type": "Regularized Linear Baseline",
                "family": "Penalized Least Squares",
                "strengths": "Ultra-fast linear baseline with L2 shrinkage against multicollinearity",
                "hyperparameters": "alpha=1.0"
            }
        ]
    }


# ------------------ DATASET-WIDE MODEL BENCHMARK ------------------
@app.get("/models/benchmark")
def get_benchmark(sample_size: int = Query(6, ge=1, le=20), refresh: bool = False):
    try:
        benchmark = benchmark_all_models(sample_size=sample_size, force_refresh=refresh)
        return {
            "status": "success",
            **benchmark,
            "evaluation_metrics_info": {
                "mae": "Mean Absolute Error: average magnitude of absolute forecast errors in units sold",
                "rmse": "Root Mean Squared Error: penalizes larger variance deviations quadratically",
                "mape": "Mean Absolute Percentage Error: average percentage error relative to actual demand",
                "accuracy": "Normalized Demand Accuracy %: max(0, 100 * (1 - WAPE))",
                "r2": "Coefficient of Determination: proportion of demand variance explained by model",
                "latency_ms": "Average model fitting and inference time in milliseconds"
            }
        }
    except Exception as e:
        return {"error": str(e)}


# ------------------ PRODUCT PAGE & PREDICT (MULTI-MODEL) ------------------
@app.get("/product")
@app.get("/predict")
def product_analysis(product_id: str, model: str = Query("best"), refresh: bool = False):
    try:
        df = load_data()
        df = preprocess_data(df)
        df = assign_inventory_and_names(df)

        df_ts, df_product = prepare_time_series(df, product_id)

        # Train and evaluate all 6 models
        multi_forecast = train_all_forecast_models(
            df_ts,
            forecast_days=7,
            eval_days=14,
            use_cache=not refresh,
            cache_key=product_id
        )

        inventory_res = calculate_inventory(df_product, multi_forecast)
        trend = detect_trend(multi_forecast["graph"])

        # Determine product name and inventory category
        product_row = df[df["Product ID"] == product_id].iloc[0] if not df[df["Product ID"] == product_id].empty else None
        product_name = str(product_row["Product Name"]) if product_row is not None and "Product Name" in product_row else f"Product {product_id}"
        inventory_id = str(product_row["inventory_id"]) if product_row is not None and "inventory_id" in product_row else "INV001"

        return {
            "product_id": product_id,
            "product_name": product_name,
            "inventory_id": inventory_id,
            "inventory": inventory_res,
            "trend": trend,
            "best_model": multi_forecast["best_model"],
            "selected_model": model,
            "models_accuracy": multi_forecast["models_accuracy"],
            "metrics_comparison_chart": multi_forecast["metrics_comparison_chart"],
            "last_3_days": multi_forecast["last_3_days"],
            "graph": multi_forecast["graph"]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ------------------ INVENTORY DASHBOARD ------------------
@app.get("/inventory/{inventory_id}")
def inventory_dashboard(inventory_id: str):
    try:
        df = load_data()
        df = preprocess_data(df)
        df = assign_inventory_and_names(df)

        df_inv = df[df["inventory_id"] == inventory_id].copy()

        if df_inv.empty:
            return {"error": f"No data found for {inventory_id}"}

        # ------------------ TOTAL PRODUCTS ------------------
        total_products = int(df_inv["Product ID"].nunique())

        # ------------------ SALES % ------------------
        total_sales_all = float(df["Units Sold"].sum())
        total_sales_inv = float(df_inv["Units Sold"].sum())

        sales_percentage = round(
            (total_sales_inv / total_sales_all) * 100, 2
        ) if total_sales_all != 0 else 0

        # ------------------ PRODUCT LIST ------------------
        product_list = sorted(df_inv["Product ID"].unique().tolist())

        # ------------------ TOP PRODUCTS ------------------
        top_products = (
            df_inv
            .groupby(["Product ID", "Product Name"], as_index=False)
            .agg({"Units Sold": "sum"})
            .sort_values(by="Units Sold", ascending=False)
        )

        top_products = top_products.drop_duplicates("Product ID").head(20)

        return {
            "inventory_id": inventory_id,
            "total_products": total_products,
            "sales_percentage": sales_percentage,
            "products": product_list,
            "top_products": top_products.to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}


# ------------------ INVENTORY LIST ------------------
@app.get("/inventories")
def get_inventories():
    return {
        "inventories": [
            {"id": "INV001", "name": "Electronics"},
            {"id": "INV002", "name": "Toys"},
            {"id": "INV003", "name": "Stationery"},
            {"id": "INV004", "name": "Gadgets"},
            {"id": "INV005", "name": "Clothing"},
            {"id": "INV006", "name": "Furniture"},
            {"id": "INV007", "name": "Sports"},
            {"id": "INV008", "name": "Accessories"}
        ]
    }


# ------------------ HOME DASHBOARD ------------------
@app.get("/home")
def home_dashboard():
    try:
        df = load_data()
        df = preprocess_data(df)
        df = assign_inventory_and_names(df)

        # -------- LOW STOCK --------
        demand_stats = (
            df.groupby("Product ID")["Units Sold"]
            .agg(["mean", "std"])
            .reset_index()
        )

        demand_stats["rop"] = (demand_stats["mean"] * 3) + (demand_stats["std"] * 2)

        latest_stock = (
            df.sort_values("Date")
            .groupby("Product ID")
            .tail(1)[["Product ID", "Inventory Level", "Product Name", "inventory_id"]]
        )

        merged = pd.merge(latest_stock, demand_stats, on="Product ID")

        low_stock = merged[merged["Inventory Level"] <= merged["rop"]]
        low_stock_table = low_stock.sort_values(by="Inventory Level").head(10)

        # -------- HIGH DEMAND (BALANCED) --------
        high_demand = (
            df.groupby(["inventory_id", "Product ID", "Product Name"])["Units Sold"]
            .sum()
            .reset_index()
        )

        top_per_inventory = (
            high_demand.sort_values(
                ["inventory_id", "Units Sold"],
                ascending=[True, False]
            )
            .groupby("inventory_id")
            .head(2)
        )

        high_demand_final = (
            top_per_inventory
            .sort_values("Units Sold", ascending=False)
            .head(10)
        )

        return {
            "low_stock": low_stock_table.to_dict(orient="records"),
            "high_demand": high_demand_final.to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}
