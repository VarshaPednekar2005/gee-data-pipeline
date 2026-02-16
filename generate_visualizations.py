#!/usr/bin/env python3
"""
Generate cost comparison visualizations for GEE Data Pipeline
"""

import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
colors_pipeline = ['#2ecc71', '#27ae60', '#229954']
colors_gee = ['#e74c3c', '#c0392b']

def create_cost_comparison_pie():
    """Pie charts comparing costs across regions"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Mumbai
    sizes_mumbai = [0.01, 6000, 24000]  # $0 shown as $0.01 for visibility
    labels_mumbai = ['This Pipeline\n$0/year', 'GEE Basic\n$6,000/year', 'GEE Pro\n$24,000/year']
    axes[0].pie(sizes_mumbai, labels=labels_mumbai, autopct='%1.1f%%', startangle=90, 
                colors=['#2ecc71', '#e74c3c', '#c0392b'])
    axes[0].set_title('Mumbai (600 km²)\nAll Datasets - Annual Composites', fontsize=14, fontweight='bold')
    
    # Maharashtra
    sizes_maha = [58, 6000, 24000]
    labels_maha = ['This Pipeline\n$58/year', 'GEE Basic\n$6,000/year', 'GEE Pro\n$24,000/year']
    axes[1].pie(sizes_maha, labels=labels_maha, autopct='%1.1f%%', startangle=90,
                colors=['#2ecc71', '#e74c3c', '#c0392b'])
    axes[1].set_title('Maharashtra (307,713 km²)\nAll Datasets - Annual Composites', fontsize=14, fontweight='bold')
    
    # India
    sizes_india = [568, 6000, 24000]
    labels_india = ['This Pipeline\n$568/year', 'GEE Basic\n$6,000/year', 'GEE Pro\n$24,000/year']
    axes[2].pie(sizes_india, labels=labels_india, autopct='%1.1f%%', startangle=90,
                colors=['#2ecc71', '#e74c3c', '#c0392b'])
    axes[2].set_title('India (3,287,263 km²)\nAll Datasets - Annual Composites', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('cost_comparison_pie.png', dpi=300, bbox_inches='tight')
    print("✓ Created: cost_comparison_pie.png")

def create_storage_cost_bars():
    """Bar chart showing storage costs by composite method"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    methods = ['Individual', 'Time Series', 'Monthly', 'Annual']
    
    # Mumbai
    mumbai_costs = [36, 8, 1, 0]
    axes[0].bar(methods, mumbai_costs, color='#3498db')
    axes[0].set_ylabel('Cost ($/year)', fontsize=12)
    axes[0].set_title('Mumbai (600 km²)\nSentinel-2 Storage Costs', fontsize=14, fontweight='bold')
    axes[0].set_ylim(0, 40)
    for i, v in enumerate(mumbai_costs):
        axes[0].text(i, v + 1, f'${v}', ha='center', fontweight='bold')
    
    # Maharashtra
    maha_costs = [1798, 374, 60, 7]
    axes[1].bar(methods, maha_costs, color='#e67e22')
    axes[1].set_ylabel('Cost ($/year)', fontsize=12)
    axes[1].set_title('Maharashtra (307,713 km²)\nSentinel-2 Storage Costs', fontsize=14, fontweight='bold')
    axes[1].set_ylim(0, 2000)
    for i, v in enumerate(maha_costs):
        axes[1].text(i, v + 50, f'${v}', ha='center', fontweight='bold')
    
    # India
    india_costs = [16392, 4680, 614, 66]
    axes[2].bar(methods, india_costs, color='#9b59b6')
    axes[2].set_ylabel('Cost ($/year)', fontsize=12)
    axes[2].set_title('India (3,287,263 km²)\nSentinel-2 Storage Costs', fontsize=14, fontweight='bold')
    axes[2].set_ylim(0, 18000)
    for i, v in enumerate(india_costs):
        axes[2].text(i, v + 500, f'${v}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('storage_cost_bars.png', dpi=300, bbox_inches='tight')
    print("✓ Created: storage_cost_bars.png")

def create_dataset_comparison():
    """Compare costs across different dataset types"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))
    
    datasets = ['Sentinel-2', 'Landsat 8/9', 'Landsat 7', 'MODIS', 'Sentinel-1', 
                'CHIRPS', 'ERA5', 'Land Cover', 'DEM']
    
    # Mumbai - all free
    mumbai_costs = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    axes[0].barh(datasets, mumbai_costs, color='#2ecc71')
    axes[0].set_xlabel('Cost ($/year)', fontsize=12)
    axes[0].set_title('Mumbai (600 km²)\nAnnual Composites - All Datasets', fontsize=14, fontweight='bold')
    axes[0].set_xlim(0, 1)
    axes[0].text(0.5, 4, 'ALL FREE\n(under 5GB)', ha='center', va='center', 
                fontsize=16, fontweight='bold', color='green')
    
    # Maharashtra
    maha_costs = [7, 5, 10, 2, 8, 4, 7, 1, 0]
    axes[1].barh(datasets, maha_costs, color='#e67e22')
    axes[1].set_xlabel('Cost ($/year)', fontsize=12)
    axes[1].set_title('Maharashtra (307,713 km²)\nAnnual Composites - All Datasets', fontsize=14, fontweight='bold')
    for i, v in enumerate(maha_costs):
        if v > 0:
            axes[1].text(v + 0.3, i, f'${v}', va='center', fontweight='bold')
    
    # India
    india_costs = [65, 49, 90, 23, 83, 42, 71, 14, 0]
    axes[2].barh(datasets, india_costs, color='#9b59b6')
    axes[2].set_xlabel('Cost ($/year)', fontsize=12)
    axes[2].set_title('India (3,287,263 km²)\nAnnual Composites - All Datasets', fontsize=14, fontweight='bold')
    for i, v in enumerate(india_costs):
        if v > 0:
            axes[2].text(v + 2, i, f'${v}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('dataset_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Created: dataset_comparison.png")

def create_5year_tco():
    """5-year Total Cost of Ownership comparison"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    regions = ['Mumbai\n(Annual)', 'Mumbai\n(Monthly)', 'Maharashtra\n(Annual)', 
               'Maharashtra\n(Monthly)', 'India\n(Annual)', 'India\n(Monthly)']
    
    pipeline_costs = [0, 65, 290, 1390, 2840, 14230]
    gee_basic_costs = [30000] * 6
    gee_pro_costs = [120000] * 6
    
    x = np.arange(len(regions))
    width = 0.25
    
    bars1 = ax.bar(x - width, pipeline_costs, width, label='This Pipeline', color='#2ecc71')
    bars2 = ax.bar(x, gee_basic_costs, width, label='GEE Basic', color='#e74c3c')
    bars3 = ax.bar(x + width, gee_pro_costs, width, label='GEE Pro', color='#c0392b')
    
    ax.set_ylabel('5-Year Total Cost ($)', fontsize=12, fontweight='bold')
    ax.set_title('5-Year Total Cost of Ownership\nAll Datasets', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(regions)
    ax.legend(fontsize=12)
    ax.set_ylim(0, 130000)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 2000,
                       f'${int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('5year_tco.png', dpi=300, bbox_inches='tight')
    print("✓ Created: 5year_tco.png")

def create_savings_multiplier():
    """Show savings multiplier across regions"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    regions = ['Mumbai', 'Maharashtra', 'India']
    savings_basic = [float('inf'), 103, 11]  # Use 1000 for infinity in visualization
    savings_pro = [float('inf'), 414, 42]
    
    # Replace infinity with 1000 for visualization
    savings_basic_viz = [1000 if x == float('inf') else x for x in savings_basic]
    savings_pro_viz = [1000 if x == float('inf') else x for x in savings_pro]
    
    x = np.arange(len(regions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, savings_basic_viz, width, label='vs GEE Basic', color='#3498db')
    bars2 = ax.bar(x + width/2, savings_pro_viz, width, label='vs GEE Pro', color='#9b59b6')
    
    ax.set_ylabel('Cost Savings Multiplier', fontsize=12, fontweight='bold')
    ax.set_title('This Pipeline Savings vs GEE Commercial\n(Annual Composites - All Datasets)', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(regions)
    ax.legend(fontsize=12)
    ax.set_ylim(0, 1100)
    
    # Add value labels
    for i, (b, p) in enumerate(zip(savings_basic, savings_pro)):
        b_label = '∞' if b == float('inf') else f'{int(b)}x'
        p_label = '∞' if p == float('inf') else f'{int(p)}x'
        ax.text(i - width/2, savings_basic_viz[i] + 30, b_label, ha='center', fontweight='bold', fontsize=12)
        ax.text(i + width/2, savings_pro_viz[i] + 30, p_label, ha='center', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('savings_multiplier.png', dpi=300, bbox_inches='tight')
    print("✓ Created: savings_multiplier.png")

def create_all_visualizations():
    """Generate all visualization charts"""
    print("\n🎨 Generating cost comparison visualizations...\n")
    
    create_cost_comparison_pie()
    create_storage_cost_bars()
    create_dataset_comparison()
    create_5year_tco()
    create_savings_multiplier()
    
    print("\n✅ All visualizations created successfully!")
    print("\nGenerated files:")
    print("  1. cost_comparison_pie.png - Pie charts comparing costs")
    print("  2. storage_cost_bars.png - Storage costs by composite method")
    print("  3. dataset_comparison.png - Costs across different datasets")
    print("  4. 5year_tco.png - 5-year total cost of ownership")
    print("  5. savings_multiplier.png - Savings multiplier comparison")

if __name__ == '__main__':
    create_all_visualizations()
