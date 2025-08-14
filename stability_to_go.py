import os
import pandas as pd
import numpy as np

from datetime import datetime as dt
from datetime import timezone
import matplotlib.pyplot as plt
import os
import datetime
import google.cloud.bigquery as bq
import json


# def stability_bq_data(*args, dataset, table_name, stability_list=None, start_dt=None, end_dt=None):
def stability_bq_data(*args, dataset, table_name):
    if stability_list is not None and stability_list in args:
        if not start_dt or not end_dt:
            raise ValueError("Both start_dt and end_dt must be provided for time range queries.")

        query_txt = f"""
            SELECT *
            FROM `{dataset}.{table_name}`
            WHERE timestamp > TIMESTAMP("{start_dt}")
                AND timestamp < TIMESTAMP("{end_dt}") 
            AND stability_id IN UNNEST({stability_list})
            order by timestamp asc
        """
    elif shelf_list is not None and shelf_list in args:
        if not start_dt or not end_dt:
            raise ValueError("Both start_dt and end_dt must be provided for time range queries.")

        query_txt = f"""
            SELECT *
            FROM `{dataset}.{table_name}`
            WHERE timestamp > TIMESTAMP("{start_dt}")
                AND timestamp < TIMESTAMP("{end_dt}")
                AND shelf_id IN UNNEST({shelf_list})
            order by timestamp asc
        """
    else:
        if not start_dt or not end_dt:
            raise ValueError("Both start_dt and end_dt must be provided for time range queries.")

        query_txt = f"""
            SELECT *
            FROM `{dataset}.{table_name}`
            WHERE timestamp > TIMESTAMP("{start_dt}")
                AND timestamp < TIMESTAMP("{end_dt}")
            order by timestamp asc
        """

    client = bq.Client()
    query_job = client.query(query_txt)
    results_df = query_job.to_dataframe()

    if results_df.empty:
        raise pd.errors.EmptyDataError("No data found for query")

    res = results_df.drop_duplicates(subset=['stability_id'])
    res = res.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
    print(f"Returned from BQ: {len(res)} records")
    return res


# def bq_query_by_ids(stability_ids):
#
#     from dateutil import tz
#     tz = tz.gettz("Asia/Jerusalem")
#     path_service_account = "C:/Users/Asael/git_projects/cart-scoring/shekel-qa-12ee1de1ae03.json"
#     os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_service_account
#
#
#     dataset = f"env_algo"
#     table_name = "StabilityEvents"
#
#
#     ''' by stab id '''
#
#     query_txt = \
#         """
#             select *
#             from {}.{}
#            where stability_id  IN UNNEST({})
#
#             """.format(dataset, table_name, stability_ids)
#     # ORDER BY timestamp DESC
#
#     a = bq.Client()
#
#     a = a.query(query_txt)
#
#     results_df = a.to_dataframe()  # to_dataframe()
#
#     if results_df.empty:
#         raise pd.errors.EmptyDataError("No data found for query")
#
#     return results_df


# def weights_to_time_series(row):
#     # x=row[ 'load_cell_data']
#     # x=res.loc[:, 'load_cell_data']
#     from collections import defaultdict
#     res = defaultdict(list)
#     for sub in row['load_cell_data']:
#         for key in sub:
#             res[key].append(sub[key])
#
#     return dict(res)


# def weights_to_time_series_2(row):
#     # x=row[ 'load_cell_data']
#     # x=res.loc[:, 'load_cell_data']
#     from collections import defaultdict
#     res = defaultdict(list)
#     for key, value in row['loadcell_data'].items():
#         # for key in sub:
#         res[key].append(value)
#
#     return dict(res)


