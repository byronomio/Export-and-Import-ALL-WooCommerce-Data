# Import Export ALL WooCommerce Data

## Introduction

This toolkit provides a set of Python scripts for exporting, cleaning, and importing WooCommerce data. It allows users to extract specific data from their WooCommerce databases, perform data cleaning and preparation operations, and import the processed data back into a WooCommerce database. The toolkit is designed to streamline the process of managing WooCommerce data, making it easier to handle large datasets or migrate data between different environments.

## Features

- Export specific WooCommerce data, such as orders, products, customers, and related metadata, based on custom criteria.
  - Products
  - Orders
  - Customers (users)
  - Product metadata
  - Order metadata
  - User metadata
  - WooCommerce options data
- Clean and prepare data by combining multiple SQL dumps into a single file.
- Import the processed data back into a WooCommerce database.

## Getting Started

### Prerequisites

- Python 3.x
- PyMySQL library (`pip install pymysql`)
- A WooCommerce environment with a MySQL database

### Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/Import-Export-ALL-WooCommerce-Data.git
```

2. Install the required Python libraries:

```
pip install -r requirements.txt
```

### Configuration

The repository already includes a `config.py` file with the necessary configurations. Update the following variables with your actual database credentials and configurations:

```python
#Variables
TABLE_PREFIX = ''
DUMPED_TABLE_PREFIX = ''
TIMESTAMP = ''

# Import from LIVE
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
DB_CHASRET = ""
DB_UNIX_SOCKET = ""

# Imported from LIVE into LOCAL
LOCAL_DB_HOST = ""
LOCAL_DB_USER = ""
LOCAL_DB_PASSWORD = ""
LOCAL_DB_NAME = ""
LOCAL_CHASRET = ""
LOCAL_UNIX_SOCKET = ""
```

The `config.py` file also includes two functions, `live_connection()` and `local_connection()`, which establish connections to the live (source) and local (target) databases, respectively.

## Usage

1. Run the `export_and_import_wc_data.py` script:

```
python export_orders_and_clients.py
```

2. The script will perform the following actions:
   - Export orders and products data from the WooCommerce database.
   - Extract order IDs, product IDs, and customer IDs.
   - Combine the SQL dumps into a single file.
   - Perform search-replace operations on the SQL dumps.
   - Import the processed data into the local WooCommerce database.

3. Monitor the console output for any errors or status messages.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

- Byron Jacobs
- Author URI: https://heavyweightdigital.co.za
- Email: info@heavyweightdigital.co.za