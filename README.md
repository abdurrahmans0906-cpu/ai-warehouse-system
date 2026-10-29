# 📦 AI Warehouse Multi-Model Demand Forecasting System

An intelligent inventory management and demand forecasting web application. The platform leverages multiple state-of-the-art machine learning and time-series algorithms (Facebook Prophet, ARIMA, Exponential Smoothing, XGBoost, Random Forest, and Ridge Regression) to forecast demand, prevent stockouts, optimize replenishment cycles, and benchmark forecasting models on retail inventory datasets.

---

## 🚀 Key Features

- **Multi-Model Demand Forecasting**: Run and compare predictions across 6 forecasting models:
  - Prophet (Facebook Time-Series Model)
  - ARIMA (Auto-Regressive Integrated Moving Average)
  - Exponential Smoothing (Holt-Winters)
  - XGBoost Regressor
  - Random Forest Regressor
  - Ridge Regression
- **Automated Inventory Analytics**: Real-time insights into stock levels, safety stock calculation, reorder thresholds, and demand variability.
- **Model Comparison & Benchmarking**: Evaluate models using standard metrics including **MAE**, **RMSE**, and **MAPE**.
- **Interactive Modern UI**: Clean React-based dashboard with dynamic Recharts visualizations, dark/light themes, and responsive design.
- **RESTful API**: Fast and modular FastAPI backend service with interactive OpenAPI / Swagger documentation.

---

## 🛠️ Architecture & Tech Stack

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework
  - [Uvicorn](https://www.uvicorn.org/) - ASGI web server implementation
  - [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) - Data manipulation and processing
  - [Prophet](https://facebook.github.io/prophet/) - Time series forecasting
  - [Statsmodels](https://www.statsmodels.org/) - Statistical models (ARIMA, Exponential Smoothing)
  - [Scikit-learn](https://scikit-learn.org/) & [XGBoost](https://xgboost.readthedocs.io/) - Machine learning algorithms
- **Frontend**:
  - [React 19](https://react.dev/) - Modern component-based web UI
  - [Recharts](https://recharts.org/) - Composable charting library
  - [Framer Motion](https://www.framer.com/motion/) - Smooth animations
  - [React Icons](https://react-icons.github.io/react-icons/) & [Fontsource Inter](https://fontsource.org/fonts/inter)

---

## 📂 Project Structure

```text
ai-warehouse-system/
├── backend/
│   ├── app/
│   │   ├── api/routes.py            # API endpoints
│   │   ├── core/config.py           # Core settings and configuration
│   │   ├── models/forecast.py       # Pydantic schemas and models
│   │   ├── services/forecast_service.py # Time-series & ML training engine
│   │   ├── utils/helpers.py         # Utility helper functions
│   │   └── main.py                  # FastAPI application entry point
│   ├── data/
│   │   ├── inventory_final.csv      # Primary retail inventory dataset
│   │   └── process_dataset.py       # Data cleaning and prep scripts
│   ├── generate_clean_data.py       # Data generation utility
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── public/                      # Static assets & icons
│   ├── src/
│   │   ├── components/              # UI components (Sidebar, Cards, etc.)
│   │   ├── pages/                   # Application views (Home, Dashboard, etc.)
│   │   ├── styles/                  # CSS stylesheets
│   │   ├── api.js                   # Axios / fetch API configuration
│   │   ├── App.js                   # Root React component
│   │   └── index.js                 # React DOM mount point
│   └── package.json                 # Node dependencies and scripts
├── report_assets/                   # Figures and diagrams for project documentation
├── AI_Warehouse_System_Project_Report.pdf # Comprehensive academic project report
├── .gitignore                       # Git ignore configuration
└── README.md                        # Project documentation
```

---

## 💻 Getting Started: Pull and Run Locally

Follow these instructions to clone and run the project locally on your machine.

### Prerequisites

Ensure you have the following installed:
- **Git**: [Download Git](https://git-scm.com/)
- **Python**: Version 3.10 or higher [Download Python](https://www.python.org/)
- **Node.js**: Version 18 or higher (includes npm) [Download Node.js](https://nodejs.org/)

---

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the repository:

```bash
git clone https://github.com/abdurrahmans0906-cpu/ai-warehouse-system.git
cd ai-warehouse-system
```

---

### Step 2: Set Up and Run the Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   - **Windows**:
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Upgrade `pip` and install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. The backend server is now running at `http://127.0.0.1:8000`:
   - Interactive API Docs (Swagger UI): **`http://127.0.0.1:8000/docs`**
   - Alternative API Docs (ReDoc): **`http://127.0.0.1:8000/redoc`**

---

### Step 3: Set Up and Run the Frontend

1. Open a **new** terminal window and navigate to the `frontend` folder:
   ```bash
   cd ai-warehouse-system/frontend
   ```

2. Install JavaScript packages:
   ```bash
   npm install
   ```

3. Launch the React development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

The application will automatically connect to the backend running at `http://127.0.0.1:8000`.

---

## 📊 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check & system metadata |
| `GET` | `/products` | List available inventory items and categories |
| `GET` | `/forecast` | Generate forecast for a product using a specific model |
| `GET` | `/forecast-all` | Generate comparative forecasts across all 6 models |
| `GET` | `/benchmark` | Model performance benchmarking (MAE, RMSE, MAPE) |
| `GET` | `/inventory` | Comprehensive inventory stock status & suggestions |

---

## 👥 Authors & Academic Credits

- **Repository**: [abdurrahmans0906-cpu/ai-warehouse-system](https://github.com/abdurrahmans0906-cpu/ai-warehouse-system)
- Developed as part of Software Engineering academic coursework. For full academic documentation and statistical methodologies, refer to [AI_Warehouse_System_Project_Report.pdf](AI_Warehouse_System_Project_Report.pdf).
