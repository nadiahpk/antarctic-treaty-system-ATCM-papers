# Summarise what we know about document number gaps and other issues
# with the dataset. Note, I am not counting revisions.

from pathlib import Path
import pandas as pd
import util_fncs as u
import re


# parameters
# ===

fout = Path("../results_describe_data/annotate_issues.csv")

# 7 URLs that 302'd
url_302s = [
    "https://documents.ats.aq/ATCM12/ip/ATCM12_ip010_e.pdf",
    "https://documents.ats.aq/ATCM27/ip/ATCM27_ip025_e.doc",
    "https://documents.ats.aq/ATCM27/ip/ATCM27_ip092_e.doc",
    "https://documents.ats.aq/ATCM25/ip/ATCM25_ip009_e.pdf",
    "https://documents.ats.aq/ATCM13/wp/ATCM13_wp013_s.pdf",
    # "https://documents.ats.aq/ATCM18/wp/ATCM18_wp005_e.pdf", exclude bc rev_1 found
    "https://documents.ats.aq/ATCM25/wp/ATCM25_wp048_e.pdf",
]


# which paper numbers we managed to acquire and extract text from
# ===

# list of documents we have + inferred gaps in the doc-nbr sequence
fin = Path("../results_describe_data/doc_nbr_gaps.csv")

df = pd.read_csv(
    fin,
    usecols=[
        "year",
        "ATCM_nbr",
        "paper_type",
        "paper_nbr",
        "path",
    ],
)

df["text_extracted"] = None
df.loc[df["path"].notna(), "text_extracted"] = True
df.loc[df["path"].isna(), "text_extracted"] = False


# which paper numbers used and not used
# ===

# start by assuming every paper with text extracted had paper number used
# (provides baseline to refine later)
df["paper_nbr_used"] = None
df.loc[df["path"].notna(), "paper_nbr_used"] = True


# 1. up to 2001, I had collated WP numbers used and not used
# ---

# data about ATADD WPs found by hand
fin_atadd = Path("../data_accountability/atadd_utas_database/wps_missing.csv")

df_atadd = pd.read_csv(
    fin_atadd,
    usecols=[
        "meeting_year",
        "paper_number",
        "is_true_gap",  # TRUE means this document number was not used / withdrawn
    ],
)

# matching based on paper_type, meeting_year, and paper_number
# df_atadd["is_true_gap"] == True -> paper_nbr_used == False
# df_atadd["is_true_gap"] == False -> paper_nbr_used == True
paper_type = "wp"
for year, paper_nbr, is_true_gap in zip(
    df_atadd["meeting_year"], df_atadd["paper_number"], df_atadd["is_true_gap"]
):
    # find the location of that WP in df
    mask = (
        (df["year"] == year)
        & (df["paper_type"] == paper_type)
        & (df["paper_nbr"] == paper_nbr)
    )
    matching_rows = df[mask]

    # add information
    df.loc[mask, "paper_nbr_used"] = not is_true_gap


# 2. by looking at short-length texts, I identified some other paper numbers not used
# ---

fin_prob = Path("../results_describe_data/problematic_language_length.csv")
df_prob = pd.read_csv(
    fin_prob,
    usecols=[
        "path",
        "issue",
    ],
)


# for df_prob with issue == "document withdrawn" or issue == "number not used"
# find the matching "path" in df, and mark that row with "paper_nbr_used" = False
df_sub = df_prob[
    (df_prob["issue"] == "document withdrawn") | (df_prob["issue"] == "number not used")
]
df.loc[df["path"].isin(df_sub["path"]), "paper_nbr_used"] = False


# merge in language information
# ===

fin_prob = Path("../results_describe_data/problematic_language_length.csv")
df_prob = pd.read_csv(
    fin_prob,
    usecols=[
        "path",
        "presumptive_language",
        "contains_no_presumptive_language",
        "propn_known_english",
        "propn_known_spanish",
        "propn_known_french",
        "propn_known_russian",
    ],
)


df_prob = df_prob.rename(columns={"presumptive_language": "language_as_tagged"})

# Some of these documents are tagged with the wrong language, and
# there's ambiguity about the language bc some documents contain a mix.
# Therefore, accept the language_as_tagged for all documents EXCEPT
# those that I know to contain none of that language. These exceptions
# are marked with "contains_no_presumptive_language" == True

# determine the majority language from only words that were known
language_cols = ["propn_known_english", "propn_known_spanish", "propn_known_french", "propn_known_russian"]
df_prob["majority_language"] = df_prob[language_cols].idxmax(axis=1).str.replace("propn_known_", "").str.title()

# for those with "contains_no_presumptive_language" == True, mark
# the corrected_language as the majority language; otherwise, use the 
# language_as_tagged
df_prob["corrected_language"] = df_prob["language_as_tagged"].where(
    df_prob["contains_no_presumptive_language"] != True,
    df_prob["majority_language"]
)


# merge the corrected language and mistagged flag into main df
df = df.merge(
    df_prob[["path", "corrected_language"]],
    on="path", 
    how="left"
)



# missing content
# ===

