import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re
import numpy as np
import bisect
# Define time windows for each configuration at each distance
# Format: {(distance, config): (start_millis, end_millis)}
CONFIG_WINDOWS = {
    #
    (0, 'DR2_PL0'): (3000, 20000),
    (0, 'DR2_PL1'): (21000, 28000),
    (0, 'DR2_PL2'): (30000, 38000),
    (0, 'DR2_PL3'): (40000, 48000),
    #
    (0, 'DR1_PL0'): (9000, 14000),
    (0, 'DR1_PL1'): (2100, 2800),
    #(0, 'DR1_PL2'): (30000, 38000),
    (0, 'DR1_PL3'): (4500, 8800),
    #
    (0, 'DR250_PL0'): (1000, 10000),
    (0, 'DR250_PL1'): (30000, 45000),
    (0, 'DR250_PL2'): (55000, 70000),
    (0, 'DR250_PL3'): (75000, 85000),
#
    (50, 'DR2_PL0'): (0, 30000),
    (50, 'DR2_PL1'): (43000, 73000),
    (50, 'DR2_PL2'): (110000, 140000),
    (50, 'DR2_PL3'): (79000, 109000),
#
    (50, 'DR1_PL0'): (0, 30000),
    (50, 'DR1_PL1'): (41000, 71000),
    (50, 'DR1_PL2'): (79000, 109000),
    (50, 'DR1_PL3'): (110000, 140000),
#
    (50, 'DR250_PL0'): (1000, 31000),
    (50, 'DR250_PL1'): (48000, 78000),
    (50, 'DR250_PL2'): (78000, 70000),
    (50, 'DR250_PL3'): (75000, 85000),

    #(100, 'DR2_PL0'): (0, 30000),
    #(100, 'DR2_PL1'): (43000, 73000),
    (100, 'DR2_PL2'): (54000, 84000),
    (100, 'DR2_PL3'): (102000, 132000),

   # (100, 'DR1_PL0'): (24000, 54000),
    (100, 'DR1_PL1'): (24000, 54000),
    (100, 'DR1_PL2'): (56000, 86000),
    (100, 'DR1_PL3'): (110000, 140000),

#    (100, 'DR250_PL0'): (1000, 31000),
    (100, 'DR250_PL1'): (20000, 50000),
    (100, 'DR250_PL2'): (115000, 145000),
    (100, 'DR250_PL3'): (85000, 115000),

#    (150, 'DR2_PL0'): (0, 30000),
#    (150, 'DR2_PL1'): (43000, 73000),
    (150, 'DR2_PL2'): (310000, 61000),
    (150, 'DR2_PL3'): (98000, 128000),
#
   # (150, 'DR1_PL0'): (0, 30000),
    #(150, 'DR1_PL1'): (41000, 71000),
    #(150, 'DR1_PL2'): (79000, 109000),
    (150, 'DR1_PL3'): (26000, 56000),

#   (150, 'DR250_PL0'): (1000, 31000),
#   (150, 'DR250_PL1'): (48000, 78000),
    (150, 'DR250_PL2'): (50000, 80000),
    (150, 'DR250_PL3'): (100000, 130000),

   # (200, 'DR2_PL0'): (0, 30000),
    #(200, 'DR2_PL1'): (43000, 73000),
    (200, 'DR2_PL2'): (40000, 70000),
    (200, 'DR2_PL3'): (0, 30000),

 #  (200, 'DR1_PL0'): (0, 30000),
#   (200, 'DR1_PL1'): (41000, 71000),
    (200, 'DR1_PL2'): (30000, 60000),
    (200, 'DR1_PL3'): (75000, 105000),

#   (200, 'DR250_PL0'): (1000, 31000),
#   (200, 'DR250_PL1'): (48000, 78000),
    (200, 'DR250_PL2'): (2500, 50000),
    (200, 'DR250_PL3'): (60000, 90000),

#    (250, 'DR2_PL0'): (0, 30000),
#    (250, 'DR2_PL1'): (20000, 50000),
    (250, 'DR2_PL2'): (0, 30000),
    (250, 'DR2_PL3'): (20000, 50000),
#the switch was likely resting between on and off- skewed data
#   (250, 'DR1_PL0'): (0, 30000),
#   (250, 'DR1_PL1'): (41000, 71000),
    (250, 'DR1_PL2'): (0, 12000),
    (250, 'DR1_PL3'): (12000, 42000),
# again, the switch was likely resting between on and off- skewed data
#  (250, 'DR250_PL0'): (1000, 31000),
#    (250, 'DR250_PL1'): (48000, 78000),
    (250, 'DR250_PL2'): (0, 30000),
    (250, 'DR250_PL3'): (10000, 40000),

#    (300, 'DR2_PL0'): (0, 30000),
#    (300, 'DR2_PL1'): (43000, 73000),
#    (300, 'DR2_PL2'): (110000, 140000),
    (300, 'DR2_PL3'): (0, 30000),

#    (300, 'DR1_PL0'): (0, 30000),
#    (300, 'DR1_PL1'): (41000, 71000),
#    (300, 'DR1_PL2'): (7900, 109000),
    (300, 'DR1_PL3'): (10000, 40000),

#    (300, 'DR250_PL0'): (1000, 31000),
#    (300, 'DR250_PL1'): (48000, 78000),
    (300, 'DR250_PL2'): (5000, 35000),
    (300, 'DR250_PL3'): (00, 55000),

  #  (350, 'DR2_PL0'): (0, 30000),
   # (350, 'DR2_PL1'): (43000, 73000),
    #(350, 'DR2_PL2'): (110000, 140000),
    (350, 'DR2_PL3'): (0, 30000),

#    (350, 'DR1_PL0'): (0, 30000),
#    (350, 'DR1_PL1'): (41000, 71000),
#    (350, 'DR1_PL2'): (79000, 109000),
    (350, 'DR1_PL3'): (0, 30000),

#    (350, 'DR250_PL0'): (1000, 31000),
#    (350, 'DR250_PL1'): (48000, 78000),
    (350, 'DR250_PL2'): (0, 30000),
    (350, 'DR250_PL3'): (15000, 45000),
    # Add more combinations as needed
}

