# Content of this directory

The purpose of this directory is provide data accountability for the download of IPs and WPs
from the Secretariat database (accessible online at https://www.ats.aq/).

## HTTP Cache

The file `http-cache-no-body.sqlite3` is a copy of the HTTP cache database minus the `body` column.
The `body` column was removed because of its size -- it contained the PDFs of the documents themselves.
The original can be found in the full-data download **URL goes here**

`http-cache-no-body.sqlite3` contains a table named `cache` with 14729 rows and 6 columns.
The columns are: `method`, `url`, `status_code`, `status`, `headers`, and `timestamp`.

The entries provide an audit trail of the data collection and metadata for reproducibility:
1. How the data was retrieved (`method`)
2. What was accessed (`url` -- full paths to PDFs, APIs, etc.)
3. Success or failure of each access (`status_code`, `status`)
4. Technical details of the requests (`headers`)
5. When each query was made and each document was accessed (`timestamp`)

