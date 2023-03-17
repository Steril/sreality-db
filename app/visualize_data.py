import sqlite3
import pandas as pd

def visualize_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('/root/sreality-db/app/sreality_db.sqlite3')

    # Read data from the database into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM property", conn)

    # Close the database connection
    conn.close()

    # Display the data in a tabular format
    print(df)

def export_data_to_csv():
    # Connect to the SQLite database
    conn = sqlite3.connect('/root/sreality-db/app/sreality_db.sqlite3')

    # Read data from the database into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM property", conn)

    # Close the database connection
    conn.close()

    # Export the data to a CSV file
    df.to_csv('property_data.csv', index=False)

if __name__ == "__main__":
    visualize_data()
    export_data_to_csv()