def extract_distance(filename):
    """Extract distance from filename (e.g., '150m1mpbsnew.csv' -> 150)"""
    match = re.match(r'(\d+)m', filename)
    return int(match.group(1)) if match else None

def analyze_packets_by_distance():
    current_dir = Path(__file__).parent
    graphs_dir = current_dir / "graphs"
    graphs_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # Process all CSV files
    for csv_file in current_dir.glob('*m*.csv'):
        distance = extract_distance(csv_file.name)
        if distance is None:
            continue
            
        print(f"\nProcessing {csv_file.name}...")
        df = pd.read_csv(csv_file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%H:%M:%S')
        
        # Create configuration identifier
        df['Config'] = df.apply(lambda x: f'DR{x.DataRate}_PL{x.PowerLevel}', axis=1)
        
        # Process each configuration in the file
        for config in df['Config'].unique():
            if (distance, config) not in CONFIG_WINDOWS:
                print(f"Skipping {config} at {distance}m - no time window defined")
                continue
                
            config_data = df[df['Config'] == config]
            start_millis, end_millis = CONFIG_WINDOWS[(distance, config)]
            
            print(f"{config} at {distance}m: Using period {start_millis}ms to {end_millis}ms")
            
            # Calculate average PPS during specified period
            mask = (config_data['Millis'] >= start_millis) & (config_data['Millis'] <= end_millis)
            stable_data = config_data[mask]
            
            duration = (end_millis - start_millis) / 1000  # convert to seconds
            pps = len(stable_data) / duration if duration > 0 else 0
            
            # Store results
            if config not in results:
                results[config] = {'distances': [], 'pps': []}
            results[config]['distances'].append(distance)
            results[config]['pps'].append(pps)
    
    # Initialize dr_configs dictionary to group configurations by data rate
    dr_configs = {
        'DR250': [],
        'DR1': [],
        'DR2': []
    }
    
    # Group configurations by data rate
    for config in results.keys():
        if 'DR250' in config:
            dr_configs['DR250'].append(config)
        elif 'DR1' in config:
            dr_configs['DR1'].append(config)
        elif 'DR2' in config:
            dr_configs['DR2'].append(config)

    # Define color scheme for power levels (same across all data rates)
    color_schemes = {
        'PL0': '#0066FF',  # Blue
        'PL1': '#33CC33',  # Green
        'PL2': '#FFD700',  # Yellow
        'PL3': '#FF0000'   # Red
    }

    # Define markers for power levels
    markers = {
        'PL0': 's',  # square
        'PL1': '^',  # triangle
        'PL2': 'o',  # circle
        'PL3': '*'   # star
    }

    # Create figure with three subplots sharing y-axis
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    axes = {'DR250': ax1, 'DR1': ax2, 'DR2': ax3}
    
    # Add all possible distances to results
    all_distances = set()
    for config_data in results.values():
        all_distances.update(config_data['distances'])
    all_distances = sorted(all_distances)

    # Fill in zeros for missing distances
    for config in results:
        existing_distances = set(results[config]['distances'])
        for distance in all_distances:
            if distance not in existing_distances:
                idx = bisect.bisect_left(results[config]['distances'], distance)
                results[config]['distances'].insert(idx, distance)
                results[config]['pps'].insert(idx, 0)

    # Plot data for each data rate in separate subplots
    for dr, configs in dr_configs.items():
        ax = axes[dr]
        for config in sorted(configs):
            if config in results:
                distances = np.array(results[config]['distances'])
                pps = np.array(results[config]['pps'])
                sort_idx = np.argsort(distances)
                
                # Extract power level from config string
                pl = config.split('_')[1]  # Gets 'PL0', 'PL1', etc.
                
                ax.plot(distances[sort_idx], pps[sort_idx], 
                       marker=markers[pl],
                       color=color_schemes[pl],  # Simplified color lookup
                       linestyle='-',
                       alpha=0.5,
                       label=config, 
                       markersize=10,
                       markeredgewidth=1,
                       markeredgecolor='black',
                       linewidth=1)
        
        # Customize each subplot
        ax.set_title(f"{dr} Data Rate")
        ax.set_xlabel("Distance (m)")
        ax.grid(True, which='major', linestyle='-', alpha=0.3)
        ax.grid(True, which='minor', linestyle=':', alpha=0.2)
        ax.minorticks_on()
        ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center')

    # Add common y-label
    fig.text(0.04, 0.5, 'Packets per Second', va='center', rotation='vertical')
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Delete existing file if it exists
    outfile = graphs_dir / "distance_comparison_manual.png"
    if outfile.exists():
        outfile.unlink()
    
    # Save with extra space for legends
    plt.savefig(outfile, bbox_inches='tight', dpi=300)
    plt.show()
    
    # Print detailed results
    print("\nDetailed Results:")
    for config, data in sorted(results.items()):
        print(f"\n{config}:")
        for d, p in zip(data['distances'], data['pps']):
            print(f"  {d}m: {p:.2f} packets/second")

if __name__ == '__main__':
    analyze_packets_by_distance()