# Plot the proportion of unknown words versus year of publication.
# A negative trend is indicative of OCR problems with earlier-year documents.
#
# By hand, the y-axis has been reduced to (0, 0.3), and the one outlier 
# is annotated. THe outlier is an IP in ATCM 45 (year: 2023) with 
# proportion unknown words = 0.50

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import util_fncs as u

# parameters
# ---

# where the by-hand CSV file is stored
fin = "../results_describe_data/problematic_language_length.csv"

# where I will store the plot
fout = "../results_describe_data/propn_unknown_words_v_year_two_panel_annotate.pdf"


# get the data I need
# ---

df = pd.read_csv(
    fin,
    usecols=[
        "path",
        "issue",
        "nbr_words",
        "propn_unknown", 
    ],
)

# remove entries with "issue": "missing content", "document withdrawn", or "content elsewhere"
df = df[df["issue"] != "missing content"]
df = df[df["issue"] != "document withdrawn"]
df = df[df["issue"] != "content elsewhere"]



# use the path to ID: (1) type of paper (wp or ip), and (2) year of publication
# ---

# (1) add column called "paper_type"
# if "path" has wp in it, entry will be "wp", if "path" has ip in it, entry will be "ip",
# otherwise, leave empty
df['paper_type'] = df['path'].apply(lambda x: 'wp' if '/wp/' in x else ('ip' if '/ip/' in x else ''))

# assert that every entry in column "paper_type" is "wp" or "ip" (no empty)
assert df['paper_type'].isin(['wp', 'ip']).all(), "Found entries that are neither wp nor ip"

# (2) year of publication

# create column called "ATCM_nbr" using u.get_ATCM_nbr_from_path(path)
df['ATCM_nbr'] = df['path'].apply(u.get_ATCM_nbr_from_path)

# dictionary for converting ATCM number to year
ATCM_nbr_2_year = u.get_ATCM_nbr_2_year()

# create column called "year" that uses dictionary above to convert from "ATCM_nbr" to year
df['year'] = df['ATCM_nbr'].map(ATCM_nbr_2_year)

# create year groups for box plots (5-year bins)
year_min = df['year'].min()
year_max = df['year'].max()
bins = range(int(year_min), int(year_max) + 6, 5)  # 5-year bins
# labels = [f"{i}-{i+4}" for i in bins[:-1]]
labels = [f"{i}" for i in bins[:-1]]
df['year_group'] = pd.cut(df['year'], bins=bins, labels=labels, include_lowest=True)

# identify the outlier for annotation
outlier_threshold = 0.3
outlier_data = df[df['propn_unknown'] > outlier_threshold]
if len(outlier_data) > 0:
    outlier_row = outlier_data.iloc[0]  # take the first (highest) outlier
    outlier_year = outlier_row['year']
    outlier_propn = outlier_row['propn_unknown']
    outlier_type = outlier_row['paper_type']


# plot
# ---

# two-panel plot: left = box plots by year group, right = scatter with trend lines
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# LEFT PANEL: Box plots by year group
# combine both paper types for overall distribution by year
sns.boxplot(data=df, x='year_group', y='propn_unknown', ax=ax1)
ax1.set_xlabel('Year Group')
ax1.set_ylabel('Proportion of Unknown Words')
ax1.tick_params(axis='x', labelsize=8)
ax1.grid(True, alpha=0.3)

# truncate y-axis and add outlier annotation
ax1.set_ylim(0, outlier_threshold)
if len(outlier_data) > 0:
    ax1.annotate(f'outlier\nat {outlier_propn:.2f}',
                xy=(0.96, 1.), xycoords='axes fraction',
                fontsize=6,
                ha='center', va='top',
                arrowprops=dict(arrowstyle='->', color='black', lw=1),
                xytext=(0.96, 0.93), textcoords='axes fraction')

# RIGHT PANEL: Scatter plot with trend lines
wp_data = df[df['paper_type'] == 'wp']
ip_data = df[df['paper_type'] == 'ip']

# filter out outliers for trend lines and main plotting
wp_data_filtered = wp_data[wp_data['propn_unknown'] <= outlier_threshold]
ip_data_filtered = ip_data[ip_data['propn_unknown'] <= outlier_threshold]

# scatter plots with reduced alpha for busy plot (only show points <= threshold)
ax2.scatter(wp_data_filtered['year'], wp_data_filtered['propn_unknown'], 
           alpha=0.5, s=5, marker='.', color='blue')
ax2.scatter(ip_data_filtered['year'], ip_data_filtered['propn_unknown'], 
           alpha=0.5, s=5, marker='.', color='red')

# add trend lines using seaborn's regplot (LOWESS smoothing) on filtered data
sns.regplot(data=wp_data_filtered, x='year', y='propn_unknown', ax=ax2, 
           scatter=False, lowess=True, color='blue', line_kws={'linewidth': 2},
           label="Working Papers")
sns.regplot(data=ip_data_filtered, x='year', y='propn_unknown', ax=ax2, 
           scatter=False, lowess=True, color='red', line_kws={'linewidth': 2},
           label="Information Papers")

ax2.set_xlabel('Year of Publication')
ax2.set_ylabel("")
#ax2.set_title('Scatter Plot with Trend Lines')
ax2.legend(fontsize="small")
ax2.grid(True, alpha=0.3)

# truncate y-axis and add outlier annotation
ax2.set_ylim(0, outlier_threshold)
if len(outlier_data) > 0:
    # add arrow pointing to where the outlier would be
    ax2.annotate(f'outlier IP\nat {outlier_propn:.2f}', 
                xy=(outlier_year, outlier_threshold), xycoords='data',
                ha='center', va='top',
                fontsize=6,
                arrowprops=dict(arrowstyle='->', color='black', lw=1),
                xytext=(outlier_year, outlier_threshold-0.02), textcoords='data')

# save plot to fout
plt.tight_layout()
plt.savefig(fout, dpi=300, bbox_inches='tight')
plt.close()