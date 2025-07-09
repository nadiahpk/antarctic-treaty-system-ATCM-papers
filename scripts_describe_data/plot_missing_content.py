# Describe the distribution of the number of words in the text files, 
# how that was indicative of missing content, and show where the 
# by-hand checking cut-off was applied

import pandas as pd
import matplotlib.pyplot as plt


# parameters
# ---

# where the by-hand CSV file is stored
fin = "../results_describe_data/problematic_language_length.csv"

# where I will store the plots
fout = "../results_describe_data/missing_content.pdf"


# get the data I need
# ---

df = pd.read_csv(
    fin,
    usecols=[
        "issue", # incls. "missing content"
        "nbr_words",
        "reason_short_length",
    ],
)

# sort from lowest number of words to highest
df = df.sort_values("nbr_words", ascending=True).reset_index(
    drop=True
)

# add a column with the cumulative count of issue = "missing content"
df["cumulative_missing"] = (df["issue"] == "missing content").cumsum()

# find the last non-empty entry in "reason_short_length"
# this is the cut-off propn of my by-hand checks of the documents
last_checked_idx = df["reason_short_length"].notna()[::-1].idxmax()
cutoff_nbr = df.loc[last_checked_idx, "nbr_words"]

# do an assertion check that every entry above it is nonempty
assert (
    df.loc[:last_checked_idx, "reason_short_length"].notna().all()
), "Found empty entries above the cutoff point"


# plots
# ---

# single plot with inset
fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

# the top plot has each document in order of increasing nbr words x-axis,
# and on the y-axis has nbr words; the line increases in a staircase fashion
x = range(len(df))
ax1.plot(x, df["nbr_words"], drawstyle="steps-post", color="darkblue", linewidth=1.5)
ax1.set_ylabel("Number of words")
ax1.set_xlabel("Paper index")
ax1.grid(True, alpha=0.3)

# find the cutoff position in the sorted dataframe
cutoff_idx = df[df["nbr_words"] == cutoff_nbr].index[0]

# add vertical line at cutoff
ax1.axvline(
    x=cutoff_idx,
    color="red",
    alpha=0.7,
    label=f"Manual check cutoff ({cutoff_nbr:d} words)",
)
ax1.legend()

# create inset for cumulative count
# position: [left, bottom, width, height] in ax1's coordinate system
ax2 = ax1.inset_axes([0.45, 0.35, 0.35, 0.35])  # adjust position as needed

# plot only up to cutoff point for the inset
x_inset = x[: cutoff_idx + 1]
y_inset = df["cumulative_missing"].iloc[: cutoff_idx + 1]

# add the same red line marking the cut-off
ax2.axvline(x=cutoff_idx, color="red", alpha=0.7)

ax2.plot(x_inset, y_inset, drawstyle="steps-post", linewidth=1.5, color="darkblue")
ax2.set_xlabel("Paper index", fontsize=9)
ax2.set_ylabel("Cumulative\nmissing content", fontsize=9)
ax2.set_title("Manual check", fontsize=9)
ax2.tick_params(labelsize=8)
ax2.grid(True, alpha=0.3)

# save plot to fout
plt.tight_layout()
plt.savefig(fout)
plt.close()