# weight calculation weightsGr[i] = (v - e.calibPrms.ZeroFactors[i]) * e.calibPrms.CalibFactors[i]
# def compute_weight():
#     res.loc[:, 'load_cell_df'] = res.apply(lambda row: weights_to_time_series(row), axis=1)
#     x = res.loc[:, 'load_cell_df']
#     stab_1 = pd.DataFrame(list(map(np.ravel, x[0]['weights'])))
#     time_1 = [t.strftime(format="%m_%d_%Y_%H_%M_%S.%f") for t in x[0]['timestamp']]
#
#     ''' weight computation '''
#     # TODO get two dimensional location for weight average calculation
#
#     weight_left_mean = pd.DataFrame(stab_1).iloc[:, [0, 3]].mean(axis=1)
#     weight_right_mean = pd.DataFrame(stab_1).iloc[:, [1, 2]].mean(axis=1)
#     weight_total_mean = pd.DataFrame(stab_1).mean(axis=1)
#
#     weight_right_sum = pd.DataFrame(stab_1).iloc[:, [1, 2]].sum(axis=1)
#     weight_total_sum = pd.DataFrame(stab_1).sum(axis=1)
#     location = max(weight_right_sum) / max(weight_total_sum)
#
#     final_weight_opt_1 = (1 - location) * weight_right_mean.mean() + location * weight_left_mean.mean()
#
#     import statistics
#     final_weight_opt_2 = weight_total_mean.mean() - statistics.mode(np.floor(weight_total_mean))
#     final_weight_opt_3 = max(weight_total_sum) - statistics.mode(np.floor(weight_total_sum))
#
#     for col in range(len(stab_1.columns)):
#         plt.plot(time_1, stab_1.loc[:, col])
#     # plt.plot(time_1, stab_1)
#     plt.xticks(np.arange(0, len(time_1), step=15))
#     plt.xlabel('time')
#     plt.ylabel('mean weight from censors in gram')
#
#     plt.show()
#     import statistics
#
#     weight = max(weight_total_sum) - statistics.mode(np.floor(stab_1))
#     print(' ')
#
#     return


# def bq_res_tostab(res):
#     res.loc[:, 'load_cell_df'] = res.apply(lambda row: weights_to_time_series(row), axis=1)
#     x = res.loc[:, 'load_cell_df']
#     stab_1 = pd.DataFrame(list(map(np.ravel, x[0]['weights'])))
#     time_1 = [t.strftime(format="%m_%d_%Y_%H_%M_%S.%f") for t in x[0]['timestamp']]
#     factors = res['factors']
#     return stab_1, time_1, factors
#
#
# def bq_res_tostab2(res):
#     x = pd.DataFrame.from_dict(list(res.loadcell_data['unit']), orient="columns")
#     stab_1 = pd.DataFrame(list(map(np.ravel, x['lc_values'])), columns=['lc1', 'lc2', 'lc3', 'lc4'])
#     time_1 = [t.strftime(format="%m_%d_%Y_%H_%M_%S.%f") for t in x['timestamp']]
#     time_2 = x['timestamp']
#     factors = res.loadcell_data['factors']
#     return stab_1, time_1, factors,time_2
#
# def get_stab(res,s_id):
#     stability = res.loc[res['stability_id'] == s_id].iloc[0]
#     # last_stab = list(res.loc[res.loc[res['stability_id'] == s_id].index[0] + 1].loadcell_data['unit'][-1]['lc_values'])
#     stab, time, factors,timestamp = bq_res_tostab2(stability)
#     ''' weight computation '''
#     # TODO get two dimensional location for weight average calculation
#
#     weights_times_factors = stab * factors
#     # last_stab_with_factors = last_stab * factors
#     weight_total_sum = pd.DataFrame(weights_times_factors).sum(axis=1)
#     return weight_total_sum,time,timestamp

# def plot_stability(res, s_id):
#     weight_total_sum,time=get_stab(res, s_id)
#
#     plt.plot(time, weight_total_sum, '.')
#     # plt.plot(time_1, stab)
#     plt.xticks(np.arange(0, len(time), step=200))
#     plt.title(s_id+' stability')
#     plt.xlabel('time')
#     plt.ylabel(' weight from censors in gram')
#     path='C:/Users/Asael/Documents/stability_java_to_Go_docs/PAB_tests/sarel experimets/'
#     #plt.savefig(path+f"plot_{s_id}.png")
#
#     plt.show()
#     # Clear the plot to generate the next one
#     plt.clf()
#
#     print(' ')
#
#     return


