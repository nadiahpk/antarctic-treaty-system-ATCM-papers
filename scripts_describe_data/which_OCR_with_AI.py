# Identify which text files were extracted with AI and which
# with other means

import os
from pathlib import Path
import sqlite3
import pandas as pd

# parameters
# ---

# location of the data (extracted text files)
data_base = Path(os.environ.get("DATA", "."))


# location of the SQLite database with URLs of docs in it
# this is available from the full-data download
sq_path = Path("../large_data/document-pipeline.sqlite3")


# get urls from database
# ---

# `id`` below are shared between `ocr` and `documents`
#   sqlite> .schema documents
#   CREATE TABLE documents (
#           id TEXT PRIMARY KEY,
#           url TEXT,
#           document BLOB,
#           timestamp DATETIME,
#           is_scanned BOOLEAN DEFAULT FALSE,
#           status TEXT DEFAULT 'new'
#       );
#
#   sqlite> .schema ocr
#   CREATE TABLE ocr (
#           id TEXT,
#           page_nr INTEGER,
#           page_text TEXT,
#           method TEXT,
#           timestamp DATETIME,
#           PRIMARY KEY (id, page_nr, method, timestamp),
#           FOREIGN KEY (id, page_nr) REFERENCES pages(id, page_nr) ON DELETE CASCADE
#       );

conn = sqlite3.connect(str(sq_path))  # Convert Path to string
cursor = conn.cursor()

# get all documents with OCR status and extract file format
query = """
    SELECT 
        documents.url,
        CASE WHEN ocr.id IS NOT NULL THEN 1 ELSE 0 END as has_ocr
    FROM documents
    LEFT JOIN (SELECT DISTINCT id FROM ocr) ocr ON documents.id = ocr.id
"""
cursor.execute(query)
results = cursor.fetchall()

# Extract URLs, OCR status, and file formats
all_urls = [row[0] for row in results]
ocr_status = [bool(row[1]) for row in results]  # Convert 1/0 to True/False

# Extract file format from URL extension
file_formats = []
for url in all_urls:
    # Get the last part after the last dot, but before any query parameters
    extension = url.split('?')[0].split('.')[-1].lower()
    file_formats.append(extension)

# For backward compatibility, keep the original urls list (OCR'd documents only)
# urls = [url for url, has_ocr in zip(all_urls, ocr_status) if has_ocr]

# Close the connection
conn.close()

# split into those from ATSD and those from ATADD
# ---

url_ocr_formats = list(zip(all_urls, ocr_status, file_formats))

atsd_uofs = [
    uof for uof in url_ocr_formats if "documents.ats.aq" in uof[0]
] # -- 2036

atadd_uofs = [
    uof for uof in url_ocr_formats if "documents.ats.aq" not in uof[0]
] # -- 41


# I know that every ATADD url gave a pdf that went through the OCR system
assert(len(atadd_uofs) == 41)
# so I can focus on the atsd_urls only from here on out


# sort out details of atsd documents
# ---

# turn URLs into relative path
atsd_paths = [
    "atsd_secretariat_database/" + atsd_uof[0].split("https://documents.ats.aq/")[1].split(".")[0] + ".txt"
    for atsd_uof in atsd_uofs
]

atsd_urls, atsd_ocreds, atsd_extns = zip(*atsd_uofs)


# sort out details of atadd documents
# ---

# their paths
atadd_data_base = data_base / "atadd_utas_database"
atadd_full_paths = [f for f in atadd_data_base.rglob("*.txt")]
atadd_paths = [str(path.relative_to(data_base)) for path in atadd_full_paths]

# all were pdfs that were ocr'ed
nbr_txt_files = len(atadd_paths)
atadd_ocreds = [True]*nbr_txt_files
atadd_extns = ["pdf"]*nbr_txt_files

# merge
# ---

paths = atsd_paths + atadd_paths
ocreds = list(atsd_ocreds) + atadd_ocreds
extns = list(atsd_extns) + atadd_extns


# write to a csv file 
# ---

df = pd.DataFrame(
    {
        "path": paths,
        "doc_format": extns,
        "OCR_with_AI": ocreds,
    }
)

df.to_csv("../results_describe_data/which_OCR_with_AI.csv", index=False)