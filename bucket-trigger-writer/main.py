# Copyright 2020 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START eventarc_audit_storage_server]
import os
from pyclbr import Class

from flask import Flask, request

from google.cloud import firestore
from google.cloud import storage
import sqlalchemy

app = Flask(__name__)
# [END eventarc_audit_storage_server]

# [START eventarc_audit_storage_handler]
@app.route('/', methods=['POST'])
def index():
    # Gets the GCS bucket name from the CloudEvent header
    # Example: "storage.googleapis.com/projects/_/buckets/my-bucket"
    # objects/GossyTsukagoshi012.jpg

    # Eventarc の bucket の表示
    bucket = request.headers.get('ce-subject')
    file = gcs_object(bucket)
    print(f"Detected change in Cloud Storage bucket: {bucket}")

    # secret の取得
    test = os.environ.get("TAP_TEST")
    print(f"os get env tap-secret: {test}")

    # DB 接続 sample
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_name = "quickstart_db"
    table_name = "aupay"
    db = init_db(db_user=db_user, db_pass=db_pass, db_name=db_name,table_name=table_name,db_socket_dir="/cloudsql", instance_connection_name="tap-samples:asia-northeast1:tap-samples-aupay")

    return (f"Detected change in Cloud Storage bucket: {file}", 200)
# [END eventarc_audit_storage_handler]

def init_tcp_connection_engine(
    db_user: str, db_pass: str, db_name: str, db_host: str
) -> sqlalchemy.engine.base.Engine:
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.

    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name,  # e.g. "my-database-name"
        ),
    )
    print("Created TCP connection pool")
    return pool


def init_unix_connection_engine(
    db_user: str,
    db_pass: str,
    db_name: str,
    instance_connection_name: str,
    db_socket_dir: str,
) -> sqlalchemy.engine.base.Engine:
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={"unix_socket": f"{db_socket_dir}/{instance_connection_name}"},
        ),
    )
    print("Created Unix socket connection pool")
    return pool


def init_db(
    db_user: str,
    db_pass: str,
    db_name: str,
    table_name: str,
    instance_connection_name: str = None,
    db_socket_dir: str = None,
    db_host: str = None,
) -> sqlalchemy.engine.base.Engine:

    if db_host:
        db = init_tcp_connection_engine(db_user, db_pass, db_name, db_host)
    else:
        db = init_unix_connection_engine(
            db_user, db_pass, db_name, instance_connection_name, db_socket_dir
        )

    # Create tables (if they don't already exist)
    print("create start")
    with db.connect() as conn:
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} "
            "( vote_id SERIAL NOT NULL, time_cast timestamp NOT NULL, "
            "team CHAR(6) NOT NULL, voter_email VARBINARY(255), "
            "PRIMARY KEY (vote_id) );"
        )

    print(f"Created table {table_name} in db {db_name}")
    return db


# [END cloud_sql_mysql_cse_db]





def download_object(bucket_name, file_path, local_path):

    # storage_client = storage.Client()
    # bucket = storage_client.bucket(bucket_name)
    # blob = bucket.blob(source_blob_name)
    # blob.download_to_filename(destination_file_name)

    bucket = bucket_client(bucket_name)
    blob = blob_client(bucket, file_path)
    download(blob, local_path)

def bucket_client(bucket_name):
    storage_client = storage.Client()
    return storage_client.bucket(bucket_name)

def blob_client(bucket_client, file_path):
    return bucket_client.blob(file_path)

def download(blob_client, local_path):
    blob_client.download_to_filename(local_path)

def gcs_object(ce_subject):
    return ce_subject.split("/")[-1]

# [START eventarc_audit_storage_server]
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# [END eventarc_audit_storage_server]