# importing the required modules
from airflow.decorators import dag, task
from airflow.models import Variable
import snowflake.connector
import datetime as dt
import pandas as pd
import requests
from datetime import datetime, timedelta

# Establishing connection to snowflake
def return_snowflake_conn():
    user_id = Variable.get('snowflake_userid')
    password = Variable.get('snowflake_password')
    account = Variable.get('snowflake_account')

    conn = snowflake.connector.connect(
        user=user_id,
        password=password,
        account=account,  
        warehouse='compute_wh',
        database='homework3',
        schema='raw_data'
    )
    return conn.cursor()

#Returning the last 90 day price of the stock
def return_last_90d_price(symbol):
    vantage_api_key = Variable.get('vantage_api_key')
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={vantage_api_key}'
    r = requests.get(url)
    data = r.json()

    if "Time Series (Daily)" not in data:
        raise ValueError("Error fetching data from Alpha Vantage API. Please check the symbol or API key.")

    results = []
    today = datetime.today()
    last_90_days = today - timedelta(days=90)

    for d in data["Time Series (Daily)"]:
        stock_date = datetime.strptime(d, "%Y-%m-%d")

        if stock_date >= last_90_days:
            stock_info = data["Time Series (Daily)"][d]
            stock_info["date"] = d
            stock_info["symbol"] = symbol
            results.append(stock_info)

    return results

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
    'start_date': dt.datetime(2024, 10, 1),
}

# DAG definition
@dag(
    dag_id='META_stock_data',
    default_args=default_args,
    schedule='@daily',
    catchup=False
) 

# Defining the tasks 
def stock_data_pipeline():

    @task
    def fetch_stock_data(symbol='META'):
        return return_last_90d_price(symbol)

    @task
    def process_stock_data(initial_data):
        stock_data = pd.DataFrame(initial_data)
        stock_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol']
        print(f"Processed DataFrame:\n{stock_data.head()}")  # Checking the DataFrame structure
        return stock_data

    @task
    def load_to_snowflake(processed_data):
        cursor = return_snowflake_conn()
        table_name = 'META_STOCK_DATA'

        try:
            cursor.execute("BEGIN")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS homework3.raw_data.{table_name} (
                Date STRING PRIMARY KEY,
                Open FLOAT,
                High FLOAT,
                Low FLOAT,
                Close FLOAT,
                Volume FLOAT,
                Symbol STRING
            )
            """
            cursor.execute(create_table_query)
            print(f"Table {table_name} created or verified.")
            
            for index, row in processed_data.iterrows():
                check_query = f"SELECT COUNT(*) FROM homework3.raw_data.{table_name} WHERE Date = '{row['Date']}'"
                cursor.execute(check_query)
                record_exists = cursor.fetchone()[0]

                if record_exists == 0:
                    # Insert if record does not exist
                    insert_query = f"""
                    INSERT INTO homework3.raw_data.{table_name} (Date, Open, High, Low, Close, Volume, Symbol)
                    VALUES ('{row['Date']}', {row['Open']}, {row['High']}, {row['Low']}, {row['Close']}, {row['Volume']}, '{row['Symbol']}')
                    """
                    cursor.execute(insert_query)
                else:
                    print(f"Record for {row['Date']} already exists. Skipping insert.")

            cursor.connection.commit()
            print(f"Inserted {len(processed_data)} records into {table_name}.")

        except Exception as e:
            cursor.connection.rollback()
            print(f"Transaction failed. Error: {e}")

        finally:
            cursor.close()

    initial_data = fetch_stock_data() 
    processed_data = process_stock_data(initial_data)
    load_to_snowflake(processed_data)

dag = stock_data_pipeline()