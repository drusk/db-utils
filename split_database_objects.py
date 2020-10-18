import re
import os
import sys


class DatabaseObject:
    SIGNATURE_REGEX = re.compile(
        "CREATE (FUNCTION|PROCEDURE|TABLE) ([^\s^\(]+)",
        re.IGNORECASE
    )

    TYPE_CODES = {
        "PROCEDURE": "SP",
        "FUNCTION": "FN",
        "TABLE": "TB"
    }

    def __init__(self, text):
        self._text = text
        self._type, self._name = self._parse(text)

    def _parse(self, text):
        """
        Parses the name and type (function, procedure or table).

        Example database objects and signatures:
        CREATE FUNCTION [addr].[InstitutionCountryCode] (@InstitutionID INT)
        CREATE PROCEDURE [addr].[GetAddressTypes]
        CREATE TABLE [addr].[ADDRESS_TYPES]

        The names are '[addr].[InstitutionCountryCode]',
        '[addr].[GetAddressTypes]' and '[addr].[ADDRESS_TYPES]'
        """
        match = re.search(self.SIGNATURE_REGEX, text)
        if match:
            return match.group(1), match.group(2)
        else:
            raise ValueError(f"No name found for database object: {self._text}")

    def get_type_code(self):
        return self.TYPE_CODES[self._type.upper()]

    def get_name(self):
        return self._name

    def get_pretty_name(self):
        name = self.get_name()

        pretty_name = name.replace(".", "_")
        pretty_name = pretty_name.replace("[", "")
        pretty_name = pretty_name.replace("]", "")

        pretty_name += f"_{self.get_type_code()}"

        return pretty_name

    def get_text(self):
        return self._text

    def get_undated_text(self):
        """
        Removes the timestamp from the text.
        """
        return re.sub(r"Script Date: [^\*]+", "", self._text)


def split_database_objects(all_text):
    # If the comment format can change, maybe make this more robust
    delimiter = "/****** Object:"

    chunks = [delimiter + chunk
              for chunk in all_text.split("/****** Object:")]

    # First chunk is just the database name so leave it out
    return [DatabaseObject(chunk) for chunk in chunks[1:]]


def get_table_name(all_text):
    """
    Gets the name of the table or return None.
    """
    first_line = all_text.partition("\n")[0]
    match = re.search(r"USE \[(\w+)\]", first_line, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None


class OutputFileGenerator:
    def __init__(self, output_directory):
        self._output_directory = output_directory

        self._setup_directories()

    def _setup_directories(self):
        for type_code in DatabaseObject.TYPE_CODES.values():
            os.makedirs(
                os.path.join(self._output_directory, type_code),
                exist_ok=True
            )

    def write_to_file(self, stored_procedure):
        output_path = os.path.join(
            self._output_directory, stored_procedure.get_type_code(),
            stored_procedure.get_pretty_name()
        )
        output_path += ".sql"

        with open(output_path, "w") as filehandle:
            filehandle.write(stored_procedure.get_undated_text())
            print(f"Wrote {output_path}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <stored procedure dump file> "
              f"<optional: output directory (database name is used if this "
              f"is not provided)>")
        sys.exit(1)

    with open(sys.argv[1], "r") as filehandle:
        dump_text = filehandle.read()

    stored_procedures = split_database_objects(dump_text)
    print(f"Parsed {len(stored_procedures)} database objects.")

    output_directory = None
    table_name = get_table_name(dump_text)
    if table_name and len(sys.argv) == 2:
        output_directory = table_name
        print(f"Set output directory based on database instance name: {output_directory}")
    if len(sys.argv) == 3:
        output_directory = sys.argv[2]
        print(f"Command line override of output directory: {output_directory}")

    if not output_directory:
        raise ValueError("No output directory provided on command line and "
                         "no database instance name in dump.")

    output_file_generator = OutputFileGenerator(output_directory)
    for stored_procedure in stored_procedures:
        output_file_generator.write_to_file(stored_procedure)


if __name__ == "__main__":
    main()
