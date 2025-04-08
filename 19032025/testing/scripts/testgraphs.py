import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import os

def process_csv(csv_path, graphs_dir):
    """Process a single CSV file and generate graphs"""
    # Get CSV filename without extension for graph titles
    csv_name = csv_path.stem
    
    df = pd.read_csv(csv_path)
    
    # Convert timestamp strings to datetime objects
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%H:%M:%S')
    
    # Create a unique identifier for each DataRate-PowerLevel combination
    df['Config'] = df.apply(lambda x: f'DR{x.DataRate}_PL{x.PowerLevel}', axis=1)
    
    # bin size in milliseconds
    bin_size = 100
    df['Bin'] = (df['Millis'] // bin_size).astype(int)
    
    # Get unique configurations
    configs = df['Config'].unique()
    
    # Create separate plots for each metric
    
    # 1. Success Rate by Configuration
    plt.figure(figsize=(12, 6))
    for config in configs:
        config_data = df[df['Config'] == config]
        grouped = config_data.groupby('Bin').agg(
            count=('Indicator', 'size'),
            successes=('Indicator', 'sum')
        ).reset_index()
        grouped['success_rate'] = (grouped['successes'] / grouped['count']) * 100
        grouped['bin_start'] = grouped['Bin'] * bin_size
        
        plt.plot(grouped['bin_start'], grouped['success_rate'], 
                marker='o', linestyle='-', label=config)
    
    plt.title("Success Rate by Configuration")
    plt.xlabel("Milliseconds")
    plt.ylabel("Success Rate (%)")
    plt.grid(True)
    plt.legend()
    
    # Add minor ticks
    plt.minorticks_on()
    plt.grid(True, which='major', linestyle='-')
    plt.grid(True, which='minor', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    # Delete existing file if it exists
    outfile = graphs_dir / f"{csv_name}_success_rate.png"
    if outfile.exists():
        outfile.unlink()
    plt.savefig(outfile)
    plt.show()
    
    # 2. Packets per Second by Configuration
    plt.figure(figsize=(12, 6))
    for config in configs:
        config_data = df[df['Config'] == config]
        grouped = config_data.groupby('Bin').agg(
            packets=('Indicator', 'sum')
        ).reset_index()
        grouped['packets_per_second'] = grouped['packets'] * 10
        grouped['bin_start'] = grouped['Bin'] * bin_size
        
        plt.plot(grouped['bin_start'], grouped['packets_per_second'], 
                marker='o', linestyle='-', label=config)
    
    plt.title("Packets Per Second by Configuration")
    plt.xlabel("Milliseconds")
    plt.ylabel("Packets per Second")
    plt.grid(True)
    plt.legend()
    
    # Add minor ticks
    plt.minorticks_on()
    plt.grid(True, which='major', linestyle='-')
    plt.grid(True, which='minor', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    # Delete existing file if it exists
    outfile = graphs_dir / f"{csv_name}_packets_per_second.png"
    if outfile.exists():
        outfile.unlink()
    plt.savefig(outfile)
    plt.show()
    
    # 3. Time Series by Second for each Configuration
    plt.figure(figsize=(12, 6))
    for config in configs:
        config_data = df[df['Config'] == config]
        
        # Calculate elapsed time in seconds from start of data collection
        start_time = config_data['Timestamp'].min()
        config_data['ElapsedSeconds'] = (config_data['Timestamp'] - start_time).dt.total_seconds()
        
        # Group by elapsed seconds and count packets
        second_grouped = config_data.groupby('ElapsedSeconds').agg(
            packets=('Indicator', 'count')
        ).reset_index()
        
        # Sort by elapsed seconds to ensure correct line plotting
        second_grouped = second_grouped.sort_values('ElapsedSeconds')
        
        plt.plot(second_grouped['ElapsedSeconds'], second_grouped['packets'], 
                marker='o', linestyle='-', label=config)
    
    plt.title(f"Packets per Second by Configuration - {csv_name}")
    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("Number of Packets")
    plt.grid(True)
    plt.legend()
    
    # Set x-axis ticks every 5 seconds up to max time
    max_seconds = int(second_grouped['ElapsedSeconds'].max())
    plt.xticks(range(0, max_seconds + 5, 5))
    
    # Add minor ticks
    plt.minorticks_on()
    plt.grid(True, which='major', linestyle='-')
    plt.grid(True, which='minor', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    # Delete existing file if it exists
    outfile = graphs_dir / f"{csv_name}_timeseries.png"
    if outfile.exists():
        outfile.unlink()
    plt.savefig(outfile)
    plt.show()
    
    # 4. Time Delay Analysis
    plt.figure(figsize=(12, 6))
    for config in configs:
        config_data = df[df['Config'] == config].copy()
        
        # Calculate elapsed time from both timestamp and millis
        start_timestamp = config_data['Timestamp'].min()
        start_millis = config_data['Millis'].min()
        
        # Convert to comparable units (milliseconds)
        config_data['TimestampElapsed'] = (config_data['Timestamp'] - start_timestamp).dt.total_seconds() * 1000
        config_data['MillisElapsed'] = config_data['Millis'] - start_millis
        
        # Calculate delay
        config_data['TimeDelay'] = config_data['TimestampElapsed'] - config_data['MillisElapsed']
        
        plt.plot(config_data['Index'], config_data['TimeDelay'], 
                marker='o', linestyle='-', label=config)
    
    plt.title(f"Time Delay Analysis - {csv_name}")
    plt.xlabel("Packet Index")
    plt.ylabel("Time Delay (ms)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()  # Only show, don't save
    
    # 5. Time Delay Analysis (Averaged)
    plt.figure(figsize=(12, 6))
    for config in configs:
        config_data = df[df['Config'] == config].copy()
        
        # Calculate elapsed time from both timestamp and millis
        start_timestamp = config_data['Timestamp'].min()
        start_millis = config_data['Millis'].min()
        
        # Convert to comparable units (milliseconds)
        config_data['TimestampElapsed'] = (config_data['Timestamp'] - start_timestamp).dt.total_seconds() * 1000
        config_data['MillisElapsed'] = config_data['Millis'] - start_millis
        
        # Calculate delay (millis - timestamp)
        config_data['TimeDelay'] = config_data['MillisElapsed'] - config_data['TimestampElapsed']
        
        # Create bins of 100 points for averaging
        config_data['DelayBin'] = config_data.index // 100
        
        # Calculate average delay for each bin
        delay_grouped = config_data.groupby('DelayBin').agg(
            avg_delay=('TimeDelay', 'mean'),
            bin_index=('Index', 'mean')  # Use mean index for x-axis
        ).reset_index()
        
        plt.plot(delay_grouped['bin_index'], delay_grouped['avg_delay'], 
                marker='o', linestyle='-', label=config)
    
    plt.title(f"Average Time Delay Analysis (per 600 packets) - {csv_name}")
    plt.xlabel("Packet Index")
    plt.ylabel("Average Time Delay (ms)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()  # Only show, don't save

def main():
    current_dir = Path(__file__).parent
    
    # Create graphs directory if it doesn't exist
    graphs_dir = current_dir / "graphs"
    graphs_dir.mkdir(exist_ok=True)
    
    # Process all CSV files in the directory
    for csv_file in current_dir.glob('*.csv'):
        print(f"Processing {csv_file.name}...")
        try:
            process_csv(csv_file, graphs_dir)
            print(f"Successfully processed {csv_file.name}")
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")

if __name__ == '__main__':
    main()