# def plot_weight(stab):
#     ''' weight computation '''
#     # TODO get two dimensional location for weight average calculation
#
#     weights_times_factors = stab.load_cell_data * stab.factors
#     weight_total_sum = pd.DataFrame(weights_times_factors).sum(axis=1)
#
#     # for col in range(len(weight_total_sum)):
#     plt.plot(stab.time, weight_total_sum)
#     # plt.plot(time_1, stab)
#     plt.xticks(np.arange(0, len(stab.time), step=15))
#     plt.xlabel('time')
#     plt.ylabel(' weight from censors in gram')
#
#     plt.show()
#
#     print(' ')
#
#     return


def read_json_to_df(file_path):
    import pandas as pd
    import json
    # Load the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Extract the 'lcData' key from the dictionary and store it in a dataframe
    df = pd.DataFrame(data['lc_data'])  # pd.DataFrame(data['lcData'])

    return df[['lc1', 'lc2', 'lc3', 'lc4']], df.timestamp


# def bq_data_to_json(stability_message,zeros=[0, 0, 0, 0]):
#     stability_message_current = stability_message.iloc[0]
#     #stability_message_current = stability_message_current.loadcell_data
#     dict_of_stab = {}
#     dict_of_stab['factors'] = stability_message_current.loadcell_data['factors'].tolist()
#     dict_of_stab['zeros'] = zeros#[stability_message_current.shelf_id]
#     dict_of_stab['lcData'] = [weight_array_edit(sample,[]) for sample in stability_message_current.loadcell_data['unit']] #stability_message_current['factors'].tolist()
#     dict_of_stab['lastStab'] = list(stability_message.iloc[-1].loadcell_data['unit'][-1]['lc_values'])
#     return dict_of_stab

def bq_data_to_json_per_stability(stability_message,laststab_point,last_stab_window,zeros=[0, 0, 0, 0]):

    stability_message_current = stability_message.loadcell_data
    dict_of_stab = {}
    dict_of_stab['stability_id'] = stability_message['stability_id']
    dict_of_stab['shelf_id'] = stability_message['shelf_id']
    dict_of_stab['timestamp'] = stability_message['timestamp'].strftime("%Y-%m-%d %H:%M:%S.%f")
    dict_of_stab['last_stable_timestamp'] = stability_message['last_stable_timestamp'].strftime("%Y-%m-%d %H:%M:%S.%f")
    dict_of_stab['weight_gr'] = stability_message['weight_gr']
    dict_of_stab['location'] = stability_message['location']
    dict_of_stab['factors'] = stability_message_current['factors'].tolist()
    dict_of_stab['zeros'] = zeros #[stability_message.shelf_id]
    dict_of_stab['lcData'] = [weight_array_edit(sample,[]) for sample in stability_message_current['unit']]
    dict_of_stab['lastStab'] = [weight_array_edit(sample,[]) for sample in laststab_point]
    dict_of_stab['lastStabWindow'] = [weight_array_edit(sample,[]) for sample in last_stab_window]
    return dict_of_stab


def weight_array_edit(stability_message,factors):
    dict_of_weights = {}
    dt = stability_message['timestamp']
    unix_time = dt.timestamp()

    dict_of_weights['timestamp'] = str(unix_time)  # dt.strftime("%Y-%m-%d %H:%M:%S.%f") #str(unix_time)
    dict_of_weights['timestamp_str'] = dt.strftime("%Y-%m-%d %H:%M:%S.%f") #str(unix_time)
    if len(factors)>0:
        for i in range(len(stability_message['lc_values'])):
            dict_of_weights['lc' + str(i + 1)] = stability_message['lc_values'][i]/factors[i]
    else:
        for i in range(len(stability_message['lc_values'])):
            dict_of_weights['lc' + str(i + 1)] = stability_message['lc_values'][i]
    return dict_of_weights


# def conv_to_mili(timestamp):
#     import datetime
#
#     epoch = datetime.datetime.utcfromtimestamp(0)
#     naive = timestamp.replace(tzinfo=None)
#
#     def unix_time_millis(dt):
#         return (dt - epoch).total_seconds()
#
#     return unix_time_millis(naive)

