# Plot the coverage of document texts for WPs and IPs over time

import pandas as pd
import matplotlib.pyplot as plt


# parameters
# ---

# CSV documenting known coverage and issues
fin = "../results_describe_data/annotate_issues.csv"

# where I will store the plot
fout = "../results_describe_data/coverage_v_year_combined.pdf"


# get the data I need
# ---

df = pd.read_csv(
    fin,
    usecols=[
        "year",
        "paper_type",
        "summary",
    ],
)

# check it's how I expect it
assert(set(df["paper_type"]) == {"wp", "ip"})
df["summary"] = df["summary"].astype(str)
assert(set(df["summary"]) == {"nan", "content in English", "content non-English", "definitely missing", "potentially missing"})


# plot a stacked bar chart for WPs and IPs
# ---

# Create a figure with two subplots (stacked vertically)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

# paper_type, ylabel, ax, panel_label
data_configs = [
    ("wp", "Number of Working Papers", ax1, "(a)"),
    ("ip", "Number of Information Papers", ax2, "(b)"),
]

for paper_type, ylabel, ax, panel_label in data_configs:

    # Filter for working papers only
    wp_df = df[df['paper_type'] == paper_type]

    # Create pivot table for stacked bar chart
    pivot_wp = wp_df.pivot_table(
        index='year', 
        columns='summary', 
        aggfunc='size', 
        fill_value=0
    )

    # Define colors for each summary
    # Using Paul Tol's colourblind safe
    colors = {
        'content in English': '#117733', 
        'content non-English': '#88ccee',
        'definitely missing': '#882255',
        'potentially missing': '#cc6677'
    }

    # Get the range of years to include gaps
    # min_year = pivot_wp.index.min()
    min_year = 1960
    max_year = pivot_wp.index.max()
    all_years = range(min_year, max_year + 1)

    # Reindex to include all years (gaps will have 0 values)
    pivot_wp = pivot_wp.reindex(all_years, fill_value=0)

    # Get extraction methods in consistent order
    methods = ['content in English', 'content non-English', 'definitely missing', 'potentially missing']
    methods = [m for m in methods if m in pivot_wp.columns]

    # Dictionary for naming the method in the legend
    method2label = {
        "content in English": "Content in English",
        "content non-English": "Content non-English",
        "definitely missing": "Definitely missing",
        "potentially missing": "Potentially missing",
    }

    # Create the stacked bars manually to preserve year spacing
    bar_width = 0.8
    x_positions = pivot_wp.index

    # Initialize bottom positions for stacking
    bottoms = [0] * len(pivot_wp)

    # Plot each extraction method as a layer
    for method in methods:
        if method in pivot_wp.columns:
            values = pivot_wp[method].values
            ax.bar(x_positions, values, bar_width, 
                bottom=bottoms, label=method2label[method], 
                color=colors.get(method, '#333333'))
            # Update bottoms for next layer
            bottoms = [b + v for b, v in zip(bottoms, values)]

    # Only add xlabel to the bottom subplot
    if ax == ax2:
        ax.set_xlabel('Year of Publication', fontsize="large")
    ax.set_ylabel(ylabel, fontsize="large")
    
    # Add panel label in top left corner
    ax.text(0.02, 0.95, panel_label, transform=ax.transAxes, 
            fontsize=14, va='top')
    
    # Only show legend on the top subplot
    if ax == ax1:
        ax.legend(title='Availability', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Set x-axis to show all years with labels every 10 years
    ax.set_xticks(x_positions)
    # Only show labels for years divisible by 10, plus first and last years
    labels = []
    for i, year in enumerate(x_positions):
        if year % 10 == 0: # or i == 0: # or i == len(x_positions) - 1:
            labels.append(str(year))
        else:
            labels.append('')
    ax.set_xticklabels(labels)

    # Make decadal ticks longer
    for i, year in enumerate(x_positions):
        if year % 10 == 0:
            ax.xaxis.get_major_ticks()[i].tick1line.set_markersize(6)
            ax.xaxis.get_major_ticks()[i].tick2line.set_markersize(6)

    # Add grid for better readability
    ax.grid(axis='y', alpha=0.3)
    
    # Set y-axis limit with padding to ensure bars aren't cut off
    max_height = max(bottoms)
    ax.set_ylim(0, max_height * 1.05)  # Add 5% padding

# Save the combined figure
plt.tight_layout()
plt.savefig(fout, dpi=300, bbox_inches='tight')
plt.close()