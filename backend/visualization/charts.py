"""
Chart generation module using Matplotlib
Generates various charts and saves them as images
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from typing import Optional, List, Dict
import io
import base64


class ChartGenerator:
    """
    Generates charts using Matplotlib
    Supports: bar charts, line charts, scatter plots, histograms, pie charts
    """

    def __init__(self, output_dir: str = 'storage/charts'):
        """Initialize with output directory for saving charts"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def create_bar_chart(self, data: Dict[str, float], title: str,
                        xlabel: str, ylabel: str, filename: str) -> str:
        """
        Create a bar chart using Matplotlib
        Returns: path to saved image
        """
        plt.figure(figsize=(10, 6))
        categories = list(data.keys())
        values = list(data.values())

        plt.bar(categories, values, color='skyblue', edgecolor='navy', alpha=0.7)
        plt.xlabel(xlabel, fontsize=12, fontweight='bold')
        plt.ylabel(ylabel, fontsize=12, fontweight='bold')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_line_chart(self, x_data: List, y_data: List, title: str,
                         xlabel: str, ylabel: str, filename: str) -> str:
        """
        Create a line chart using Matplotlib
        Returns: path to saved image
        """
        plt.figure(figsize=(10, 6))

        plt.plot(x_data, y_data, marker='o', linewidth=2, markersize=6,
                color='blue', markerfacecolor='red', markeredgecolor='darkred')
        plt.xlabel(xlabel, fontsize=12, fontweight='bold')
        plt.ylabel(ylabel, fontsize=12, fontweight='bold')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_histogram(self, data: List[float], title: str,
                        xlabel: str, ylabel: str, bins: int, filename: str) -> str:
        """
        Create a histogram using Matplotlib
        Returns: path to saved image
        """
        plt.figure(figsize=(10, 6))

        plt.hist(data, bins=bins, color='green', alpha=0.7, edgecolor='black')
        plt.xlabel(xlabel, fontsize=12, fontweight='bold')
        plt.ylabel(ylabel, fontsize=12, fontweight='bold')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_scatter_plot(self, x_data: List, y_data: List, title: str,
                           xlabel: str, ylabel: str, filename: str) -> str:
        """
        Create a scatter plot using Matplotlib
        Returns: path to saved image
        """
        plt.figure(figsize=(10, 6))

        plt.scatter(x_data, y_data, alpha=0.6, c='purple', edgecolors='black', s=100)
        plt.xlabel(xlabel, fontsize=12, fontweight='bold')
        plt.ylabel(ylabel, fontsize=12, fontweight='bold')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_pie_chart(self, data: Dict[str, float], title: str, filename: str) -> str:
        """
        Create a pie chart using Matplotlib
        Returns: path to saved image
        """
        plt.figure(figsize=(10, 8))

        labels = list(data.keys())
        sizes = list(data.values())
        cmap = plt.get_cmap('Set3')
        colors = [tuple(color) for color in cmap(np.linspace(0, 1, len(labels)))]

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
        plt.title(title, fontsize=14, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_statistics_visualization(self, statistics: Dict[str, Dict[str, float]],
                                       job_id: str) -> Dict[str, str]:
        """
        Create multiple charts for statistical data
        Returns: {chart_type: filepath}
        """
        charts = {}

        # 1. Bar chart for means
        if statistics:
            means = {col: stats['mean'] for col, stats in statistics.items()}
            charts['means'] = self.create_bar_chart(
                means,
                'Mean Values by Column',
                'Columns',
                'Mean Value',
                f'{job_id}_means.png'
            )

            # 2. Bar chart for standard deviations
            stds = {col: stats['std'] for col, stats in statistics.items()}
            charts['stds'] = self.create_bar_chart(
                stds,
                'Standard Deviation by Column',
                'Columns',
                'Std Dev',
                f'{job_id}_stds.png'
            )

            # 3. Comparison chart (mean vs median)
            fig, ax = plt.subplots(figsize=(12, 6))
            columns = list(statistics.keys())
            x = np.arange(len(columns))
            width = 0.35

            means_list = [statistics[col]['mean'] for col in columns]
            medians_list = [statistics[col]['median'] for col in columns]

            ax.bar(x - width/2, means_list, width, label='Mean', color='skyblue')
            ax.bar(x + width/2, medians_list, width, label='Median', color='orange')

            ax.set_xlabel('Columns', fontweight='bold')
            ax.set_ylabel('Values', fontweight='bold')
            ax.set_title('Mean vs Median Comparison', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(columns, rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()

            comparison_path = os.path.join(self.output_dir, f'{job_id}_comparison.png')
            plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
            plt.close()

            charts['comparison'] = comparison_path

        return charts

    def get_chart_as_base64(self, filepath: str) -> str:
        """
        Read chart image and convert to base64 string
        Useful for embedding in HTML or JSON responses
        """
        with open(filepath, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
