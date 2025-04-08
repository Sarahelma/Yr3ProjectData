import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import numpy as np

def main():
    current_dir = Path(__file__).parent
    csv_path = current_dir / "DRIVINGONEMBPS250kbpsnew.csv"
    df = pd.read_csv(csv_path)
    
    # Convert CurrentTime strings to datetime objects
    df['CurrentTime'] = pd.to_datetime(df['CurrentTime'], format='%H:%M:%S')
    
    # Calculate time differences using Timestamp_ms
    df['time_elapsed'] = df['Timestamp_ms'].diff().fillna(0)
    
    # bin size in milliseconds
    bin_size = 100
    
    # Create bins based on Timestamp_ms
    df['Bin'] = (df['Timestamp_ms'] // bin_size).astype(int)
    
    # Group data and calculate statistics
    grouped = df.groupby('Bin').agg(
        total=('Index', 'size'),
        successes=('Indicator', 'sum'),  # Sum of Indicator=1 gives us successful packets
        avg_data_rate=('DataRate', 'mean'),
        avg_power=('PowerLevel', 'mean')
    ).reset_index()
    
    # Calculate success rate and packets per second
    grouped['success_rate'] = (grouped['successes'] / grouped['total']) * 100
    grouped['packets_per_second'] = grouped['successes'] * (1000 / bin_size)  # Only count successful packets
    grouped['bin_start'] = grouped['Bin'] * bin_size
    
    # Add packets per second calculation using CurrentTime
    df_real = df[df['Indicator'] == 1]  # Only use real data points
    df_real['SecondBin'] = df_real['CurrentTime'].dt.floor('s')  # Changed from 'S' to 's'
    df_real.loc[:, 'SecondBin'] = df_real['CurrentTime'].dt.floor('s')
    time_grouped = df_real.groupby('SecondBin').agg(
        packets=('Index', 'count'),
        counter=('counter', 'first')
    ).reset_index()
    time_grouped['packets_per_second'] = time_grouped['packets']

    # Get base name from input file for output files
    base_name = csv_path.stem.replace('new', '')  # Gets 'walking_250kbps'
    
    # Create plots with light background style
    plt.style.use('default')  # Use default light style
    
    # Calculate rolling averages (window of 10 points)
    window_size = 10
    grouped['success_rate_rolling'] = grouped['success_rate'].rolling(window=window_size, center=True).mean()
    grouped['packets_per_second_rolling'] = grouped['packets_per_second'].rolling(window=window_size, center=True).mean()
    grouped['avg_data_rate_rolling'] = grouped['avg_data_rate'].rolling(window=window_size, center=True).mean()
    df['time_elapsed_rolling'] = df['time_elapsed'].rolling(window=window_size, center=True).mean()

    # Add two window sizes for rolling averages
    short_window = 10    # For detailed trends
    long_window = 100   # For smoother trend line (changed from 50 to 100)
    
    # Calculate both short and long rolling averages
    grouped['success_rate_short'] = grouped['success_rate'].rolling(window=short_window, center=True).mean()
    grouped['success_rate_long'] = grouped['success_rate'].rolling(window=long_window, center=True).mean()
    grouped['packets_per_second_short'] = grouped['packets_per_second'].rolling(window=short_window, center=True).mean()
    grouped['packets_per_second_long'] = grouped['packets_per_second'].rolling(window=long_window, center=True).mean()
    grouped['avg_data_rate_short'] = grouped['avg_data_rate'].rolling(window=short_window, center=True).mean()
    grouped['avg_data_rate_long'] = grouped['avg_data_rate'].rolling(window=long_window, center=True).mean()
    df['time_elapsed_short'] = df['time_elapsed'].rolling(window=short_window, center=True).mean()
    df['time_elapsed_long'] = df['time_elapsed'].rolling(window=long_window, center=True).mean()

    # Create graphs directory if it doesn't exist
    graphs_dir = current_dir / "graphs"
    graphs_dir.mkdir(exist_ok=True)

    # Plot 1: Success Rate with both rolling averages
    plt.figure(figsize=(12, 6))
    plt.plot(grouped['bin_start'], grouped['success_rate'], 
             color='blue', marker='.', linestyle='-', linewidth=1, alpha=0.3,
             label='100ms Interval')
    plt.plot(grouped['bin_start'], grouped['success_rate_short'],
             color='darkblue', linestyle='-', linewidth=1.5,  # Changed from black
             label=f'10-point Average')
    plt.plot(grouped['bin_start'], grouped['success_rate_long'],
             color='red', linestyle='-', linewidth=2,
             label=f'100-point Average')
    plt.title("Success Rate per 100ms Interval")
    plt.xlabel("Time (ms)")
    plt.ylabel("Success Rate (%)")
    plt.grid(True, alpha=0.3)
    plt.grid(True, which='minor', alpha=0.15)  # Added minor gridlines
    plt.minorticks_on()  # Enable minor ticks
    plt.legend()
    plt.tight_layout()
    plt.savefig(graphs_dir / f"{base_name}_success_rate.png", facecolor='white')
    plt.show()

    # Plot 2: Packets per Second with both rolling averages
    plt.figure(figsize=(12, 6))
    plt.plot(grouped['bin_start'], grouped['packets_per_second'],
             color='green', marker='.', linestyle='-', linewidth=1, alpha=0.3,
             label='100ms Interval')
    plt.plot(grouped['bin_start'], grouped['packets_per_second_short'],
             color='darkgreen', linestyle='-', linewidth=1.5,  # Changed from white
             label=f'10-point Average')
    plt.plot(grouped['bin_start'], grouped['packets_per_second_long'],
             color='red', linestyle='-', linewidth=2,
             label=f'100-point Average')
    plt.grid(True, alpha=0.3)
    plt.grid(True, which='minor', alpha=0.15)  # Added minor gridlines
    plt.minorticks_on()  # Enable minor ticks
    plt.title("Packets Per Second (100ms Interval)")
    plt.xlabel("Time (ms)")
    plt.ylabel("Packets/s")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(graphs_dir / f"{base_name}_pps_ms.png", facecolor='white')
    plt.show()

    # Plot 3: Average Data Rate with both rolling averages
    plt.figure(figsize=(12, 6))
    plt.plot(grouped['bin_start'], grouped['avg_data_rate'],
             color='magenta', marker='.', linestyle='-', linewidth=1, alpha=0.3,
             label='Raw Data')
    plt.plot(grouped['bin_start'], grouped['avg_data_rate_short'],
             color='white', linestyle='-', linewidth=1.5,
             label=f'{short_window}-point Average')
    plt.plot(grouped['bin_start'], grouped['avg_data_rate_long'],
             color='red', linestyle='-', linewidth=2,
             label=f'{long_window}-point Average')
    plt.title("Average Data Rate")
    plt.xlabel("Time (ms)")
    plt.ylabel("Data Rate")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("data_rate_plot.png", facecolor='white')
    plt.show()

    # Plot 4: Time Elapsed Between Packets with both rolling averages
    plt.figure(figsize=(12, 6))
    plt.plot(df['Timestamp_ms'], df['time_elapsed'],
             color='yellow', marker='.', linestyle='-', linewidth=1, alpha=0.3,
             label='Raw Data')
    plt.plot(df['Timestamp_ms'], df['time_elapsed_short'],
             color='white', linestyle='-', linewidth=1.5,
             label=f'{short_window}-point Average')
    plt.plot(df['Timestamp_ms'], df['time_elapsed_long'],
             color='red', linestyle='-', linewidth=2,
             label=f'{long_window}-point Average')
    plt.title("Time Elapsed Between Packets")
    plt.xlabel("Time (ms)")
    plt.ylabel("Time Elapsed (ms)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("time_elapsed_plot.png", facecolor='white')
    plt.show()

    # Create new plot for time-based packets per second with counter colors
    plt.figure(figsize=(12, 6))
    
    # Define counter meanings with grouping
    counter_groups = {
        "0m to 50m": [0],
        "50m to 100m": [1],
        "100m to 150m": [2],
        "150m to 200m": [3,4],
        "200m to 250m": [5],
        "250m to 300m": [6],
        "300m to 350m": [7],
        "350m +": [8],
    }
    
    # Get colors from Dark2 colormap for all possible groups
    all_colors = plt.cm.Dark2(np.linspace(0, 1, len(counter_groups)))
    
    # Plot each group, always using the correct color index
    for i, (label, counters) in enumerate(counter_groups.items()):
        color = all_colors[i]  # Get color based on position in dictionary
        
        # Combine data for all counters in group
        group_data = pd.DataFrame()
        for counter in counters:
            mask = time_grouped['counter'] == counter
            group_data = pd.concat([group_data, time_grouped[mask]])
        
        # Always add to legend even if no data (for consistent color scheme)
        plt.plot([], [], 
                label=label,
                color=color,
                marker='.',
                linestyle='-',
                linewidth=1)
        
        if not group_data.empty:
            # Sort and plot actual data
            group_data = group_data.sort_values('SecondBin')
            plt.plot(group_data['SecondBin'], group_data['packets_per_second'],
                    color=color,
                    marker='.',
                    linestyle='-',
                    linewidth=1,
                    alpha=0.3)
            
            # Add rolling average
            rolling = group_data['packets_per_second'].rolling(window=window_size, center=True).mean()
            plt.plot(group_data['SecondBin'], rolling,
                    color=color,
                    linestyle='-',
                    linewidth=2,
                    alpha=1.0)

    # Format x-axis to show only time HH:MM:SS
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    
    plt.title("Packets Per Second (by CurrentTime)")
    plt.xlabel("Time")
    plt.ylabel("Packets/s")
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(graphs_dir / f"{base_name}_pps_time.png", 
                facecolor='white', 
                bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    main()
