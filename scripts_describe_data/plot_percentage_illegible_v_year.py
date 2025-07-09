# Plot the percentage of characters that the AI indicated were
# illegible (marked "[?]" or "?") in each year

import pandas as pd
import matplotlib.pyplot as plt
import util_fncs as u

# parameters
# ---

# where the informaton about illegible characters is
fin = "../results_describe_data/count_illegible_ocr_hand_checked.csv"

# where to store the plot
fout = "../results_describe_data/percentage_illegible_v_year.pdf"


# read in data about illegible characters
# ---

df = pd.read_csv(
    fin,
    usecols=[
        "path", # location of text file
        "determination_by_human", # my by-hand determinations
        "nbr_characters", 
        "nbr_bracketed_illegible", # "[?]" definitely illegible
        "nbr_likely_illegible_qmarks", # "?" in middle of words, etc. heuristic
    ],
)

# check data is how I expect it
set(df["determination_by_human"]) == {"none illegible", "some illegible"}


# determine the year each document was published from its text-file name
# ---

df['ATCM_nbr'] = df['path'].apply(u.get_ATCM_nbr_from_path)
ATCM_nbr_2_year = u.get_ATCM_nbr_2_year()
df['year'] = df['ATCM_nbr'].map(ATCM_nbr_2_year)


# add a column counting total illegible characters
# ---

df['total_illegible'] = df.apply(
    lambda row: (row['nbr_bracketed_illegible'] + row['nbr_likely_illegible_qmarks']) 
    if row['determination_by_human'] == 'some illegible' else 0, 
    axis=1
)


# aggregate by year: sum total characters and total illegible characters
# ---

yearly_stats = df.groupby('year').agg({
    'nbr_characters': 'sum',
    'total_illegible': 'sum'
}).reset_index()

yearly_stats['perc_illegible'] = 100 * yearly_stats['total_illegible'] / yearly_stats['nbr_characters']


# plot year on x-axis, proportion of characters illegible on y axis
# ---

plt.figure(figsize=(5, 4))
plt.bar(yearly_stats['year'], yearly_stats['perc_illegible'], color="blue", alpha=0.5)

# Add small tick marks at y=0 for each year with documents
for year in yearly_stats['year']:
    plt.plot([year, year], [0, 5e-4], 'b-', alpha=0.6, linewidth=1)


plt.xlabel('Year of Publication', fontsize="large")
plt.ylabel("Percentage of Characters Illegible", fontsize="large")
# plt.xticks(yearly_stats['year'])
# plt.title('Proportion of illegible characters by year')
# plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(fout, dpi=300, bbox_inches='tight')
plt.close()