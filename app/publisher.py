from google.cloud import pubsub_v1
import time
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# TODO(developer)

def getConnCur():
    conn = psycopg2.connect(user='postgres',
    host ='34.172.205.229',
    database = 'vault',
    port = 5432,
    password = 'admin123')
    cur = conn.cursor()
    print("log: Connected to DB")
    return conn, cur

def closeCon(conn):
    if (conn != None):
        conn.commit()
        print("log: Commited changes to DB")
        conn.close()
        print("log: Disconnected from DB")

# Function to fetch changes from source database
def fetch_changes():
    conn,cur=getConnCur()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, table_name, operation, data FROM replication_logs WHERE processed = FALSE;")
        changes = cursor.fetchall()
    closeCon(conn)
    return changes


project_id = "dm-test-415122"
topic_id = "pg-topic"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

while True:
    changes=fetch_changes()
    if len(changes)>0:
        print(changes)
        data_str = str(changes)
        data = data_str.encode("utf-8")
        #When you publish a message, the client returns a future.
        future = publisher.publish(topic_path, data)
        print(future.result())

    time.sleep(30)
    





