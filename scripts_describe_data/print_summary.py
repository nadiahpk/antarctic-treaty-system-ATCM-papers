# Print summary information about the data

import pandas as pd

# parameters
# ---

# file annotating issues found
fin = "../results_describe_data/annotate_issues.csv"


# read in summary CSV
# ---

df = pd.read_csv(
    fin,
    usecols = [
        "path",
        "paper_type",
        "ATCM_nbr",
        "year",
        "paper_nbr",
        "text_extracted",
        "paper_nbr_used",
        "corrected_language",
        "missing_content",
        "text_extraction_failed",
        "file_corrupted",
        "http_302",
        "summary",
    ]
)

# some summary stats
# ---

print("\n= Extracted Texts =\n")

nbr_text_extracted = len(df[df["text_extracted"]])
print(f"nbr texts extracted = {nbr_text_extracted}")

# the document number was not used or document withdrawn
nbr_not_used = len(df[
    (df["text_extracted"] == True) &
    (df["paper_nbr_used"] == False) 
])
print(f"nbr doc withdrawn / not used = {nbr_not_used}")

# content missing includes: extraction failed, corrupted, just had content missing
nbr_content_missing = len(df[df["missing_content"] == True])
print(f"nbr content missing = {nbr_content_missing}")

nbr_corrupted = len(df[df["file_corrupted"] == True])
print(f" - nbr corrupted = {nbr_corrupted}")

nbr_failed_extraction = len(df[df["text_extraction_failed"] == True])
print(f" - nbr failed extraction = {nbr_failed_extraction}")

nbr_content_elsewhere = len(df[
    (df["missing_content"] == True) &
    (df["file_corrupted"] != True) &
    (df["text_extraction_failed"] != True) 
])
print(f" - nbr content elsewhere = {nbr_content_elsewhere}")

print(f"nbr unusable papers: {nbr_not_used + nbr_content_missing}")

# usable papers
nbr_usable = len(df[
    (df["summary"] == "content in English") |
    (df["summary"] == "content non-English") 
])
print(f"nbr usable = {nbr_usable}")

# usable wps and ips
nbr_usable_wp = len(df[
    ((df["summary"] == "content in English") |
    (df["summary"] == "content non-English")) &
    (df["paper_type"] == "wp")
])
print(f" - nbr usable wp = {nbr_usable_wp}")
nbr_usable_ip = len(df[
    ((df["summary"] == "content in English") |
    (df["summary"] == "content non-English")) &
    (df["paper_type"] == "ip")
])
print(f" - nbr usable ip = {nbr_usable_ip}")

print("\n= Missing =\n")

nbr_def_missing = len(df[(df["summary"] == "definitely missing")])
nbr_pot_missing = len(df[(df["summary"] == "potentially missing")])

print(f"nbr definitely missing = {nbr_def_missing}")
print(f"nbr potentially missing = {nbr_pot_missing}")