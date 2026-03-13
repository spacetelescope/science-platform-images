import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets, HTML
import datetime
from IPython.display import display
import glob


# Path to the folder containing the CSV files
folder_path = "/cost-metrics/"
all_files = glob.glob(folder_path + "**/*.csv.gz", recursive=True)

# Expected columns
EXPECTED_COLUMNS = [
    "date",
    "teamname",
    "cost_last_interval_cpu",
    "cost_last_interval_memory",
    "cost_last_interval_egress",
    "cost_last_interval_efs_storage",
    "total_cost",
    "user",
]

# Read and validate CSV files
dfs = []
for f in all_files:
    try:
        df_temp = pd.read_csv(f, parse_dates=["date"])
        # Validate columns
        if list(df_temp.columns) != EXPECTED_COLUMNS:
            raise ValueError(f"File {f} has unexpected columns: {df_temp.columns.tolist()}")
        dfs.append(df_temp)
    except Exception as e:
        print(f"Skipping {f}: {e}")

# Combine valid files
df = pd.concat(dfs, ignore_index=True)

# Ensure 'date' is datetime and sort
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Plot function
def plot_dashboard(selected_user="All", selected_team="Total credit usage", start_date=None, end_date=None, cost_metric="total_cost"):
    # Convert display name to actual value for filtering
    actual_team = selected_team
    if selected_team == "Personal Server":
        actual_team = "no-team"

    filtered_df = df.copy()

    # Filter by user
    if selected_user != "All":
        filtered_df = filtered_df[filtered_df["user"] == selected_user]

    # Filter by team
    if actual_team != "Total credit usage":
        filtered_df = filtered_df[filtered_df["teamname"] == actual_team]

    # Filter by date range
    if start_date:
        filtered_df = filtered_df[filtered_df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df["date"] <= pd.to_datetime(end_date)]

    if filtered_df.empty:
        print("No data in the selected range.")
        return

    # Determine team label for display
    if selected_team == "Total credit usage":
        team_label = "Total credit usage"
    elif selected_team == "no-team":
        team_label = "Personal Server"
    else:
        team_label = selected_team

    # Prepare pie chart data
    team_totals = filtered_df.groupby("teamname")["total_cost"].sum()
    team_totals = team_totals[team_totals > 0]
    has_pie = False # not team_totals.empty
    if has_pie:
        team_totals.index = [("Personal Server" if t == "no-team" else t) for t in team_totals.index]

    if has_pie:
        fig, (ax_bar, ax_pie) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={'width_ratios': [2, 1]})
    else:
        fig, ax_bar = plt.subplots(1, 1, figsize=(13, 5))

    # Determine which metrics to show based on selection
    # Determine which metrics to show based on selection
    # Define consistent color mapping for all metrics
    metric_colors = {
        'cost_last_interval_cpu': '#1f77b4',
        'cost_last_interval_memory': '#ff7f0e',
        'cost_last_interval_egress': '#2ca02c',
        'cost_last_interval_efs_storage': '#d62728'
    }
    
    if cost_metric == "total_cost":
        # Show stacked bar chart with all components
        metrics_to_plot = ['cost_last_interval_cpu', 'cost_last_interval_memory',
                          'cost_last_interval_egress', 'cost_last_interval_efs_storage']
        labels = ['CPU', 'Memory', 'Egress', 'EFS Storage']
        colors = [metric_colors[metric] for metric in metrics_to_plot]
    else:
        # Show stacked bar chart with just the selected metric
        metrics_to_plot = [cost_metric]
        labels = [metric_display_names.get(cost_metric, cost_metric)]
        colors = [metric_colors.get(cost_metric, '#1f77b4')]

    if selected_user == "All":
        # For multiple users, show grouped stacked bars
        users = sorted(filtered_df["user"].unique())
        dates = sorted(filtered_df["date"].unique())
        x = range(len(dates))
        width = 0.8 / len(users)

        for i, user in enumerate(users):
            user_df = filtered_df[filtered_df["user"] == user]
            bottom = None
            for j, metric in enumerate(metrics_to_plot):
                values = [user_df[user_df["date"] == d][metric].sum() if d in user_df["date"].values else 0 for d in dates]
                ax_bar.bar([pos + i * width for pos in x], values, width,
                           label=f"{user} - {labels[j]}" if len(metrics_to_plot) > 1 else user,
                           color=colors[j], bottom=bottom)
                if bottom is None:
                    bottom = values
                else:
                    bottom = [b + v for b, v in zip(bottom, values)]

        ax_bar.set_xticks([pos + width * (len(users) - 1) / 2 for pos in x])
        ax_bar.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates], rotation=45)
        ax_bar.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        title_suffix = f" — {team_label}" if selected_team != "Total credit usage" else ""
        ax_bar.set_title(f"{metric_display_names.get(cost_metric, cost_metric)} Over Time (All Users){title_suffix}")
    else:
        # For single user, show stacked bars
        dates = sorted(filtered_df["date"].unique())
        x = range(len(dates))
        bottom = None

        for i, metric in enumerate(metrics_to_plot):
            values = [filtered_df[filtered_df["date"] == d][metric].sum() for d in dates]
            ax_bar.bar(x, values, label=labels[i], color=colors[i], bottom=bottom)
            if bottom is None:
                bottom = values
            else:
                bottom = [b + v for b, v in zip(bottom, values)]

        ax_bar.set_xticks(x)
        ax_bar.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates], rotation=45)
        if len(metrics_to_plot) > 1:
            ax_bar.legend()
        title_suffix = f" — {team_label}" if selected_team != "Total credit usage" else " — Total credit usage"
        ax_bar.set_title(f"{metric_display_names.get(cost_metric, cost_metric)} Over Time — {selected_user}{title_suffix}")

    ax_bar.set_xlabel("Date")
    ax_bar.set_ylabel("Credits")
    ax_bar.grid(axis='y', alpha=0.3)

    # print("No have pie...")
    # Pie chart: total cost per team
    # if has_pie:
    #     ax_pie.pie(team_totals, labels=team_totals.index, autopct='%1.1f%%',
    #                startangle=140, colors=plt.cm.Set2.colors[:len(team_totals)])
    #     ax_pie.set_title("Total Cost by Team")

    plt.tight_layout()
    plt.show()

    # Display summary statistics
    html_content = f"""
    <style>
        .credit-summary {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-top: 30px;
            margin-bottom: 20px;
            clear: both;
            overflow: auto;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
            overflow: hidden;
        }}
        .card-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }}
        .credit-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 10px;
        }}
        .credit-item {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .credit-label {{
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .credit-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        .total-item {{
            grid-column: 1 / -1;
            background: rgba(255, 255, 255, 0.3);
            text-align: center;
        }}
        .total-item .credit-value {{
            font-size: 32px;
        }}
    </style>

    <div class="credit-summary">
        <div class="summary-card">
            <div class="card-title">Cumulative credits for {selected_user} over selected period of time</div>
            <div class="credit-grid">
                <!--
                <div class="credit-item total-item">
                    <div class="credit-label">TOTAL CREDITS</div>
                    <div class="credit-value">{filtered_df['total_cost'].sum():.4f}</div>
                </div>
                -->
                <div class="credit-item">
                    <div class="credit-label">CPU Credits</div>
                    <div class="credit-value">{filtered_df['cost_last_interval_cpu'].sum():.4f}</div>
                </div>
                <div class="credit-item">
                    <div class="credit-label">Memory Credits</div>
                    <div class="credit-value">{filtered_df['cost_last_interval_memory'].sum():.4f}</div>
                </div>
                <div class="credit-item">
                    <div class="credit-label">Egress Credits</div>
                    <div class="credit-value">{filtered_df['cost_last_interval_egress'].sum():.4f}</div>
                </div>
                <div class="credit-item">
                    <div class="credit-label">EFS Storage Credits</div>
                    <div class="credit-value">{filtered_df['cost_last_interval_efs_storage'].sum():.4f}</div>
                </div>
            </div>
        </div>
    </div>
    """

    display(HTML(html_content))