# def convert_to_unix_millis(date_string,utc=False,local=False,n=6):
#     import datetime
#     import pytz
#
#     timezone = pytz.timezone("Asia/Jerusalem")
#
#     # Convert to UTC timezone
#     utc_tz = pytz.utc
#     try:
#     # parse the string into a datetime object
#         dt = datetime.datetime.fromisoformat(date_string[:-n])
#     except Exception as e:
#         print()
#     # get the Unix timestamp in seconds and convert to milliseconds
#     #unix_millis = int(dt.timestamp() * 1000)
#
#     # Convert to UTC timezone if requested
#     if utc:
#         dt = pytz.utc.localize(dt).astimezone(pytz.timezone('UTC'))
#
#     if local:
#         dt = pytz.utc.localize(dt).astimezone(timezone)
#
#
#     # Get the Unix timestamp in seconds and convert to milliseconds
#     unix_millis = int(dt.timestamp() * 1000)
#
#     return unix_millis




# def conv_datetime_to_mili(timestamp):
#     from datetime import datetime
#     import time
#
#     # dt = datetime.now()
#     unix_time = int(time.mktime(timestamp.timetuple()))
#     unix_miliseconds = unix_time * 1000
#     # print(unix_miliseconds)
#     return unix_miliseconds


# def contimetmili(dt):
#     unix_miliseconds = int(dt.timestamp() * 1000)
#     return unix_miliseconds


# def create_test_files_from_bq(directory, res,zeros):
#     ''' writing files for Go/java'''
#     # comments- printing / testing
#     # stabjson2 = bq_data_to_json(res.loc[2, :])
#     # laststabres=res.loc[6, :].loadcell_data['unit'][-1]['lc_values']
#     # for val in laststabres:
#     #     print(val)
#     directory = directory + "/bq_cases_tests/"
#
#     # k = 0
#     # while k < (len(res)):
#     #     two_events = res.loc[k:k + 2, :]
#     #     stabjson = bq_data_to_json(two_events)
#     #
#     #     # stab_id=0
#     #     stab_id = two_events.iloc[0, 0]
#     #     write = True
#     #     if write:
#     #         with open(directory + str(stab_id) + ".json",
#     #                   "w") as outfile:
#     #             json.dump(stabjson, outfile)
#     #     k += 2
#     df = res.sort_values(by='timestamp', ascending=False)
#     df.reset_index(inplace=True)
#     k = 0
#     while k < (len(res)):
#
#         # two_events = res.loc[k:k + 2, :]
#         stab=df.loc[k,:]
#         last_stab=df[df['timestamp']==stab.last_stable_timestamp]
#
#         two_events =df.loc[k:k +1, :]# df.groupby('stability_id').head(2)
#
#         stabjson = bq_data_to_json(two_events,zeros)
#
#         # stab_id=0
#         stab_id = two_events.iloc[0, 0]
#         write = True
#         if write:
#             with open(directory + str(stab_id) + ".json",
#                       "w") as outfile:
#                 json.dump(stabjson, outfile)
#         k += 1
#
#     return



# def unix_to_datetime(unix_timestamp):
#     if isinstance(unix_timestamp, float):
#         unix_timestamp = int(unix_timestamp)
#     if len(str(unix_timestamp)) > 10:
#         unix_timestamp = unix_timestamp // 1000
#     return datetime.datetime.fromtimestamp(unix_timestamp)



