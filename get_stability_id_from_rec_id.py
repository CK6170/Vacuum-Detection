import pandas as pd
from google.cloud import bigquery
import json


# Function to load list of IDs from CSV and run BigQuery
def get_stability_event_ids(csv_file_path, project_id, dataset, table, ok_events):
    # Load the CSV with pandas
    ids_df = pd.read_csv(csv_file_path)

    # Ensure 'id' column exists
    if 'cart_id' not in ids_df.columns:
        raise ValueError("CSV file must contain an 'cart_id' column")

    # Convert list of IDs into a string format suitable for SQL IN clause
    id_list = ids_df['cart_id'].tolist()
    id_str = ', '.join(f"'{i}'" for i in id_list)

    # Construct the query with UNNEST for stability_packages
    query_good = f"""
    SELECT
        id as rec_id,
        highest_probActor as cart_id,
        stability_event.stability_event_id as stab_id,
        r.weight_gr as recognition_weight,
        stability_event.weight_gr as stab_weight,
    FROM
        `{project_id}.{dataset}.{table}` as r,
        UNNEST(stability_packages) as stability_event
    WHERE
        highest_probActor IN ({id_str})
    """

    query_bad = f"""
        WITH event_counts AS (
            SELECT
                id as rec_id,
                COUNT(stability_event.stability_event_id) as event_count
            FROM
                `{project_id}.{dataset}.{table}` as r,
                UNNEST(stability_packages) as stability_event
            WHERE
                highest_probActor IN ({id_str})
            GROUP BY rec_id
        )

        SELECT
            r.id as rec_id,
            highest_probActor as cart_id,
            stability_event.stability_event_id as stab_id,
            r.weight_gr as recognition_weight,
            has_ufo,
            has_misplaced,
            ec.event_count,
            stability_event.weight_gr as stab_weight,
            CASE 
                WHEN has_ufo = TRUE OR ABS(stability_event.weight_gr) < 30 THEN 0
                WHEN has_ufo = FALSE AND ec.event_count > 1 AND (ABS(stability_event.weight_gr) / ABS(r.weight_gr) < 0.5 
                                             OR ABS(stability_event.weight_gr) / ABS(r.weight_gr) > 1.75) THEN 0
                ELSE 1
            END as expected
        FROM
            `{project_id}.{dataset}.{table}` as r,
            UNNEST(stability_packages) as stability_event
        JOIN
            event_counts ec
        ON
            r.id = ec.rec_id
        WHERE
            highest_probActor IN ({id_str})
            AND (has_ufo = TRUE OR has_misplaced = TRUE OR ec.event_count > 1)
    """

    query = query_good if ok_events else query_bad

    # Initialize BigQuery client
    client = bigquery.Client()

    # Execute the query and return the results
    query_job = client.query(query)
    results = query_job.result()

    # Convert results to DataFrame for easier manipulation
    results_df = results.to_dataframe()

    return results_df


with open('../config.json', 'r') as config_file:
    config = json.load(config_file)

# qa_path_service_account = config['qa_path_service_account']
tests_folder = config['tests_folder']

# Example usage - "Good" events
# csv_file_path = tests_folder + "cart_ids_list\\cart_ids_ok_list.csv"
# project_id = "shekel-gcloud"
# dataset = "env_cooler"
# table = "RecognitionStorage"
# output_file_path = tests_folder + "tagged_stability_ids\\output_OK_stab_ids.xlsx"
# ok_events = True

# Example usage - "Noise" events
# csv_file_path = tests_folder + "cart_ids_list\\cart_ids_nonOk_list.csv"
# project_id = "shekel-gcloud"
# dataset = "env_cooler"
# table = "RecognitionStorage"
# output_file_path = tests_folder + "tagged_stability_ids\\output_nonOK_stab_ids.xlsx"
# ok_events = False

# Example usage - "Planogramm issues" events
csv_file_path = tests_folder + "cart_ids_list\\cart_ids_planogram_issue_list.csv"
project_id = "shekel-gcloud"
dataset = "env_cooler"
table = "RecognitionStorage"
output_file_path = tests_folder + "tagged_stability_ids\\planogram_issue_stab_ids.xlsx"
ok_events = True

result_df = get_stability_event_ids(csv_file_path, project_id, dataset, table, ok_events)
result_df.to_excel(output_file_path, index=False)
print(result_df)
