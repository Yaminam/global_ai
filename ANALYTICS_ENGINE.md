# Analytics Engine Documentation

## Overview

The Analytics Engine is a comprehensive data analysis and visualization system built with Python, Pandas, NumPy, and Matplotlib. It provides powerful tools for data processing, statistical analysis, visualization, and insights generation.

## Architecture

### Core Components

#### 1. **VisualizationEngine** (`backend/services/visualization_engine.py`)
Handles all chart and graph generation using Matplotlib.

**Features:**
- Bar charts (`generate_bar_chart()`)
- Line charts (`generate_line_chart()`)
- Pie charts (`generate_pie_chart()`)
- Histograms (`generate_histogram()`)
- Scatter plots (`generate_scatter_plot()`)
- Box plots (`generate_box_plot()`)
- Heatmaps (`generate_heatmap()`)
- Multi-chart reports (`generate_multi_chart_report()`)

**Configuration:**
- Output directory: `./analytics/reports/`
- DPI: 300 (high resolution)
- Style: seaborn-v0_8-darkgrid (or fallback)

#### 2. **DataAggregator** (`backend/services/data_aggregator.py`)
Performs data transformations, aggregations, and statistical calculations.

**Core Methods:**
- `clean_data()` - Remove duplicates, handle missing values
- `filter_data()` - Filter by complex criteria with operators
- `aggregate()` - Group and aggregate data
- `calculate_statistics()` - Detailed statistical analysis
- `calculate_correlations()` - Correlation matrix
- `detect_outliers()` - IQR and Z-score based outlier detection
- `normalize_columns()` - Min-Max and Z-score normalization
- `group_and_count()` - Value counts with grouping
- `pivot_data()` - Pivot tables
- `resample_time_series()` - Time series resampling

#### 3. **AnalyticsService** (`backend/services/analytics_service.py`)
Performs comprehensive analytics on datasets.

**Capabilities:**
- Statistical analysis
- Anomaly detection
- Trend analysis
- AI-generated insights
- Export in JSON format

#### 4. **VisualizationDemo** (`backend/services/visualization_scripts.py`)
Demonstration scripts showing real-world visualization examples.

**Includes:**
- Sales analytics with trends and breakdowns
- Employee analytics with salary and performance analysis
- Customer analytics with segmentation
- Financial analysis with revenue and profit trends

#### 5. **SampleDataGenerator** (`backend/services/sample_analytics.py`)
Generate realistic sample datasets for testing and demonstration.

**Datasets:**
- Sales data (1000 records with products, regions, discounts)
- Employee data (500 records with departments, performance)
- Customer data (2000 records with lifetime value, segments)
- Financial data (60 months of revenue, expenses, profits)

## API Endpoints

### Basic Analytics
```
POST /api/analytics
- file_path: Path to data file
- job_id: Optional job identifier
- dataset_id: Optional dataset identifier
```

### Visualizations

#### Histogram
```
POST /api/analytics/visualize/histogram
{
  "file_path": "uploads/data.csv",
  "column": "age",
  "title": "Age Distribution",
  "bins": 30
}
```

#### Bar Chart
```
POST /api/analytics/visualize/bar
{
  "file_path": "uploads/data.csv",
  "column": "product",
  "agg_func": "sum|mean|count",
  "top_n": 10
}
```

#### Pie Chart
```
POST /api/analytics/visualize/pie
{
  "file_path": "uploads/data.csv",
  "column": "category"
}
```

### Data Processing

#### Aggregation
```
POST /api/analytics/aggregate
{
  "file_path": "uploads/data.csv",
  "group_by": "department",
  "aggregations": {
    "salary": ["sum", "mean"],
    "performance": "mean"
  }
}
```

#### Filtering
```
POST /api/analytics/filter
{
  "file_path": "uploads/data.csv",
  "filters": {
    "salary": {"$gte": 50000, "$lte": 150000},
    "department": "Engineering",
    "status": {"$in": ["active", "pending"]}
  }
}
```

**Filter Operators:**
- `$eq` - Equal
- `$ne` - Not equal
- `$gt` - Greater than
- `$gte` - Greater than or equal
- `$lt` - Less than
- `$lte` - Less than or equal
- `$in` - In list
- `$nin` - Not in list
- `$contains` - String contains

#### Statistics
```
POST /api/analytics/statistics
{
  "file_path": "uploads/data.csv",
  "columns": ["salary", "age", "performance"]
}
```

**Returns:** Mean, median, std, min, max, quartiles, variance, sum

#### Correlations
```
POST /api/analytics/correlations
{
  "file_path": "uploads/data.csv",
  "method": "pearson|spearman|kendall"
}
```

#### Outlier Detection
```
POST /api/analytics/outliers
{
  "file_path": "uploads/data.csv",
  "method": "iqr|zscore",
  "threshold": 1.5
}
```

#### Data Cleaning
```
POST /api/analytics/clean
{
  "file_path": "uploads/data.csv",
  "drop_duplicates": true,
  "drop_null_rows": false,
  "fill_strategy": "mean|median|forward_fill"
}
```

## Usage Examples

### Python Code Example

