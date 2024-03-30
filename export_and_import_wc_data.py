import subprocess
import re
import config 
from config import live_connection, local_connection

################### FUNCTIONS START ###################

def run_mysqldump(dump_command):
    """
    Executes the mysqldump command specified in dump_command.
    If the command runs successfully, it prints a success message.
    If an error occurs, it prints the error message.
    """
    try:
        subprocess.run(dump_command, shell=True, check=True)
        print(f"Export successful for command: {dump_command}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def extract_ids_from_sql(sql_file, regex_pattern):
    """
    Extracts IDs from the SQL dump file using the specified regex pattern.
    Returns a list of extracted IDs.
    """
    ids = []
    with open(sql_file, 'r') as f:
        for line in f:
            matches = re.findall(regex_pattern, line)
            ids.extend(matches)
    return ids


def combine_sql_dumps(dump_files, combined_file):
    """
    Combines multiple SQL dump files into a single file.
    Prints a message indicating the location of the combined file.
    """
    with open(combined_file, 'w') as outfile:
        for fname in dump_files:
            with open(fname) as infile:
                outfile.write(infile.read())
            outfile.write('\n')
    print(f"Combined SQL dumps saved to {combined_file}")


def search_and_replace_in_sql(dump_files, search_text, replace_text):
    """
    Performs a search and replace operation within the specified SQL dump files.
    Replaces the search_text with the replace_text.
    Additionally, it removes 'DROP TABLE IF EXISTS' lines and 'CREATE TABLE' blocks.
    Prints a message indicating the completion of the operation.
    """
    for fname in dump_files:
        with open(fname, 'r') as file:
            filedata = file.read()

        # Replace specific text
        filedata = filedata.replace(search_text, replace_text)

        # Remove 'DROP TABLE IF EXISTS' lines
        filedata = re.sub(r'^DROP TABLE IF EXISTS .+?;$', '', filedata, flags=re.MULTILINE)

        # Remove 'CREATE TABLE' blocks
        filedata = re.sub(r'CREATE TABLE `[^`]+` \([^;]+;\n', '', filedata, flags=re.MULTILINE)

        # Write the modified content back to the file
        with open(fname, 'w') as file:
            file.write(filedata)

    print("Search and replace completed in SQL files.")

def get_customer_ids():
    """
    Gets customer IDs from the usermeta table in the database.
    Returns a list of customer IDs.
    """
    customer_ids = []

    # Connect to the database
    connection = live_connection()
    try:
        with connection.cursor() as cursor:
            # SQL query to get customer user IDs from usermeta
            sql = f"SELECT user_id FROM `{config.DB_NAME}`.`{config.TABLE_PREFIX}_usermeta` WHERE `meta_value` = 'a:1:{{s:8:\"customer\";b:1;}}';"
            cursor.execute(sql)
            result = cursor.fetchall()

            # Extracting user_ids from the result
            customer_ids = [str(row['user_id']) for row in result]
    finally:
        connection.close()

    return customer_ids


def import_sql_dump(sql_file):
    """
    Imports the combined SQL dump file into the local database.
    Prints a success message or an error message if an exception occurs.
    """
    connection = local_connection()
    try:
        with connection.cursor() as cursor:
            # Read the SQL dump file
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            # Execute the SQL script
            cursor.execute(sql_script)
        print(f"SQL dump imported into database: {config.LOCAL_DB_NAME}")
    except Exception as e:
        print(f"An error occurred while importing SQL dump: {e}")
    finally:
        connection.close()

################### FUNCTIONS END ###################

# Combine all SQL dumps into one file and then perform search and replace
sql_dump_file = f"combined_sql_dump-{config.TIMESTAMP}.sql"

# Define the mysqldump commands for each table
dump_commands = {
    'posts': f"mysqldump --insert-ignore -u {config.DB_USER} -p'{config.DB_PASSWORD}' -h {config.DB_HOST} --column-statistics=0 {config.DB_NAME} {config.TABLE_PREFIX}_posts --where=\"post_type IN ('shop_order', 'product')\" > {config.DUMPED_TABLE_PREFIX}_posts-{config.TIMESTAMP}.sql",
    'product': f"mysqldump --insert-ignore -u {config.DB_USER} -p'{config.DB_PASSWORD}' -h {config.DB_HOST} --column-statistics=0 {config.DB_NAME} {config.TABLE_PREFIX}_posts --where=\"post_type='product'\" > {config.DUMPED_TABLE_PREFIX}_product-{config.TIMESTAMP}.sql",

}

run_mysqldump(dump_commands['posts'])
run_mysqldump(dump_commands['product'])

# Run the mysqldump for 'product' and extract product IDs
product_ids = extract_ids_from_sql(f"{config.DUMPED_TABLE_PREFIX}_product-{config.TIMESTAMP}.sql", r"\((\d+),")

# Use the function to get customer IDs
customer_ids = get_customer_ids()

# Run the mysqldump for 'posts' and extract order IDs
order_ids = extract_ids_from_sql(f"{config.DUMPED_TABLE_PREFIX}_posts-{config.TIMESTAMP}.sql", r"\((\d+),")

temp_ids = {'order_ids': order_ids}
temp_product_ids = {'product_ids': product_ids}

# Combine order and product IDs
combined_ids = temp_ids['order_ids'] + temp_product_ids['product_ids']

# Define the mysqldump commands for each table
dump_commands = {
    'postmeta': f"mysqldump --insert-ignore -u {config.DB_USER} -p'{config.DB_PASSWORD}' -h {config.DB_HOST} --column-statistics=0 {config.DB_NAME} {config.TABLE_PREFIX}_postmeta --where=\"post_id IN ({','.join(combined_ids)})\" > {config.DUMPED_TABLE_PREFIX}_postmeta-{config.TIMESTAMP}.sql",
    'usermeta': f"mysqldump --insert-ignore -u {config.DB_USER} -p'{config.DB_PASSWORD}' -h {config.DB_HOST} --column-statistics=0 {config.DB_NAME} {config.TABLE_PREFIX}_usermeta --where=\"user_id IN ({','.join(customer_ids)})\" > {config.DUMPED_TABLE_PREFIX}_usermeta-{config.TIMESTAMP}.sql",
    'users': f"mysqldump --insert-ignore -u {config.DB_USER} -p'{config.DB_PASSWORD}' -h {config.DB_HOST} --column-statistics=0 {config.DB_NAME} {config.TABLE_PREFIX}_users --where=\"ID IN ({','.join(customer_ids)})\" > {config.DUMPED_TABLE_PREFIX}_users-{config.TIMESTAMP}.sql",
    'options': "with open('dump_options.py') as file: exec(file.read())"  # Define additional commands for other tables if necessary
}

# Create a list of SQL file names
sql_files = [f"{config.DUMPED_TABLE_PREFIX}_{table}-{config.TIMESTAMP}.sql" for table in dump_commands.keys()]

# Run mysqldump commands for specified tables
run_mysqldump(dump_commands['postmeta'])
run_mysqldump(dump_commands['usermeta'])
run_mysqldump(dump_commands['users'])
exec(dump_commands['options'])

# Combine SQL dump files into a single file
combine_sql_dumps(sql_files, f"combined_sql_dump-{config.TIMESTAMP}.sql")

# Perform search and replace operations on SQL files
search_and_replace_in_sql(sql_files + [f"combined_sql_dump-{config.TIMESTAMP}.sql"], f"`{config.TABLE_PREFIX}_", f"`{config.DUMPED_TABLE_PREFIX}_")

# Import the combined SQL dump into the local database
import_sql_dump(sql_dump_file)