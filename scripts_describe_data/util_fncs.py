# construct paths to where each extracted text document is stored

import os
import re

# import pandas as pd
from pathlib import Path


def get_ATCM_nbr_from_path(path):
    """
    Given a path to a text file, 
    e.g., "atsd_secretariat_database/ATCM3/wp/ATCM3_wp058_f.txt",
    extract the ATCM number.
    """

    # convert from posix path if needed
    path = str(path)
    match = re.search(r'ATCM(\d+)', path)
    ATCM_nbr = int(match.group(1)) if match else None

    return ATCM_nbr


def get_ATCM_nbr_2_year():
    """
    Returns a useful dictionary that that has ATCM numbers
    as the key and years as the values
    """
    ATCM_nbr_2_year = {
        1: 1961,
        2: 1962,
        3: 1964,
        4: 1966,
        5: 1968,
        6: 1970,
        7: 1972,
        8: 1975,
        9: 1977,
        10: 1979,
        11: 1981,
        12: 1983,
        13: 1985,
        14: 1987,
        15: 1989,
        16: 1991,
        17: 1992,
        18: 1994,
        19: 1995,
        20: 1996,
        21: 1997,
        22: 1998,
        23: 1999,
        24: 2001,
        25: 2002,
        26: 2003,
        27: 2004,
        28: 2005,
        29: 2006,
        30: 2007,
        31: 2008,
        32: 2009,
        33: 2010,
        34: 2011,
        35: 2012,
        36: 2013,
        37: 2014,
        38: 2015,
        39: 2016,
        40: 2017,
        41: 2018,
        42: 2019,
        43: 2021,
        44: 2022,
        45: 2023,
        46: 2024,
    }

    return ATCM_nbr_2_year


def get_doc_path(
    database_name,
    meeting_number,
    paper_type,
    paper_number,
    paper_revision,
    language,
):
    """
    Get the path location of the extracted text for a specific document.

    >> text_path = get_doc_path("atsd", 11, "wp", 33, 2, "English")
    >> text = text_path.read_text(encoding='utf-8')
    >> text[:40]
    'ANT/XI/33/Rev.2\n\nThe coincidence between'
    """

    # check inputs
    # ---

    # only two databases used
    if database_name not in ["atsd", "atadd"]:
        raise ValueError(
            f"Invalid database name: {database_name}. Expected 'atsd' or 'atadd'."
        )

    # only Working Papers and Information papers
    if paper_type not in ["wp", "ip"]:
        raise ValueError(f"Invalid paper_type: {paper_type}. Expected 'ip' or 'wp'.")

    # paper revision and other numbers convert to integers
    if not isinstance(paper_number, int):
        try:
            paper_number = int(paper_number)
        except ValueError as e:
            raise ValueError(f"Invalid paper_number: {paper_number}") from e
    if not isinstance(paper_revision, int):
        try:
            paper_revision = int(paper_revision)
        except ValueError as e:
            raise ValueError(f"Invalid paper_revision: {paper_revision}") from e

    # only accept the four language types or "unknown"
    if language not in ["English", "Spanish", "French", "Russian", "unknown"]:
        raise ValueError(
            f"Invalid language: {language}.  Expected 'English', 'Spanish', 'French', or 'unknown'."
        )

    # fixed values
    # ---

    data_base = Path(os.environ.get("DATA"), ".")

    # might need to update in the future
    meeting_type = "ATCM"

    # construct the path to the document's extracted text
    # ---

    if database_name == "atsd":
        doc_dir = data_base / "atsd_secretariat_database"
    else:  # database_name == "atadd":
        doc_dir = data_base / "atadd_utas_database"

    doc_dir = doc_dir / f"{meeting_type}{meeting_number}/{paper_type}"

    # construct the file name for each to mirror the atsd convention
    # i.e., in a format like ATCM27_wp019_rev1_e.txt

    # part1: ATCM27
    part1 = f"{meeting_type}{meeting_number}"

    # part2: _wp019 (the paper numbers are three-digits padded with leading zeros)
    part2 = f"_{paper_type}{str(paper_number).zfill(3)}"

    # part 3: _rev1
    # the revision number is appended iff the revision number is greater than 0
    part3 = f"_rev{int(paper_revision)}" if paper_revision != 0 else ""

    # part 4: _e.txt, or an _x.txt if unknown, not specified
    languageD = {
        "English": "_e.txt",
        "Spanish": "_s.txt",
        "French": "_f.txt",
        "Russian": "_r.txt",
        "unknown": "_x.txt",
    }
    part4 = languageD[language]

    fname = f"{part1}{part2}{part3}{part4}"
    doc_path = doc_dir / fname

    return doc_path
