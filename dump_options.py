import subprocess
import mysql.connector
import config  # Assumes the existence of a config.py file with DB connection details
import re

# Function to create a temporary copy of the options table without the option_id column, dump it to a SQL file, and then remove the copy
def dump_options_table_without_option_id():
    """Creates a copy of the options table without the option_id column, dumps it, and then removes the copy."""

    temp_table_name = "temp_options"

    # Establishing a connection to the database
    db_connection = mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )
    cursor = db_connection.cursor()

    # Creating a temporary table based on the structure of the original options table
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {temp_table_name} LIKE {config.TABLE_PREFIX}_options;")

    # Dropping the option_id column if it exists in the temporary table
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{config.DB_NAME}'
        AND TABLE_NAME = '{temp_table_name}'
        AND COLUMN_NAME = 'option_id';
    """)
    if cursor.fetchone()[0] == 1:
        cursor.execute(f"ALTER TABLE {temp_table_name} DROP COLUMN option_id;")

    # Copying data from the original options table to the temporary table, excluding the option_id column
    cursor.execute(f"""
        INSERT INTO {temp_table_name} (option_name, option_value, autoload)
        SELECT option_name, option_value, autoload
        FROM {config.TABLE_PREFIX}_options
        WHERE option_name LIKE 'woocommerce_%';
    """)
    db_connection.commit()

    # Dumping the temporary table to a SQL file
    dump_command = f"mysqldump -u {config.DB_USER} -p'{config.DB_PASSWORD}' -h {config.DB_HOST} --column-statistics=0 {config.DB_NAME} {temp_table_name} > {config.DUMPED_TABLE_PREFIX}_options-{config.TIMESTAMP}.sql"
    subprocess.run(dump_command, shell=True)

    # Removing the temporary table
    cursor.execute(f"DROP TABLE IF EXISTS {temp_table_name};")
    cursor.close()
    db_connection.close()

    print(f"Dumped options table without option_id to {config.DUMPED_TABLE_PREFIX}_options-{config.TIMESTAMP}.sql")
    return f"{config.DUMPED_TABLE_PREFIX}_options-{config.TIMESTAMP}.sql"

# Function to add the ON DUPLICATE KEY UPDATE clause to all INSERT statements in the dumped SQL file
def add_on_duplicate_key_update_to_options_dump(options_dumped_sql):
    """Adds ON DUPLICATE KEY UPDATE clause to the insert statements in the dumped SQL file."""
    updated_lines = []
    is_inserting = False  # Flag to track if we are within an INSERT block

    # Reading and updating the SQL dump file
    with open(options_dumped_sql, 'r') as file:
        for line in file.readlines():
            if line.startswith("INSERT INTO"):
                is_inserting = True
            if is_inserting and line.strip().endswith(';'):
                line = line.rstrip('\n') + " ON DUPLICATE KEY UPDATE `option_value` = VALUES(`option_value`), `autoload` = VALUES(`autoload`);\n"
                is_inserting = False
            
            updated_lines.append(line)

    # Writing the updated lines back to the SQL dump file
    with open(options_dumped_sql, 'w') as file:
        file.writelines(updated_lines)

    print(f"Updated {options_dumped_sql} with ON DUPLICATE KEY UPDATE clause.")

# Function to perform search and replace operations within the specified SQL dump file
def search_and_replace_in_sql2(options_dumped_sql):
    """Performs search and replace operations in the specified SQL dump file."""
    with open(options_dumped_sql, 'r') as file:
        filedata = file.read()

    # Replacing temporary table names and adjusting ON DUPLICATE KEY UPDATE clauses
    search_text = 'temp_options'
    replace_text = f'{config.DUMPED_TABLE_PREFIX}_options'
    filedata = filedata.replace(search_text, replace_text)

    search_text2 = '; ON DUPLICATE KEY UPDATE'
    replace_text2 = ' ON DUPLICATE KEY UPDATE'
    filedata = filedata.replace(search_text2, replace_text2)

    # Removing 'DROP TABLE IF EXISTS' and 'CREATE TABLE' statements from the dump
    filedata = re.sub(r'^DROP TABLE IF EXISTS .+?;$', '', filedata, flags=re.MULTILINE)
    filedata = re.sub(r'CREATE TABLE `[^`]+` \([^;]+;\n', '', filedata, flags=re.MULTILINE)

    # Writing the modified content back to the file
    with open(options_dumped_sql, 'w') as file:
        file.write(filedata)

    print("Search and replace completed in SQL files.")

# Function to add column names to INSERT INTO statements in the SQL dump
def add_column_names_to_inserts(options_dumped_sql):
    """Adds column names to INSERT INTO statements in the SQL dump file."""
    with open(options_dumped_sql, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    insert_regex = re.compile(r'^INSERT INTO `(\w+)` VALUES')

    # Updating INSERT INTO statements with column names
    for line in lines:
        match = insert_regex.match(line)
        if match:
            line = line.replace(' VALUES', f' {options_columns} VALUES')
        updated_lines.append(line)

    # Writing the updated lines back to the SQL dump file
    with open(options_dumped_sql, 'w') as file:
        file.writelines(updated_lines)

# Example usage of functions:
options_columns = "(`option_name`, `option_value`, `autoload`)"
options_dumped_sql = f'{config.DUMPED_TABLE_PREFIX}_options-{config.TIMESTAMP}.sql'

# Sequentially executing functions to dump the table, update the SQL dump, and perform search and replace operations
dump_options_table_without_option_id()
add_column_names_to_inserts(options_dumped_sql)
add_on_duplicate_key_update_to_options_dump(options_dumped_sql)
search_and_replace_in_sql2(options_dumped_sql)
