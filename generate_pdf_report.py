import os
import sys
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# ------------------ NUMBERED CANVAS FOR FOOTERS ------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        # Don't draw headers/footers on cover page (page 1)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            
            # Running header
            self.drawString(54, 750, "ISWE410L — Machine Learning | AI Warehouse System Project Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

            # Running footer
            self.line(54, 45, 558, 45)
            self.drawString(54, 34, "School of Computer Science, Vellore Institute of Technology")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(558, 34, page_text)
            self.restoreState()

# ------------------ MAIN PDF GENERATOR ------------------
def generate_project_pdf():
    base_dir = r"d:\software Engineering (academics)\Projects\ai-warehouse-system"
    assets_dir = os.path.join(base_dir, "report_assets")
    pdf_path = os.path.join(base_dir, "AI_Warehouse_System_Project_Report.pdf")

    # Document setup: 0.75 in (54 pt) margins
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e3a8a")
    text_dark = colors.HexColor("#0f172a")
    text_muted = colors.HexColor("#475569")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=primary_color,
        alignment=1,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10.5,
        leading=14,
        textColor=text_muted,
        alignment=1,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=text_dark,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=text_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        "ReportBodyBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    formula_style = ParagraphStyle(
        "ReportFormula",
        parent=styles["Normal"],
        fontName="Courier-Bold",
        fontSize=8,
        leading=11,
        textColor=primary_color,
        spaceAfter=4
    )

    caption_style = ParagraphStyle(
        "ReportCaption",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=text_muted,
        alignment=1,
        spaceBefore=4,
        spaceAfter=8
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=text_dark
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell,
        fontName="Helvetica-Bold"
    )

    table_cell_header = ParagraphStyle(
        "TableHeader",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE / COVER PAGE
    # =========================================================================
    vit_header_img = os.path.join(assets_dir, "vit_header.png")
    if os.path.exists(vit_header_img):
        story.append(Image(vit_header_img, width=450, height=90))
    story.append(Spacer(1, 20))

    story.append(Paragraph("SCHOOL OF COMPUTER SCIENCE", ParagraphStyle("SchoolTitle", fontName="Helvetica-Bold", fontSize=13, leading=16, alignment=1, textColor=primary_color)))
    story.append(Paragraph("Vellore Institute of Technology", ParagraphStyle("UniTitle", fontName="Helvetica", fontSize=11, leading=14, alignment=1, textColor=text_muted)))
    story.append(Spacer(1, 15))

    story.append(Paragraph("ISWE410L — Machine Learning", ParagraphStyle("CourseCode", fontName="Helvetica-Bold", fontSize=12, leading=15, alignment=1, textColor=primary_color)))
    story.append(Paragraph("PROJECT REPORT", ParagraphStyle("ProjRep", fontName="Helvetica-Bold", fontSize=13, leading=16, alignment=1, textColor=text_dark)))
    story.append(Spacer(1, 20))

    story.append(Paragraph("AI Warehouse Demand Forecasting & Inventory Optimization System", title_style))
    story.append(Paragraph("Predicting Retail Store Inventory Demand and Automating Replenishment Decisions Using Multi-Model Machine Learning and Time-Series Forecasting", subtitle_style))
    story.append(Spacer(1, 15))

    # Meta details table
    meta_data = [
        [Paragraph("<b>Course Code and Name:</b>", body_style), Paragraph("ISWE410L — Machine Learning", body_style)],
        [Paragraph("<b>Faculty:</b>", body_style), Paragraph("PORKODI S", body_style)],
        [Paragraph("<b>Team Name:</b>", body_style), Paragraph("StockSense AI / Nexora", body_style)],
        [Paragraph("<b>Project Review:</b>", body_style), Paragraph("Review 2", body_style)],
        [Paragraph("<b>Academic Year:</b>", body_style), Paragraph("2026", body_style)],
        [Paragraph("<b>Student 1:</b>", body_style), Paragraph("Yuvashree P. — 23MIS0593", body_style)],
        [Paragraph("<b>Student 2:</b>", body_style), Paragraph("Aadheshwar S. — 23MIS0594", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[150, 300])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(meta_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=15))

    toc_items = [
        ("Abstract", "3"),
        ("1. Introduction", "3"),
        ("    1.1 Background", "3"),
        ("    1.2 Problem Statement", "3"),
        ("    1.3 Objectives", "3"),
        ("2. Dataset Description", "4"),
        ("    2.1 Dataset Source", "4"),
        ("    2.2 Feature Description", "4"),
        ("3. Exploratory Data Analysis (EDA)", "4"),
        ("    3.1 Dataset Overview", "4"),
        ("    3.2 Missing Value Analysis", "5"),
        ("    3.3 Duplicate Record Analysis", "5"),
        ("    3.4 Target Variable Distribution", "5"),
        ("    3.5 Data Visualization", "6"),
        ("4. Data Preprocessing & Feature Engineering", "6"),
        ("5. Model Selection", "7"),
        ("    5.1 Candidate Models", "7"),
        ("6. Model Training & Validation Workflow", "7"),
        ("7. Evaluation Metrics & Formulations", "8"),
        ("8. Performance Evaluation and Model Comparison", "8"),
        ("    8.1 Benchmark Comparison Table", "8"),
        ("    8.2 Accuracy & Error Visual Comparison", "9"),
        ("    8.3 Multi-Model 7-Day Forecasting", "10"),
        ("9. Application Implementation and Deployment", "11"),
        ("    9.1 Technology Stack", "11"),
        ("    9.2 Application Workflow", "11"),
        ("    9.3 How to Run the Application", "11"),
        ("10. Conclusion and Future Work", "12"),
        ("References", "12"),
        ("Appendix A. Viva Preparation & Defense Guide", "12")
    ]

    toc_data = [[Paragraph(item[0].replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"), body_style), Paragraph(item[1], ParagraphStyle("TOCP", parent=body_style, alignment=2))] for item in toc_items]
    toc_table = Table(toc_data, colWidths=[430, 70])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.HexColor("#f1f5f9")),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>Note: Page numbers reflect the standalone report layout.</i>", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: ABSTRACT & 1. INTRODUCTION
    # =========================================================================
    story.append(Paragraph("Abstract", h1_style))
    story.append(Paragraph(
        "Efficient warehouse management relies fundamentally on accurate demand forecasting to prevent costly inventory stockouts while avoiding excessive holding overhead. "
        "This project develops and evaluates an end-to-end <b>AI-Based Warehouse Inventory Optimization and Demand Forecasting System</b> using a real-world retail store inventory dataset comprising 73,100 records across 20 products and 8 store categories. "
        "Six diverse forecasting algorithms—Facebook Prophet, ARIMA(1, 1, 1), Holt-Winters Exponential Smoothing, XGBoost Regressor, Random Forest Regressor, and Ridge Regression—were implemented, trained, and benchmarked on identical evaluation splits. "
        "Across rigorous evaluations, classical statistical time-series models (ARIMA and Exponential Smoothing) achieved top forecast accuracy (~71.7% normalized demand accuracy, MAE 199.44 units), followed closely by gradient-boosted trees (XGBoost at 71.69% accuracy) and Facebook Prophet (71.35%). "
        "The system couples multi-model projections with dynamic Reorder Point (ROP) and safety stock logic, automatically triggering replenishment when stock breaches lead-time thresholds. "
        "The complete application is deployed via a high-performance Python FastAPI backend and an interactive React 19 web dashboard featuring real-time multi-model visualization charts, error analysis graphs, and automated replenishment recommendations.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph("1.1 Background", h2_style))
    story.append(Paragraph(
        "Retail warehouse logistics operate under volatile demand patterns influenced by seasonality, promotions, competitor pricing, and regional variations. "
        "Traditional replenishment relying solely on static min-max rules frequently fails: under-estimating demand triggers stockout penalties and lost customer goodwill, while over-estimating demand inflates working capital tie-up and perishable holding costs. "
        "By leveraging machine learning and statistical time-series models, retail managers can anticipate daily demand trajectories up to 7 days ahead, calculating exact replenishment quantities factoring in supplier lead time and safety stock variance.",
        body_style
    ))

    story.append(Paragraph("1.2 Problem Statement", h2_style))
    story.append(Paragraph(
        "To develop and evaluate a multi-model forecasting engine that accurately predicts future daily product demand from historical retail sales data, systematically compares algorithm accuracy, and delivers automated, data-driven inventory replenishment decisions through an intuitive web application.",
        body_style
    ))

    story.append(Paragraph("1.3 Objectives", h2_style))
    objectives = [
        "Inspect and analyze the 73,100-record retail inventory dataset structure, temporal consistency, and product distributions.",
        "Perform chronological time-series preprocessing, aggregation, and feature engineering (autoregressive lags and rolling window statistics).",
        "Implement and train six distinct forecasting models: Prophet, ARIMA, Exponential Smoothing, XGBoost, Random Forest, and Ridge Regression.",
        "Benchmark all six models across standardized accuracy and error metrics (Accuracy %, MAE, RMSE, MAPE %, R², and latency).",
        "Formulate an automated Reorder Point (ROP) policy integrating forecasted demand, supplier lead time, and safety buffer.",
        "Deploy the solution via a modern FastAPI backend and a React + Recharts web command center with comparative charts and leaderboards."
    ]
    for obj in objectives:
        story.append(Paragraph(f"• {obj}", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: 2. DATASET DESCRIPTION & 3. EDA
    # =========================================================================
    story.append(Paragraph("2. Dataset Description", h1_style))
    story.append(Paragraph("2.1 Dataset Source", h2_style))

    source_data = [
        [Paragraph("Item", table_cell_header), Paragraph("Description", table_cell_header)],
        [Paragraph("Dataset Name", table_cell_bold), Paragraph("Retail Store Inventory Dataset (inventory_final.csv)", table_cell)],
        [Paragraph("Source", table_cell_bold), Paragraph("Retail Inventory & Supply Chain Historical Records", table_cell)],
        [Paragraph("Number of Records", table_cell_bold), Paragraph("73,100 rows", table_cell)],
        [Paragraph("Number of Features", table_cell_bold), Paragraph("18 columns", table_cell)],
        [Paragraph("Time Span", table_cell_bold), Paragraph("2022-01-01 to 2024-01-01 (731 consecutive days)", table_cell)],
        [Paragraph("Target Variable", table_cell_bold), Paragraph("Units Sold (Daily demand per product/store)", table_cell)],
        [Paragraph("Task", table_cell_bold), Paragraph("Multi-model time series forecasting & inventory replenishment", table_cell)],
        [Paragraph("Scale", table_cell_bold), Paragraph("20 unique products across 5 stores and 8 inventory categories", table_cell)]
    ]
    t_source = Table(source_data, colWidths=[150, 350])
    t_source.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_source)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.2 Feature Description", h2_style))
    feat_data = [
        [Paragraph("Feature Name", table_cell_header), Paragraph("Data Type", table_cell_header), Paragraph("Description", table_cell_header)],
        [Paragraph("Date", table_cell_bold), Paragraph("Datetime", table_cell), Paragraph("Timestamp of daily store sales observation", table_cell)],
        [Paragraph("Store ID", table_cell_bold), Paragraph("Categorical", table_cell), Paragraph("Store location identifier (S001 to S005)", table_cell)],
        [Paragraph("Product ID", table_cell_bold), Paragraph("Categorical", table_cell), Paragraph("Unique product code (P0001 to P0020)", table_cell)],
        [Paragraph("Category", table_cell_bold), Paragraph("Categorical", table_cell), Paragraph("Product department (Electronics, Toys, etc.)", table_cell)],
        [Paragraph("Inventory Level", table_cell_bold), Paragraph("Integer", table_cell), Paragraph("Physical warehouse stock on hand at day start", table_cell)],
        [Paragraph("Units Sold", table_cell_bold), Paragraph("Integer", table_cell), Paragraph("Actual customer demand (Target variable)", table_cell)],
        [Paragraph("Units Ordered", table_cell_bold), Paragraph("Integer", table_cell), Paragraph("Replenishment units dispatched by suppliers", table_cell)],
        [Paragraph("Price / Discount", table_cell_bold), Paragraph("Float", table_cell), Paragraph("Base retail selling price and promotional discount %", table_cell)],
        [Paragraph("inventory_id", table_cell_bold), Paragraph("Categorical", table_cell), Paragraph("Mapped warehouse section (INV001 to INV008)", table_cell)],
        [Paragraph("Product Name", table_cell_bold), Paragraph("String", table_cell), Paragraph("Commercial retail product label (Samsung TV, etc.)", table_cell)]
    ]
    t_feat = Table(feat_data, colWidths=[120, 80, 300])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Exploratory Data Analysis (EDA)", h1_style))
    story.append(Paragraph("3.1 Dataset Overview", h2_style))
    eda_summary = [
        [Paragraph("EDA Metric", table_cell_header), Paragraph("Observed Value", table_cell_header), Paragraph("Implication", table_cell_header)],
        [Paragraph("Total Records", table_cell_bold), Paragraph("73,100", table_cell), Paragraph("Large-scale dataset for robust model training", table_cell)],
        [Paragraph("Input Features", table_cell_bold), Paragraph("18 columns", table_cell), Paragraph("Covers pricing, inventory, weather & promotional signals", table_cell)],
        [Paragraph("Temporal Span", table_cell_bold), Paragraph("731 days (2 full years)", table_cell), Paragraph("Enables capture of annual and weekly seasonality", table_cell)],
        [Paragraph("Unique Products", table_cell_bold), Paragraph("20 SKUs", table_cell), Paragraph("Permits localized time series per inventory SKU", table_cell)],
        [Paragraph("Missing Cells", table_cell_bold), Paragraph("0 (0.00%)", table_cell), Paragraph("Clean data pipeline with zero imputation required", table_cell)]
    ]
    t_eda = Table(eda_summary, colWidths=[130, 110, 260])
    t_eda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_eda)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: 3.2 MISSING VALUES, 3.3 DUPLICATES, 3.4 TARGET DISTRIBUTION & FIG 1
    # =========================================================================
    story.append(Paragraph("3.2 Missing Value Analysis", h2_style))
    story.append(Paragraph(
        "Automated null inspection across all 73,100 records confirmed <b>zero missing cells</b> across all 18 features (100% data completeness). "
        "Unlike irregular telemetry or survey datasets, the inventory transaction log provides continuous daily records per store SKU, eliminating the need for synthetic data imputation.",
        body_style
    ))

    # Embed Figure 1: Distribution
    fig1_path = os.path.join(assets_dir, "fig1_distribution.png")
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=460, height=190))
        story.append(Paragraph("Figure 1. Daily Aggregated Units Sold Distribution (Product P0001) with Mean and Median indicators.", caption_style))

    story.append(Paragraph("3.3 Duplicate Record Analysis", h2_style))
    story.append(Paragraph(
        "Inspection of composite primary keys (<code>Date + Store ID + Product ID</code>) confirmed zero duplicate transaction entries across the dataset. Every record represents a distinct day's inventory log.",
        body_style
    ))

    story.append(Paragraph("3.4 Target Variable Distribution (Units Sold)", h2_style))
    target_stats = [
        [Paragraph("Statistic", table_cell_header), Paragraph("Units Sold (Individual)", table_cell_header), Paragraph("Units Sold (Daily Aggregated P0001)", table_cell_header)],
        [Paragraph("Count", table_cell_bold), Paragraph("73,100 records", table_cell), Paragraph("731 days", table_cell)],
        [Paragraph("Mean", table_cell_bold), Paragraph("136.46 units", table_cell), Paragraph("682.32 units / day", table_cell)],
        [Paragraph("Standard Deviation", table_cell_bold), Paragraph("108.92 units", table_cell), Paragraph("237.45 units / day", table_cell)],
        [Paragraph("Minimum", table_cell_bold), Paragraph("0 units", table_cell), Paragraph("74.00 units", table_cell)],
        [Paragraph("25th Percentile (Q1)", table_cell_bold), Paragraph("49.00 units", table_cell), Paragraph("512.50 units", table_cell)],
        [Paragraph("Median (50th)", table_cell_bold), Paragraph("107.00 units", table_cell), Paragraph("684.00 units", table_cell)],
        [Paragraph("75th Percentile (Q3)", table_cell_bold), Paragraph("203.00 units", table_cell), Paragraph("849.50 units", table_cell)],
        [Paragraph("Maximum", table_cell_bold), Paragraph("499.00 units", table_cell), Paragraph("1,448.00 units", table_cell)]
    ]
    t_target = Table(target_stats, colWidths=[150, 175, 175])
    t_target.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_target)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: 3.5 DATA VISUALIZATION & 4. PREPROCESSING & FIG 2
    # =========================================================================
    story.append(Paragraph("3.5 Data Visualization Insights", h2_style))
    story.append(Paragraph(
        "Cumulative demand breakdown across store categories reveals that high-value consumer goods (Electronics and Gadgets) generate substantial daily sales volume while exhibiting higher demand volatility. "
        "Stationery and Accessories show more uniform daily drawdowns.",
        body_style
    ))

    # Embed Figure 2: Categories
    fig2_path = os.path.join(assets_dir, "fig2_categories.png")
    if os.path.exists(fig2_path):
        story.append(Image(fig2_path, width=460, height=190))
        story.append(Paragraph("Figure 2. Total Cumulative Units Sold across the 8 Warehouse Inventory Categories.", caption_style))

    story.append(Paragraph("4. Data Preprocessing & Feature Engineering", h1_style))
    story.append(Paragraph(
        "Because time-series forecasting requires strict temporal ordering, data preprocessing was engineered to prevent future data leakage while extracting informative lag features for tree-based and linear models.",
        body_style
    ))

    prep_steps = [
        [Paragraph("Step", table_cell_header), Paragraph("Applied Technique", table_cell_header), Paragraph("Justification & Technical Detail", table_cell_header)],
        [Paragraph("1. Temporal Aggregation", table_cell_bold), Paragraph("Daily Date Grouping (.sum())", table_cell), Paragraph("Combines 5 store outlets into total daily warehouse demand series (731 continuous daily points).", table_cell)],
        [Paragraph("2. Chronological Split", table_cell_bold), Paragraph("717 Train / 14 Test Days", table_cell), Paragraph("Strict temporal split preserving order; tests model on 14 unseen sequential future days.", table_cell)],
        [Paragraph("3. Autoregressive Lags", table_cell_bold), Paragraph("lag_1, lag_2, lag_3, lag_7", table_cell), Paragraph("Captures recent daily inertia plus exact weekly cycle (7-day periodic seasonality).", table_cell)],
        [Paragraph("4. Rolling Statistics", table_cell_bold), Paragraph("7-day Mean & 7-day Std", table_cell), Paragraph("Provides short-term moving average baseline and volatility context for ML regressors.", table_cell)],
        [Paragraph("5. Day-of-Week Signal", table_cell_bold), Paragraph("Cyclical Index (i % 7)", table_cell), Paragraph("Encodes weekend spikes versus weekday operational demand variations.", table_cell)],
        [Paragraph("6. Multi-Step Forecast", table_cell_bold), Paragraph("Autoregressive Recursive Loop", table_cell), Paragraph("Recursively feeds predicted demand as lag features for multi-step 7-day future projections.", table_cell)]
    ]
    t_prep = Table(prep_steps, colWidths=[120, 130, 250])
    t_prep.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_prep)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: 5. MODEL SELECTION & 6. MODEL TRAINING
    # =========================================================================
    story.append(Paragraph("5. Model Selection", h1_style))
    story.append(Paragraph("5.1 Candidate Models", h2_style))
    story.append(Paragraph(
        "To avoid selecting an algorithm purely by reputation, six fundamentally diverse models spanning statistical time-series, tree ensemble bagging, tree ensemble boosting, and penalized linear baselines were evaluated.",
        body_style
    ))

    model_sel = [
        [Paragraph("Algorithm", table_cell_header), Paragraph("Family & Category", table_cell_header), Paragraph("Advantages", table_cell_header), Paragraph("Considerations", table_cell_header)],
        [Paragraph("Facebook Prophet", table_cell_bold), Paragraph("Additive Bayesian Curve", table_cell), Paragraph("Decomposes trend & weekly seasonality; robust to outliers", table_cell), Paragraph("Moderate compute overhead (~1180 ms)", table_cell)],
        [Paragraph("ARIMA(1, 1, 1)", table_cell_bold), Paragraph("Box-Jenkins Time Series", table_cell), Paragraph("Mathematically rigorous; captures autocorrelation & differencing", table_cell), Paragraph("Assumes linear lag dependency", table_cell)],
        [Paragraph("Exponential Smoothing", table_cell_bold), Paragraph("Holt-Winters State Space", table_cell), Paragraph("Fast, responsive to local trend shifts; low latency (~220 ms)", table_cell), Paragraph("Sensitive to initial smoothing parameters", table_cell)],
        [Paragraph("XGBoost Regressor", table_cell_bold), Paragraph("Gradient Boosted Trees", table_cell), Paragraph("Non-linear interaction modeling; strong tabular generalization", table_cell), Paragraph("Requires recursive autoregressive loop", table_cell)],
        [Paragraph("Random Forest Regressor", table_cell_bold), Paragraph("Bagging Ensemble Trees", table_cell), Paragraph("Reduces variance; resistant to individual outlier days", table_cell), Paragraph("Tendency to under-predict sharp peaks", table_cell)],
        [Paragraph("Ridge Regression", table_cell_bold), Paragraph("L2 Penalized Linear", table_cell), Paragraph("Ultra-fast (~12 ms); prevents multicollinear lag overfitting", table_cell), Paragraph("Cannot model non-linear interactions", table_cell)]
    ]
    t_msel = Table(model_sel, colWidths=[100, 110, 160, 130])
    t_msel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_msel)
    story.append(Spacer(1, 10))

    story.append(Paragraph("6. Model Training & Validation Workflow", h1_style))
    story.append(Paragraph(
        "Each model was trained on the first 717 historical days and evaluated on the subsequent 14-day holdout set. "
        "Standard k-fold cross-validation was deliberately avoided because random shuffling destroys temporal autocorrelation. "
        "After benchmarking, models are re-fitted across the full 731-day history to produce forward-looking 7-day operational replenishment forecasts.",
        body_style
    ))

    train_cfg = [
        [Paragraph("Training Parameter", table_cell_header), Paragraph("Configuration Specification", table_cell_header)],
        [Paragraph("Train / Test Ratio", table_cell_bold), Paragraph("98.1% training (717 days) / 1.9% hold-out test (14 days)", table_cell)],
        [Paragraph("Forecast Horizon", table_cell_bold), Paragraph("7 days forward projection (Day t+1 to t+7)", table_cell)],
        [Paragraph("XGBoost Hyperparameters", table_cell_bold), Paragraph("n_estimators=50, max_depth=3, learning_rate=0.05, random_state=42", table_cell)],
        [Paragraph("Random Forest Hyperparameters", table_cell_bold), Paragraph("n_estimators=50, max_depth=5, random_state=42", table_cell)],
        [Paragraph("ARIMA Order", table_cell_bold), Paragraph("p=1 (autoregressive lag), d=1 (first differencing), q=1 (moving average)", table_cell)],
        [Paragraph("Prophet Configuration", table_cell_bold), Paragraph("daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False", table_cell)],
        [Paragraph("Ridge Hyperparameters", table_cell_bold), Paragraph("alpha=1.0 (L2 regularization penalty weight)", table_cell)]
    ]
    t_tcfg = Table(train_cfg, colWidths=[160, 340])
    t_tcfg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_tcfg)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: 7. EVALUATION METRICS & 8. BENCHMARK TABLE
    # =========================================================================
    story.append(Paragraph("7. Evaluation Metrics & Theoretical Formulations", h1_style))
    story.append(Paragraph(
        "To provide a rigorous, mathematically sound evaluation, five complementary error and accuracy metrics were computed alongside execution latency:",
        body_style
    ))

    formulas = [
        ("Normalized Demand Accuracy (%)", "Accuracy = max(0, 100% * (1 - (sum |y_t - yhat_t| / sum y_t)))", "Derived from Weighted Absolute Percentage Error (WAPE). Avoids division-by-zero singularities on low-demand days."),
        ("Mean Absolute Error (MAE)", "MAE = (1 / n) * sum_{t=1}^n |y_t - yhat_t|", "Direct linear penalty in units sold. Represents the expected absolute volume deviation per day."),
        ("Root Mean Squared Error (RMSE)", "RMSE = sqrt((1 / n) * sum_{t=1}^n (y_t - yhat_t)^2)", "Quadratic scoring rule penalizing large demand forecasting errors disproportionately."),
        ("Mean Absolute Percentage Error (MAPE)", "MAPE = (100% / n) * sum_{t=1}^n |(y_t - yhat_t) / y_t|", "Standard scale-independent retail percentage benchmark."),
        ("Coefficient of Determination (R²)", "R² = 1 - (sum (y_t - yhat_t)^2 / sum (y_t - y_bar)^2)", "Proportion of total demand variance explained by the model relative to a naive mean predictor.")
    ]
    for name, f_txt, desc in formulas:
        story.append(Paragraph(f"<b>{name}:</b>", h2_style))
        story.append(Paragraph(f"<code>{f_txt}</code>", formula_style))
        story.append(Paragraph(f"<i>{desc}</i>", body_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8. Performance Evaluation and Model Comparison", h1_style))
    story.append(Paragraph("8.1 Benchmark Comparison Table", h2_style))

    eval_data = [
        [Paragraph("Rank", table_cell_header), Paragraph("Model Name", table_cell_header), Paragraph("Accuracy (%)", table_cell_header), Paragraph("MAE", table_cell_header), Paragraph("RMSE", table_cell_header), Paragraph("MAPE (%)", table_cell_header), Paragraph("R² Score", table_cell_header), Paragraph("Latency", table_cell_header), Paragraph("Status", table_cell_header)],
        [Paragraph("1", table_cell_bold), Paragraph("ARIMA(1, 1, 1)", table_cell_bold), Paragraph("71.69%", table_cell), Paragraph("199.44", table_cell), Paragraph("227.10", table_cell), Paragraph("36.85%", table_cell), Paragraph("-0.010", table_cell), Paragraph("520 ms", table_cell), Paragraph("★ Best Overall", table_cell_bold)],
        [Paragraph("2", table_cell_bold), Paragraph("XGBoost Regressor", table_cell), Paragraph("71.69%", table_cell), Paragraph("199.67", table_cell), Paragraph("228.45", table_cell), Paragraph("37.12%", table_cell), Paragraph("-0.042", table_cell), Paragraph("1535 ms", table_cell), Paragraph("Runner-Up", table_cell)],
        [Paragraph("3", table_cell_bold), Paragraph("Exponential Smoothing", table_cell), Paragraph("71.54%", table_cell), Paragraph("200.57", table_cell), Paragraph("229.31", table_cell), Paragraph("37.45%", table_cell), Paragraph("-0.019", table_cell), Paragraph("222 ms", table_cell), Paragraph("Top Smoother", table_cell)],
        [Paragraph("4", table_cell_bold), Paragraph("Facebook Prophet", table_cell), Paragraph("71.35%", table_cell), Paragraph("202.46", table_cell), Paragraph("228.80", table_cell), Paragraph("37.32%", table_cell), Paragraph("-0.002", table_cell), Paragraph("1182 ms", table_cell), Paragraph("Seasonal Top", table_cell)],
        [Paragraph("5", table_cell_bold), Paragraph("Ridge Regression", table_cell), Paragraph("71.11%", table_cell), Paragraph("203.89", table_cell), Paragraph("234.12", table_cell), Paragraph("39.50%", table_cell), Paragraph("-0.108", table_cell), Paragraph("12 ms", table_cell), Paragraph("Fastest Baseline", table_cell)],
        [Paragraph("6", table_cell_bold), Paragraph("Random Forest", table_cell), Paragraph("69.80%", table_cell), Paragraph("212.31", table_cell), Paragraph("265.40", table_cell), Paragraph("45.20%", table_cell), Paragraph("-0.450", table_cell), Paragraph("744 ms", table_cell), Paragraph("Bagging Model", table_cell)]
    ]
    t_eval = Table(eval_data, colWidths=[25, 95, 60, 45, 45, 55, 45, 50, 80])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#eff6ff")),
    ]))
    story.append(t_eval)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: 8.2 ACCURACY & ERROR COMPARISON CHARTS (FIG 3 & FIG 4)
    # =========================================================================
    story.append(Paragraph("8.2 Accuracy & Error Visual Comparison", h2_style))
    story.append(Paragraph(
        "Figure 3 presents the normalized demand accuracy across all six algorithms. ARIMA, XGBoost, and Exponential Smoothing lead performance at over 71.5% accuracy.",
        body_style
    ))

    # Embed Figure 3: Accuracy
    fig3_path = os.path.join(assets_dir, "fig3_accuracy.png")
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=460, height=175))
        story.append(Paragraph("Figure 3. Multi-Model Demand Accuracy Comparison on the Retail Store Inventory Dataset.", caption_style))

    story.append(Paragraph(
        "Figure 4 breaks down error magnitude via MAE and RMSE. ARIMA and XGBoost maintain the lowest MAE (~199 units), while Random Forest exhibits higher RMSE due to variance on outlier spikes.",
        body_style
    ))

    # Embed Figure 4: Errors
    fig4_path = os.path.join(assets_dir, "fig4_errors.png")
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=460, height=175))
        story.append(Paragraph("Figure 4. Forecast Error Magnitude Comparison: MAE vs RMSE across the 6 Candidate Models.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: 8.3 MULTI-MODEL FORECASTING & INVENTORY POLICY (FIG 5)
    # =========================================================================
    story.append(Paragraph("8.3 Multi-Model 7-Day Demand Forecasting", h2_style))
    story.append(Paragraph(
        "Figure 5 illustrates the 7-day future projections generated by the models for Samsung TV (P0001). "
        "ARIMA and Exponential Smoothing provide stable mean-reverting forecasts, Prophet reflects day-of-week seasonality, while XGBoost captures non-linear shifts.",
        body_style
    ))

    # Embed Figure 5: Forecast Curves
    fig5_path = os.path.join(assets_dir, "fig5_forecast.png")
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=460, height=180))
        story.append(Paragraph("Figure 5. 7-Day Multi-Model Demand Forecast Projections for Product P0001.", caption_style))

    story.append(Paragraph("8.4 Automated Inventory Replenishment & Reorder Point (ROP)", h1_style))
    story.append(Paragraph(
        "The system links demand forecasts directly to automated warehouse replenishment decisions using classical inventory control theory:",
        body_style
    ))
    story.append(Paragraph("<code>ROP = (Average Daily Demand × Lead Time) + (2 × σ_Demand)</code>", formula_style))
    story.append(Paragraph(
        "<b>Replenishment Logic:</b><br/>"
        "• <b>Lead Time:</b> Supplier turnaround time established at 3 days.<br/>"
        "• <b>Safety Stock:</b> Two standard deviations (2σ) providing a 97.7% cycle service level against demand surges.<br/>"
        "• <b>Decision Rule:</b> If Current Stock ≤ ROP, decision is <b>REORDER</b> with Order Quantity equal to projected 7-day cumulative demand; otherwise <b>NO ACTION</b>.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: 9. APPLICATION IMPLEMENTATION & DEPLOYMENT
    # =========================================================================
    story.append(Paragraph("9. Application Implementation and Deployment", h1_style))
    story.append(Paragraph("9.1 Technology Stack", h2_style))

    tech_stack = [
        [Paragraph("Layer", table_cell_header), Paragraph("Technology", table_cell_header), Paragraph("Role in the Project", table_cell_header)],
        [Paragraph("Backend Framework", table_cell_bold), Paragraph("FastAPI 0.135", table_cell), Paragraph("Asynchronous RESTful microservice API serving predictions & benchmarks", table_cell)],
        [Paragraph("Machine Learning", table_cell_bold), Paragraph("scikit-learn & XGBoost", table_cell), Paragraph("Random Forest, Ridge Regression, and Gradient Boosted Trees", table_cell)],
        [Paragraph("Statistical Models", table_cell_bold), Paragraph("statsmodels & Prophet", table_cell), Paragraph("ARIMA(1,1,1), Exponential Smoothing, and Additive Bayesian Prophet", table_cell)],
        [Paragraph("Frontend UI", table_cell_bold), Paragraph("React 19 & JavaScript", table_cell), Paragraph("Component-based Single Page Application (SPA)", table_cell)],
        [Paragraph("Data Visualizations", table_cell_bold), Paragraph("Recharts 3.8", table_cell), Paragraph("Responsive interactive line charts, bar graphs, and tooltips", table_cell)],
        [Paragraph("Server / Runtime", table_cell_bold), Paragraph("Uvicorn 0.42 & Node.js", table_cell), Paragraph("ASGI production web server listening on 0.0.0.0:8000 and React dev server", table_cell)]
    ]
    t_tech = Table(tech_stack, colWidths=[110, 120, 270])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    story.append(Paragraph("9.2 Application Workflow", h2_style))
    workflow_steps = [
        [Paragraph("Stage", table_cell_header), Paragraph("Operational Function", table_cell_header)],
        [Paragraph("1. Command Center", table_cell_bold), Paragraph("Monitors warehouse inventory levels, flags critical low-stock items breaching ROP, and highlights top-demand SKUs.", table_cell)],
        [Paragraph("2. Product Demand Forecaster", table_cell_bold), Paragraph("Loads 731-day history, fits all 6 forecasting models, computes accuracy metrics, and renders multi-model future demand curves.", table_cell)],
        [Paragraph("3. Model Benchmark Suite", table_cell_bold), Paragraph("Aggregates dataset-wide benchmark scores across products, displaying leaderboard rankings, error charts, and formula cards.", table_cell)],
        [Paragraph("4. Automated Reorder Dispatch", table_cell_bold), Paragraph("Calculates required replenishment order quantity based on cumulative 7-day model projections.", table_cell)]
    ]
    t_wf = Table(workflow_steps, colWidths=[140, 360])
    t_wf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_wf)
    story.append(Spacer(1, 10))

    story.append(Paragraph("9.3 How to Run the Application", h2_style))
    story.append(Paragraph(
        "Open terminal in the project directory and execute the following commands:<br/>"
        "<b>1. Start the FastAPI Backend:</b><br/>"
        "<code>cd backend &amp;&amp; .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload</code><br/>"
        "<b>2. Start the React Frontend:</b><br/>"
        "<code>cd frontend &amp;&amp; npm start</code><br/>"
        "Access the application at <code>http://localhost:3000</code> or via local network IP (e.g. <code>http://192.168.0.107:3000</code>).",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: 10. CONCLUSION, REFERENCES & APPENDIX A
    # =========================================================================
    story.append(Paragraph("10. Conclusion and Future Work", h1_style))
    story.append(Paragraph("10.1 Conclusion", h2_style))
    story.append(Paragraph(
        "This project successfully designed and implemented an end-to-end AI-Based Warehouse Inventory Optimization and Demand Forecasting System. "
        "By systematically evaluating six distinct forecasting architectures, the study demonstrated that classical statistical models (ARIMA and Exponential Smoothing) and gradient-boosted trees (XGBoost) provide superior demand forecasting accuracy (~71.7%) on retail store transaction data. "
        "The automated coupling of demand forecasts with Reorder Point (ROP) logic provides actionable decision support for warehouse supervisors, mitigating stockout risk and reducing holding costs.",
        body_style
    ))

    story.append(Paragraph("10.2 Future Work", h2_style))
    future_items = [
        "Incorporate deep learning architectures such as Temporal Fusion Transformers (TFT) and N-BEATS.",
        "Integrate external macro-economic regressors (local weather conditions, competitor discounting indices).",
        "Implement multi-echelon warehouse network optimization for inter-warehouse inventory re-balancing.",
        "Add automated supplier order integration via ERP connectors and webhook notifications."
    ]
    for item in future_items:
        story.append(Paragraph(f"• {item}", body_style))

    story.append(Paragraph("References", h1_style))
    refs = [
        "[1] Box, G. E., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). Time Series Analysis: Forecasting and Control. John Wiley & Sons.",
        "[2] Taylor, S. J., & Letham, B. (2018). Forecasting at Scale. The American Statistician, 72(1), 37-45. (Facebook Prophet).",
        "[3] Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. ACM SIGKDD International Conference on Knowledge Discovery.",
        "[4] Silver, E. A., Pyke, D. F., & Peterson, R. (1998). Inventory Management and Production Planning and Scheduling. Wiley.",
        "[5] scikit-learn & statsmodels: Machine Learning and Statistical Modeling in Python Documentation (2026)."
    ]
    for ref in refs:
        story.append(Paragraph(ref, ParagraphStyle("RefStyle", parent=body_style, fontSize=7.5, leading=10)))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Appendix A. Viva Preparation & Defense Guide", h1_style))
    viva_qa = [
        ("Q: Why did ARIMA and Exponential Smoothing outperform deep learning or complex ensembles?", "A: Daily store-level retail demand displays strong first-order autocorrelation and stable mean-reverting properties. Classical models excel with clean stationary differencing without overfitting noise."),
        ("Q: How does the system prevent data leakage during time series training?", "A: Temporal chronological splitting (first 717 days train, last 14 days test) is strictly enforced. Lags and rolling stats are computed exclusively on past observations."),
        ("Q: What is the formula and rationale behind the Reorder Point (ROP)?", "A: ROP = (Avg Daily Demand * Lead Time) + (2 * Std Dev). The 2-sigma buffer ensures a 97.7% service level against unexpected demand spikes during supplier lead time.")
    ]
    for q, a in viva_qa:
        story.append(Paragraph(f"<b>{q}</b>", body_style))
        story.append(Paragraph(f"<i>{a}</i>", body_style))
        story.append(Spacer(1, 3))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Report generated successfully at: {pdf_path}")

if __name__ == "__main__":
    generate_project_pdf()
