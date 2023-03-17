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

if __name__ == "__main__":
    visualize_data()
