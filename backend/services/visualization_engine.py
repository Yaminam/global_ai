"""
Visualization Engine - handles chart generation and visualization
Uses Matplotlib to generate bar, line, and pie charts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Any, Tuple, Optional
import os
from datetime import datetime
from pathlib import Path


class VisualizationEngine:
    """Engine for generating data visualizations"""
    
    def __init__(self, output_dir: str = './analytics/reports', dpi: int = 300, style: str = 'seaborn-v0_8-darkgrid'):
        """Initialize visualization engine
        
        Args:
            output_dir: Directory to save generated charts
            dpi: DPI for saved images (resolution)
            style: Matplotlib style to use
        """
        self.output_dir = output_dir
        self.dpi = dpi
        self.style = style
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Set matplotlib style
        try:
            plt.style.use(self.style)
        except Exception:
            # Fallback if style not available
            plt.style.use('default')
    
    def _get_output_path(self, filename: str) -> str:
        """Get full path for output file
        
        Args:
            filename: Name of the file
            
        Returns:
            Full path to output file
        """
        return os.path.join(self.output_dir, filename)
    
    def generate_bar_chart(self, 
                          data: Dict[str, float] | pd.Series,
                          title: str = "Bar Chart",
                          xlabel: str = "Categories",
                          ylabel: str = "Values",
                          filename: Optional[str] = None,
                          figsize: Tuple[int, int] = (12, 6),
                          color: str = 'steelblue') -> str:
        """Generate a bar chart
        
        Args:
            data: Dictionary with labels and values or pandas Series
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            filename: Output filename (auto-generated if not provided)
            figsize: Figure size (width, height)
            color: Bar color
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"bar_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Handle different input types
        if isinstance(data, dict):
            labels = list(data.keys())
            values = list(data.values())  # Must be flat values, not lists
        elif isinstance(data, pd.Series):
            labels = data.index.tolist()
            values = data.values
        else:
            raise ValueError("Data must be dictionary or pandas Series")
        
        # Normalize values for plotting to avoid pandas extension array type issues.
        numeric_values = pd.to_numeric(pd.Series(values), errors='coerce').to_numpy(dtype=float)

        # Create bar chart
        bars = ax.bar(labels, numeric_values, color=color, edgecolor='black', linewidth=1.2)
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=10)
        
        # Rotate x-axis labels if needed
        if len(labels) > 10:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_line_chart(self,
                           data: Dict[str, List[float]] | pd.DataFrame,
                           title: str = "Line Chart",
                           xlabel: str = "X-axis",
                           ylabel: str = "Y-axis",
                           filename: Optional[str] = None,
                           figsize: Tuple[int, int] = (12, 6),
                           legend: Optional[List[str]] = None) -> str:
        """Generate a line chart
        
        Args:
            data: Dictionary of series or pandas DataFrame
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            filename: Output filename
            figsize: Figure size
            legend: Legend labels
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"line_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Handle different input types
        if isinstance(data, pd.DataFrame):
            for column in data.columns:
                ax.plot(data.index, data[column], marker='o', linewidth=2, label=column)
        elif isinstance(data, dict):
            for label, values in data.items():
                # For dict input, create x-axis as range or use provided indices
                x_values = range(len(values)) if isinstance(values, (list, np.ndarray)) else values.index
                ax.plot(x_values, values, marker='o', linewidth=2, label=label)
        else:
            raise ValueError("Data must be dictionary or pandas DataFrame")
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='best')
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_pie_chart(self,
                          data: Dict[str, float] | pd.Series,
                          title: str = "Pie Chart",
                          filename: Optional[str] = None,
                          figsize: Tuple[int, int] = (10, 8),
                          explode: Optional[List[float]] = None) -> str:
        """Generate a pie chart
        
        Args:
            data: Dictionary or pandas Series with labels and values
            title: Chart title
            filename: Output filename
            figsize: Figure size
            explode: List of offsets for slices (highlight effect)
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"pie_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Handle different input types
        if isinstance(data, dict):
            labels = list(data.keys())
            values = list(data.values())
        elif isinstance(data, pd.Series):
            labels = data.index.tolist()
            values = data.values
        else:
            raise ValueError("Data must be dictionary or pandas Series")
        
        # Create pie chart
        colors = [tuple(c) for c in plt.get_cmap('Set3')(np.linspace(0, 1, len(labels)))]
        numeric_values = pd.to_numeric(pd.Series(values), errors='coerce').to_numpy(dtype=float)
        pie_result = ax.pie(
            numeric_values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            explode=explode,
            startangle=90,
            textprops={'fontsize': 10}
        )
        autotexts = pie_result[2] if len(pie_result) > 2 else []
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_histogram(self,
                          data: List[float] | pd.Series,
                          title: str = "Histogram",
                          xlabel: str = "Values",
                          ylabel: str = "Frequency",
                          filename: Optional[str] = None,
                          figsize: Tuple[int, int] = (12, 6),
                          bins: int = 30,
                          color: str = 'skyblue') -> str:
        """Generate a histogram
        
        Args:
            data: List or pandas Series of values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            filename: Output filename
            figsize: Figure size
            bins: Number of bins
            color: Bar color
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"histogram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create histogram
        if isinstance(data, pd.Series):
            data = data.dropna()
        
        ax.hist(data, bins=bins, color=color, edgecolor='black', alpha=0.7)
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_scatter_plot(self,
                             x_data: List[float] | pd.Series,
                             y_data: List[float] | pd.Series,
                             title: str = "Scatter Plot",
                             xlabel: str = "X-axis",
                             ylabel: str = "Y-axis",
                             filename: Optional[str] = None,
                             figsize: Tuple[int, int] = (12, 6),
                             color: str = 'steelblue',
                             alpha: float = 0.6) -> str:
        """Generate a scatter plot
        
        Args:
            x_data: X-axis values
            y_data: Y-axis values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            filename: Output filename
            figsize: Figure size
            color: Point color
            alpha: Transparency
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"scatter_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.scatter(x_data, y_data, color=color, alpha=alpha, s=100, edgecolors='black', linewidth=0.5)
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_box_plot(self,
                         data: Dict[str, List[float]] | pd.DataFrame,
                         title: str = "Box Plot",
                         ylabel: str = "Values",
                         filename: Optional[str] = None,
                         figsize: Tuple[int, int] = (12, 6),
                         color: str = 'lightblue') -> str:
        """Generate a box plot
        
        Args:
            data: Dictionary of data series or DataFrame
            title: Chart title
            ylabel: Y-axis label
            filename: Output filename
            figsize: Figure size
            color: Box color
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"box_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Prepare data
        if isinstance(data, dict):
            plot_data = [values for values in data.values()]
            labels = list(data.keys())
        elif isinstance(data, pd.DataFrame):
            plot_data = [data[col].dropna() for col in data.columns]
            labels = data.columns.tolist()
        else:
            raise ValueError("Data must be dictionary or pandas DataFrame")
        
        # Create box plot
        bp = ax.boxplot(plot_data, tick_labels=labels, patch_artist=True)
        
        # Color the boxes
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_heatmap(self,
                        data: pd.DataFrame,
                        title: str = "Heatmap",
                        filename: Optional[str] = None,
                        figsize: Tuple[int, int] = (10, 8),
                        cmap: str = 'coolwarm') -> str:
        """Generate a heatmap from correlation or numeric data
        
        Args:
            data: Pandas DataFrame with numeric data
            title: Chart title
            filename: Output filename
            figsize: Figure size
            cmap: Colormap name
            
        Returns:
            Path to saved chart
        """
        if filename is None:
            filename = f"heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calculate correlation matrix if needed
        is_correlation = data.shape[1] > 1
        if is_correlation:
            corr_data = data.corr()
            im = ax.imshow(corr_data.values, cmap=cmap, aspect='auto', vmin=-1, vmax=1)
        else:
            corr_data = data
            # For raw numeric data, don't force color limits to [-1, 1]
            im = ax.imshow(corr_data.values, cmap=cmap, aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(corr_data.columns)))
        ax.set_yticks(np.arange(len(corr_data.columns)))
        ax.set_xticklabels(corr_data.columns)
        ax.set_yticklabels(corr_data.columns)
        
        # Rotate labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation', rotation=270, labelpad=20)
        
        # Customize chart
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add correlation values in cells
        for i in range(len(corr_data.columns)):
            for j in range(len(corr_data.columns)):
                text = ax.text(j, i, f'{corr_data.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=9)
        
        plt.tight_layout()
        
        output_path = self._get_output_path(filename)
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_multi_chart_report(self,
                                   data: pd.DataFrame,
                                   numeric_columns: Optional[List[str]] = None,
                                   categorical_columns: Optional[List[str]] = None,
                                   filename_prefix: str = "analytics_report") -> Dict[str, str]:
        """Generate a comprehensive report with multiple charts
        
        Args:
            data: Pandas DataFrame
            numeric_columns: List of numeric columns to visualize
            categorical_columns: List of categorical columns to visualize
            filename_prefix: Prefix for generated files
            
        Returns:
            Dictionary with chart names and paths
        """
        charts = {}
        
        # Auto-detect numeric and categorical columns if not provided
        if numeric_columns is None:
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        if categorical_columns is None:
            categorical_columns = data.select_dtypes(include=['object']).columns.tolist()
        
        # Generate histograms for numeric columns
        for col in numeric_columns[:3]:  # Limit to first 3 columns
            try:
                path = self.generate_histogram(
                    data[col],
                    title=f"Distribution of {col}",
                    xlabel=col,
                    filename=f"{filename_prefix}_histogram_{col}.png"
                )
                charts[f"histogram_{col}"] = path
            except Exception as e:
                print(f"Error generating histogram for {col}: {e}")
        
        # Generate bar charts for categorical columns
        for col in categorical_columns[:3]:  # Limit to first 3 columns
            try:
                value_counts = data[col].value_counts().head(10)
                path = self.generate_bar_chart(
                    value_counts,
                    title=f"Distribution of {col}",
                    ylabel="Count",
                    filename=f"{filename_prefix}_bar_{col}.png"
                )
                charts[f"bar_{col}"] = path
            except Exception as e:
                print(f"Error generating bar chart for {col}: {e}")
        
        # Generate correlation heatmap if multiple numeric columns exist
        if len(numeric_columns) > 1:
            try:
                path = self.generate_heatmap(
                    data[numeric_columns],
                    title="Correlation Matrix",
                    filename=f"{filename_prefix}_heatmap.png"
                )
                charts["heatmap_correlation"] = path
            except Exception as e:
                print(f"Error generating heatmap: {e}")
        
        return charts
