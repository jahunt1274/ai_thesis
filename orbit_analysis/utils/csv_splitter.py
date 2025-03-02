import pandas as pd
import math
import os

def split_csv(input_file, rows_per_file, output_dir='split_files'):
    """
    Split a CSV file into multiple files with specified number of rows.
    
    Parameters:
    input_file (str): Path to the input CSV file
    rows_per_file (int): Number of rows per output file
    output_dir (str): Directory to store the split files (default: 'split_files')
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    total_rows = len(df)
    
    # Calculate number of files needed
    num_files = math.ceil(total_rows / rows_per_file)
    
    # Split and save files
    for i in range(num_files):
        start_idx = i * rows_per_file
        end_idx = min((i + 1) * rows_per_file, total_rows)
        
        # Create filename with padding (e.g., split_001.csv)
        filename = f'split_{str(i+1).zfill(3)}.csv'
        output_path = os.path.join(output_dir, filename)
        
        # Write the chunk to a CSV file
        df[start_idx:end_idx].to_csv(output_path, index=False)
        print(f'Created {filename} with {end_idx - start_idx} rows')

# Example usage
if __name__ == "__main__":
    # Replace these with your actual values
    # input_csv = r"C:\Users\BYO Display 2.0\Desktop\MIT\Thesis\Orbit Data\idea_titles.csv"
    input_csv = "/mnt/c/Users/BYO Display 2.0/Desktop/MIT/Thesis/Orbit_Data/idea_titles.csv"
    rows_per_split = 100
    # output_dir = r"C:\Users\BYO Display 2.0\Desktop\MIT\Thesis\Orbit Data\split_ideas"
    output_dir = "/mnt/c/Users/BYO Display 2.0/Desktop/MIT/Thesis/Orbit_Data/split_ideas"
    
    split_csv(input_csv, rows_per_split, output_dir)