# Interactive widgets
user_options = sorted(df["user"].unique())
user_dropdown = widgets.Dropdown(options=user_options, description="User:")

team_options = ["Total credit usage"] + sorted([t if t != "no-team" else "Personal Server" for t in df["teamname"].unique()])
team_display_to_value = {"Total credit usage": "Total credit usage", "Personal Server": "no-team"}
for team in df["teamname"].unique():
    if team != "no-team":
        team_display_to_value[team] = team

account_dropdown = widgets.Dropdown(options=team_options, description="Account:", value="Total credit usage")

start_picker = widgets.DatePicker(
    description="Start date", value=(datetime.datetime.now() - datetime.timedelta(days=30)).date()
)
end_picker = widgets.DatePicker(
    description="End date", value=df["date"].max().to_pydatetime().date()
)

cost_metrics = [
    ("Credits", "total_cost"),
    ("CPU Credits", "cost_last_interval_cpu"),
    ("Memory Credits", "cost_last_interval_memory"),
    ("Egress Credits", "cost_last_interval_egress"),
    ("EFS Storage Credits", "cost_last_interval_efs_storage")
]
cost_dropdown = widgets.Dropdown(options=cost_metrics, description="Credit Metric:")

metric_display_names = {
    "total_cost": "Credits",
    "cost_last_interval_cpu": "CPU Credits",
    "cost_last_interval_memory": "Memory Credits",
    "cost_last_interval_egress": "Egress Credits",
    "cost_last_interval_efs_storage": "EFS Storage Credits"
}

# Display interactive plot
interact(
    plot_dashboard,
    selected_user=user_dropdown,
    selected_team=account_dropdown,
    start_date=start_picker,
    end_date=end_picker,
    cost_metric=cost_dropdown
)

# Export button 
export_button = widgets.Button(description="Export CSV")

def export_to_csv(b):
    selected_user_val = user_dropdown.value
    selected_team_val = account_dropdown.value
    start_date_val = start_picker.value
    end_date_val = end_picker.value

    export_df = df.copy()
    if selected_user_val != "All":
        export_df = export_df[export_df["user"] == selected_user_val]
    # Filter by team
    if selected_team_val != "Total credit usage":
        actual_team = "no-team" if selected_team_val == "Personal Server" else selected_team_val
        export_df = export_df[export_df["teamname"] == actual_team]
    if start_date_val:
        export_df = export_df[export_df["date"] >= pd.to_datetime(start_date_val)]
    if end_date_val:
        export_df = export_df[export_df["date"] <= pd.to_datetime(end_date_val)]
    if export_df.empty:
        print("No data to export with the current filters.")
        return

    filename = f"~/exported_credits_{selected_user_val}_{selected_team_val}_{start_date_val}_{end_date_val}.csv".replace(" ", "_")
    export_df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")

export_button.on_click(export_to_csv)
display(export_button)