fin_prob = Path("../results_describe_data/problematic_language_length.csv")
df_prob = pd.read_csv(
    fin_prob,
    usecols=[
        "path",
        "check_original_doc_with_missing_content_by_hand",
    ],
)

# check content of column is what I expect
df_prob = df_prob.rename(columns={"check_original_doc_with_missing_content_by_hand": "check"})
df_prob["check"] = df_prob["check"].astype(str)

assert(set(df_prob["check"]) == {"nan", "content elsewhere", "extraction failed", "missing content", "original corrupted"})

# in this category, combine: 
# - content elsewhere
# - extraction failed, 
# - missing content, 
# - original corrupted
df["missing_content"] = None
df.loc[df["path"].notna(), "missing_content"] = False
df_sub = df_prob[
    (df_prob["check"] == "content elsewhere") | 
    (df_prob["check"] == "extraction failed") | 
    (df_prob["check"] == "missing content") | 
    (df_prob["check"] == "original corrupted")
]
df.loc[df["path"].isin(df_sub["path"]), "missing_content"] = True

# I went through missing-content docs by hand to find the cause, which I stored in this CSV file
fin_miss = Path("../results_describe_data/check_missing_content.csv")
df_miss = pd.read_csv(
    fin_miss,
    usecols=[
        "path",
        "classify",
    ],
)
assert set(df_miss["classify"]) == {
    "AI failed",
    "LibreOffice failed",
    "pymupdf failed",
    "original content short",
    "original file corrupted",
}

# group together those with a failure of the text extraction
df["text_extraction_failed"] = None
df_sub = df_miss[
    (df_miss["classify"] == "AI failed")
    | (df_miss["classify"] == "LibreOffice failed")
    | (df_miss["classify"] == "pymupdf failed")
]
df.loc[df["path"].isin(df_sub["path"]), "text_extraction_failed"] = True

# also mark those with original file corrupted
df["file_corrupted"] = None
df_sub = df_miss[df_miss["classify"] == "original file corrupted"]
df.loc[df["path"].isin(df_sub["path"]), "file_corrupted"] = True


# server errors
# ===

# get the year, ATCM nbr, paper type, paper number of 7 documents that 302'd
df_302 = pd.DataFrame({"url": url_302s})
df_302["path"] = df_302["url"].apply(lambda x: x.split("https://documents.ats.aq/")[1])

# paper type
df_302["paper_type"] = df_302["path"].apply(
    lambda x: "wp" if "/wp/" in x else ("ip" if "/ip/" in x else "")
)
assert df_302["paper_type"].isin(["wp", "ip"]).all(), (
    "Found entries that are neither wp nor ip"
)

# year of publication
df_302["ATCM_nbr"] = df_302["path"].apply(u.get_ATCM_nbr_from_path)
ATCM_nbr_2_year = u.get_ATCM_nbr_2_year()
df_302["year"] = df_302["ATCM_nbr"].map(ATCM_nbr_2_year)

# extract the document number
df_302["paper_nbr"] = df_302.apply(
    lambda row: int(match.group(1))
    if (
        match := re.search(
            rf"ATCM{row['ATCM_nbr']}_{row['paper_type']}(\d+)", row["path"]
        )
    )
    else None,
    axis=1,
)

# mark in df
df["http_302"] = None

for year, paper_nbr, paper_type in zip(
    df_302["year"], df_302["paper_nbr"], df_302["paper_type"]
):
    mask = (
        (df["year"] == year)
        & (df["paper_type"] == paper_type)
        & (df["paper_nbr"] == paper_nbr)
    )
    matching_rows = df[mask]

    # add information
    df.loc[mask, "http_302"] = True
    df.loc[mask, "paper_nbr_used"] = True


# write summary data column
# ===

df["summary"] = None

# paper_nbr_used == False means number not used or doc withdrawn
# don't include in summary

# potentially missing: paper_nbr_used == None AND text_extracted == False
# ---
mask = (df["text_extracted"] == False) & (df["paper_nbr_used"].isna())
df.loc[mask, "summary"] = "potentially missing"

# definitely missing
# ---
# paper_nbr_used == True AND
#   text_extracted == False OR
#   text_extracted == True AND missing_content == True
mask = (df["paper_nbr_used"] == True) & (
    (df["text_extracted"] == False)
    | ((df["text_extracted"] == True) & (df["missing_content"] == True))
)
df.loc[mask, "summary"] = "definitely missing"

# have content in English
# ---
# paper_nbr_used == True AND text_extracted == True AND missing_content == False
# AND corrected_language == English 
mask = (
    (df["paper_nbr_used"] == True)
    & (df["text_extracted"] == True)
    & (df["missing_content"] == False)
    & (df["corrected_language"] == "English")
)
df.loc[mask, "summary"] = "content in English"

# have content in non-English
# ---
# paper_nbr_used == True AND text_extracted == True AND missing_content == False
# AND corrected_language != English
mask = (
    (df["paper_nbr_used"] == True)
    & (df["text_extracted"] == True)
    & (df["missing_content"] == False)
    & (df["corrected_language"] != "English")
)
df.loc[mask, "summary"] = "content non-English"


# save to CSV
# ===

df.to_csv(fout, index=False)
