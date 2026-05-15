import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# --- PRE-PROCESSING FOR MAILS GRAPH ---
df = pd.read_csv('C://Users//metet//Desktop//microservice-kafka-rqueue-mail-tests//kafka//log-analyzer//log_report.csv')
df['consumer_label'] = df['topic'].apply(lambda x: x.split('-')[0].capitalize()) + ": " + df['consumer'].astype(str)
df_agg = df.groupby(['report_id', 'topic']).agg({
    'max_execution_time_(s)': 'max',
    'average_execution_time_(s)': 'mean'
}).reset_index()

# 2. Setup Visualization (2 Rows, 2 Columns)
sns.set_theme(style="whitegrid")
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2)

ax1 = fig.add_subplot(gs[0, 0]) 
ax2 = fig.add_subplot(gs[0, 1]) 
ax3 = fig.add_subplot(gs[1, :]) 

# --- Graph 1: Max Time (Top Left) ---
sns.barplot(
    data=df_agg,
    x='report_id',
    y='max_execution_time_(s)',
    hue='topic',
    palette='viridis',
    ax=ax1
)
ax1.set_title('Max Execution Time (Aggregated by Topic)')

# --- Graph 2: Avg Time (Top Right) ---
sns.barplot(
    data=df_agg,
    x='report_id',
    y='average_execution_time_(s)',
    hue='topic',
    palette='viridis',
    ax=ax2
)
ax2.set_title('Avg Execution Time (Aggregated by Topic)')

# --- Prepare Custom Colors for Graph 3 ---
unique_consumers = df['consumer_label'].unique()
custom_colors = {
    label: 'red' if 'High' in label else 'blue' 
    for label in unique_consumers
}

# --- Graph 3: Total Mails (Bottom) ---
sns.pointplot(
    data=df,
    x='report_id',
    y='total_mails',
    hue='consumer_label',
    palette=custom_colors,  
    dodge=True,
    linestyle='none',
    markersize=5,
    linewidth=1,
    ax=ax3
)
ax3.grid(True, axis='y', alpha=0.3)
ax3.set_title('Total Mails Handled (Point Comparison)')
ax3.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')

# --- 4. SHOW THE PLOT ---
plt.tight_layout()  

# --- SAVE THE PLOT ---
save_path = r'C:/Users/metet/Desktop/microservice-kafka-rqueue-mail-tests/kafka/log-analyzer/report.png'
plt.savefig(save_path, dpi=300) # dpi=300 ensures high quality for reports
print(f"Plot successfully saved to: {save_path}")

# Optional: Close the plot to free up memory
plt.close()      