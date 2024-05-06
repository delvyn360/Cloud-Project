from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import json
import ast
from datetime import datetime
import re


# TODO(developer)
project_id = "dm-test-415122"
subscription_id = "pg-sub"
# Number of seconds the subscriber should listen for messages

subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)

backup_db = {
    "user" : "postgres",
    "host" : "34.42.210.132",
    "database" : "vault_backup",
    "port" : 5432,
    "password" : "admin123"
}

primary_db = {
    "user" : "postgres",
    "host" : "34.172.205.229",
    "database" : "vault",
    "port" : 5432,
    "password" : "admin123"
}

def getConnCur(db_config):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    print("log: Connected to DB")
    return conn, cur

def closeCon(conn):
    if (conn != None):
        conn.commit()
        print("log: Commited changes to DB")
        conn.close()
        print("log: Disconnected from DB")

def parse_string_repr(string_repr):
    # Use regular expressions to extract function calls
    function_calls = re.findall(r'\w+\((.*?)\)', string_repr)
    # Initialize an empty list to store parsed elements
    parsed_list = []
    # Loop through function calls and append them to the parsed list
    for call in function_calls:
        parsed_list.append(call)
    return parsed_list

def process_replication(id):
    conn, cur = getConnCur(primary_db)
    cur.execute('UPDATE replication_logs SET processed=True, processed_at=NOW() WHERE id=%s', (id,))
    closeCon(conn)
    print("Procesed record in Primary DB")

# Function to apply changes to destination database
def apply_changes(message):
    msg_data = message.data.decode('utf-8')
    print("\nMessage Data", msg_data)    
    print(type(msg_data))
    change_list=parse_string_repr(msg_data) 
    print("Change List: ",change_list)  
    for change in change_list:
        print("\nChange inside for", change)
        print(type(change))
        # Convert string to dictionary
        change_dict = ast.literal_eval(change)

        print(change_dict)
        print(type(change_dict))   
        table_name = change_dict['table_name']
        operation = change_dict['operation']
        log_id=change_dict['id']
        data = change_dict['data']
        columns = ', '.join(data.keys())
        # Extract values from the dictionary
        values = list(data.values())
        print(values)
        print(data['id'])
        conn, cur =  getConnCur(backup_db)

    
        if operation == 'INSERT':
            # Construct the SQL query

            values_template = ', '.join(['%s'] * len(data))
            query="INSERT INTO {} ({}) VALUES ({})".format(table_name,columns,values_template)
            print("\n",operation)
            print("\n",query)
            cur.execute( query, values)
            print("\nInserted to Backup DB")
            process_replication(log_id)


        elif operation == 'UPDATE':
            execute_values = tuple(values) + (data['id'],)
            # Construct the SQL query
            set_clause = ', '.join(f"{column} = %s" for column in columns.split(', '))
            query="UPDATE {} SET {} WHERE id = %s".format(table_name,set_clause)
            print("\n",operation)
            print("\n", query)
            cur.execute(query,execute_values)
            print("\nUpdated to Backup DB")
            process_replication(log_id)


        elif operation == 'DELETE':

            # Construct the SQL query
            query="DELETE FROM {} WHERE id=%s".format(table_name)
            print("\n",operation)
            print("\n",query)
            cur.execute(query, (data['id'],))
            print("\nDeleted from Backup DB")
            process_replication(log_id)

        closeCon(conn)


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    apply_changes(message)
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")


try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopped receiving messages.")