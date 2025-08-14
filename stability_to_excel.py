import os
import google.cloud.bigquery as bq
import stability_to_go
from datetime import datetime as dt
from datetime import timezone

def main(stability_id, start_dt, end_dt):
    #dataset = f"env_qa"
    #dataset = f"env_cooler_test"
    dataset = f"env_cooler"
    #dataset = f"env_integration"
    #dataset = f"env_algo"
    table_name = "StabilityEvents"

    #path_service_account = "../shekel-qa-12ee1de1ae03.json"
    path_service_account = "C:/Lena/Projects/shekel-qa-9066809a1872.json"

    if dataset != "env_integration" and dataset != "env_cooler":
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_service_account

    query_txt = \
        """
            select stability_id, weight_gr, location, loadcell_data, last_stable_timestamp, timestamp
            from {}.{}
            where timestamp > TIMESTAMP("{}")
                AND timestamp < TIMESTAMP("{}") 
            AND 
            stability_id = "{}"
                #limit 10000
            """.format(dataset, table_name, start_dt, end_dt, stability_id) #start_dt end_dt

    a = bq.Client()
    a = a.query(query_txt)
    stability_df = a.to_dataframe()
    if stability_df.empty:
        print("No data found for query")
        #raise EmptyDataError("No data found for query")

    stability_df = stability_df.drop_duplicates(subset='stability_id', keep='first')

    return stability_df


def plot_stab_chart_from_excel(excel_filename,chart_filename):
    import matplotlib.pyplot as plt
    import pandas as pd

    combined_df = pd.read_excel(excel_filename)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])

    # # Filter for total_weight in specified range
    # combined_df = combined_df[
    #     (combined_df['total_weight'] > 149000) &
    #     (combined_df['total_weight'] < 150000)
    #     ]

    # === Plotting ===
    plt.figure(figsize=(12, 6))
    plt.plot(combined_df['timestamp'], combined_df['total_weight'], label='Total Weight', marker='o')

    # # Plot stability values
    # stability_df = combined_df.dropna(subset=['stability'])
    # if not stability_df.empty:
    #     plt.plot(
    #         stability_df['timestamp'],
    #         stability_df['stability'],
    #         'ro',
    #         markersize=10,
    #         label='Stability'
    #     )

    plt.title("Filtered Total Weight and Stability per Timestamp")
    plt.xlabel("Timestamp")
    plt.ylabel("Weight")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_filename)
    plt.show()
    return


