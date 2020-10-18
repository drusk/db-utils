# db-utils

Utility scripts for working with databases.

## `split_database_objects.py`

Splits the tables, stored procedures and functions from a MS SQL dump into separate
files.
One use case of this is to take a legacy database and start keeping its
stored procedures in version control.

Basic usage:

```
python3 split_database_objects.py dump.txt
```

This will look for the database name in the dump and create a folder with
that name in the current directory if it does not exist.
Then the tables, stored procedures and functions will be split and organized
into subdirectories.

You can override the output directory by specifying it as a second
parameter to the script:

```
python3 split_database_objects.py dump.txt output_directory
```

CAVEAT 1: If the MS SQL Server dump contains UTF-16 Unicode text, a utility
like dos2unix (https://waterlan.home.xs4all.nl/dos2unix.html) must be used
to convert the dump file to UTF-8 Unicode text before it is processed
by split_database_objects.py.  For instance

```
dos2unix dump.txt
```
CAVEAT 2: The database dump must be created with comments preceding each database object.
For instance,
```
/****** Object:  Table [addr].[ADDRESS_TYPES] ...
```
The "Script Date" contained in the comment will not appear in the output as it is the date
of the database dump rather than the last modification date of the database object.  This
is too allow tracking of actual changes to the database object in a version control system.
