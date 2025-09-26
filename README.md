# 🌟 MoonLight Energy Solutions - Solar Radiation Analysis

**Strategic Investment Analysis for Solar Farm Development in West Africa**

This project analyzes solar radiation measurement data from Benin, Sierra Leone, and Togo to identify high-potential regions for solar installations, supporting MoonLight Energy Solutions' sustainability goals.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Data Description](#data-description)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Analysis Components](#analysis-components)
- [Dashboard Features](#dashboard-features)
- [Key Findings](#key-findings)
- [Contributing](#contributing)

## 🎯 Project Overview

As an Analytics Engineer at MoonLight Energy Solutions, this analysis provides data-driven strategic recommendations for solar investment prioritization across three West African countries. The comprehensive EDA covers data quality assessment, statistical analysis, time series patterns, correlation studies, and outlier detection to support evidence-based decision making.

## 📊 Data Description

The dataset contains solar radiation measurements with the following key variables:

- **GHI**: Global Horizontal Irradiance (W/m²)
- **DNI**: Direct Normal Irradiance (W/m²)
- **DHI**: Diffuse Horizontal Irradiance (W/m²)
- **Tamb**: Ambient Temperature (°C)
- **RH**: Relative Humidity (%)
- **WS**: Wind Speed (m/s)
- **WD**: Wind Direction (°)
- **ModA/ModB**: Sensor measurements
- **Cleaning**: Cleaning event indicator
- **Precipitation**: Precipitation rate (mm/min)

**Data Sources:**
- Benin: Malanville region
- Sierra Leone: Bumbuna region
- Togo: Dapaong region

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SosiSis/MoonLight-Energy-Solutions
   cd MoonLight-Energy-Solutions
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure data files are in place:**
   Place the CSV data files in the `data/raw/` directory:
   - `benin-malanville.csv`
   - `sierraleone-bumbuna.csv`
   - `togo-dapaong_qc.csv`

## 📈 Usage

### Jupyter Notebook Analysis

Run the comprehensive EDA notebook:

```bash
jupyter notebook notebooks/week0_comprehensive_eda.ipynb
```

The notebook includes:
- Data loading and preprocessing
- Statistical analysis for all three countries
- Time series visualizations
- Correlation analysis
- Wind pattern analysis
- Temperature studies
- Outlier detection
- Strategic recommendations

### Interactive Dashboard

Launch the Streamlit dashboard:

```bash
streamlit run app/main.py
```

The dashboard provides:
- Interactive country selection
- Multiple analysis views
- Real-time visualizations
- Comparative analysis
- Strategic insights

## 🏗️ Project Structure

```
MoonLight-Energy-Solutions/
├── .streamlit/              # Streamlit configuration
│   └── config.toml
├── .github/                 # GitHub Actions workflows
│   └── workflows/
│       └── unittests.yml
├── app/                     # Streamlit dashboard
│   ├── main.py             # Main dashboard application
│   └── utils.py            # Dashboard utility functions
├── data/                    # Data directory
│   └── raw/                # Raw CSV data files
├── notebooks/              # Jupyter notebooks
│   ├── week0_comprehensive_eda.ipynb  # Main analysis notebook
│   └── 00_eda_and_quality_checks.ipynb
├── scripts/                # Reusable Python modules
│   ├── data_load.py        # Data loading utilities
│   ├── eda.py             # Exploratory data analysis functions
│   ├── qa.py              # Data quality assessment
│   ├── stats.py           # Statistical analysis
│   ├── transform.py       # Data transformation
│   └── scoring.py         # Country scoring algorithms
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── .gitignore             # Git ignore rules
```

## 🔬 Analysis Components

### 1. Data Quality Assessment
- Missing value analysis
- Negative value detection
- Duplicate record identification
- Data type validation

### 2. Statistical Analysis
- Summary statistics (mean, median, std, skewness, kurtosis)
- Distribution analysis
- Outlier detection using Z-scores

### 3. Time Series Analysis
- Daily irradiance patterns
- Seasonal variations
- Cleaning event impact assessment
- Temporal trend identification

### 4. Correlation Analysis
- Solar radiation component relationships
- Environmental factor correlations
- Wind-solar irradiance interactions

### 5. Wind Analysis
- Wind speed and direction distributions
- Wind pattern characterization
- Turbulence analysis

### 6. Temperature Analysis
- Temperature-humidity relationships
- Diurnal temperature patterns
- Solar radiation-temperature correlations

### 7. Strategic Scoring
- Country ranking algorithm
- Investment priority recommendations
- Risk assessment factors

## 📊 Dashboard Features

### Interactive Analysis Types
- **Overview & Summary**: Key metrics and data preview
- **Time Series Analysis**: Temporal patterns and trends
- **Data Quality Assessment**: Missing values and anomalies
- **Correlation Analysis**: Relationship visualizations
- **Wind Analysis**: Wind patterns and statistics
- **Temperature Analysis**: Thermal environment assessment
- **Distribution Analysis**: Statistical distributions
- **Outlier Analysis**: Z-score based anomaly detection
- **Bubble Charts**: Multi-variable relationship exploration
- **Country Comparison**: Cross-country analysis
- **Strategic Recommendations**: Investment prioritization

### Visualization Types
- Interactive Plotly charts
- Statistical plots with matplotlib/seaborn
- Real-time metric displays
- Comparative bar charts
- Correlation heatmaps
- Time series plots
- Distribution histograms

## 🏆 Key Findings

### Country Ranking (Solar Potential)
1. **Primary Recommendation**: [Top-ranked country based on analysis]
2. **Investment Priority**: High/Medium/Low classifications
3. **Key Advantages**: Superior irradiance, favorable conditions

### Critical Insights
- **Cleaning Impact**: Regular maintenance improves sensor accuracy by ~X%
- **Seasonal Patterns**: Peak irradiance occurs during [specific periods]
- **Temperature Correlations**: Higher temperatures correlate with [findings]
- **Wind Integration**: Potential for hybrid solar-wind systems in [locations]

### Strategic Recommendations
1. **Site Selection**: Prioritize locations with GHI > 200 W/m²
2. **Technology Choice**: Consider CSP for high DNI regions
3. **Maintenance Planning**: Implement scheduled cleaning protocols
4. **Risk Mitigation**: Account for seasonal variations in planning
5. **Hybrid Systems**: Evaluate wind-solar combinations where applicable

## 🤝 Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run tests: `python -m pytest tests/`
4. Commit changes: `git commit -m "Add your feature"`
5. Push and create pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to functions
- Include unit tests for new features
- Update documentation for API changes

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_data_load.py

# Run with coverage
python -m pytest --cov=scripts tests/
```

## 📄 License

This project is part of the 10 Academy AI Mastery program. All rights reserved.

## 🙏 Acknowledgments

- 10 Academy for the challenging and comprehensive learning experience
- MoonLight Energy Solutions for the strategic use case
- Open-source community for the powerful data science tools

## 📞 Support

For questions or issues:
- Check the [Issues](../../issues) page
- Review the analysis notebook for detailed methodology
- Run the interactive dashboard for visual exploration

---

**Built with ❤️ for sustainable energy solutions in West Africa**
