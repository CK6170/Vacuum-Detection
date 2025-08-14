import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# === Inputs ===
ids = [
    # '57c923a1-288f-4fb0-99e5-045fc35bdf0a',
    # '9f3b7926-7f39-435b-a481-aab3db6ee5fe',
    # '51d0ff3e-3a9f-4071-8758-311fc2176d4a',
    # '47bd738a-0a30-43a5-be09-f88164130f7c',
    # '85f1bcf0-20e7-4112-b995-7a3c21d8e709',
    # '2a344446-60c0-4062-ad61-fa775111944a',
    # 'c24708b9-49c5-401a-9416-01963241d99e'
    'eb2bfd3d-b9f0-4d40-98ff-7652454a418f',
'abc7cd5e-1e30-4870-b6cb-cd6047c4684f',
'6f64d2b7-78a9-48d5-a35e-cd2ee0588d89',

]

file_dir = Path('.')  # Change if files are in a different directory

# === Load and Concatenate Data ===
dfs = []
for id_ in ids:
    file_path = file_dir / f"{id_}_lc_data.xlsx"
    if file_path.exists():
        df = pd.read_excel(file_path)
        df['stability'] = None  # Add stability column
        df.loc[df.index[-1], 'stability'] = df.loc[df.index[-1], 'total_weight']  # Set last row stability
        dfs.append(df)
    else:
        print(f"File not found: {file_path}")

if not dfs:
    raise ValueError("No valid Excel files found.")

# Combine data
combined_df = pd.concat(dfs, ignore_index=True)

# Convert timestamp column to datetime
combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])

# Drop duplicate timestamps only where stability is empty
mask_empty_stability = combined_df['stability'].isna()
df_empty_stab = combined_df[mask_empty_stability].drop_duplicates(subset='timestamp')
df_with_stab = combined_df[~mask_empty_stability]
combined_df = pd.concat([df_empty_stab, df_with_stab], ignore_index=True)

# Filter for total_weight in specified range
# combined_df = combined_df[
#     (combined_df['total_weight'] > 149000) &
#     (combined_df['total_weight'] < 150000)
# ]

# Sort final DataFrame
combined_df = combined_df.sort_values('timestamp')

# === Save to Excel ===
combined_df.to_excel("case_1.xlsx", index=False)

# === Plotting ===
plt.figure(figsize=(12, 6))
plt.plot(combined_df['timestamp'], combined_df['total_weight'], label='Total Weight', marker='o')

# Plot stability values
stability_df = combined_df.dropna(subset=['stability'])
if not stability_df.empty:
    plt.plot(
        stability_df['timestamp'],
        stability_df['stability'],
        'ro',
        markersize=10,
        label='Stability'
    )

plt.title("Filtered Total Weight and Stability per Timestamp")
plt.xlabel("Timestamp")
plt.ylabel("Weight")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("total_weight_plot.png")
plt.show()