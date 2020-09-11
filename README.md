# db-utils

Utility scripts for working with databases.

## `split_stored_procedures.py`

Splits the stored procedures and functions from a MS SQL dump into separate
files.
One use case of this is to take a legacy database and start keeping its
stored procedures in version control.

Basic usage:

```
python3 split_stored_procedures.py dump.txt
```

This will look for the database name in the dump and create a folder with
that name in the current directory if it does not exist.
Then the stored procedures and functions will be split and organized
into subdirectories.

You can override the output directory by specifying it as a second
parameter to the script:

```
python3 split_stored_procedures.py dump.txt output_directory
```
