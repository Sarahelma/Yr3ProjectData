import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def process_file(file_path):
    """Process a single CSV file and return success rate and PPS data"""
    df = pd.read_csv(file_path)
    
    # bin size in milliseconds
    bin_size = 100
    df['Bin'] = (df['Timestamp_ms'] // bin_size).astype(int)
    
    # Group and calculate statistics
    grouped = df.groupby('Bin').agg(
        total=('Index', 'size'),
        successes=('Indicator', 'sum')
    ).reset_index()
    
    # Calculate metrics
    grouped['success_rate'] = (grouped['successes'] / grouped['total']) * 100
    grouped['packets_per_second'] = grouped['successes'] * (1000 / bin_size)
    grouped['bin_start'] = grouped['Bin'] * bin_size
    
    return grouped

def main():
    current_dir = Path(__file__).parent
    graphs_dir = current_dir / "graphs"
    graphs_dir.mkdir(exist_ok=True)
    
    # Define files and their labels
    files = {
        'dynamic2mbpsnew.csv': '2 Mbps',
        'dynamic1mbpsnew.csv': '1 Mbps',
        'dynamic250kbpsnew.csv': '250 kbps'
    }
    
    # Process all files
    data = {}
    for filename, label in files.items():
        file_path = current_dir / filename
        if file_path.exists():
            data[label] = process_file(file_path)
    
    # Plot colors
    colors = ['blue', 'red', 'green']
    
    # Plot 1: Success Rate Comparison
    plt.figure(figsize=(12, 6))
    for (label, grouped), color in zip(data.items(), colors):
        # Filter data between 5000 and 20000 ms
        mask = (grouped['bin_start'] >= 5000) & (grouped['bin_start'] <= 20000)
        filtered_data = grouped[mask]
        
        plt.plot(filtered_data['bin_start'], filtered_data['success_rate'],
                color=color, label=label,
                marker='.', markersize=2, linewidth=1)
    
    plt.title("Success Rate Comparison")
    plt.xlabel("Time (ms)")
    plt.ylabel("Success Rate (%)")
    plt.grid(True, alpha=0.3)
    plt.grid(True, which='minor', alpha=0.15)
    plt.minorticks_on()
    plt.xlim(5000, 20000)  # Set x-axis limits
    plt.ylim(0, 100)  # Set y-axis limits from 0 to 100%
    plt.legend()
    plt.tight_layout()
    plt.savefig(graphs_dir / "success_rate_comparison.png", facecolor='white')
    plt.show()
    
    # Plot 2: Packets per Second Comparison
    plt.figure(figsize=(12, 6))
    for (label, grouped), color in zip(data.items(), colors):
        # Filter data between 5000 and 20000 ms
        mask = (grouped['bin_start'] >= 5000) & (grouped['bin_start'] <= 20000)
        filtered_data = grouped[mask]
        
        plt.plot(filtered_data['bin_start'], filtered_data['packets_per_second'],
                color=color, label=label,
                marker='.', markersize=2, linewidth=1)
    
    plt.title("Packets Per Second Comparison")
    plt.xlabel("Time (ms)")
    plt.ylabel("Packets/s")
    plt.grid(True, alpha=0.3)
    plt.grid(True, which='minor', alpha=0.15)
    plt.minorticks_on()
    plt.xlim(5000, 20000)  # Set x-axis limits
    plt.legend()
    plt.tight_layout()
    plt.savefig(graphs_dir / "pps_comparison.png", facecolor='white')
    plt.show()

if __name__ == '__main__':
    main()