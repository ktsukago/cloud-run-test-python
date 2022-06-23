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
import copy
from unittest import mock

from uuid import uuid4

import pytest
import main


binary_headers = {
    "ce-id": str(uuid4),
    "ce-type": "com.pytest.sample.event",
    "ce-source": "<my-test-source>",
    "ce-specversion": "1.0"
}


@pytest.fixture
def client(mocker):
    main.app.testing = True
    return main.app.test_client()


# eventarcから入ってきた object 名を取得してfirestore に書き込むことを確認したい
def test_endpoint(client, capsys, mocker):

    test_headers = copy.copy(binary_headers)
    # Ce-Subject にファイル名が入る objects/filename
    test_headers['Ce-Subject'] = 'objects/Testfile.jpg'
    mock_gcs_object = mocker.patch("main.gcs_object")
    
    r = client.post('/', headers=test_headers)
    assert r.status_code == 200
    mock_gcs_object.assert_called_once_with(test_headers['Ce-Subject'])


    out, _ = capsys.readouterr()
    assert f"Detected change in Cloud Storage bucket: {test_headers['Ce-Subject']}" in out


    # write = mocker.patch('main.products')
    # write.assert_call_once_with(test_headers['Ce-Subject'])

    # firestore にかきこめていることの確認
    # app から product_data.write("object_name")みたいにして、product_data経由でfirestore に書き込む
    # products.write は 1回コールされているか、writeにそのままデータがわたっているかを検証できればよい


# request データからupload したファイル名を取り出せること
def test_gcs_object():
    test_headers = copy.copy(binary_headers)
    test_headers['Ce-Subject'] = 'objects/Testfile.jpg'
    assert main.gcs_object(test_headers['Ce-Subject']) == 'Testfile.jpg'

    test_headers['Ce-Subject'] = 'Testfile.jpg'
    assert main.gcs_object(test_headers['Ce-Subject']) == 'Testfile.jpg'

    test_headers['Ce-Subject'] = 'objects/hoge/Testfile.jpg'
    assert main.gcs_object(test_headers['Ce-Subject']) == 'Testfile.jpg'

# secret の部分をインプットしてoutput されることのテスト
def test_main_should_get_env_and_output_syslog(client, capsys, mocker):
    test_headers = copy.copy(binary_headers)
    # Ce-Subject にファイル名が入る objects/filename
    test_headers['Ce-Subject'] = 'objects/Testfile.jpg'    
    r = client.post('/', headers=test_headers)
    assert r.status_code == 200

    env_mock = mocker.patch("os.environ.get", return_value={"key":"value"})
    out, _ = capsys.readouterr()
#    assert f"Detected change in #Cloud Storage bucket: {test_headers['Ce-Subject']}" in out
