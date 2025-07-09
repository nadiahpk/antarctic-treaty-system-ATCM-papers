# Gaps in the document-number sequence are indicative of missing 
# documents. Identify remaining document-number gaps. 

import re
import os
from pathlib import Path
import pandas as pd

import util_fncs as u


# parameters
# ---

# location of the data (extracted text files)
data_base = Path(os.environ.get("DATA", "."))

# where to store results
fout = Path("../results_describe_data/doc_nbr_gaps.csv")


# create a dataframe listing document-number sequence
# ---

txt_paths = [f for f in data_base.rglob("*.txt")]
txt_rel_path_strs = [str(path.relative_to(data_base)) for path in txt_paths]

df = pd.DataFrame({"path": txt_rel_path_strs})


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


# extract the document number
df['paper_nbr'] = df.apply(
    lambda row: int(match.group(1)) if (match := re.search(
        rf'ATCM{row["ATCM_nbr"]}_{row["paper_type"]}(\d+)',
        row['path']
    )) else None,
    axis=1
)


# for wp and for ip, find the max document index
# ---

years = sorted(set(df["year"]))
year_2_paper_type_2_max_nbr = {
    paper_type: {
        year: max(df[(df["year"] == year) & (df["paper_type"] == paper_type)]["paper_nbr"], default=None)
        for year in years
    }
    for paper_type in ["ip", "wp"]
}


# list document numbers in sequence to max not found in dataframe
# ---

missing_nbrsD = {"ip": dict(), "wp": dict()}
for paper_type in ["ip", "wp"]:
    for year in years:
        max_nbr = year_2_paper_type_2_max_nbr[paper_type][year]
        if max_nbr:
            df_sub = df[(df["year"] == year) & (df["paper_type"] == paper_type)]
            missing_nbrsD[paper_type][year] = [
                nbr for nbr in range(1, max_nbr + 1)
                if nbr not in df_sub["paper_nbr"].values
            ]

# for each missing document number, add a row to the table
# ---

year_2_ATCM_nbr = {
    year: ATCM_nbr
    for ATCM_nbr, year in ATCM_nbr_2_year.items()
}

for paper_type, year_2_missing_nbrs in missing_nbrsD.items():
    for year, missing_nbrs in year_2_missing_nbrs.items():
        ATCM_nbr = year_2_ATCM_nbr[year]
        nbr_rows = len(missing_nbrs)
        new_rows = pd.DataFrame({
            "path": [None] * nbr_rows,
            "paper_type": [paper_type] * nbr_rows,
            "ATCM_nbr": [ATCM_nbr] * nbr_rows,
            "year": [year] * nbr_rows,
            "paper_nbr": missing_nbrs
        })
        new_rows = new_rows.astype({"ATCM_nbr": "Int64", "year": "Int64", "paper_nbr": "Int64"})
        df = pd.concat([df, new_rows], ignore_index=True)

# write to CSV
# ---

df.to_csv(fout, index=False)