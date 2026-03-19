"""
Visualization Scripts - Example scripts showing how to generate various visualizations
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from backend.services.visualization_engine import VisualizationEngine
from backend.services.data_aggregator import DataAggregator
from pathlib import Path
import os
import json
from datetime import datetime, timedelta


class VisualizationDemo:
    """Demonstration of visualization capabilities"""
    
    def __init__(self, output_dir: str = './analytics/reports'):
        """Initialize visualization demo
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        self.viz_engine = VisualizationEngine(output_dir=output_dir)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_sales_analysis(self, data: Optional[pd.DataFrame] = None) -> Dict[str, str]:
        """Generate sales analysis visualizations
        
        Args:
            data: Sales DataFrame or None to generate sample data
            
        Returns:
            Dictionary of chart paths
        """
        # Generate sample data if not provided
        if data is None:
            np.random.seed(42)
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            data = pd.DataFrame({
                'date': dates,
                'sales': np.random.uniform(1000, 5000, 100),
                'quantity': np.random.randint(10, 100, 100),
                'product': np.random.choice(['Product A', 'Product B', 'Product C'], 100),
                'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
            })
        
        charts = {}
        
        # 1. Daily sales trend line chart
        daily_sales = data.groupby('date')['sales'].sum()
        path = self.viz_engine.generate_line_chart(
            {'Sales Trend': daily_sales.values},
            title='Daily Sales Trend',
            xlabel='Days',
            ylabel='Sales ($)',
            filename='sales_trend_line.png'
        )
        charts['daily_sales_trend'] = path
        
        # 2. Sales by product bar chart
        product_sales = data.groupby('product')['sales'].sum().sort_values(ascending=False)
        path = self.viz_engine.generate_bar_chart(
            product_sales,
            title='Sales by Product',
            xlabel='Product',
            ylabel='Total Sales ($)',
            filename='sales_by_product.png'
        )
        charts['product_sales'] = path
        
        # 3. Sales distribution histogram
        path = self.viz_engine.generate_histogram(
            data['sales'],
            title='Sales Distribution',
            xlabel='Sales Amount ($)',
            ylabel='Frequency',
            filename='sales_histogram.png',
            bins=20
        )
        charts['sales_distribution'] = path
        
        # 4. Regional sales pie chart
        region_sales = data.groupby('region')['sales'].sum()
        path = self.viz_engine.generate_pie_chart(
            region_sales,
            title='Sales by Region',
            filename='sales_by_region.png',
            explode=[0.05 if i == region_sales.idxmax() else 0 for i in range(len(region_sales))]
        )
        charts['regional_sales'] = path
        
        # 5. Quantity vs Sales scatter plot
        path = self.viz_engine.generate_scatter_plot(
            data['quantity'],
            data['sales'],
            title='Quantity vs Sales',
            xlabel='Quantity (units)',
            ylabel='Sales ($)',
            filename='quantity_vs_sales.png'
        )
        charts['quantity_vs_sales'] = path
        
        return charts
    
    def generate_employee_analytics(self, data: Optional[pd.DataFrame] = None) -> Dict[str, str]:
        """Generate employee analytics visualizations
        
        Args:
            data: Employee DataFrame or None to generate sample data
            
        Returns:
            Dictionary of chart paths
        """
        # Generate sample data if not provided
        if data is None:
            np.random.seed(42)
            data = pd.DataFrame({
                'employee_id': range(1, 101),
                'age': np.random.randint(22, 65, 100),
                'salary': np.random.uniform(40000, 200000, 100),
                'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR'], 100),
                'performance_score': np.random.uniform(1, 10, 100),
                'years_employed': np.random.randint(0, 30, 100)
            })
        
        charts = {}
        
        # 1. Age distribution histogram
        path = self.viz_engine.generate_histogram(
            data['age'],
            title='Employee Age Distribution',
            xlabel='Age (years)',
            ylabel='Count',
            filename='age_distribution.png',
            bins=15
        )
        charts['age_distribution'] = path
        
        # 2. Salary by department box plot
        dept_salary_data = {dept: data[data['department'] == dept]['salary'].values 
                           for dept in data['department'].unique()}
        path = self.viz_engine.generate_box_plot(
            dept_salary_data,
            title='Salary Distribution by Department',
            ylabel='Salary ($)',
            filename='salary_by_department.png'
        )
        charts['salary_by_dept'] = path
        
        # 3. Employee count by department bar chart
        dept_counts = data['department'].value_counts()
        path = self.viz_engine.generate_bar_chart(
            dept_counts,
            title='Employees by Department',
            xlabel='Department',
            ylabel='Count',
            filename='employees_by_dept.png',
            color='coral'
        )
        charts['employees_count'] = path
        
        # 4. Performance score histogram
        path = self.viz_engine.generate_histogram(
            data['performance_score'],
            title='Performance Score Distribution',
            xlabel='Score (1-10)',
            ylabel='Count',
            filename='performance_distribution.png',
            bins=10,
            color='lightgreen'
        )
        charts['performance_distribution'] = path
        
        # 5. Salary vs Performance scatter
        path = self.viz_engine.generate_scatter_plot(
            data['performance_score'],
            data['salary'],
            title='Performance vs Salary',
            xlabel='Performance Score',
            ylabel='Salary ($)',
            filename='performance_vs_salary.png'
        )
        charts['performance_vs_salary'] = path
        
        # 6. Correlation heatmap
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        path = self.viz_engine.generate_heatmap(
            data[numeric_cols],
            title='Employee Data Correlations',
            filename='employee_correlations.png'
        )
        charts['correlations'] = path
        
        return charts
    
    def generate_customer_analytics(self, data: Optional[pd.DataFrame] = None) -> Dict[str, str]:
        """Generate customer analytics visualizations
        
        Args:
            data: Customer DataFrame or None to generate sample data
            
        Returns:
            Dictionary of chart paths
        """
        # Generate sample data if not provided
        if data is None:
            np.random.seed(42)
            data = pd.DataFrame({
                'customer_id': range(1, 201),
                'age': np.random.randint(18, 80, 200),
                'lifetime_value': np.random.exponential(2000, 200),
                'purchase_frequency': np.random.randint(1, 52, 200),
                'last_purchase_days_ago': np.random.randint(0, 365, 200),
                'segment': np.random.choice(['Premium', 'Standard', 'Basic'], 200),
                'satisfaction_score': np.random.uniform(1, 5, 200)
            })
        
        charts = {}
        
        # 1. Customer segment pie chart
        segment_counts = data['segment'].value_counts()
        path = self.viz_engine.generate_pie_chart(
            segment_counts,
            title='Customer Segments',
            filename='customer_segments.png'
        )
        charts['segments'] = path
        
        # 2. Lifetime value by segment box plot
        segment_ltv_data = {seg: data[data['segment'] == seg]['lifetime_value'].values 
                           for seg in data['segment'].unique()}
        path = self.viz_engine.generate_box_plot(
            segment_ltv_data,
            title='Lifetime Value by Segment',
            ylabel='Lifetime Value ($)',
            filename='ltv_by_segment.png'
        )
        charts['ltv_by_segment'] = path
        
        # 3. Purchase frequency histogram
        path = self.viz_engine.generate_histogram(
            data['purchase_frequency'],
            title='Customer Purchase Frequency',
            xlabel='Purchases per Year',
            ylabel='Count',
            filename='purchase_frequency.png',
            bins=20,
            color='steelblue'
        )
        charts['purchase_frequency'] = path
        
        # 4. Lifetime value vs satisfaction scatter
        path = self.viz_engine.generate_scatter_plot(
            data['satisfaction_score'],
            data['lifetime_value'],
            title='Satisfaction vs Lifetime Value',
            xlabel='Satisfaction Score (1-5)',
            ylabel='Lifetime Value ($)',
            filename='satisfaction_vs_ltv.png'
        )
        charts['satisfaction_vs_ltv'] = path
        
        # 5. Average LTV line chart by age groups
        age_bins = [0, 25, 35, 45, 55, 65, 100]
        age_groups = pd.cut(data['age'], bins=age_bins)
        avg_ltv_by_age = data.groupby(age_groups)['lifetime_value'].mean()
        
        path = self.viz_engine.generate_line_chart(
            {'Avg Lifetime Value': avg_ltv_by_age.values},
            title='Average Lifetime Value by Age Group',
            xlabel='Age Group',
            ylabel='Avg Lifetime Value ($)',
            filename='ltv_by_age.png'
        )
        charts['ltv_by_age'] = path
        
        return charts
    
    def generate_financial_analysis(self, data: Optional[pd.DataFrame] = None) -> Dict[str, str]:
        """Generate financial analysis visualizations
        
        Args:
            data: Financial DataFrame or None to generate sample data
            
        Returns:
            Dictionary of chart paths
        """
        # Generate sample data if not provided
        if data is None:
            np.random.seed(42)
            months = pd.date_range('2023-01-01', periods=24, freq='M')
            data = pd.DataFrame({
                'month': months,
                'revenue': np.cumsum(np.random.uniform(10000, 30000, 24)) + 100000,
                'expenses': np.cumsum(np.random.uniform(5000, 15000, 24)) + 50000,
                'profit_margin': np.random.uniform(0.15, 0.45, 24)
            })
            data['profit'] = data['revenue'] - data['expenses']
        
        charts = {}
        
        # 1. Revenue and expenses trend line chart
        path = self.viz_engine.generate_line_chart(
            pd.DataFrame({
                'Revenue': data['revenue'].values,
                'Expenses': data['expenses'].values,
                'Profit': data['profit'].values
            }),
            title='Financial Trends Over Time',
            xlabel='Month',
            ylabel='Amount ($)',
            filename='financial_trends.png'
        )
        charts['financial_trends'] = path
        
        # 2. Profit margin trend
        path = self.viz_engine.generate_line_chart(
            {'Profit Margin': data['profit_margin'].values},
            title='Profit Margin Trend',
            xlabel='Month',
            ylabel='Margin (%)',
            filename='profit_margin_trend.png'
        )
        charts['profit_margin'] = path
        
        # 3. Latest month breakdown pie chart
        latest = data.iloc[-1]
        breakdown = pd.Series({
            'Profit': latest['profit'],
            'Expenses': latest['expenses']
        })
        path = self.viz_engine.generate_pie_chart(
            breakdown,
            title='Latest Month: Revenue Breakdown',
            filename='latest_month_breakdown.png'
        )
        charts['month_breakdown'] = path
        
        # 4. Cumulative revenue bar chart (last 6 months)
        last_6_months = data.tail(6)
        path = self.viz_engine.generate_bar_chart(
            pd.Series(last_6_months['revenue'].values, 
                     index=[d.strftime('%b') for d in last_6_months['month']]),
            title='Revenue - Last 6 Months',
            xlabel='Month',
            ylabel='Revenue ($)',
            filename='revenue_last_6_months.png',
            color='green'
        )
        charts['revenue_6m'] = path
        
        return charts
    
    def generate_comprehensive_report(self, output_file: str = 'visualization_report.json'):
        """Generate a comprehensive report with all visualization examples
        
        Args:
            output_file: Output JSON file with metadata
            
        Returns:
            Dictionary with all generated charts and metadata
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Sales Analysis
        print("Generating Sales Analytics...")
        sales_charts = self.generate_sales_analysis()
        report['sections']['sales_analysis'] = {
            'title': 'Sales Analysis',
            'charts': sales_charts
        }
        
        # Employee Analytics
        print("Generating Employee Analytics...")
        employee_charts = self.generate_employee_analytics()
        report['sections']['employee_analytics'] = {
            'title': 'Employee Analytics',
            'charts': employee_charts
        }
        
        # Customer Analytics
        print("Generating Customer Analytics...")
        customer_charts = self.generate_customer_analytics()
        report['sections']['customer_analytics'] = {
            'title': 'Customer Analytics',
            'charts': customer_charts
        }
        
        # Financial Analysis
        print("Generating Financial Analysis...")
        financial_charts = self.generate_financial_analysis()
        report['sections']['financial_analysis'] = {
            'title': 'Financial Analysis',
            'charts': financial_charts
        }
        
        # Save report metadata
        report_path = os.path.join(self.output_dir, output_file)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nComprehensive report generated at: {report_path}")
        
        return report


def main():
    """Main function to generate all visualization examples"""
    
    # Initialize visualization demo
    demo = VisualizationDemo()
    
    # Generate comprehensive report
    report = demo.generate_comprehensive_report()
    
    # Print summary
    print("\n" + "="*50)
    print("VISUALIZATION GENERATION COMPLETE")
    print("="*50)
    print(f"\nGenerated {sum(len(section['charts']) for section in report['sections'].values())} visualizations")
    print(f"Output directory: {demo.output_dir}")
    
    # Print details
    for section_name, section_data in report['sections'].items():
        print(f"\n{section_data['title']}:")
        for chart_name in section_data['charts'].keys():
            print(f"  - {chart_name}")


if __name__ == '__main__':
    main()