def create_stability_file_from_bq(directory, events_data_from_bq, zeros, stab_window_size,
                                            filter_bad_previous_stability, filter_above_weight):
    """
    Groups stability events by shelf and generates JSON files for each stability event.

    Args:
        directory (str): The directory where JSON files will be saved.
        events_data_from_bq (DataFrame): DataFrame containing stability events data from BigQuery.
        zeros (list): Zero calibration values.
    """
    directory_xls = directory + "bq_cases_xlsx/"
    directory += "bq_cases_tests/"


    # Check if the folder exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Folder '{directory}' created.")
    else:
        print(f"Folder '{directory}' already exists.")

    # Check if the folder exists
    if not os.path.exists(directory_xls):
        os.makedirs(directory_xls)
        print(f"Folder '{directory_xls}' created.")
    else:
        print(f"Folder '{directory_xls}' already exists.")

    # Assuming 'shelf_id' is the column name for shelf identifier
    for shelf_id in events_data_from_bq['shelf_id'].unique():
        shelf_events = events_data_from_bq[events_data_from_bq['shelf_id'] == shelf_id]

        # Sort shelf events by timestamp to ensure chronological order
        shelf_events = shelf_events.sort_values(by='timestamp')

        for i in range(1, len(shelf_events)):
            stab_window_size = min(stab_window_size, len(shelf_events.iloc[0].loadcell_data['unit']))
            last_stab_window = [{
                'timestamp': event['timestamp'],
                'lc_values': np.array(event['lc_values']).tolist()
            } for event in list(shelf_events.iloc[i - 1].loadcell_data['unit'][-stab_window_size:])]

            last_stab_point = [{
                'timestamp': shelf_events.iloc[i - 1].loadcell_data['unit'][-1]['timestamp'],
                'lc_values': np.array(shelf_events.iloc[i - 1].loadcell_data['unit'][-1]['lc_values']).tolist()}]

            # Extract current and last stability events
            last_stab = shelf_events.iloc[i - 1]
            current_stab = shelf_events.iloc[i]

            # Convert data to JSON format
            stabjson = bq_data_to_json_per_stability(current_stab, last_stab_point, last_stab_window, zeros)

            # if current_stab['stability_id'] == 'c80c6fc6-1b47-4285-834d-cd15d66adbc5' or current_stab['stability_id'] == 'e0b21f2b-f35d-4406-aef8-cad11ca6e602':
            #     print(current_stab['stability_id'])
            #     print("Stop")

            if filter_bad_previous_stability:
                if last_stab_point_is_bad(current_stab, last_stab_point,filter_above_weight):
                    continue

            # Write the JSON data to a file
            #filename = f"{directory}{i}_{current_stab['stability_id']}.json"#{shelf_id}_
            filename = f"{directory}{current_stab['stability_id']}.json"#{shelf_id}_
            with open(filename, "w") as outfile:
                json.dump(stabjson, outfile)

            # Save LCs data to excel file
            excel_filename = f"{directory_xls}{current_stab['stability_id']}.xlsx"  #
            save_lc_data_array_to_excel(current_stab.loadcell_data['unit'], excel_filename)

        print("Files stored for " + str(i) + " shelf events.")


def calc_delta_weight_with_last_stab_point(current_stab, current_stab_index, last_stab_point):
    factors = current_stab.loadcell_data['factors']
    first_weight_message_lc = current_stab.loadcell_data['unit'][current_stab_index]['lc_values']
    last_stab_point_lc = last_stab_point[0]['lc_values']
    delta_lc = first_weight_message_lc - last_stab_point_lc
    total_init_delta_w = sum(delta_lc * factors)
    return total_init_delta_w

def last_stab_point_is_bad(current_stab, last_stab_point, filter_above_weight, stbilizationThreshold = 20):
    total_init_delta_w = calc_delta_weight_with_last_stab_point(current_stab, 0, last_stab_point)
    expected_delta_w = calc_delta_weight_with_last_stab_point(current_stab, -1, last_stab_point)
    time_delta_sec = (current_stab.loadcell_data['unit'][0]['timestamp'] - last_stab_point[0]['timestamp']).total_seconds()
    if (abs(total_init_delta_w) > filter_above_weight) and time_delta_sec > 0:
        print("Skip stability_id: {}; total_init_delta_w: {}".format(current_stab['stability_id'], total_init_delta_w))
        return True
    if (abs(expected_delta_w) < stbilizationThreshold) and time_delta_sec > 0:
        print("Skip stability_id: {}; expected_delta_w: {} is below stbilizationThreshold {}".format(current_stab['stability_id'], expected_delta_w, stbilizationThreshold))
        return True
    return False


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

    # Save the DataFrame to an Excel file
    df.to_excel(filename, index=False)


# def datetime_to_unix_milli(dt):
#     '''Converts a datetime object to a Unix timestamp in milliseconds as a string.'''
#     # Convert datetime to timestamp in seconds
#     timestamp = dt.timestamp()
#     # Convert to milliseconds and format as a string with 3 decimal places
#     return f"{timestamp:.3f}"
#
# def process_files(directory):
#     for filename in os.listdir(directory):
#         filepath = os.path.join(directory, filename)
#         if os.path.isfile(filepath):
#             # do something with the file
#             with open(filepath) as f:
#                 contents = f.read()
#                 print(contents)


