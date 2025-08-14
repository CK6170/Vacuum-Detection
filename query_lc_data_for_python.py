import pandas as pd
import os
import google.cloud.bigquery as bq
import stability_to_go
from datetime import datetime as dt
from datetime import timezone

def main(dataset, start_dt, end_dt):
    table_name = "StabilityEvents"
    path_service_account = r"D:\Coolers\Google\shekel-qa-9066809a1872.json"

    if dataset != "env_integration" and dataset != "env_cooler":
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_service_account

    # First, let's check how many total records exist in the table
    count_query = f"""
        SELECT COUNT(*) as total_records
        FROM {dataset}.{table_name}
    """
    
    # Check records in our date range
    range_count_query = f"""
        SELECT COUNT(*) as records_in_range
        FROM {dataset}.{table_name}
        WHERE timestamp > TIMESTAMP("{start_dt}")
            AND timestamp < TIMESTAMP("{end_dt}")
    """
    
    # Check the actual data range available
    date_range_query = f"""
        SELECT 
            MIN(timestamp) as earliest_timestamp,
            MAX(timestamp) as latest_timestamp,
            COUNT(*) as total_records
        FROM {dataset}.{table_name}
    """
    
    print(f"Querying dataset: {dataset}.{table_name}")
    print(f"Date range: {start_dt} to {end_dt}")
    
    client = bq.Client()
    
    # Get total table info
    try:
        print("\n=== TABLE OVERVIEW ===")
        date_range_result = client.query(date_range_query).to_dataframe()
        print(f"Total records in table: {date_range_result.iloc[0]['total_records']:,}")
        print(f"Earliest timestamp: {date_range_result.iloc[0]['earliest_timestamp']}")
        print(f"Latest timestamp: {date_range_result.iloc[0]['latest_timestamp']}")
        
        range_count_result = client.query(range_count_query).to_dataframe()
        print(f"Records in specified date range: {range_count_result.iloc[0]['records_in_range']:,}")
        
    except Exception as e:
        print(f"Error getting table overview: {e}")
    
    # Main query with explicit LIMIT to see if that's the issue
    query_txt = f"""
        SELECT stability_id, weight_gr, location, loadcell_data, last_stable_timestamp, timestamp
        FROM {dataset}.{table_name}
        WHERE timestamp > TIMESTAMP("{start_dt}")
            AND timestamp < TIMESTAMP("{end_dt}")
        ORDER BY timestamp DESC
        LIMIT 10000  -- Explicitly set a higher limit
    """
    
    print(f"\n=== EXECUTING MAIN QUERY ===")
    print(f"Query: {query_txt}")
    
    try:
        query_job = client.query(query_txt)
        stability_df = query_job.to_dataframe()
        print(f"Query returned {len(stability_df)} rows")
        
        if stability_df.empty:
            print("No data found for query")
            return stability_df
            
        # Check for duplicates before removing them
        print(f"Records before removing duplicates: {len(stability_df)}")
        stability_df = stability_df.drop_duplicates(subset='stability_id', keep='first')
        print(f"Records after removing duplicates: {len(stability_df)}")
        
        return stability_df
        
    except Exception as e:
        print(f"Error executing main query: {e}")
        return pd.DataFrame()


def save_lc_data_array_to_excel(lc_data_array, filename):
    # Initialize an empty list to store rows
    rows = []

    # Iterate over each dictionary in the ndarray
    for data in lc_data_array:
        # Extract timestamp, lc_values, and weights
        timestamp = data['timestamp']

        # Remove timezone info from the timestamp
        timestamp_naive = timestamp.replace(tzinfo=None)

        lc_values = data['lc_values']
        weights = data['weights']

        # Convert lc_values and weights arrays to list for easier handling
        lc_values_list = lc_values.tolist()
        weights_list = weights.tolist()

        # Calculate total_weight as the sum of weights
        total_weight = sum(weights_list)

        # Combine timestamp, lc_values, and weights into one row
        row = [timestamp_naive] + lc_values_list + weights_list + [total_weight]
        rows.append(row)

    # Create a DataFrame, columns names can be customized based on the size of arrays
    columns = (
        ['timestamp'] +
        [f'lc_value_{i+1}' for i in range(len(lc_values))] +
        [f'weight_{i+1}' for i in range(len(weights))] +
        ['total_weight']
    )
    df = pd.DataFrame(rows, columns=columns)
    df.to_excel(filename, index=False)


def plot_stab_chart_from_excel(excel_filename, chart_filename, show=False):
    import matplotlib.pyplot as plt
    import pandas as pd

    combined_df = pd.read_excel(excel_filename)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])

    # === Plotting ===
    plt.figure(figsize=(12, 6))
    plt.plot(combined_df['timestamp'], combined_df['total_weight'], label='Total Weight', marker='o')
    plt.title("Filtered Total Weight and Stability per Timestamp")
    plt.xlabel("Timestamp")
    plt.ylabel("Weight")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_filename)
    if show:
        plt.show()
    return


if __name__ == '__main__':
    from dateutil import tz
    tz = tz.gettz("Asia/Jerusalem")

    dataset = f"env_cooler"
    # Fix the dates to use current year instead of future year
    start_dt = dt(2024, 8, 14, 00, 00, tzinfo=tz).astimezone(timezone.utc)
    end_dt = dt(2025, 8, 14, 23, 59, tzinfo=tz).astimezone(timezone.utc)

    # Get data
    print("="*60)
    print("STARTING DATA RETRIEVAL")
    print("="*60)
    
    stability_df = main(dataset, start_dt, end_dt)
    
    if stability_df.empty:
        print("No data retrieved, exiting.")
        exit()
    
    print(f"\n" + "="*60)
    print("PROCESSING RETRIEVED DATA")
    print("="*60)
    print(f"Total records to process: {len(stability_df)}")
    
    # Create directories if they don't exist
    os.makedirs("./excel_files", exist_ok=True)
    
    processed_count = 0
    error_count = 0
    
    # Store in Excel files per stability
    for index, row in stability_df.iterrows():
        try:
            print(f"Processing record {index + 1}/{len(stability_df)}: {row['stability_id']}")
            
            stability_id = row['stability_id']
            loadcell_data = row['loadcell_data']['unit']
            factors = row['loadcell_data']['factors']

            excel_filename = f"./excel_files/{stability_id}_lc_data.xlsx"
            stability_to_go.save_lc_data_array_to_excel(loadcell_data, excel_filename)
            
            processed_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"Error processing record {index + 1}: {e}")
            continue
    
    print(f"\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Total records processed: {processed_count}")
    print(f"Errors encountered: {error_count}")
    print(f"Success rate: {processed_count/len(stability_df)*100:.1f}%")


