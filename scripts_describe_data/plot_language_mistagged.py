# Describe the distribution of the proportion of non-English words
# in the text files, how that was indicative of misstagged documents,
# and show where the by-hand checking cut-off was applied

import pandas as pd
import matplotlib.pyplot as plt


# parameters
# ---

# where the by-hand CSV file is stored
fin = "../results_describe_data/problematic_language_length.csv"

# where I will store the plots
fout = "../results_describe_data/language_mistagged.pdf"


# get the data I need
# ---

df = pd.read_csv(
    fin,
    usecols=[
        "nbr_words",
        "presumptive_language",
        "propn_known_non_presumptive",
        "reason_high_propn_known_non_presumptive", # by-hand checked if non-empty
        "contains_no_presumptive_language",
    ],
)

# only include those rows with non-zero number of words
df = df[df["nbr_words"] != 0]

# sort from highest proportion to lowest
df = df.sort_values("propn_known_non_presumptive", ascending=False).reset_index(
    drop=True
)

# add a column with the cumulative count of "contains_no_presumptive_language" = TRUE
df["cumulative_mistagged"] = (df["contains_no_presumptive_language"] == True).cumsum()

# find the last non-empty entry in "reason_high_propn_known_non_presumptive"
# this is the cut-off propn of my by-hand checks of the documents
last_checked_idx = df["reason_high_propn_known_non_presumptive"].notna()[::-1].idxmax()
cutoff_propn = df.loc[last_checked_idx, "propn_known_non_presumptive"]

# do an assertion check that every entry above it is nonempty
assert (
    df.loc[:last_checked_idx, "reason_high_propn_known_non_presumptive"].notna().all()
), "Found empty entries above the cutoff point"

# plots
# ---

# single plot with inset
fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

# the top plot has each document in order of declining propn on the x-axis,
# and on the y-axis has propn; the line declines in a staircase fashion
x = range(len(df))
ax1.plot(x, df["propn_known_non_presumptive"], drawstyle="steps-post", color="darkblue", linewidth=1.5)
ax1.set_ylabel("Proportion of Non-tagged-language Words")
ax1.set_xlabel("Paper Index")
ax1.grid(True, alpha=0.3)

# find the cutoff position in the sorted dataframe
cutoff_idx = df[df["propn_known_non_presumptive"] == cutoff_propn].index[0]

# add vertical line at cutoff
ax1.axvline(
    x=cutoff_idx,
    color="red",
    alpha=0.7,
    label=f"Manual check cutoff ({cutoff_propn:.2f})",
)
ax1.legend()

# create inset for cumulative count
# position: [left, bottom, width, height] in ax1's coordinate system
ax2 = ax1.inset_axes([0.45, 0.35, 0.35, 0.35])  # adjust position as needed

# plot only up to cutoff point for the inset
x_inset = x[: cutoff_idx + 1]
y_inset = df["cumulative_mistagged"].iloc[: cutoff_idx + 1]

# add the same red line marking the cut-off
ax2.axvline(x=cutoff_idx, color="red", alpha=0.7)
#ax2.set_ylim((0, 20))

ax2.plot(x_inset, y_inset, drawstyle="steps-post", linewidth=1.5, color="darkblue")
ax2.set_xlabel("Document index", fontsize=9)
ax2.set_ylabel("Cumulative\nmistagged", fontsize=9)
ax2.set_title("Manual check", fontsize=9)
ax2.tick_params(labelsize=8)
ax2.grid(True, alpha=0.3)

# add text showing total mistagged at cutoff
"""
mistagged_at_cutoff = df.loc[cutoff_idx, "cumulative_mistagged"]
ax2.text(
    0.95,
    0.05,
    f"{mistagged_at_cutoff} total\nmistagged",
    transform=ax2.transAxes,
    fontsize=9,
    verticalalignment="bottom",
    horizontalalignment="right",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
)
"""


# save plot to fout
plt.tight_layout()
plt.savefig(fout)
plt.close()