# def compare_tests_to_reults_from_listensor(res, directory,test_folder):
#     # res = bq_query()
#     counter = 0
#     num_files = 0
#     results_pd = pd.DataFrame()
#     directory = directory +test_folder
#     for dirname in os.listdir(directory):
#         print('stab id: ' + str(dirname))
#         if dirname=="99f57150-49ad-4983-b062-aafab9cd2801":
#             #004687a0-066f-41f7-a7b3-4bb082612837
#             print('')
#         num_files += 1
#         num_files_in_folder = 0
#         for filename in os.listdir(directory + dirname):
#             # filename=os.listdir(directory + dirname)[-1]
#             filepath = os.path.join(directory + dirname, filename)
#             if os.path.isfile(filepath):
#                 # do something with the file
#                 with open(filepath) as f:
#                     contents = f.read()
#                     contents_json = json.loads(contents)
#                     if len(res.loc[res['stability_id'] == dirname].index) > 0:
#                         k = res.loc[res['stability_id'] == dirname].index[0]
#                         if k and res.loc[k, "stability_id"] in list(os.listdir(directory)):
#                             # if res.loc[k, "weight_gr"]-1< contents_json['Weight'] and  contents_json['Weight']<res.loc[k, "weight_gr"]+1:
#                             #     counter+=1
#                             if "weight" in contents_json.keys():
#                                 actual_weight=contents_json['weight']
#                                 index = contents_json['index']
#                                 location = max(min(1,contents_json['location']),0)
#                                 timestamp = contents_json['timestamp']
#                             if "Weight" in contents_json.keys():
#                                 actual_weight = contents_json['Weight']
#                                 index = contents_json['Index']
#                                 location = max(min(1,contents_json['Location']),0)
#                                 timestamp = contents_json['timestamp']
#                             try:
#                                 nanos_to_seconds = timestamp['nanos'] / 1e9
#                                 full_timestamp = timestamp['seconds'] + nanos_to_seconds
#                             except Exception as e:
#                                 print(e)
#                                 full_timestamp = timestamp['seconds']
#                             # Full timestamp in seconds with nanoseconds as fractional part
#
#                             # Convert to datetime object
#                             dt_object = dt.utcfromtimestamp(full_timestamp)
#
#                             # Format datetime into a string (for example, in ISO format)
#                             readable_timestamp = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC'  # Adjusting microseconds to nanoseconds precision
#
#                             print('stability expected:' + str(res.loc[k, "weight_gr"]) + 'stability actual:' + str(actual_weight))
#                             results_pd.loc[counter, 'stability_id'] = dirname
#
#                             results_pd.loc[counter, 'point_cloud_weight'] = res.loc[k, "weight_gr"]
#                             results_pd.loc[counter, 'window_local_weight'] = actual_weight
#                             results_pd.loc[counter, 'point_cloud_location'] = res.loc[k, "location"]
#                             results_pd.loc[counter, 'window_local_location'] = location
#                             results_pd.loc[counter, 'index'] = index
#                             results_pd.loc[counter, 'local_timestamp'] = readable_timestamp
#                             results_pd.loc[counter, 'stab_timestamp'] =res.loc[k, "timestamp"]
#                             results_pd.loc[counter, 'num_stabilities_in_result'] =  len(os.listdir(directory + dirname))
#                             counter += 1
#
#     accuracy = 100 * counter / num_files
#     print("accuracy is : " + str(accuracy) + "\n")
#
#     # Then, sort the DataFrame by 'local_timestamp' in ascending order
#     results_pd.sort_values('local_timestamp', ascending=True, inplace=True)
#
#     # Now, drop duplicates based on 'stability_id', keeping the last occurrence (which is the latest due to the sort)
#     results_pd_no_duplicates = results_pd.drop_duplicates(subset='stability_id', keep='last')
#
#     results_pd_no_duplicates.sort_values('local_timestamp', ascending=True, inplace=True)
#     return results_pd_no_duplicates


# default_factors=[0.00016737552478256632, 0.00016856154589557767, 0.0001650441178345271, 0.00017250088010195726]
# default_zeros =[155078403.40206185, 157975228.3024055, 156668409.0137457, 159053332.16838488]
#
# DEFAULT_FACTORS = [1.8e-4, 1.8e-4, 1.8e-4, 1.8e-4]
# DEFAULT_ZEROES = [1.48938115E8, 1.48312189E8, 1.69847023E8, 1.73262903E8]


