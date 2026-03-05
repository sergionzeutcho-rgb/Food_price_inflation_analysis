# ![CI logo](https://codeinstitute.s3.amazonaws.com/fullstack/ci_logo_small.png)

# Food Price Inflation Analysis

## Team Members

This project was developed as part of a Code Institute Hackathon by:

| Name | Role |
|------|------|
| **Florence** | Hypothesis Testing, Documentation & Power BI |
| **Gia** | Streamlit Dashboard, Hypothesis Testing & Project Board |
| **Sergio** | Streamlit Dashboard, Machine Learning & Hypothesis Testing |

**Streamlit Dashboard Live link**: [Live App](https://food-prices-inflation-a5cfe8052e3a.herokuapp.com/)

**Power BI Dasboard Live link**: [Power BI Link](https://app.powerbi.com/groups/me/reports/891a4da5-dcf0-4de5-98ec-5659a0854c47/cfe237a79690ad3488a2?experience=power-bi)

**Slides Presentation Video link**: [Video](https://docs.google.com/videos/d/1pK4ZvWCtVdnW7txnMlWDXatMUNgdfZgka9LfnycS__4/edit?usp=sharing)

---

## Project Overview

This project analyses global food price inflation trends using the World Real-Time Food Prices (RTFP) dataset. The analysis aims to understand how food prices have evolved across different countries over time, identify patterns in inflation, and provide actionable insights for stakeholders.

### Business Problem

Food price inflation significantly impacts economies and household budgets worldwide. Understanding these trends helps policymakers, businesses, and consumers make informed decisions. This project addresses:
- How have food prices changed across different regions?
- What are the key drivers of food price inflation?
- Can we identify patterns or predict future trends?

---

## Table of Contents

1. [Dataset Information](#dataset-information)
2. [Project Objectives](#project-objectives)
3. [Methodology](#methodology)
4. [Project Structure](#project-structure)
5. [ETL Pipeline](#etl-pipeline)
6. [Data Analysis](#data-analysis)
7. [Visualisations](#visualisations)
8. [Key Findings](#key-findings)
9. [Ethical Considerations](#ethical-considerations)
10. [Installation & Setup](#installation--setup)
11. [Technologies Used](#technologies-used)
12. [Future Improvements](#future-improvements)
13. [Credits & References](#credits--references)

---

## Dataset Information

**Source**: World Bank - Real-Time Food Prices (RTFP)  
**File**: `data/raw/WLD_RTFP_country_2023-10-02.csv`  
**Time Period**: January 2007 - October 2023  
**Records**: 4,798 observations  

### Variables

| Variable | Description | Type |
|----------|-------------|------|
| Open | Opening price index for the month | Float |
| High | Highest price index for the month | Float |
| Low | Lowest price index for the month | Float |
| Close | Closing price index for the month | Float |
| Inflation | Year-over-year inflation rate (%) | Float |
| country | Country name | String |
| ISO3 | ISO 3166-1 alpha-3 country code | String |
| date | Date of observation (monthly) | Date |

---

## Project Objectives

### Primary Objectives
1. **Analyse global food price trends** across multiple countries and time periods
2. **Identify inflation patterns** and their correlation with price movements
3. **Develop statistical insights** to understand price volatility
4. **Create visualisations** that communicate findings to diverse audiences

### Learning Outcomes Addressed
- LO1: Apply core principles of statistics and probability
- LO2: Demonstrate practical data manipulation skills with Python
- LO3: Analyse real-world problems using data analytics
- LO4: Utilise Jupyter Notebooks enhanced by AI assistance
- LO5: Implement effective data management practices
- LO6: Address ethical considerations in data analytics
- LO7: Design independent research methodology
- LO8: Communicate complex insights effectively
- LO9: Apply data analytics across domains
- LO10: Plan and evaluate data analytics projects
- LO11: Adapt to new tools and methodologies

---

## Methodology

### Research Approach
This project follows the **CRISP-DM (Cross-Industry Standard Process for Data Mining)** methodology:

1. **Business Understanding**: Define the problem and objectives
2. **Data Understanding**: Explore and assess the dataset
3. **Data Preparation**: Clean, transform, and prepare data
4. **Modeling**: Apply statistical analysis and hypothesis testing
5. **Evaluation**: Assess results and validate findings
6. **Deployment**: Create visualisations and documentation

### Hypothesis Testing

**H1**: Food price inflation varies significantly across different regions

**H2**: Price volatility (High-Low range) correlates with inflation rates

**H3**: There are seasonal patterns in food price movements

**H4**: Food prices have increased significantly over time (2007-2023)

**H5**: Machine learning models can reasonably forecast short-term inflation trends

---

## Project Structure

```
Food_price_inflation_analysis/
│
├── data/
│   ├── raw/                                        # Original, immutable data
│   │   └── WLD_RTFP_country_2023-10-02.csv
│   └── cleaned/                                    # Processed, analysis-ready data
│       └── food_prices_cleaned.csv
│
├── images/                                         # Power BI dashboard screenshots
│   ├── Executive Overview.png
│   ├── Forecast Actual vs Predicted.png
│   └── Volatility & Country Inflation.png
│
├── jupyter_notebooks/
│   ├── Data_Cleaning.ipynb                         # ETL pipeline & data preprocessing
│   ├── Data_Analysis.ipynb                         # EDA & statistical analysis
│   ├── Hypothesis_Testing.ipynb                    # H1–H5 statistical tests
│   ├── ML_Predictions.ipynb                        # Model training, evaluation & export
│   └── predicted_inflation.csv                     # Exported prediction results
│
├── outputs/
│   ├── figures/                                    # Charts generated by notebooks
│   │   ├── actual_vs_predicted.png
│   │   ├── correlation_matrix.png
│   │   ├── country_comparison.png
│   │   ├── distribution_analysis.png
│   │   ├── feature_importance.png
│   │   ├── h1_regional_inflation.png
│   │   ├── h2_volatility_inflation.png
│   │   ├── h3_seasonal_inflation.png
│   │   ├── h4_price_trend.png
│   │   ├── h5_arima_forecast.png
│   │   ├── ml_model_comparison.png
│   │   ├── seasonal_analysis.png
│   │   └── time_series_analysis.png
│   ├── models/                                     # Serialised ML model artefacts
│   │   ├── best_model.joblib
│   │   ├── country_encoder.joblib
│   │   ├── feature_columns.joblib
│   │   └── feature_scaler.joblib
│   └── reports/                                    # Summary CSVs from analysis
│       ├── hypothesis_test_results.csv
│       └── ml_model_comparison.csv
│
├── Power Bi/
│   └── Food Price Inflation Analysis.pbix          # Power BI interactive report
│
├── powerbi Images/
│   └── Images.pdf                                  # Power BI visuals export
│
├── app.py                                          # Streamlit web dashboard (8 pages)
├── .gitignore
├── .python-version
├── .slugignore
├── Procfile                                        # Heroku deployment config
├── README.md
├── requirements.txt
└── setup.sh
```

---

## ETL Pipeline

### Extract
- Loaded raw CSV data from World Bank RTFP dataset
- Verified data integrity and structure

### Transform
- Converted date columns to datetime format
- Handled missing values in inflation column (364 records with NaN)
- Renamed columns to snake_case for consistency
- Created derived features:
  - `price_range`: High - Low (volatility indicator)
  - `price_change`: Close - Open
  - `price_change_pct`: Percentage change within period
  - `year`, `month`, `quarter`: Temporal decomposition

### Load
- Saved cleaned data to `data/cleaned/food_prices_cleaned.csv`
- Maintained data lineage documentation

### Validation Checks
- ✅ No negative prices detected
- ✅ High >= Low consistency verified
- ✅ No duplicate records found
- ✅ Date range: 2007-01-01 to 2023-10-01

---

## Data Analysis

### Statistical Summary

| Metric | Description |
|--------|-------------|
| Countries | 25 unique countries analysed |
| Time Span | 16+ years of monthly data |
| Inflation Range | -31.37% to 96.79% |

### Key Analyses Performed
1. **Descriptive Statistics**: Central tendency, dispersion measures
2. **Time Series Analysis**: Trend identification, seasonality
3. **Correlation Analysis**: Price-inflation relationships
4. **Comparative Analysis**: Cross-country comparisons

#### Sample Visualisations from the Analysis

<p align="center">
  <img src="outputs/figures/distribution_analysis.png" alt="Distribution Analysis" width="700"/>
  <br><em>Distribution of key price and inflation variables</em>
</p>

<p align="center">
  <img src="outputs/figures/correlation_matrix.png" alt="Correlation Matrix" width="700"/>
  <br><em>Correlation heatmap showing relationships between price indicators and inflation</em>
</p>

<p align="center">
  <img src="outputs/figures/time_series_analysis.png" alt="Time Series Analysis" width="700"/>
  <br><em>Food price trends over time (2007–2023)</em>
</p>

<p align="center">
  <img src="outputs/figures/country_comparison.png" alt="Country Comparison" width="700"/>
  <br><em>Comparative food price inflation across countries</em>
</p>

<p align="center">
  <img src="outputs/figures/seasonal_analysis.png" alt="Seasonal Analysis" width="700"/>
  <br><em>Seasonal patterns in food price movements</em>
</p>

---

## Visualisations

This project delivers **two complementary dashboards** built for different audiences:

### 🖥️ Streamlit Web Dashboard (`app.py`)
An interactive Python-powered web app with 8 pages, deployed via Heroku.

| Page | Description |
|------|-------------|
| Overview | Key metrics, price trend chart, quick actions |
| Data Cleaning | ETL process walkthrough with code snippets |
| Data Analysis | Distribution, correlation heatmap, seasonal & country charts |
| Hypothesis Testing | Live H1–H5 statistical tests with dynamic results |
| ML Predictions | Model comparison, feature importance, performance metrics |
| Prediction Tool | Quick & custom inflation forecasting with risk gauge |
| Country Explorer | Per-country stats, trend chart, and CSV export |
| About | Team cards, CRISP-DM methodology, data sources |

**Key features:** sidebar filters (country, year), Key Takeaway insight boxes, "What does this mean?" interpretation panels, risk badges (Low / Medium / High), and 24-month historical charts with forecast overlay.

### 📊 Power BI Dashboard (`Power Bi/Food Price Inflation Analysis.pbix`)
A standalone interactive report built in Power BI Desktop, designed for business stakeholders.[Power BI Link](https://app.powerbi.com/groups/me/reports/891a4da5-dcf0-4de5-98ec-5659a0854c47/cfe237a79690ad3488a2?experience=power-bi)

- Country and year slicers for cross-filtering
- Inflation trend line charts by region
- Comparative country performance visuals
- Volatility and price range analysis
- KPI cards for key summary statistics

## Executive Dashboard
An overview of global food inflation trends, highlighting overall price movements, key summary metrics, and country slicers

<p align="center">
  <img src="images/Executive Overview.png" width="700">
</p>

### Volatility Analysis (H1 & H2)
Visual analysis of how inflation varies across countries and the relationship between price volatility and inflation levels.
<p align="center">
  <img src="images/Volatility & Country Inflation.png" width="700">
</p>

### Forecast Validation (H5)
Comparison of actual and predicted inflation values to evaluate the forecasting model’s short-term predictive performance.

<p align="center">
  <img src="images/Forecast Actual vs Predicted.png" width="700">
</p>


---

## Key Findings

### Statistical Test Results

| Hypothesis | Test Used | p-value | Result |
|------------|-----------|---------|--------|
| **H1:** Countries have different inflation rates | Kruskal-Wallis | < 0.05 | ✅ Significant |
| **H2:** Volatility is related to inflation | Spearman Correlation | < 0.05 | ✅ Significant |
| **H3:** Seasonal patterns exist in inflation | Kruskal-Wallis | 1.00 | ❌ Not Significant |
| **H4:** Prices have increased over time | Mann-Whitney U | < 0.05 | ✅ Significant |
| **H5:** Time-series models can forecast short-term trends | ARIMA(1,1,1) | RMSE = 10.29, MAE = 8.93 | ✅ Partially Supported |

#### Hypothesis Test Visualisations

<p align="center">
  <img src="outputs/figures/h1_regional_inflation.png" alt="H1: Regional Inflation" width="700"/>
  <br><em>H1: Regional inflation distribution, showing significant differences across countries</em>
</p>

<p align="center">
  <img src="outputs/figures/h2_volatility_inflation.png" alt="H2: Volatility vs Inflation" width="700"/>
  <br><em>H2: Price volatility (High−Low range) vs inflation rate</em>
</p>

<p align="center">
  <img src="outputs/figures/h3_seasonal_inflation.png" alt="H3: Seasonal Inflation" width="700"/>
  <br><em>H3: Seasonal patterns in food price inflation</em>
</p>

<p align="center">
  <img src="outputs/figures/h4_price_trend.png" alt="H4: Long-term Price Trend" width="700"/>
  <br><em>H4: Long-term upward trend in food prices (2007–2023)</em>
</p>

<p align="center">
  <img src="outputs/figures/h5_arima_forecast.png" alt="H5: ARIMA Forecast" width="700"/>
  <br><em>H5: ARIMA(1,1,1) forecast vs actual inflation on 12-month holdout</em>
</p>

### Key Insights

1. **Regional Disparities**: Food price inflation varies significantly across countries, indicating that local factors (supply chains, policies, climate) play a crucial role
2. **Volatility-Inflation Link**: Higher price volatility is associated with higher inflation rates, suggesting that price stabilisation policies could help control inflation
3. **Long-term Upward Trend**: Food prices have significantly increased from 2007 to 2023, raising concerns about food affordability globally
4. **Predictive Potential**: Machine learning models can forecast inflation trends with reasonable accuracy, enabling proactive policy responses
5. **ARIMA Forecasting**: The ARIMA(1,1,1) model captures time dependency and general trend direction, but forecasting accuracy is moderate due to structural volatility and post-2020 inflation shocks.

#### Machine Learning Visualisations

<p align="center">
  <img src="outputs/figures/ml_model_comparison.png" alt="ML Model Comparison" width="700"/>
  <br><em>Model performance comparison: R² scores across candidate algorithms</em>
</p>

<p align="center">
  <img src="outputs/figures/feature_importance.png" alt="Feature Importance" width="700"/>
  <br><em>Feature importance from the best-performing model</em>
</p>

<p align="center">
  <img src="outputs/figures/actual_vs_predicted.png" alt="Actual vs Predicted" width="700"/>
  <br><em>Actual vs predicted inflation: model validation</em>
</p>

---

## Ethical Considerations

### Data Privacy & Governance
- **Data Source**: Publicly available World Bank dataset
- **No PII**: Dataset contains aggregate economic indicators only
- **Transparency**: All data sources and transformations documented
- **Reproducibility**: Analysis can be fully reproduced from raw data

### GDPR & Data Protection Compliance
This project is fully compliant with the **General Data Protection Regulation (GDPR)** and broader data protection principles:

- **No personal data processed**: The dataset contains only aggregate, country-level economic indicators. No individual-level data, names, addresses, or other personally identifiable information (PII) is collected, stored, or processed at any stage of the pipeline.
- **Lawful basis**: All data is sourced from the World Bank's publicly available open data portal, released under a permissive licence for research and educational use.
- **Data minimisation**: Only the variables necessary for the analysis objectives are retained. No surplus data is collected or stored beyond what is required.
- **Storage & retention**: Raw and cleaned datasets are stored locally within the project repository. No data is transmitted to external servers beyond the Heroku deployment, which serves only the Streamlit dashboard (no database or user tracking).
- **No automated decision-making**: The machine learning predictions are provided for informational and educational purposes only. No automated decisions affecting individuals are made based on model outputs.
- **Right to transparency**: This README, the Jupyter notebooks, and the dashboard itself document every data transformation, statistical test, and modelling decision, ensuring full auditability.

### Data Ethics Management
- **Bias awareness**: Country-level aggregation may mask within-country inequalities. Findings should not be used to stereotype nations or populations.
- **Responsible communication**: Statistical results are presented with appropriate caveats, confidence levels, and limitations to prevent misinterpretation.
- **Vulnerable populations**: Food price inflation disproportionately affects low-income households. The analysis aims to inform policy interventions that support, rather than exploit, affected communities.
- **AI transparency**: AI-assisted development is documented in the notebooks. All AI-generated code was reviewed, tested, and validated by the team before inclusion.
- **Open access**: The project is open-source, enabling peer review, reproducibility, and community contribution.

### Legal Implications
- Data used under World Bank open data licence
- No commercial restrictions on analysis
- Findings presented objectively without political bias

### Social Considerations
- Food price data affects vulnerable populations
- Analysis aims to inform, not exploit
- Findings presented with appropriate context

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- pip package manager
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Food_price_inflation_analysis.git
   cd Food_price_inflation_analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Jupyter notebooks**
   ```bash
   jupyter notebook
   ```

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| Python 3.12 | Primary programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical computations |
| Plotly | Interactive charts in the Streamlit app |
| Matplotlib / Seaborn | Static charts in Jupyter notebooks |
| Streamlit 1.40 | 8-page interactive web dashboard |
| Power BI Desktop | Business-facing interactive report (.pbix) |
| SciPy | Statistical hypothesis testing (H1–H5) |
| Scikit-learn | Machine learning pipeline & preprocessing |
| XGBoost | Best-performing inflation prediction model |
| Joblib | Model serialisation & loading |
| Jupyter Notebook | Data exploration and experimentation |
| Git / GitHub | Version control & team collaboration |

---

## Future Improvements

1. **Enhanced Predictive Models**: Incorporate ARIMA/SARIMA for better time series forecasting
2. **Additional Data Sources**: Integrate macroeconomic indicators (GDP, exchange rates, oil prices)
3. **Real-time Updates**: Automate data refresh pipeline with scheduled API calls
4. **API Development**: Create REST API endpoints for data access
5. **Extended Geographic Coverage**: Include more countries and regional breakdowns
6. **Deep Learning Models**: Implement LSTM networks for sequential pattern recognition
7. **Anomaly Detection**: Add alerts for unusual price movements

---

## Credits

* **Dataset:** This project uses the World Bank Real-Time Food Prices (RTFP) dataset from the [World Bank Food Prices for Nutrition](https://www.worldbank.org/en/programs/food-prices-for-nutrition) program. The dataset provides monthly food price indicators including Open, High, Low, Close prices and inflation rates for 25 countries spanning over 16 years (2007-2023).

* **Code Institute:** Project structure and methodology guidance from the Code Institute Data Analytics program. The project follows the assessment criteria and best practices taught in the capstone project module.

* **Streamlit Documentation:** Used Streamlit's official documentation and examples for building the interactive 8-page dashboard with dynamic visualisations and user-friendly filters.

* **Scikit-learn Documentation:** Referenced for implementing machine learning models, evaluation metrics, and best practices for train-test splitting, preprocessing pipelines, and model validation.

* **XGBoost Documentation:** Used for implementing the Gradient Boosting regression model that achieved the best performance in inflation prediction.

* **Plotly Documentation:** Used for creating interactive visualisations with professional styling, hover tooltips, and responsive charts throughout the Streamlit dashboard.

* **SciPy Documentation:** Referenced for statistical hypothesis testing including Kruskal-Wallis, Mann-Whitney U, and Spearman correlation tests.

* **Power BI Documentation:** Used for creating the business-focused interactive dashboard with slicers, KPI cards, and cross-filtering capabilities.

* **GitHub Copilot:** AI assistance was used for code suggestions, documentation improvements, and debugging during development. All AI-generated code was reviewed, tested, and validated by the team.

## Acknowledgements

* I would like to thank Code Institute for providing the educational framework and assessment structure for this hackathon project.
* Special thanks to our mentors for guidance and feedback throughout the project development.
* Thanks to the World Bank for making the Real-Time Food Prices dataset publicly available for research and educational purposes.
* Thanks to the open-source community for developing and maintaining the excellent Python libraries used in this project (Pandas, NumPy, Scikit-learn, Plotly, Streamlit, and more).
* Thanks to the hackathon team members (Florence, Gia, and Sergio) for their collaboration and dedication throughout the project.

---

## Deployment

### Streamlit Dashboard

The interactive web dashboard was built using **Streamlit**, a Python framework that transforms data scripts into shareable web applications. Streamlit was chosen for its simplicity, native Python integration, and ability to create professional data apps without requiring front-end development expertise.

**Key advantages of using Streamlit:**
- **Rapid prototyping:** Changes to the Python code are instantly reflected in the dashboard
- **Native Plotly support:** Interactive charts render seamlessly with hover tooltips and zoom functionality
- **Built-in widgets:** Sidebar filters, selectboxes, and sliders enable user interactivity without custom JavaScript
- **Session state management:** Allows data persistence across page navigation and user interactions
- **Multi-page architecture:** The app is organised into 8 logical pages for improved user experience

### Heroku Deployment

The Streamlit app is deployed on **Heroku**, a cloud platform that supports Python applications. The deployment uses:
- `Procfile`: Specifies the command to run the Streamlit server
- `setup.sh`: Configures Streamlit server settings for Heroku
- `requirements.txt`: Lists all Python dependencies for automatic installation

**Live link**: https://food-prices-inflation-a5cfe8052e3a.herokuapp.com/

---

## Live Dashboards

### 🖥️ Streamlit Web App
Run locally or access the deployed version:
- **Local**: `streamlit run app.py` (after setup steps above)
- **Deployed**: https://food-prices-inflation-a5cfe8052e3a.herokuapp.com/

### 📊 Power BI Report
Open the `.pbix` file in Power BI Desktop to explore the interactive business dashboard:
- **File**: `Power Bi/Food Price Inflation Analysis.pbix`
- **Requirements**: [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (free download)

---

## Contact

For questions or collaboration opportunities, please reach out through GitHub issues.

**Team**: Sergio, Gia & Florence  
**Hackathon**: Code Institute Data Analytics

---

*Last Updated: March 2026*
