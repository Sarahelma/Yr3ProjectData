import csv

def transform_dataset(input_data):
    """
    Transforms the input dataset into a table with columns:
    Index, Timestamp, Millis, DataRate, PowerLevel, and Indicator.
    """
    # Create a dictionary for quick lookup: index -> (timestamp, millis, datarate, powerlevel)
    data_dict = {index: (timestamp, millis, datarate, powerlevel) 
                for timestamp, millis, index, datarate, powerlevel in input_data}
    max_index = max(data_dict.keys())
    
    # Build the initial full table
    result = []
    for i in range(1, max_index + 1):
        if i in data_dict:
            result.append([i, data_dict[i][0], data_dict[i][1], 
                         data_dict[i][2], data_dict[i][3], 1])
        else:
            result.append([i, None, None, None, None, 0])
    
    # Perform linear interpolation between known timestamps
    i = 0
    while i < len(result):
        if result[i][5] == 1:  # known timestamp at this index
            start_index = i
            start_timestamp = result[i][1]
            start_millis = result[i][2]
            # Find the next known timestamp
            j = i + 1
            while j < len(result) and result[j][5] == 0:
                j += 1
            if j < len(result):
                end_millis = result[j][2]
                gap = j - i
                # Fill in missing values between start_index and j
                for k in range(i + 1, j):
                    interpolated = round(start_millis + 
                                      (end_millis - start_millis) * (k - i) / gap)
                    result[k][1] = start_timestamp
                    result[k][2] = interpolated
                    result[k][3] = result[i][3]  # Copy DataRate from previous known value
                    result[k][4] = result[i][4]  # Copy PowerLevel from previous known value
            i = j
        else:
            i += 1
    return result

def main():
    input_data = []
    input_filename = '250m250kbps.csv'
    output_filename = '250m2kbpnew.csv'
    
    # Read CSV file
    with open(input_filename, 'r', newline='') as csvfile:
        # Skip the header line
        next(csvfile)
        for line in csvfile:
            try:
                # Split the line by comma
                timestamp, millis, index, datarate, powerlevel = line.strip().split(',')
                # Convert numeric values to integers
                millis = int(millis)
                index = int(index)
                datarate = int(datarate)
                powerlevel = int(powerlevel)
                
                if index > 121635:
                    break
                
                input_data.append((timestamp, millis, index, datarate, powerlevel))
            except ValueError as e:
                print(f"Error processing line {line}: {e}")
                continue
    
    if not input_data:
        print("No data found in the CSV file.")
        return

    # Transform the dataset
    transformed = transform_dataset(input_data)
    
    # Write the final table to a new CSV file
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Index', 'Timestamp', 'Millis', 'DataRate', 
                        'PowerLevel', 'Indicator'])
        # Write transformed dataset
        for row in transformed:
            writer.writerow(row)
    
    print(f"Transformed data has been saved to '{output_filename}'.")

if __name__ == "__main__":
    main()