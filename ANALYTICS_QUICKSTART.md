# Analytics Engine - Quick Start Guide

## Installation & Setup

### 1. Install Required Packages
```bash
pip install pandas numpy matplotlib openpyxl
```

### 2. Check Existing Installation
The project already has most dependencies in `backend/requirements.txt`:
```bash
pip install -r backend/requirements.txt
```

## Quick Examples

### Example 1: Basic Data Analysis

```python
import pandas as pd
from backend.services.data_aggregator import DataAggregator
from backend.services.visualization_engine import VisualizationEngine

# Load data
df = pd.read_csv('data.csv')

# Initialize services
aggregator = DataAggregator()
viz = VisualizationEngine()

# Clean data
clean_df = aggregator.clean_data(df, drop_duplicates=True, fill_strategy='mean')
print(f"Cleaned: {len(clean_df)} rows")

# Get statistics
stats = aggregator.calculate_statistics(clean_df)
for col, stat in stats.items():
    print(f"\n{col}:")
    print(f"  Mean: {stat['mean']:.2f}")
    print(f"  Median: {stat['median']:.2f}")

# Create visualization
chart = viz.generate_histogram(clean_df['age'], title='Age Distribution')
print(f"Chart saved: {chart}")
```

### Example 2: Sales Analysis

```python
from backend.services.visualization_scripts import VisualizationDemo

demo = VisualizationDemo()
charts = demo.generate_sales_analysis()

for name, path in charts.items():
    print(f"{name}: {path}")
```

### Example 3: API Integration

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Get statistics
response = requests.post(
    f"{BASE_URL}/api/analytics/statistics",
    json={
        "file_path": "uploads/sales.csv",
        "columns": ["amount", "quantity"]
    }
)

stats = response.json()['data']['statistics']
print(json.dumps(stats, indent=2))
```

## Common Operations

### Data Cleaning
```python
# Remove duplicates and fill missing values
clean_data = aggregator.clean_data(
    df, 
    drop_duplicates=True,
    fill_strategy='mean'  # or 'median', 'forward_fill'
)
```

### Filtering
```python
# Complex filtering
filtered = aggregator.filter_data(df, {
    'salary': {'$gte': 50000, '$lte': 150000},
    'department': 'Engineering',
    'status': {'$in': ['active', 'approved']}
})
```

### Aggregation
```python
# Group and aggregate
result = aggregator.aggregate(
    df,
    group_by='department',
    aggregations={
        'salary': ['sum', 'mean', 'count'],
        'performance': 'mean'
    }
)
```

### Visualizations
```python
# Histogram
viz.generate_histogram(df['age'], title='Age Distribution', bins=30)

# Bar chart
revenue = df.groupby('product')['amount'].sum()
viz.generate_bar_chart(revenue, title='Revenue by Product')

# Pie chart
categories = df['category'].value_counts()
viz.generate_pie_chart(categories, title='Category Distribution')

# Scatter plot
viz.generate_scatter_plot(
    df['hours'],
    df['salary'],
    title='Hours vs Salary'
)

# Box plot
departments = {dept: df[df['dept']==dept]['salary'] for dept in df['dept'].unique()}
viz.generate_box_plot(departments, title='Salary by Department')

# Heatmap
viz.generate_heatmap(df[['age', 'salary', 'performance']], title='Correlations')
```

### Statistical Analysis
```python
# Get detailed statistics
stats = aggregator.calculate_statistics(df, columns=['salary', 'age'])

# Calculate correlations
correlations = aggregator.calculate_correlations(df)

# Detect outliers
outliers = aggregator.detect_outliers(df, method='iqr', threshold=1.5)

# Normalize data
normalized = aggregator.normalize_columns(df, method='minmax')

# Detect unique patterns
counts = aggregator.group_and_count(df, 'category', top_n=10)
```

## Sample Data Generation

```python
from backend.services.sample_analytics import SampleDataGenerator

gen = SampleDataGenerator()

# Generate sample datasets
gen.generate_sales_data(num_records=1000)
gen.generate_employee_data(num_records=500)
gen.generate_customer_data(num_records=2000)
gen.generate_financial_data(num_records=60)
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/analytics` | Perform full analytics |
| POST | `/api/analytics/aggregate` | Aggregate data |
| POST | `/api/analytics/filter` | Filter data |
| POST | `/api/analytics/statistics` | Get statistics |
| POST | `/api/analytics/correlations` | Get correlations |
| POST | `/api/analytics/outliers` | Detect outliers |
| POST | `/api/analytics/clean` | Clean data |
| POST | `/api/analytics/visualize/histogram` | Create histogram |
| POST | `/api/analytics/visualize/bar` | Create bar chart |
| POST | `/api/analytics/visualize/pie` | Create pie chart |

## Troubleshooting

### Issue: Charts not saving
**Solution:** Ensure `analytics/reports/` directory exists
```bash
mkdir -p analytics/reports
```

### Issue: Missing matplotlib backends
**Solution:** Install required graphics backend
```bash
pip install kaleido  # For static image export
```

### Issue: Large file memory errors
**Solution:** Process data in chunks
```python
chunks = pd.read_csv('large_file.csv', chunksize=10000)
for chunk in chunks:
    # Process each chunk
    pass
```

### Issue: Matplotlib style not found
**Solution:** Engine automatically falls back to default style. No action needed.

## Performance Tips

1. **Clean data first** to reduce processing overhead
2. **Filter before aggregating** to work with smaller datasets
3. **Use list comprehensions** for custom transformations
4. **Batch visualizations** when generating multiple charts
5. **Cache aggregations** if using same data multiple times

## Output Locations

```
analytics/
├── reports/          # Generated visualizations
│   ├── histogram_*.png
│   ├── bar_*.png
│   ├── pie_*.png
│   └── ...
└── sample_data/      # Sample datasets
    ├── sample_sales.csv
    ├── sample_employees.csv
    └── ...
```

## Next Steps

1. **Explore Samples:** Run `python backend/services/sample_analytics.py`
2. **Try API:** Use curl or Postman with API examples
3. **Custom Analysis:** Build your own analysis scripts
4. **Deploy:** Integrate with your application

## Resources

- **Full Documentation:** See `ANALYTICS_ENGINE.md`
- **API Examples:** See `API_TESTING.md`
- **Sample Code:** See `backend/services/sample_analytics.py`
- **Visualization Demo:** See `backend/services/visualization_scripts.py`

---

**Pro Tips:**
- Use `drop_duplicates=True` and `fill_strategy='mean'` for most datasets
- IQR method (default) is better for non-normal distributions
- Generate multiple chart types for better data understanding
- Use correlations to find relationships between variables
- Combine filtering and aggregation for segmented analysis

---

**Last Updated:** March 2026
