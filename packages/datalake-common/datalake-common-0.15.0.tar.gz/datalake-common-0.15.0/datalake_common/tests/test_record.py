# Copyright 2015 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import pytest

from datalake_common import has_s3, DatalakeRecord
from datalake_common.errors import InsufficientConfiguration


@pytest.mark.skipif(not has_s3, reason='requires s3 features')
def test_list_from_s3_url(s3_file_from_metadata, random_metadata):
    url = 's3://foo/bar'
    s3_file_from_metadata(url, random_metadata)
    records = DatalakeRecord.list_from_url(url)
    assert len(records) >= 1
    for r in records:
        assert r['metadata'] == random_metadata


@pytest.mark.skipif(has_s3, reason='')
def test_from_url_fails_without_boto():
    with pytest.raises(InsufficientConfiguration):
        DatalakeRecord.list_from_url('s3://foo/bar')


def test_list_from_metadata(random_metadata):
    url = 's3://foo/baz'
    records = DatalakeRecord.list_from_metadata(url, random_metadata)
    assert len(records) >= 1
    for r in records:
        assert r['metadata'] == random_metadata
