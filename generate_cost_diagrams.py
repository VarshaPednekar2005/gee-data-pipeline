#!/usr/bin/env python3
"""Generate 3D cost comparison diagrams for all composite methods and datasets"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Dataset names
datasets = ['Sentinel-2', 'Landsat 8/9', 'Landsat 7', 'Landsat 4-5', 'MODIS', 
            'Sentinel-1', 'CHIRPS', 'ERA5', 'Land Cover', 'DEM']

# Composite methods
methods = ['Individual', 'Time Series', 'Monthly', 'Annual']

# Cost data for Mumbai (in $/year)
mumbai_costs = {
    'Sentinel-2': [36, 8, 1, 0],
    'Landsat 8/9': [28, 6, 0.8, 0],
    'Landsat 7': [52, 11, 1.5, 0],
    'Landsat 4-5': [75, 16, 2.2, 0],
    'MODIS': [18, 4, 0.5, 0],
    'Sentinel-1': [48, 10, 2, 0],
    'CHIRPS': [42, 9, 1.8, 0],
    'ERA5': [85, 18, 3.5, 0],
    'Land Cover': [12, 2.5, 0.3, 0],
    'DEM': [2, 0.5, 0.05, 0]
}

# Cost data for Maharashtra (in $/year)
maharashtra_costs = {
    'Sentinel-2': [1798, 374, 60, 7],
    'Landsat 8/9': [1350, 280, 44, 5],
    'Landsat 7': [2400, 500, 80, 10],
    'Landsat 4-5': [3500, 730, 117, 14],
    'MODIS': [650, 135, 22, 2],
    'Sentinel-1': [2150, 450, 72, 8],
    'CHIRPS': [900, 190, 30, 4],
    'ERA5': [1900, 395, 63, 7],
    'Land Cover': [430, 90, 14, 1],
    'DEM': [25, 5, 0.8, 0]
}

# Cost data for India (in $/year)
india_costs = {
    'Sentinel-2': [16392, 4680, 614, 65],
    'Landsat 8/9': [12300, 3510, 456, 49],
    'Landsat 7': [21900, 6250, 820, 90],
    'Landsat 4-5': [31900, 9100, 1193, 131],
    'MODIS': [5900, 1685, 221, 23],
    'Sentinel-1': [19600, 5600, 734, 83],
    'CHIRPS': [8200, 2340, 307, 42],
    'ERA5': [17300, 4940, 648, 71],
    'Land Cover': [3900, 1115, 146, 14],
    'DEM': [230, 65, 8.5, 0]
}

def create_3d_cost_comparison():
    """3D surface plot comparing all methods and datasets"""
    fig = plt.figure(figsize=(20, 7))
    
    regions = [
        ('Mumbai', mumbai_costs, 1),
        ('Maharashtra', maharashtra_costs, 2),
        ('India', india_costs, 3)
    ]
    
    for region_name, cost_data, subplot_idx in regions:
        ax = fig.add_subplot(1, 3, subplot_idx, projection='3d')
        
        # Prepare data matrix
        X, Y = np.meshgrid(range(len(datasets)), range(len(methods)))
        Z = np.zeros((len(methods), len(datasets)))
        
        for i, dataset in enumerate(datasets):
            for j, method in enumerate(methods):
                Z[j, i] = cost_data[dataset][j]
        
        # Create surface plot with gradient colors
        surf = ax.plot_surface(X, Y, Z, cmap='RdYlGn_r', alpha=0.9, 
                              edgecolor='black', linewidth=0.3, antialiased=True)
        
        # Add contour lines at the bottom
        ax.contour(X, Y, Z, zdir='z', offset=0, cmap='RdYlGn_r', alpha=0.4, linewidths=1)
        
        # Labels with better formatting
        ax.set_xlabel('\nDataset', fontsize=11, fontweight='bold', labelpad=12)
        ax.set_ylabel('\nMethod', fontsize=11, fontweight='bold', labelpad=12)
        ax.set_zlabel('\nCost ($/year)', fontsize=11, fontweight='bold', labelpad=12)
        ax.set_title(f'{region_name}\nCost Analysis (All Methods × Datasets)', 
                    fontsize=13, fontweight='bold', pad=25)
        
        # Set ticks with better labels
        ax.set_xticks(range(len(datasets)))
        ax.set_xticklabels([d.replace(' ', '\n') for d in datasets], 
                          rotation=0, ha='center', fontsize=8)
        ax.set_yticks(range(len(methods)))
        ax.set_yticklabels(methods, fontsize=9)
        
        # Better viewing angle
        ax.view_init(elev=20, azim=135)
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1, label='Cost ($/year)')
        
        # Grid styling
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
    
    plt.tight_layout()
    plt.savefig('images/3d_cost_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: images/3d_cost_comparison.png")

def create_method_comparison_chart():
    """Compare all 4 methods across regions"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    regions_data = {
        'Mumbai': mumbai_costs,
        'Maharashtra': maharashtra_costs,
        'India': india_costs
    }
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    for idx, method in enumerate(methods):
        ax = axes[idx // 2, idx % 2]
        
        # Prepare data for this method
        x = np.arange(len(datasets))
        width = 0.25
        
        for i, (region, cost_data) in enumerate(regions_data.items()):
            costs = [cost_data[dataset][idx] for dataset in datasets]
            ax.bar(x + i * width, costs, width, label=region, color=colors[i], alpha=0.8)
        
        ax.set_xlabel('Dataset', fontsize=11, fontweight='bold')
        ax.set_ylabel('Cost ($/year)', fontsize=11, fontweight='bold')
        ax.set_title(f'{method} Composites\nCost Comparison', fontsize=13, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels([d[:10] for d in datasets], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('images/method_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Created: images/method_comparison.png")

def create_dataset_cost_heatmap():
    """Heatmap showing cost for each dataset-method-region combination"""
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    
    regions_data = [
        ('Mumbai', mumbai_costs),
        ('Maharashtra', maharashtra_costs),
        ('India', india_costs)
    ]
    
    for idx, (region_name, cost_data) in enumerate(regions_data):
        # Prepare matrix
        matrix = np.zeros((len(datasets), len(methods)))
        for i, dataset in enumerate(datasets):
            for j, method in enumerate(methods):
                matrix[i, j] = cost_data[dataset][j]
        
        # Create heatmap
        im = axes[idx].imshow(matrix, cmap='RdYlGn_r', aspect='auto')
        
        # Labels
        axes[idx].set_xticks(range(len(methods)))
        axes[idx].set_xticklabels(methods, rotation=45, ha='right')
        axes[idx].set_yticks(range(len(datasets)))
        axes[idx].set_yticklabels(datasets)
        axes[idx].set_title(f'{region_name}\nCost Heatmap ($/year)', fontsize=13, fontweight='bold')
        
        # Add values
        for i in range(len(datasets)):
            for j in range(len(methods)):
                value = matrix[i, j]
                text_color = 'white' if value > matrix.max() / 2 else 'black'
                axes[idx].text(j, i, f'${value:.0f}' if value > 0 else 'FREE',
                             ha='center', va='center', color=text_color, fontsize=8)
        
        # Colorbar
        plt.colorbar(im, ax=axes[idx], label='Cost ($/year)')
    
    plt.tight_layout()
    plt.savefig('images/cost_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Created: images/cost_heatmap.png")

def create_savings_by_method():
    """Show savings compared to GEE for each method"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    gee_basic = 6000
    gee_pro = 24000
    
    regions_data = {
        'Mumbai': mumbai_costs,
        'Maharashtra': maharashtra_costs,
        'India': india_costs
    }
    
    for idx, method in enumerate(methods):
        ax = axes[idx // 2, idx % 2]
        
        # Calculate total cost for each region
        region_totals = []
        for region, cost_data in regions_data.items():
            total = sum(cost_data[dataset][idx] for dataset in datasets)
            region_totals.append(total)
        
        x = np.arange(len(regions_data))
        width = 0.25
        
        ax.bar(x - width, region_totals, width, label='This Pipeline', color='#2ecc71', alpha=0.8)
        ax.bar(x, [gee_basic] * len(x), width, label='GEE Basic', color='#e74c3c', alpha=0.8)
        ax.bar(x + width, [gee_pro] * len(x), width, label='GEE Pro', color='#c0392b', alpha=0.8)
        
        ax.set_ylabel('Cost ($/year)', fontsize=11, fontweight='bold')
        ax.set_title(f'{method} Composites\nTotal Cost (All Datasets)', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(regions_data.keys())
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add savings text
        for i, (region, total) in enumerate(zip(regions_data.keys(), region_totals)):
            if total > 0:
                savings_basic = gee_basic / total
                ax.text(i, total + 500, f'{savings_basic:.0f}x\nsavings', 
                       ha='center', fontsize=9, fontweight='bold', color='green')
    
    plt.tight_layout()
    plt.savefig('images/savings_by_method.png', dpi=300, bbox_inches='tight')
    print("✓ Created: images/savings_by_method.png")

if __name__ == '__main__':
    print("Generating cost comparison diagrams...")
    create_method_comparison_chart()
    create_dataset_cost_heatmap()
    create_savings_by_method()
    print("\n✓ All diagrams generated successfully!")
    print("\nGenerated files:")
    print("  - images/method_comparison.png (Compare methods across regions)")
    print("  - images/cost_heatmap.png (Heatmap of all combinations)")
    print("  - images/savings_by_method.png (Savings vs GEE by method)")
