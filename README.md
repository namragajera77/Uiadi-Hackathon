# 🪪 UIDAI Aadhaar Analytics Dashboard

A comprehensive, interactive Streamlit dashboard for analyzing UIDAI Aadhaar enrolment, demographic, and biometric datasets. Built with Python, Pandas, and Plotly for powerful data visualization and insights.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **Multi-Dataset Support**: Analyze Enrolment, Demographic, and Biometric data separately or in a combined view
- **Interactive Visualizations**: Dynamic charts powered by Plotly
- **Advanced Filtering**: Filter by date range, state, district, and pincode
- **Real-time Analytics**: 
  - Total records and metrics
  - State/District/Pincode statistics
  - Top contributors analysis
  - Age distribution breakdowns
  - Time-series trends
  - Month-wise heatmaps
- **Data Export**: Download filtered datasets as CSV
- **File Upload**: Upload custom CSV files for testing
- **Responsive Design**: Beautiful gradient UI with dark mode support

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/namragajera77/uiadi.git
   cd uiadi
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit pandas numpy plotly
   ```

## 📊 Data Files Setup

The dashboard expects CSV files in the same directory as `app.py`. You need to provide your own data files:

### Required File Structure:

**Enrollment Data:**
- `enrollment_all (1)_1.csv`
- `enrollment_all (1)_2.csv`
- `enrollment_all (1)_3.csv`

**Biometric Data:**
- `mightymerge.io__xzzeu4zp (1)_1.csv`
- `mightymerge.io__xzzeu4zp (1)_2.csv`
- `mightymerge.io__xzzeu4zp (1)_3.csv`
- `mightymerge.io__xzzeu4zp (1)_4.csv`

**Demographic Data:**
- `demo_all (1)_1.csv`
- `demo_all (1)_2.csv`
- `demo_all (1)_3.csv`
- `demo_all (1)_4.csv`
- `demo_all (1)_5.csv`

> **Note**: CSV files are not included in the repository due to file size. Add your own data files to the project directory.

## 🎯 Usage

1. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**
   - The dashboard will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

3. **Explore the dashboard**
   - Select dataset type from the sidebar (Enrolment/Demographic/Biometric/Combined View)
   - Apply filters (date range, state, district, pincode)
   - View visualizations in three tabs:
     - 📌 **Overview**: KPIs, top contributors, distribution charts
     - 📈 **Trends**: Time-series analysis, month-wise heatmaps
     - 🧾 **Data**: Raw data preview and export

## ⚙️ Configuration

### Environment Variable (Optional)

Set `UIDAI_DATA_DIR` to use a custom data directory:

```bash
# Windows
setx UIDAI_DATA_DIR "D:\Your\Data\Folder"

# Linux/Mac
export UIDAI_DATA_DIR="/path/to/your/data"
```

### Custom File Paths

Edit `app.py` to modify the default CSV file paths:

```python
DEFAULT_ENROLMENT = [
    r"your_enrollment_file_1.csv",
    r"your_enrollment_file_2.csv"
]
```

## 📁 Project Structure

```
uiadi/
├── app.py                          # Main Streamlit application
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
└── [CSV files]                     # Your data files (not in repo)
```

## 🎨 Features in Detail

### Dashboard Sections

1. **Overview Tab**
   - Key Performance Indicators (KPIs)
   - Total records count
   - State, District, and Pincode statistics
   - Top contributors bar chart
   - Age distribution pie chart

2. **Trends Tab**
   - Time-series line chart
   - Month-wise heatmap for top 15 states
   - Customizable grouping options

3. **Data Tab**
   - Preview up to 5000 records
   - Download filtered data as CSV
   - Export functionality

### Filtering Options

- **Date Range**: Select start and end dates
- **Geographic**: Filter by state and district
- **Pincode**: Search by pincode
- **Chart Settings**: Adjust Top N contributors, grouping method

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly Express**: Interactive visualizations
- **Python**: Core programming language

## 📝 Data Format

### Expected CSV Columns

**Enrollment Data:**
- `date`, `state`, `district`, `pincode`
- `age_0_5`, `age_5_17`, `age_18_greater`

**Demographic Data:**
- `date`, `state`, `district`, `pincode`
- `demo_age_5_17`, `demo_age_17_`

**Biometric Data:**
- `date`, `state`, `district`, `pincode`
- `bio_age_5_17`, `bio_age_17_`

**Date Format**: `DD-MM-YYYY`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

- Namra Gajera - [@namragajera77](https://github.com/namragajera77)

## 🙏 Acknowledgments

- UIDAI for Aadhaar data standards
- Streamlit community for excellent documentation
- Plotly for powerful visualization tools

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/namragajera77/uiadi/issues)
- Contact: [Your Email/Contact Info]

---

**Made with ❤️ for better data insights**
