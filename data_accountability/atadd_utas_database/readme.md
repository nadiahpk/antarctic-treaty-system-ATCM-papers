# Content of this directory

The purpose of this directory is provide data accountability for the download of WPs
from the Antarctic Documents Database (ATADD) hosted by the University of Tasmania
(accessible online at https://www.utas.edu.au/library-resources/atadd). These are
WPs that were identified as missing from the Secretariat's Antarctic Treaty 
System database ATSD (see `../secretariat_database/`) and supplemented with WPs 
downloaded by hand from the ATADD web portal.

## Documentation of potentially missing WPs

The file `wps_missing.csv` documents the process that was used to identify missing WPs,
and consolidates information about them in a way that mirrors the information available
from the ATSD.

1. We identified WPs potentially missing from the ATSD by gaps in the WP-numbering scheme.
This was also indicative of problematic years.
2. We consulted various 'lists of documents' we collected (below) to identify which
gaps in the numbering represented WPs truly missing from the ATSD, and which gaps 
occurred for other reasons (e.g., that WP-number was skipped).
3. We recorded the titles of every missing WP and other information available from the 'lists of documents'.
4. For each missing WP, we searched for its title using the ATADD web portal and recorded the URL where it was stored.

### Columns of the documentation file

The file `wps_missing.csv` contains the following columns, which were chosen to mirror the information available from ATSD:
1. `meeting_year`: The year of the ATCM
1. `meeting_type`: All entries are `ATCM` (included for future updates)
1. `meeting_number`: Starting with `1` (Arabic numerals) for the first ATCM in 1961
1. `paper_type`: All entries are `wp` meaning "Working Paper" (included for future updates)
1. `paper_number`: The number assigned to the document (Arabic numeral)
1. `paper_revision`: The first (potentially only) drafts are marked `0`
1. `paper_name`: The title of the document
1. `detailed_agendas`: Meeting agenda numbers to which the document refers. Note that the format is variable (e.g., "ATCM 5" or "7a") and that documents referring to multiple agenda numbers are pipe-separated (e.g., "6a | 7b | 10")
1. `agendas`: Meeting agenda numbers is a standardised format (e.g., "ATCM 6 | ATCM 7 | ATCM 10")
1. `parties`: Authors of the document. When the document has multiple authors, they are pipe-separated. Note that WPs with no author were designated as being authored by the host-country of the meeting to match the convention used by the ATSD.
1. `url`: The ATADD URL from which the document can be downloaded.
1. `is_true_gap`: If `TRUE`, the gap found in the WP-numbering sequence is a true gap in the numbering sequence rather than indicative of a missing WP. 
For example, ATCM 1 (1961) WP 10 is marked `TRUE` because the 'list of documents' from that meeting has that WP-number marked as "cancelled".
If `FALSE`, then the gap was because that WP was missing from the ATSD. 
These were the documents that were supplemented by the ATADD.
1. `notes`: Pipe-separated documentation of the process of resolving each WP-number gap. Information includes:
why a WP was designated as a `TRUE` gap; where the information used to fill other columns (`paper_name`, `parties`, `agendas`, etc.) was sourced, and any other information that may help future workers verify the data.

Note that, for documents with known multiple revisions, the URL is repeated.
In the extracted text, all revisions are included in all files 
(this is the form in which the source documents were received from ATADD).

## Lists of Documents

The sub-directory `list_of_docs/` stores the official 'lists of documents' that were used
to identify missing WPs (above).
Some 'lists of documents' have pencil annotations on them.
These are the work of international lawyer Bill Bush, 
who assembled the original documents that were eventually digitised to create the 
ATADD.
Where this type of information was used, it is noted in `wps_missing.csv` (in the `notes` column).

## Shortcomings

**WPs missing from the ATSD from the years 2001 and 2002 could not be found in the ATADD.**
The ATADD archive ends before 2001.
However, the missing WPs' titles, authors, and agenda numbers were found in their 'lists of documents'
and are recorded in `wps_missing.csv`.
- From 2001, the WP numbers that remain missing are:
1, 3, 6, 8, 17, 18, 27, 28, 30, 35, and 36.
- From 2002, a single WP remains missing, WP 24.

**WPs with no author are designated as authored by the meeting-host country.**
This was done to mirror the convention used by the ATSD.
For example,
ATCM V (1968) WP 23 "Records of the Antarctic Treaty Meeting of Experts on Logistics"
has no authorship given. The host country of ATCM V was Australia.
Therefore, in `wps_missing.csv`, the `parties` column for this WP is filled with "Australia".

**We did not attempt to obtain coverage of WP revisions.**
Some WPs have multiple revisions.
While some revisions of WPs were captured in our search for missing WPs,
this was done opportunistically.
We did not otherwise attempt to fill all WP revision-number gaps.
