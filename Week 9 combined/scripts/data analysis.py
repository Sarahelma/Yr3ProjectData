import csv
from pathlib import Path

def transform_dataset(input_data):
    """
    Transforms the input dataset keeping both CurrentTime and Timestamp(ms).
    Input data format: (current_time, timestamp_ms, index, data_rate, power_level, counter)
    """
    # Create dictionary with index -> full data mapping
    data_dict = {int(index): (current_time, int(timestamp), data_rate, power_level, counter) 
                for current_time, timestamp, index, data_rate, power_level, counter in input_data}
    
    max_index = max(data_dict.keys())
    
    # Build initial table with all indices
    result = []
    for i in range(1, max_index + 1):
        if i in data_dict:
            current_time, timestamp, data_rate, power_level, counter = data_dict[i]
            result.append([i, current_time, timestamp, data_rate, power_level, counter, 1])
        else:
            result.append([i, None, None, None, None, None, 0])
    
    # Interpolate missing values
    i = 0
    while i < len(result):
        if result[i][6] == 1:  # Found known data point
            start_index = i
            start_timestamp = result[i][2]  # Use millisecond timestamp for interpolation
            j = i + 1
            while j < len(result) and result[j][6] == 0:
                j += 1
            if j < len(result):
                end_timestamp = result[j][2]
                gap = j - i
                for k in range(i + 1, j):
                    # Interpolate timestamp in milliseconds
                    interpolated = start_timestamp + ((end_timestamp - start_timestamp) * (k - i)) // gap
                    result[k][2] = interpolated  # Update timestamp
                    result[k][1] = result[i][1]  # Copy CurrentTime from previous known point
                    # Copy other values
                    result[k][3:6] = result[i][3:6]
            i = j
        else:
            i += 1
    return result

def main():
    current_dir = Path(__file__).parent
    input_filename = current_dir / 'DRIVINGONEMBPS250kbps.csv'
    output_filename = current_dir / 'DRIVINGONEMBPS250kbpsnew.csv'
    
    input_data = []
    
    with open(input_filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        next(reader)  # Skip column names row
        
        for row in reader:
            try:
                current_time, timestamp, index, data_rate, power_level, counter = row
                input_data.append((
                    current_time,           # Keep as string
                    int(timestamp),         # Convert to int
                    int(index),
                    int(data_rate),
                    int(power_level),
                    int(counter)
                ))
            except (ValueError, IndexError) as e:
                print(f"Skipping invalid row {row}: {e}")
                continue

    if not input_data:
        print("No valid data found in the CSV file.")
        return

    transformed = transform_dataset(input_data)
    
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'CurrentTime', 'Timestamp_ms', 'DataRate', 
                        'PowerLevel', 'counter', 'Indicator'])
        writer.writerows(transformed)
    
    print(f"Processed data saved to '{output_filename}'")

if __name__ == "__main__":
    main()
