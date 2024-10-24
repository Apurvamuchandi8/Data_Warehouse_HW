from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.operators.python import get_current_context
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

import snowflake.connector
import requests
from datetime import datetime, timedelta

def return_snowflake_conn():

    # Initialize the SnowflakeHook
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    
    # Execute the query and fetch results
    conn = hook.get_conn()
    return conn.cursor()

@task
def load(target_table):
    cur = return_snowflake_conn()

    try:
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {target_table}  (
            userId int not NULL,
            sessionId varchar(32) primary key,
            channel varchar(32) default 'direct'  
        )""")
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {target_table_1}  (
            sessionId varchar(32) primary key,
            ts timestamp   
        )""")
        cur.execute("BEGIN;")
        cur.execute(f"""CREATE OR REPLACE STAGE homework3.raw_data.blob_stage
            url = 's3://s3-geospatial/readonly/'
            file_format = (type = csv, skip_header = 1, field_optionally_enclosed_by = '"');""")
        sql = f"""COPY INTO homework3.raw_data.user_session_channel
                FROM @homework3.raw_data.blob_stage/user_session_channel.csv """
        print(sql)
        cur.execute(sql)
        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        print(e)
        raise e

@task
def load_1(target_table_1):
    cur = return_snowflake_conn()

    try:
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {target_table_1}  (
            sessionId varchar(32) primary key,
            ts timestamp   
        )""")
        cur.execute("BEGIN;")
        cur.execute(f"""CREATE OR REPLACE STAGE homework3.raw_data.blob_stage
            url = 's3://s3-geospatial/readonly/'
            file_format = (type = csv, skip_header = 1, field_optionally_enclosed_by = '"');""")
        sql = f"""COPY INTO homework3.raw_data.session_timestamp
                FROM @homework3.raw_data.blob_stage/session_timestamp.csv """
        print(sql)
        cur.execute(sql)
        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        print(e)
        raise e

with DAG(
    dag_id = 'Homework7',
    start_date = datetime(2024,10,2),
    catchup=False,
    tags=['ETL'],
    schedule = '30 2 * * *'
) as dag:

    target_table = "homework3.raw_data.user_session_channel"
    target_table_1 = "homework3.raw_data.session_timestamp"
    load(target_table)
    load_1(target_table_1)