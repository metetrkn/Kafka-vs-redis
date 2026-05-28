import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

# 1. Load Data
csv_path = r'C:\Users\metet\Desktop\aws-version\kafka\log-analyzer-new\log_report_kafka.csv'
df = pd.read_csv(csv_path)

# Generate dynamic display labels for consumers
df['consumer_label'] = df['topic'].apply(lambda x: x.split('-')[0].capitalize()) + ": " + df['consumer'].astype(str)

# 2. Fix: Check and Fill Missing Topics Grouped per Report ID
required_topics = ['low-priority-mails', 'high-priority-mails']
filled_rows = []

for report_id, group in df.groupby('report_id'):
    for topic in required_topics:
        if topic not in group['topic'].values:
            filled_rows.append({
                'report_id': report_id,
                'topic': topic,
                'consumer': 0,
                'total_mails': 0,
                'average_execution_time_(s)': 0.0,
                'max_execution_time_(s)': 0.0,
                'grand_total_mails': group['grand_total_mails'].values[0] if len(group) > 0 else 0,
                'total_errors': 0,
                'consumer_label': topic.split('-')[0].capitalize() + ': 0'
            })

if filled_rows:
    df = pd.concat([df, pd.DataFrame(filled_rows)], ignore_index=True)

# 3. Aggregate Metrics cleanly by ID and Topic
df_agg = df.groupby(['report_id', 'topic']).agg({
    'max_execution_time_(s)': 'max',
    'average_execution_time_(s)': 'mean'
}).reset_index()

# 4. Initialize Plot Layout
sns.set_theme(style="whitegrid")
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2)

ax1 = fig.add_subplot(gs[0, 0]) 
ax2 = fig.add_subplot(gs[0, 1]) 
ax3 = fig.add_subplot(gs[1, :]) 

palette = {'low-priority-mails': 'blue', 'high-priority-mails': 'red'}

# --- Chart 1: Max Execution Time ---
sns.barplot(
    data=df_agg,
    x='report_id',
    y='max_execution_time_(s)',
    hue='topic',
    palette=palette,
    ax=ax1
)
ax1.set_title('Max Execution Time (Aggregated by Topic)')
ax1.set_xlabel('Report ID')
ax1.set_ylabel('Max Time (s)')

# --- Chart 2: Average Execution Time ---
sns.barplot(
    data=df_agg,
    x='report_id',
    y='average_execution_time_(s)',
    hue='topic',
    palette=palette,
    ax=ax2
)
ax2.set_title('Avg Execution Time (Aggregated by Topic)')
ax2.set_xlabel('Report ID')
ax2.set_ylabel('Avg Time (s)')

# --- Chart 3: Total Mails Handled Per Consumer ---
unique_consumers = df['consumer_label'].unique()
custom_colors = {
    label: 'red' if 'High' in label or 'high' in label else 'blue' 
    for label in unique_consumers
}

sns.pointplot(
    data=df,
    x='report_id',
    y='total_mails',
    hue='consumer_label',
    palette=custom_colors,  
    dodge=0.2,  # Added minor visual separation for identical x-points
    linestyle='none',
    markersize=6,
    ax=ax3
)
ax3.grid(True, axis='y', alpha=0.3)
ax3.set_title('Total Mails Handled (Point Comparison)')
ax3.set_xlabel('Report ID')
ax3.set_ylabel('Total Mails')
ax3.legend(bbox_to_anchor=(1.01, 1.0), loc='upper left', title='Consumer (Low/High)')

# 5. Save and Close Plot
plt.tight_layout()
save_path = r'C:/Users/metet/Desktop/aws-version/kafka/log-analyzer-new/report-kafka.png'

# Ensure parent path directory exists before saving
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=300)
plt.close()

print(f"Reporting compilation complete! Output saved to: {save_path}")