def get_distinct_shelf_ids(bay_ids, dataset, table_name):
    # Initialize a BigQuery client
    client = bq.Client()

    # Format the bay_id list for the query
    bay_ids_str = ', '.join(f"'{bay_id}'" for bay_id in bay_ids)

    # Define the query
    query = f"""
    SELECT DISTINCT shelf_id
    FROM `{dataset}.{table_name}`
    WHERE bay_id IN ({bay_ids_str})
    """

    # Run the query and fetch the results
    query_job = client.query(query)
    results = query_job.result()

    # Extract distinct shelf_ids from the results
    shelf_ids = set()
    for row in results:
        shelf_ids.add(row.shelf_id)

    # Return the unified list of distinct shelf_ids
    return list(shelf_ids)



''' Export stability LC data for debug and experiments by listensor emulation_test. '''


def get_data_per_bay_ids():
    global start_dt, end_dt, stability_list, shelf_list, id, res
    start_dt = dt(2024, 3, 20, 00, 00, 00, tzinfo=tz)
    end_dt = dt(2024, 9, 9, 00, 00, 00, tzinfo=tz)
    stability_list = None
    # shelf_list = ['exQUru94RG2I+MoJwotiQQ', '1tZ0xN-HT1Gg+LEUOAiWmA', '18oGcrecQASwnJL94v-Dlg', 'dsuzxH0ETHi4A0MDPk925g','B33-orwXRjiF-a7Q2g5nkA']  #MegaMat
    bay_ids = [
        '8X4NsUH0R-W82IORzU02eA',  # 'Ramat_Gan',
        'G1kMNVBjRMOSHfWo-10eGQ',  # 'Estar2',
        'Mj2WdQkUSq6Fp9kdcwZDuw',  # 'MegaMat',
        'Epd1G16SQlyUvyeCO8RJkg',  # 'UK-SM-RECKITT-02',
        'O-zPS3SsQpaOjwY8hMzoxA',  # 'UK-SM-ATLAS-ELECTRONIKS-01',
        'CcjV8hKlS4eOeLnFirptoA',  # 'UK-SM-AO-02',
        'Ad3NzQ0-RGSKJx4tTBEWHw',  # 'UK-SM-RECKITT-01',
        'Cfjn3NYIQ6SPkMI4cWSOEg',  # 'DE-SOEHNLE-TRYBUY',
        'H2tkl29CSBGbenAYj3jc8A',  # 'DK-CFC-TRYBUY',
        'qt6OJ-8HR6+kDc5Y7ReRYA',  # 'NL-HLF-TRYBUY'
    ]
    ### Not in RETROFIX Yet:
    # 'C9VK0e5rTGOqSP6d2nQFCg', # 'FR-ET-SD-011',
    # 'QYQKuPMCQCiX9LaI9hocuQ', # 'FR-ET-SD-008',
    # 'dDMfb511S0iJ3PpNXz1hig', # 'UK-SM-CATERHAM-SCHOOLS-1 ',
    # 'JiQtg5UPR8OKndNfoTokSQ', # 'UK-SM-DANONE-NUTRICIA-1',
    shelf_list = get_distinct_shelf_ids(bay_ids, dataset=dataset, table_name='RecognitionStorage')
    print("Shelves list:")
    for id in shelf_list:
        print(id)
    res = stability_bq_data(start_dt, end_dt, shelf_list, stability_list, dataset=dataset, table_name=table_name)
    return res


