"""
Complete Analytics Workflow Example
Demonstrates end-to-end analytics pipeline with real-world scenario
"""

import pandas as pd
import numpy as np
from backend.services.visualization_engine import VisualizationEngine
from backend.services.data_aggregator import DataAggregator
from backend.services.analytics_service import AnalyticsService
import json


class CompleteAnalyticsWorkflow:
    """Comprehensive example of using all analytics components"""
    
    @staticmethod
    def scenario_1_sales_performance_analysis():
        """
        Scenario: Analyze sales performance across regions and products
        
        Steps:
        1. Load and explore data
        2. Clean data
        3. Filter for quality records
        4. Analyze by region and product
        5. Detect anomalies
        6. Generate visualizations
        """
        print("\n" + "="*70)
        print("SCENARIO 1: SALES PERFORMANCE ANALYSIS")
        print("="*70)
        
        # Generate sample sales data
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=500, freq='D')
        
        df = pd.DataFrame({
            'date': dates,
            'product': np.random.choice(['Product A', 'Product B', 'Product C', 'Product D'], 500),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 500),
            'quantity': np.random.randint(1, 100, 500),
            'price': np.random.uniform(10, 1000, 500),
            'discount': np.random.uniform(0, 20, 500),
            'salesperson': np.random.choice(['John', 'Sarah', 'Mike', 'Emily'], 500)
        })
        
        # Add some missing values
        df.loc[np.random.choice(df.index, 10), 'discount'] = np.nan
        
        # Calculate metrics
        df['revenue'] = df['quantity'] * df['price'] * (1 - df['discount']/100)
        
        print("\n1. DATA OVERVIEW")
        print("-" * 40)
        print(f"Total records: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Unique products: {df['product'].nunique()}")
        print(f"Unique regions: {df['region'].nunique()}")
        
        # Initialize services
        aggregator = DataAggregator()
        viz = VisualizationEngine()
        
        # Step 1: Data Cleaning
        print("\n2. DATA CLEANING")
        print("-" * 40)
        original_rows = len(df)
        df_clean = aggregator.clean_data(df, drop_duplicates=True, fill_strategy='mean')
        print(f"Rows removed: {original_rows - len(df_clean)}")
        print(f"Missing values after cleaning: {df_clean.isnull().sum().sum()}")
        
        # Step 2: Filter for valid records
        print("\n3. DATA FILTERING")
        print("-" * 40)
        filters = {
            'revenue': {'$gt': 100},
            'region': {'$nin': []}  # Keep all regions
        }
        df_filtered = aggregator.filter_data(df_clean, filters)
        print(f"Valid records: {len(df_filtered)} out of {len(df_clean)}")
        
        # Step 3: Regional Analysis
        print("\n4. REGIONAL ANALYSIS")
        print("-" * 40)
        regional_stats = aggregator.aggregate(
            df_filtered,
            group_by='region',
            aggregations={'revenue': ['sum', 'mean'], 'quantity': 'sum'}
        )
        print("\nRevenue by Region:")
        print(regional_stats.to_string())
        
        # Step 4: Product Analysis
        print("\n5. PRODUCT ANALYSIS")
        print("-" * 40)
        product_stats = aggregator.aggregate(
            df_filtered,
            group_by='product',
            aggregations={'revenue': ['sum', 'mean'], 'quantity': 'sum'}
        )
        print("\nRevenue by Product:")
        print(product_stats.to_string())
        
        # Step 5: Anomaly Detection
        print("\n6. ANOMALY DETECTION")
        print("-" * 40)
        outliers = aggregator.detect_outliers(
            df_filtered,
            columns=['revenue', 'price'],
            method='iqr'
        )
        for col, indices in outliers.items():
            print(f"{col}: {len(indices)} outliers detected")
        
        # Step 6: Visualizations
        print("\n7. GENERATING VISUALIZATIONS")
        print("-" * 40)
        
        # Revenue by region
        region_revenue = df_filtered.groupby('region')['revenue'].sum()
        pie_chart = viz.generate_pie_chart(
            region_revenue,
            title='Revenue Distribution by Region',
            filename='scenario1_revenue_by_region.png'
        )
        print(f"✓ Pie chart: {pie_chart}")
        
        # Revenue by product
        product_revenue = df_filtered.groupby('product')['revenue'].sum().sort_values(ascending=False)
        bar_chart = viz.generate_bar_chart(
            product_revenue,
            title='Total Revenue by Product',
            ylabel='Revenue ($)',
            filename='scenario1_revenue_by_product.png'
        )
        print(f"✓ Bar chart: {bar_chart}")
        
        # Revenue distribution
        hist_chart = viz.generate_histogram(
            df_filtered['revenue'],
            title='Revenue Distribution',
            xlabel='Revenue ($)',
            filename='scenario1_revenue_histogram.png',
            bins=25
        )
        print(f"✓ Histogram: {hist_chart}")
        
        # Price vs Quantity
        scatter_chart = viz.generate_scatter_plot(
            df_filtered['price'],
            df_filtered['quantity'],
            title='Price vs Quantity Sold',
            xlabel='Price ($)',
            ylabel='Quantity',
            filename='scenario1_price_vs_quantity.png'
        )
        print(f"✓ Scatter plot: {scatter_chart}")
        
        print("\n✓ SCENARIO 1 COMPLETE")
        return {
            'data': df_filtered,
            'regional_stats': regional_stats,
            'product_stats': product_stats,
            'outliers': outliers
        }
    
    @staticmethod
    def scenario_2_hr_employee_analysis():
        """
        Scenario: HR Analytics - Salary analysis and compensation reviews
        
        Steps:
        1. Load employee data
        2. Clean and validate
        3. Analyze by department
        4. Identify compensation outliers
        5. Create department comparisons
        6. Generate insights
        """
        print("\n" + "="*70)
        print("SCENARIO 2: HR EMPLOYEE COMPENSATION ANALYSIS")
        print("="*70)
        
        # Generate sample employee data
        np.random.seed(42)
        df = pd.DataFrame({
            'employee_id': range(1001, 1101),
            'name': [f'Employee {i}' for i in range(100)],
            'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'], 100),
            'level': np.random.choice(['Junior', 'Senior', 'Lead'], 100),
            'salary': np.random.uniform(50000, 150000, 100),
            'bonus_percent': np.random.uniform(0, 20, 100),
            'years_employed': np.random.randint(0, 15, 100),
            'performance_score': np.random.uniform(2, 5, 100)
        })
        
        print("\n1. DATA OVERVIEW")
        print("-" * 40)
        print(f"Total employees: {len(df)}")
        print(f"Departments: {df['department'].nunique()}")
        print(f"Salary range: ${df['salary'].min():.0f} - ${df['salary'].max():.0f}")
        
        # Initialize services
        aggregator = DataAggregator()
        viz = VisualizationEngine()
        
        # Step 1: Calculate total compensation
        df['total_comp'] = df['salary'] * (1 + df['bonus_percent']/100)
        
        # Step 2: Clean data
        print("\n2. DATA CLEANING & VALIDATION")
        print("-" * 40)
        df_clean = aggregator.clean_data(df, drop_duplicates=True, fill_strategy='mean')
        print(f"Data cleaned. Rows: {len(df_clean)}")
        
        # Step 3: Department Analysis
        print("\n3. DEPARTMENT COMPENSATION ANALYSIS")
        print("-" * 40)
        dept_analysis = aggregator.aggregate(
            df_clean,
            group_by='department',
            aggregations={
                'salary': ['mean', 'min', 'max', 'count'],
                'bonus_percent': 'mean',
                'performance_score': 'mean'
            }
        )
        print("\nDepartment Statistics:")
        print(dept_analysis.to_string())
        
        # Step 4: Level-based Analysis
        print("\n4. LEVEL-BASED COMPENSATION")
        print("-" * 40)
        level_analysis = aggregator.aggregate(
            df_clean,
            group_by='level',
            aggregations={
                'salary': ['mean', 'count'],
                'performance_score': 'mean'
            }
        )
        print("\nLevel Statistics:")
        print(level_analysis.to_string())
        
        # Step 5: Outlier Detection
        print("\n5. COMPENSATION OUTLIER DETECTION")
        print("-" * 40)
        outliers = aggregator.detect_outliers(
            df_clean,
            columns=['salary', 'performance_score'],
            method='iqr'
        )
        for col, indices in outliers.items():
            if indices:
                print(f"\n{col}: {len(indices)} outliers")
                print(f"  Affected employees: {indices[:5]}")
        
        # Step 6: Correlation Analysis
        print("\n6. CORRELATION ANALYSIS")
        print("-" * 40)
        numeric_cols = ['salary', 'bonus_percent', 'years_employed', 'performance_score']
        corr = aggregator.calculate_correlations(df_clean[numeric_cols])
        print("\nKey Correlations:")
        print(f"  Salary vs Performance: {corr.loc['salary', 'performance_score']:.3f}")
        print(f"  Salary vs Years: {corr.loc['salary', 'years_employed']:.3f}")
        print(f"  Performance vs Bonus: {corr.loc['performance_score', 'bonus_percent']:.3f}")
        
        # Step 7: Visualizations
        print("\n7. GENERATING VISUALIZATIONS")
        print("-" * 40)
        
        # Salary by department
        dept_salary = {dept: df_clean[df_clean['department']==dept]['salary'].values
                      for dept in df_clean['department'].unique()}
        box_chart = viz.generate_box_plot(
            dept_salary,
            title='Salary Distribution by Department',
            ylabel='Salary ($)',
            filename='scenario2_salary_by_dept.png'
        )
        print(f"✓ Box plot: {box_chart}")
        
        # Department comparison
        dept_avg_salary = df_clean.groupby('department')['salary'].mean().sort_values(ascending=False)
        bar_chart = viz.generate_bar_chart(
            dept_avg_salary,
            title='Average Salary by Department',
            ylabel='Avg Salary ($)',
            filename='scenario2_avg_salary_by_dept.png',
            color='skyblue'
        )
        print(f"✓ Bar chart: {bar_chart}")
        
        # Performance distribution
        hist_chart = viz.generate_histogram(
            df_clean['performance_score'],
            title='Performance Score Distribution',
            xlabel='Performance Score',
            filename='scenario2_performance_histogram.png',
            bins=15
        )
        print(f"✓ Histogram: {hist_chart}")
        
        # Salary vs Performance
        scatter_chart = viz.generate_scatter_plot(
            df_clean['performance_score'],
            df_clean['salary'],
            title='Performance Score vs Salary',
            xlabel='Performance Score',
            ylabel='Salary ($)',
            filename='scenario2_performance_vs_salary.png'
        )
        print(f"✓ Scatter plot: {scatter_chart}")
        
        # Correlation heatmap
        heatmap = viz.generate_heatmap(
            df_clean[numeric_cols],
            title='Employee Metrics Correlations',
            filename='scenario2_correlations.png'
        )
        print(f"✓ Heatmap: {heatmap}")
        
        print("\n✓ SCENARIO 2 COMPLETE")
        return {
            'data': df_clean,
            'dept_analysis': dept_analysis,
            'level_analysis': level_analysis,
            'outliers': outliers
        }
    
    @staticmethod
    def scenario_3_data_quality_assessment():
        """
        Scenario: Comprehensive data quality assessment and cleaning
        
        Steps:
        1. Load raw data with issues
        2. Profile missing values
        3. Detect duplicates
        4. Identify outliers
        5. Create cleaning report
        6. Generate cleaned dataset
        """
        print("\n" + "="*70)
        print("SCENARIO 3: DATA QUALITY ASSESSMENT")
        print("="*70)
        
        # Generate data with quality issues
        np.random.seed(42)
        df = pd.DataFrame({
            'id': range(1000),
            'value1': np.random.normal(100, 20, 1000),
            'value2': np.random.uniform(10, 50, 1000),
            'category': np.random.choice(['A', 'B', 'C', 'D'], 1000),
            'amount': np.random.exponential(1000, 1000)
        })
        
        # Add quality issues
        # Missing values
        missing_indices = np.random.choice(df.index, size=50, replace=False)
        df.loc[missing_indices[:20], 'value1'] = np.nan
        df.loc[missing_indices[20:40], 'value2'] = np.nan
        
        # Duplicates
        df = pd.concat([df, df.head(15)], ignore_index=True)
        
        # Outliers (add extreme values)
        df.loc[df.index[-5:], 'amount'] = 50000
        
        print("\n1. DATA QUALITY PROFILE")
        print("-" * 40)
        print(f"Total rows: {len(df)}")
        print(f"Columns: {df.shape[1]}")
        print(f"\nMissing values:")
        missing = df.isnull().sum()
        for col, count in missing[missing > 0].items():
            pct = (count/len(df))*100
            print(f"  {col}: {count} ({pct:.1f}%)")
        
        print(f"\nDuplicate rows: {df.duplicated().sum()}")
        
        # Initialize services
        aggregator = DataAggregator()
        
        # Step 1: Detailed analysis
        print("\n2. DETAILED QUALITY METRICS")
        print("-" * 40)
        stats = aggregator.calculate_statistics(df, columns=['value1', 'value2', 'amount'])
        for col, stat in stats.items():
            print(f"\n{col}:")
            print(f"  Non-null: {stat['count']} ({(stat['count']/len(df))*100:.1f}%)")
            print(f"  Mean: {stat['mean']:.2f}")
            print(f"  Std: {stat['std']:.2f}")
        
        # Step 2: Outlier detection
        print("\n3. OUTLIER DETECTION")
        print("-" * 40)
        outliers = aggregator.detect_outliers(df, method='iqr')
        for col, indices in outliers.items():
            print(f"{col}: {len(indices)} outliers ({(len(indices)/len(df))*100:.1f}%)")
        
        # Step 3: Cleaning options
        print("\n4. CLEANING OPTIONS")
        print("-" * 40)
        
        print("\nOption A: Drop rows with nulls")
        cleaned_a = aggregator.clean_data(df, drop_null_rows=True)
        print(f"  Result: {len(cleaned_a)} rows ({((len(df)-len(cleaned_a))/len(df))*100:.1f}% removed)")
        
        print("\nOption B: Fill with mean, drop duplicates")
        cleaned_b = aggregator.clean_data(df, drop_duplicates=True, fill_strategy='mean')
        print(f"  Result: {len(cleaned_b)} rows ({((len(df)-len(cleaned_b))/len(df))*100:.1f}% removed)")
        
        print("\nOption C: Fill with median, drop duplicates")
        cleaned_c = aggregator.clean_data(df, drop_duplicates=True, fill_strategy='median')
        print(f"  Result: {len(cleaned_c)} rows ({((len(df)-len(cleaned_c))/len(df))*100:.1f}% removed)")
        
        # Step 4: Recommendations
        print("\n5. RECOMMENDATIONS")
        print("-" * 40)
        print("✓ Use Option B for most datasets (balanced approach)")
        print("✓ Investigate outliers before removal")
        print("✓ Document data quality findings")
        print("✓ Establish data validation rules")
        
        print("\n✓ SCENARIO 3 COMPLETE")
        return {
            'original_data': df,
            'cleaned_data': cleaned_b,
            'quality_report': {
                'missing_values': df.isnull().sum().to_dict(),
                'duplicates': int(df.duplicated().sum()),
                'outliers': outliers
            }
        }


def run_all_scenarios():
    """Execute all workflow scenarios"""
    print("\n" + "="*70)
    print("COMPLETE ANALYTICS WORKFLOW - ALL SCENARIOS")
    print("="*70)
    
    # Run scenarios
    result1 = CompleteAnalyticsWorkflow.scenario_1_sales_performance_analysis()
    result2 = CompleteAnalyticsWorkflow.scenario_2_hr_employee_analysis()
    result3 = CompleteAnalyticsWorkflow.scenario_3_data_quality_assessment()
    
    print("\n" + "="*70)
    print("ALL SCENARIOS COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nGenerated outputs:")
    print("  - 10+ visualization charts")
    print("  - Multiple statistical analyses")
    print("  - Quality assessment reports")
    print("  - Comprehensive insights")


if __name__ == '__main__':
    run_all_scenarios()
