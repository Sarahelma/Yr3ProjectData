from pathlib import Path
import csv

def transform_dataset(input_data):
    """
    Transforms the input dataset into a table with columns:
    Index, Timestamp, and Indicator.
    
    - 'input_data' is a list of tuples (timestamp, index)
    - The output is a list of lists [index, timestamp, indicator]
      where 'indicator' is 1 if the original data had a timestamp for that index
      and 0 if it was interpolated.
    """
    # Create a dictionary for quick lookup: index -> timestamp
    data_dict = {index: timestamp for timestamp, index in input_data}
    max_index = max(data_dict.keys())
    
    # Build the initial full table for indices 1 to max_index
    result = []
    for i in range(1, max_index + 1):
        if i in data_dict:
            result.append([i, data_dict[i], 1])
        else:
            result.append([i, None, 0])
    
    # Perform linear interpolation between known timestamps
    i = 0
    while i < len(result):
        if result[i][2] == 1:  # known timestamp at this index
            start_index = i
            start_timestamp = result[i][1]
            # Find the next known timestamp
            j = i + 1
            while j < len(result) and result[j][2] == 0:
                j += 1
            if j < len(result):
                end_timestamp = result[j][1]
                gap = j - i  # number of steps between known indices
                # Fill in missing values between start_index and j using interpolation
                for k in range(i + 1, j):
                    # Linear interpolation formula
                    interpolated = round(start_timestamp + (end_timestamp - start_timestamp) * (k - i) / gap)
                    result[k][1] = interpolated
            i = j
        else:
            i += 1
    return result

def main():
    current_dir = Path(__file__).parent
    input_filename = current_dir / '200mretry.csv'
    output_filename = current_dir / '200mretryNew.csv'
    
    input_data = []
    
    # Read CSV file with Timestamp,Index headers
    with open(input_filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                timestamp = int(row['Timestamp'].strip())
                index = int(row['Index'].strip())
                input_data.append((timestamp, index))
            except (ValueError, KeyError) as e:
                print(f"Error processing row {row}: {e}")
    
    if not input_data:
        print("No data found in the CSV file.")
        return

    # Transform the dataset
    transformed = transform_dataset(input_data)
    
    # Write the final table to a new CSV file
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Index', 'Timestamp', 'Indicator'])
        # Write each row from the transformed dataset
        for row in transformed:
            writer.writerow(row)
    
    print(f"Transformed data has been saved to '{output_filename}'.")

if __name__ == "__main__":
    main()