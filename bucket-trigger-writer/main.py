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

app = Flask(__name__)
# [END eventarc_audit_storage_server]

# [START eventarc_audit_storage_handler]
@app.route('/', methods=['POST'])
def index():
    # Gets the GCS bucket name from the CloudEvent header
    # Example: "storage.googleapis.com/projects/_/buckets/my-bucket"
    # objects/GossyTsukagoshi012.jpg
    bucket = request.headers.get('ce-subject')
    file = gcs_object(bucket)
    print(f"Detected change in Cloud Storage bucket: {bucket}")
    secret = os.environ.get("tap-secret")
    print(f"os get env tap-secret: {secret}")

    test = os.environ.get("TAP_TEST")
    print(f"os get env tap-secret: {test}")

    return (f"Detected change in Cloud Storage bucket: {file}", 200)
# [END eventarc_audit_storage_handler]

def gcs_object(ce_subject):
    return ce_subject.split("/")[-1]

# [START eventarc_audit_storage_server]
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# [END eventarc_audit_storage_server]