if __name__ == "__main__":

    with open('../config.json', 'r') as config_file:
        config = json.load(config_file)

    qa_path_service_account = config['qa_path_service_account'] #example: "qa_path_service_account": "C:/Lena/Projects/shekel-qa-9066809a1872.json",
    tests_folder = config['tests_folder'] #example: "tests_folder": "C:/Lena/data/Stability_Tests/"

    # '''get stabilities from file'''
    # stab,time=read_json_to_df("C:/Users/Asael/git_projects/listensor/stability/data/50_50_3_go.json")

    # ''' gcloud'''
    # path_service_account = "C:/Users/Asael/git_projects/bi/shekel-gcloud-4d961ef67708.json"
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_service_account

    '''get stabilities from bq'''
    from dateutil import tz
    tz = tz.gettz("Etc/UTC")
    #dataset = f"env_algo"
    #dataset = f"env_qa"
    dataset = f"env_cooler"
    table_name = "StabilityEvents"


    if dataset != "env_integration" and dataset != "env_cooler":
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = qa_path_service_account

    # start_dt = dt(2024, 8, 7, 12,33,30, tzinfo=tz)
    # end_dt =   dt(2024, 8, 7, 12,38,00, tzinfo=tz)
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\Mini_LMR_ver2_0_23_AlphaHz25\\"

    # start_dt = dt(2024, 8, 7, 12,37,45, tzinfo=tz)
    # end_dt =   dt(2024, 8, 7, 13,4,30, tzinfo=tz)
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\Mini_LMR_T0_Wind_AlphaHz25\\"

    # start_dt = dt(2024, 8, 5, 14,18,20, tzinfo=tz)
    # end_dt =   dt(2024, 8, 5, 14,23,30, tzinfo=tz)
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\HUBZ_LMR_ToleranceWeight3_AlphaHz6\\"

    # start_dt = dt(2024, 8, 7, 13,48,55, tzinfo=tz)
    # end_dt =   dt(2024, 8, 7, 14,51,00, tzinfo=tz)
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\LMR_ToleranceWeight3_AlphaHz6_Aug7_withExcel\\"

    # start_dt = dt(2024, 8, 13, 14,15,40, tzinfo=tz)
    # end_dt =   dt(2024, 8, 13, 14,26,10, tzinfo=tz)
    # dataset = f"env_qa"
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\LMR_ToleranceWeight3_AlphaHz6_HUBZ_shelf3\\"

    # start_dt = dt(2024, 8, 14, 7,11,58, tzinfo=tz)
    # end_dt =   dt(2024, 8, 14, 8,21,50, tzinfo=tz)
    # dataset = f"env_qa"
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\LMR_ToleranceWeight3_AlphaHz6_HUBZ_shelf2\\"

    # start_dt = dt(2024, 8, 13, 8, 20, 00, tzinfo=tz)
    # end_dt = dt(2024, 8, 13, 8, 51, 50, tzinfo=tz)
    # tests_folder = "C:\\Lena\\data\\Stability_Tests\\LMR_ToleranceWeight3_AlphaHz6_Aug13\\"

    ''' !!! Note: set start_dt to get at least one stability prior to the experiment start for getting previous stability values'''
    #stability_list = ['c59e1c05-b5a8-4442-abb1-09f879ff7e05', 'ea3448e0-5797-4b20-bd13-f816a3e260c4', 'c0c03340-e091-49e2-987d-279d39defb19']
    #res = stability_bq_data(start_dt, end_dt, stability_list, dataset=dataset, table_name=table_name)

    ### MegaMat and more field data
    # res = get_data_per_bay_ids()


    start_dt = dt(2024, 10, 28, 00, 00, 00, tzinfo=tz)
    end_dt = dt(2024, 10, 29, 00, 00, 00, tzinfo=tz)
    tests_folder = "C:\\Lena\\data\\Stability_Tests\\debug\\wrong_last_stable_timestamp\\"
    stability_list = ['5313b421-53ee-42ad-ba2e-a7ba91536ce2', 'ab80d99c-dbe4-4e97-8baf-daaafb77d1cf']  #ab80 - stability before the debuged one
    res = stability_bq_data(start_dt, end_dt, stability_list, dataset=dataset, table_name=table_name)


    # shelf_list = None
    # stability_list = None
    # res = stability_bq_data(start_dt, end_dt, shelf_list, stability_list, dataset=dataset, table_name=table_name)
    ''' create json files'''
    STAB_WINDOW_SIZE = 50  # num of samples to keep availible in the last_stab_window - part of them can be used by Go Algo
    create_stability_file_from_bq(tests_folder,res,[0,0,0,0],stab_window_size=STAB_WINDOW_SIZE,
                                  filter_bad_previous_stability = True, filter_above_weight = 15)

    res = res.drop(columns=['loadcell_data'])
    output_file = tests_folder + 'stab_to_go_query_output.csv'
    res.to_csv(output_file)
    print('Done.')
