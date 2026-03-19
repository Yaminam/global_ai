"""
Sample data generator and comprehensive analytics examples
Demonstrates the complete analytics pipeline
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from pathlib import Path
import json
from backend.services.data_aggregator import DataAggregator
from backend.services.visualization_engine import VisualizationEngine


class SampleDataGenerator:
    """Generate sample datasets for testing and demonstration"""
    
    @staticmethod
    def generate_sales_data(num_records: int = 1000, output_file: str = 'sample_sales.csv') -> pd.DataFrame:
        """Generate sample sales data
        
        Args:
            num_records: Number of records to generate
            output_file: Output CSV filename
            
        Returns:
            DataFrame with sales data
        """
        np.random.seed(42)
        
        dates = pd.date_range('2023-01-01', periods=num_records, freq='H')
        
        data = pd.DataFrame({
            'date': dates,
            'product_id': np.random.randint(1001, 1011, num_records),
            'product_name': np.random.choice(['Laptop', 'Tablet', 'Phone', 'Headphones', 'Monitor', 
                                             'Keyboard', 'Mouse', 'Webcam', 'Speaker', 'Charger'], num_records),
            'quantity': np.random.randint(1, 20, num_records),
            'unit_price': np.random.uniform(10, 2000, num_records),
            'discount_percent': np.random.choice([0, 5, 10, 15, 20], num_records),
            'region': np.random.choice(['North America', 'Europe', 'Asia', 'South America'], num_records),
            'salesperson': np.random.choice(['John', 'Sarah', 'Mike', 'Emily', 'David'], num_records),
            'customer_type': np.random.choice(['Retail', 'Wholesale', 'Corporate'], num_records)
        })
        
        # Calculate revenue
        data['total_price'] = data['quantity'] * data['unit_price']
        data['discount_amount'] = data['total_price'] * (data['discount_percent'] / 100)
        data['revenue'] = data['total_price'] - data['discount_amount']
        
        # Add some missing values (realistic)
        missing_rows = np.random.choice(data.index, size=int(0.05 * num_records), replace=False)
        data.loc[missing_rows[:num_records//10], 'discount_percent'] = np.nan
        
        # Save to CSV
        data.to_csv(output_file, index=False)
        print(f"Generated sales data: {output_file} ({num_records} records)")
        
        return data
    
    @staticmethod
    def generate_employee_data(num_records: int = 500, output_file: str = 'sample_employees.csv') -> pd.DataFrame:
        """Generate sample employee data
        
        Args:
            num_records: Number of records to generate
            output_file: Output CSV filename
            
        Returns:
            DataFrame with employee data
        """
        np.random.seed(42)
        
        hire_dates = [datetime(2015, 1, 1) + timedelta(days=x) for x in np.random.randint(0, 3650, num_records)]
        
        data = pd.DataFrame({
            'employee_id': range(10001, 10001 + num_records),
            'first_name': np.random.choice(['John', 'Sarah', 'Mike', 'Emily', 'David', 'Jessica', 'Robert', 'Lisa'], num_records),
            'last_name': np.random.choice(['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Anderson', 'Taylor', 'Martin'], num_records),
            'age': np.random.randint(22, 65, num_records),
            'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations'], num_records),
            'job_title': np.random.choice(['Manager', 'Senior Developer', 'Analyst', 'Specialist', 'Coordinator', 'Executive'], num_records),
            'hire_date': hire_dates,
            'salary': np.random.uniform(40000, 200000, num_records),
            'bonus_percent': np.random.uniform(0, 20, num_records),
            'performance_score': np.random.uniform(1, 10, num_records),
            'years_employed': np.random.randint(0, 20, num_records),
            'location': np.random.choice(['New York', 'San Francisco', 'Chicago', 'Boston', 'Austin'], num_records)
        })
        
        # Add some missing values
        missing_rows = np.random.choice(data.index, size=int(0.02 * num_records), replace=False)
        data.loc[missing_rows[:num_records//50], 'bonus_percent'] = np.nan
        
        # Save to CSV
        data.to_csv(output_file, index=False)
        print(f"Generated employee data: {output_file} ({num_records} records)")
        
        return data
    
    @staticmethod
    def generate_customer_data(num_records: int = 2000, output_file: str = 'sample_customers.csv') -> pd.DataFrame:
        """Generate sample customer data
        
        Args:
            num_records: Number of records to generate
            output_file: Output CSV filename
            
        Returns:
            DataFrame with customer data
        """
        np.random.seed(42)
        
        signup_dates = [datetime(2020, 1, 1) + timedelta(days=x) for x in np.random.randint(0, 1460, num_records)]
        
        data = pd.DataFrame({
            'customer_id': range(20001, 20001 + num_records),
            'name': np.random.choice(['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown'], num_records),
            'email': [f'customer{i}@example.com' for i in range(num_records)],
            'phone': [f'+1{np.random.randint(2000000000, 9999999999)}' for _ in range(num_records)],
            'country': np.random.choice(['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France'], num_records),
            'city': np.random.choice(['New York', 'London', 'Toronto', 'Sydney', 'Berlin', 'Paris'], num_records),
            'signup_date': signup_dates,
            'age': np.random.randint(18, 80, num_records),
            'customer_lifetime_value': np.random.exponential(3000, num_records),
            'total_purchases': np.random.randint(1, 100, num_records),
            'purchase_frequency': np.random.uniform(0.5, 12, num_records),
            'last_purchase_days_ago': np.random.randint(0, 730, num_records),
            'satisfaction_score': np.random.uniform(1, 5, num_records),
            'segment': np.random.choice(['Premium', 'Standard', 'Basic', 'Inactive'], num_records)
        })
        
        # Add some missing values
        missing_rows = np.random.choice(data.index, size=int(0.03 * num_records), replace=False)
        data.loc[missing_rows[:num_records//100], 'satisfaction_score'] = np.nan
        
        # Save to CSV
        data.to_csv(output_file, index=False)
        print(f"Generated customer data: {output_file} ({num_records} records)")
        
        return data
    
    @staticmethod
    def generate_financial_data(num_records: int = 60, output_file: str = 'sample_financials.csv') -> pd.DataFrame:
        """Generate sample financial data (monthly)
        
        Args:
            num_records: Number of records to generate (months)
            output_file: Output CSV filename
            
        Returns:
            DataFrame with financial data
        """
        np.random.seed(42)
        
        dates = pd.date_range('2020-01-01', periods=num_records, freq='M')
        
        revenue_base = 100000
        revenue = np.cumsum(np.random.uniform(10000, 30000, num_records)) + revenue_base
        expenses = np.cumsum(np.random.uniform(5000, 15000, num_records)) + revenue_base * 0.5
        
        data = pd.DataFrame({
            'month': dates,
            'year': [d.year for d in dates],
            'month_name': [d.strftime('%B') for d in dates],
            'revenue': revenue,
            'cost_of_goods': expenses * 0.6,
            'operating_expenses': expenses * 0.3,
            'other_expenses': expenses * 0.1,
            'total_expenses': expenses,
            'ebitda': revenue - expenses * 0.6,
            'tax_rate': np.random.uniform(0.20, 0.30, num_records),
            'employee_count': np.random.randint(50, 300, num_records),
            'market_cap': revenue * np.random.uniform(2, 5, num_records)
        })
        
        data['profit'] = data['revenue'] - data['total_expenses']
        data['profit_margin'] = (data['profit'] / data['revenue']) * 100
        data['revenue_growth'] = data['revenue'].pct_change() * 100
        
        # Save to CSV
        data.to_csv(output_file, index=False)
        print(f"Generated financial data: {output_file} ({num_records} records)")
        
        return data


class AnalyticsExample:
    """Comprehensive analytics example demonstrating all features"""
    
    @staticmethod
    def analyze_sales_data():
        """Complete sales data analysis example"""
        print("\n" + "="*60)
        print("SALES DATA ANALYSIS EXAMPLE")
        print("="*60)
        
        # Generate sample data
        generator = SampleDataGenerator()
        sales_data = generator.generate_sales_data(num_records=1000)
        
        # Initialize services
        aggregator = DataAggregator()
        viz_engine = VisualizationEngine()
        
        # 1. Data Cleaning
        print("\n1. DATA CLEANING")
        print("-" * 40)
        print(f"Original shape: {sales_data.shape}")
        print(f"Missing values:\n{sales_data.isnull().sum()}")
        
        clean_data = aggregator.clean_data(sales_data, drop_duplicates=True, fill_strategy='mean')
        print(f"Cleaned shape: {clean_data.shape}")
        print(f"Missing values after cleaning:\n{clean_data.isnull().sum()}")
        
        # 2. Filtering
        print("\n2. DATA FILTERING")
        print("-" * 40)
        filters = {
            'region': 'North America',
            'revenue': {'$gte': 100}
        }
        filtered_data = aggregator.filter_data(clean_data, filters)
        print(f"Filtered data (North America, revenue >= $100): {len(filtered_data)} records")
        
        # 3. Aggregations
        print("\n3. AGGREGATIONS")
        print("-" * 40)
        
        # Total revenue by product
        product_agg = aggregator.aggregate(
            clean_data,
            group_by='product_name',
            aggregations={'revenue': 'sum', 'quantity': 'sum'}
        )
        print("\nTop 5 products by revenue:")
        print(product_agg.sort_values('revenue', ascending=False).head())
        
        # Revenue by region
        region_agg = aggregator.aggregate(
            clean_data,
            group_by='region',
            aggregations={'revenue': ['sum', 'mean', 'count']}
        )
        print("\nRevenue by region:")
        print(region_agg)
        
        # 4. Statistics
        print("\n4. STATISTICAL ANALYSIS")
        print("-" * 40)
        stats = aggregator.calculate_statistics(clean_data, columns=['quantity', 'unit_price', 'revenue'])
        for col, col_stats in stats.items():
            print(f"\n{col}:")
            print(f"  Mean: ${col_stats['mean']:.2f}")
            print(f"  Median: ${col_stats['median']:.2f}")
            print(f"  Std Dev: ${col_stats['std']:.2f}")
            print(f"  Min: ${col_stats['min']:.2f}, Max: ${col_stats['max']:.2f}")
        
        # 5. Visualizations
        print("\n5. GENERATING VISUALIZATIONS")
        print("-" * 40)
        
        # Revenue by product
        revenue_by_product = clean_data.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(10)
        chart_path = viz_engine.generate_bar_chart(
            revenue_by_product,
            title='Top 10 Products by Revenue',
            ylabel='Revenue ($)',
            filename='example_sales_by_product.png'
        )
        print(f"Generated chart: {chart_path}")
        
        # Revenue distribution
        chart_path = viz_engine.generate_histogram(
            clean_data['revenue'],
            title='Revenue Distribution',
            xlabel='Revenue ($)',
            filename='example_revenue_distribution.png',
            bins=30
        )
        print(f"Generated chart: {chart_path}")
        
        # Regional breakdown
        revenue_by_region = clean_data.groupby('region')['revenue'].sum()
        chart_path = viz_engine.generate_pie_chart(
            revenue_by_region,
            title='Revenue by Region',
            filename='example_revenue_by_region.png'
        )
        print(f"Generated chart: {chart_path}")
        
        print("\n✓ Sales analysis complete!")
    
    @staticmethod
    def analyze_employee_data():
        """Complete employee data analysis example"""
        print("\n" + "="*60)
        print("EMPLOYEE DATA ANALYSIS EXAMPLE")
        print("="*60)
        
        # Generate sample data
        generator = SampleDataGenerator()
        employee_data = generator.generate_employee_data(num_records=500)
        
        # Initialize services
        aggregator = DataAggregator()
        viz_engine = VisualizationEngine()
        
        # 1. Data Overview
        print("\n1. DATA OVERVIEW")
        print("-" * 40)
        print(f"Total employees: {len(employee_data)}")
        print(f"Departments: {employee_data['department'].nunique()}")
        print(f"Salary range: ${employee_data['salary'].min():.2f} - ${employee_data['salary'].max():.2f}")
        
        # 2. Aggregations by Department
        print("\n2. DEPARTMENT AGGREGATIONS")
        print("-" * 40)
        dept_agg = aggregator.aggregate(
            employee_data,
            group_by='department',
            aggregations={'salary': ['mean', 'count'], 'performance_score': 'mean'}
        )
        print("\nAverage salary by department:")
        print(dept_agg)
        
        # 3. Outlier Detection
        print("\n3. OUTLIER DETECTION")
        print("-" * 40)
        outliers = aggregator.detect_outliers(employee_data, columns=['salary', 'performance_score'], method='iqr')
        for col, indices in outliers.items():
            print(f"\n{col}: {len(indices)} outliers detected")
            print(f"  Outlier values sample: {employee_data.loc[indices[:3], col].values}")
        
        # 4. Correlations
        print("\n4. CORRELATION ANALYSIS")
        print("-" * 40)
        correlations = aggregator.calculate_correlations(employee_data)
        print("\nCorrelations:")
        print(correlations)
        
        # 5. Visualizations
        print("\n5. GENERATING VISUALIZATIONS")
        print("-" * 40)
        
        # Salary by department
        dept_salary_data = {dept: employee_data[employee_data['department'] == dept]['salary'].values 
                           for dept in employee_data['department'].unique()}
        chart_path = viz_engine.generate_box_plot(
            dept_salary_data,
            title='Salary Distribution by Department',
            ylabel='Salary ($)',
            filename='example_salary_by_dept.png'
        )
        print(f"Generated chart: {chart_path}")
        
        # Age distribution
        chart_path = viz_engine.generate_histogram(
            employee_data['age'],
            title='Employee Age Distribution',
            xlabel='Age',
            filename='example_age_distribution.png',
            bins=20
        )
        print(f"Generated chart: {chart_path}")
        
        # Performance vs Salary
        chart_path = viz_engine.generate_scatter_plot(
            employee_data['performance_score'],
            employee_data['salary'],
            title='Performance Score vs Salary',
            xlabel='Performance Score (1-10)',
            ylabel='Salary ($)',
            filename='example_performance_vs_salary.png'
        )
        print(f"Generated chart: {chart_path}")
        
        print("\n✓ Employee analysis complete!")
    
    @staticmethod
    def run_all_examples():
        """Run all analytics examples"""
        print("\n" + "="*70)
        print("COMPREHENSIVE ANALYTICS ENGINE EXAMPLES")
        print("="*70)
        
        # Create sample data directory
        Path('sample_data').mkdir(exist_ok=True)
        
        # Change to sample data directory
        original_cwd = os.getcwd()
        os.chdir('sample_data')
        
        try:
            # Run examples
            AnalyticsExample.analyze_sales_data()
            AnalyticsExample.analyze_employee_data()
            
            print("\n" + "="*70)
            print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
            print("="*70)
            print("\nGenerated files:")
            print(f"  - Sample data: sample_sales.csv, sample_employees.csv")
            print(f"  - Charts: Multiple PNG files in analytics/reports/")
        
        finally:
            os.chdir(original_cwd)


def main():
    """Main entry point"""
    AnalyticsExample.run_all_examples()


if __name__ == '__main__':
    main()