```python
from backend.services.visualization_engine import VisualizationEngine
from backend.services.data_aggregator import DataAggregator
import pandas as pd

# Initialize services
viz_engine = VisualizationEngine()
aggregator = DataAggregator()

# Load data
df = pd.read_csv('data.csv')

# Clean data
clean_df = aggregator.clean_data(df, drop_duplicates=True, fill_strategy='mean')

# Filter data
filtered = aggregator.filter_data(clean_df, {'salary': {'$gte': 50000}})

# Generate visualization
revenue_by_product = clean_df.groupby('product')['revenue'].sum().head(10)
chart_path = viz_engine.generate_bar_chart(
    revenue_by_product,
    title='Top 10 Products by Revenue',
    filename='product_sales.png'
)

# Get statistics
stats = aggregator.calculate_statistics(clean_df, columns=['salary', 'age'])
print(stats)

# Calculate correlations
corr = aggregator.calculate_correlations(clean_df)
print(corr)

# Detect outliers
outliers = aggregator.detect_outliers(clean_df, method='iqr')
print(f"Outliers found: {outliers}")
```

### API Usage Example (cURL)

```bash
# Upload and analyze data
curl -X POST http://localhost:5000/api/analytics \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/sales.csv"
  }'

# Create histogram
curl -X POST http://localhost:5000/api/analytics/visualize/histogram \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/sales.csv",
    "column": "amount",
    "bins": 30
  }'

# Filter data
curl -X POST http://localhost:5000/api/analytics/filter \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/employees.csv",
    "filters": {
      "department": "Engineering",
      "salary": {"$gte": 100000}
    }
  }'

# Get statistics
curl -X POST http://localhost:5000/api/analytics/statistics \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/sales.csv",
    "columns": ["amount", "quantity"]
  }'
```

### Running Sample Examples

```python
python -m backend.services.sample_analytics

# Or in Python
from backend.services.sample_analytics import AnalyticsExample
AnalyticsExample.analyze_sales_data()
AnalyticsExample.analyze_employee_data()
```

## Data Processing Pipeline

### 1. Data Cleaning
- Remove duplicate rows
- Handle missing values (mean, median, forward fill)
- Drop rows with nulls (optional)

### 2. Data Filtering
- Support for complex filter operators
- Multiple column filters with AND logic
- String containment matching

### 3. Aggregations
- Group by one or multiple columns
- Multiple aggregation functions: sum, mean, median, min, max, std, count
- Handles both numeric and categorical data

### 4. Statistical Analysis
- Descriptive statistics (mean, median, std, variance)
- Distribution metrics (skewness, kurtosis)
- Quartiles and IQR
- Data profiling (unique counts, nulls)

### 5. Anomaly Detection

**IQR Method (Interquartile Range):**
```
Lower Bound = Q1 - (1.5 × IQR)
Upper Bound = Q3 + (1.5 × IQR)
Outliers: Values outside bounds
```

**Z-Score Method:**
```
Z-Score = (Value - Mean) / StdDev
Outliers: |Z-Score| > Threshold (default 3)
```

### 6. Visualization
- Multiple chart types for different data types
- Automatic styling and formatting
- High-resolution PNG output (300 DPI)
- Customizable titles, labels, colors

### 7. Insights Generation
- Automated detection of data quality issues
- Skewness and distribution warnings
- Missing value analysis
- Duplicate detection
- High cardinality detection

## Sample Output

### Visualization Report Structure
```
analytics/reports/
├── histogram_age_*.png
├── bar_product_*.png
├── pie_segment_*.png
├── scatter_performance_salary_*.png
├── box_salary_dept_*.png
└── heatmap_correlations_*.png
```

### Statistics Output
```json
{
  "statistics": {
    "salary": {
      "count": 500,
      "mean": 85000.00,
      "median": 82000.00,
      "std": 25000.00,
      "min": 40000.00,
      "max": 200000.00,
      "q25": 65000.00,
      "q75": 105000.00,
      "variance": 625000000.00,
      "sum": 42500000.00
    }
  }
}
```

### Aggregation Output
```json
{
  "results": [
    {
      "department": "Engineering",
      "salary_sum": 12500000,
      "salary_mean": 95000,
      "performance_mean": 8.5
    },
    {
      "department": "Sales",
      "salary_sum": 8750000,
      "salary_mean": 75000,
      "performance_mean": 7.8
    }
  ]
}
```

## Performance Considerations

- **Large Datasets**: Handles files with 100K+ rows efficiently
- **Memory Management**: Optimized for streaming large files
- **Chart Generation**: Vectorized operations with NumPy
- **Correlation Matrices**: Efficient pandas implementation
- **Outlier Detection**: O(n) complexity for both methods

## Error Handling

- File load validation
- Column existence checking
- Type validation for operations
- Graceful fallback for unsupported styles
- Comprehensive error messages with codes

## Dependencies

```
pandas>=1.0.0
numpy>=1.18.0
matplotlib>=3.0.0
flask
python-dotenv
openpyxl
```

## Future Enhancements

- [ ] Real-time streaming analytics
- [ ] Advanced ML-based anomaly detection (Isolation Forest)
- [ ] Time series forecasting
- [ ] Natural language insights
- [ ] Interactive dashboards (Plotly)
- [ ] Batch processing jobs
- [ ] Data caching and optimization
- [ ] Custom aggregation functions

## Troubleshooting

### Missing Matplotlib Style
If `seaborn-v0_8-darkgrid` is not available, the engine automatically falls back to `default` style.

### Memory Issues with Large Files
- Use filtering to reduce data before processing
- Process data in chunks for very large files
- Optimize column types in source data

### Correlation Matrix Errors
- Ensure sufficient numeric columns for correlation
- Non-numeric columns are automatically excluded
- At least 2 numeric columns recommended

## Technical Notes

- All visualizations use DPI 300 for print-quality output
- Charts include gridlines for easier reading
- Value labels automatically added to bar charts
- Correlation heatmaps use diverging colormaps
- Outlier detection respects data types

---

**Last Updated:** March 2026  
**Version:** 1.0.0