if __name__ == '__main__':
    from dateutil import tz
    tz = tz.gettz("Asia/Jerusalem")
    # start_dt = dt(2024, 7, 31, 00, 00, tzinfo=tz).astimezone(timezone.utc)
    # end_dt = dt(2024, 7, 31, 23, 59, tzinfo=tz).astimezone(timezone.utc)

    #stability_id = '7d818930-55c4-4d53-806c-d821a5393356'
    #stability_id = '026a9529-efd8-4a2e-b487-51ca69e0af48'
    #stability_id = '3ac69c1a-5a6d-44f3-a93c-8c9674d40361'
    #stability_id = '5313b421-53ee-42ad-ba2e-a7ba91536ce2'
    #stability_id = 'aac80401-80cd-4e26-979d-242d195f3989'
    #stability_id = 'be721f2d-c5ef-4e06-9ad4-1a8b4d5926b4' #'abb54a9d-e2f0-445d-9dfa-f63a931c232d' #'7d818930-55c4-4d53-806c-d821a5393356' #'ae907018-2937-4ff2-9f4c-f921da5e9630'

    # --- calm
    #stability_id = 'e1dded5e-62c2-4a2c-93d2-9f1774f6aca0'  #-770 D10 after above 30 sec
    #stability_id = 'f1a56cbf-182a-40a0-9e02-9d0487b4aca8'  # 31/7 -119 after ~2 min  D10 shelf 3
    #stability_id = '810478a8-c71e-4227-842a-456017f61c47'   # 20/11 -3047 after ~1 h  D10 shelf 3 (was an event on another shelf)
    #stability_id = '005a22c7-c878-4887-9447-d750df749868'   # 20/11 420 after 20 sec  D10 shelf 2
    # --- quick
    #stability_id = '4e1f6419-87eb-43bc-b1ed-fea36d206981' # 31/7 -3000  4 sec after +3000  D10 shelf 2
    #stability_id = 'b3427cad-772b-4195-9ced-bbe694d70603' # 20/11 -2368  4 sec after +3500  D10 shelf 2
    #stability_id = '2f74cf8e-3e93-44a8-b893-1bc5cd70caa7' # 20/11 951  11 sec after +2500  D10 shelf 2
    #stability_id = '8a2f4512-0ff0-4505-b077-ab211855f9c8' # 20/11 -1490  3.5 sec after +3300  D10 shelf 3
    #stability_id = '46b322c7-f270-478a-93bc-6bbb17efe723' # 20/11 -262  2.5 sec after +3000  D10 shelf 2
    #--stability_id =  'ea0f1b9c-b30a-4fe3-8116-a4e3997c9663' # 20/11 -2400  2.5 sec after +2400  D10 shelf 2  not in DB
    #stability_id =  '1183ad13-f345-484e-ac92-c5da258c7423' # 20/11 768  3 sec after +3155  D10 shelf 2
    #stability_id =  '465e0e79-1430-496f-bce8-73b2289a4f79' # 20/11  +3155  D10 shelf 2

    # -- 2 persons 4 sec
    # stability_id = 'ebf49506-f03b-4d2e-9f10-1eb25c541ca9'  #31/7 D10 shelf5
    # stability_id = '70e7e71d-aa84-4227-8de8-d8c22c89d344'  #31/7 prev
    # stability_id = '5dcdcbff-acdb-4bc4-a6d0-2d2daf702d7e'  #20/11 D10 shelf5  PREV: 5499a350-5f6e-412e-867b-4b23da429d8d
    #stability_id = '4b2cfaf8-d231-4eab-956d-ab528fb45b2f'  # 20/11 D10 shelf5  PREV: 5499a350-5f6e-412e-867b-4b23da429d8d
    #stability_id = '59d126c0-43c4-4615-82b9-6d6e92a50a3d'  # 20/11 D10 shelf5  PREV: 5499a350-5f6e-412e-867b-4b23da429d8d

    stability_id = 'd8bc38d0-ecfc-4aeb-ab8a-64bf460af6d4'    #16/5
    stability_id = 'ca447c04-8f44-43c2-b3da-2f4590540727'   #25/4
    stability_id = '2f7aee61-8e05-4eb7-97e3-bc5eace50fce'   #17/5
    stability_id = 'ac78ab60-0889-4472-826e-c342de1891e6'   #12/4
    stability_id = '0b749fa1-aeda-4607-b379-a8aa0381e292'   #12/4
    stability_id = '48b54275-d855-4b3b-b949-965fe0dcfd16'   #17/5
    stability_id = '378ebc77-a8a7-40c2-a603-c66034b29614'   #17/5
    stability_id = 'd7c6df7e-30c3-4469-8813-4f03882b2076'   #12/4
    stability_id = 'b267527a-2fb1-4f3c-99e1-dad42a3af0f4'   #12/4

    stability_id = '311a917c-64c6-4da9-aa2b-3cfe3eba7ec7' #'b2f87f9c-b2d7-493c-8a9c-ab115a3e02e7'   #morning new listensor
    #stability_id = '0d1a22b9-08dd-421b-85f5-c528357c1edc' #'1d927d31-3399-4d8f-90a5-7482cd1dcdca'   #eve  old listensor
    stability_id = '47bd738a-0a30-43a5-be09-f88164130f7c'

    #Slow Drag case 1  yCi+n7FrRKiUoO7FzcCeDA
    stability_id = '57c923a1-288f-4fb0-99e5-045fc35bdf0a'
    stability_id = '9f3b7926-7f39-435b-a481-aab3db6ee5fe'
    stability_id = '51d0ff3e-3a9f-4071-8758-311fc2176d4a'
    stability_id = '47bd738a-0a30-43a5-be09-f88164130f7c'
    stability_id = '85f1bcf0-20e7-4112-b995-7a3c21d8e709'
    stability_id = '2a344446-60c0-4062-ad61-fa775111944a'
    stability_id = 'c24708b9-49c5-401a-9416-01963241d99e'

    #Ethik cases - cart 8902013
    stability_id = '86327288-14f9-439e-b739-89853005215e'
    stability_id = '3e510fb0-e890-478b-a325-168224ee668c'
    stability_id = 'df698246-da3f-4d3c-995e-d987d70ca2b6'
    stability_id = '6bed3d8a-9bec-47e8-8b81-9b0f15a2d18d'


    stability_id = '718dad77-9c42-4e22-9829-6e6646b4adc6'  #cart 136082 (not in Shekel)
    stability_id = '5291b53e-80d9-4c48-a358-40248bfb99fa'  #cart 9089456
    stability_id = '40c26827-30a0-43e7-90a3-4807e705e21e'  #cart 3902630  (not in Shekel)
    stability_id = '70dc1885-2cac-4c99-afff-d17ecb2c47a4'  #cart 6597537   (not in Shekel)
    stability_id = '73187060-2429-4ae6-9c05-6f8a13f9fb4a'  #cart 5409398    (not in Shekel)

    #wurth
    # stability_id = 'eb2bfd3d-b9f0-4d40-98ff-7652454a418f'
    #stability_id = 'abc7cd5e-1e30-4870-b6cb-cd6047c4684f'
    #stability_id = '6f64d2b7-78a9-48d5-a35e-cd2ee0588d89'
    stability_id = 'e467a215-ab3e-4166-80ba-22c47ff97283'
    stability_id = 'c081226d-e13d-4fc5-8d1f-4a886c185a2a'

    #Warrior Vending cases
    stability_id = '62fcf317-a605-4b4a-9e15-697573af5d0c'
    stability_id = 'b8c27945-8808-49d7-8fae-b096cc23b2cb'

    start_dt = dt(2025, 3, 29, 00, 00, tzinfo=tz).astimezone(timezone.utc)
    end_dt = dt(2025, 6, 18, 23, 59, tzinfo=tz).astimezone(timezone.utc)

    stability_list = [
        #  vacuum examples
        # 'faf95e64-a1ff-4481-b02d-736c43a3c0dc','1bf11838-fc4d-4c1e-89e7-208f1f258bc3','19367cff-f984-459f-8729-1078e6038556','8b2a8986-0b50-49f3-90c6-8d1f8ec65451','459eb87b-aca2-4aa2-9338-0ad830e013da','fb47ee54-4f3d-4c42-a4f0-941908e18c08','e33eab74-84ae-4ae4-8265-bcdbbe2f5bfa','db248c97-196b-46b8-b21d-329bb8769633',
        # '739fb430-b90e-4f56-8437-2dde4ff08c2a','e15c1375-d687-4bb3-b4c7-e30c68726ca0','9a30945e-1448-44e4-ae2f-965548209b02','2d753475-4d95-4420-bc36-99f648522b87','448d4eb3-7380-4239-94a5-b12652e18024','6d5d31a9-4857-426c-b1c2-e659fe891b61','b780bd18-bdd5-4743-8b46-b9684af49c26','5a05a049-68e0-4595-a5a7-5e0fb8d05eb8',
        # '7bc0db48-a52d-4630-a57c-743fc9ca2909','392b3854-1814-4cde-a9bb-ef1a9cf83d1b','790968eb-1f04-42e4-a9d0-0630fad7e3a7','4e268fc5-147f-4796-9dd5-2e5a92be7d0b','64bd8db5-9174-4207-8cd4-8a4f2fde2872','0869120f-980f-4246-8b14-d9f2a059fdbd'

        #  non vacuum examples
        # 'e122df8c-885a-48e0-b4f7-269b73451306', 'ae9cfedd-d814-47bf-9a86-75fe4c6098f2','7660a22c-3866-4117-842d-d3b8c2d795e1', '38323d9e-7672-4e55-a167-eb3280fcce7b',
        # 'f76cfab2-6852-4bce-bbb8-f4f291369d6f', 'f0ed7206-1c06-4a2a-93a5-fd1d88c9907d','c982a591-a1fc-49ba-b64e-c0323a86e8f9', '50514d5a-3e9f-460c-8bf7-ca3ddc7c85d0','f71268a8-ee18-428e-aebc-8c2f1090e2c4',
        # 'c2d91dc7-4434-475f-bdd0-9b0240349ab2','bc21a9c9-886c-4ff9-8e5e-a0ecf274490e', 'c90aa535-ab49-414e-8236-7617b22fadc7','62bab309-88be-4fe1-a69a-a1a5182b0f2f', '414dc292-c1ae-4776-b759-e4a933f11115',
        # '755ea52c-636d-4645-bd8a-19b763ce5349', '20f8ec59-85c1-4efc-9a3a-3ff3e6214dd0','20d75a66-7a0e-4076-b097-939a70ffcc2e', '6c51f0f0-f5ce-4220-9f50-2872329545a8'

        #mid events from the same carts
        'b9654f42-daa3-4df7-b212-00616409b03b', 'ae5d0d58-364c-42c5-bf44-268ab62a5bd9','c0bb44ff-9681-47a5-9071-34313ba03928', '86c979aa-2fe5-4bd2-b2d6-1d469196102f',
        'fc471437-717d-4dec-87b7-8b58baa4a4da', 'fbc59628-b0cb-4eb9-9cdf-d163160b1095','3ffa8597-aa36-4cea-b47a-71a1c38289b7', 'b935336f-114c-46c2-a912-0bbb83ea3c11',
        '58103cab-8ee0-4cbf-9b52-3ac7c4c7be81', 'c297006a-0b5c-4c5e-9124-b0520248c571','f38ac4da-5350-474c-984b-d5657fd1a9fb', '550fd3ec-12c0-46e6-81f5-9c9ba637eac2',
        'f4b6aee3-ea64-4446-ae9d-ca2a17fb7862', '7d18a49c-4278-4a8a-8ec8-0a28941a8564','d93f63ce-293d-4391-bd00-4395d42738c1'
    ]

    #stability_list.append(id)


    for stability_id in stability_list:
        excel_filename = f"{stability_id}_lc_data.xlsx"  #
        chart_filename = f"{stability_id}_totalW.png"  #
        stability_df = main(stability_id,  start_dt, end_dt)
        stability_to_go.save_lc_data_array_to_excel(stability_df['loadcell_data'][0]['unit'], excel_filename)
        #plot_stab_chart_from_excel(excel_filename,chart_filename)


