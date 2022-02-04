#!/usr/bin/env python3
"""
Copyright Reply.com or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

import builtins
from io import BytesIO
import os
import pytest
from types import SimpleNamespace

from code.configuration import Configuration


pytestmark = pytest.mark.wip


@pytest.fixture
def toggles():
    builtins.toggles = SimpleNamespace()
    return builtins.toggles


def test_expand_text(toggles):
    text = 'this is some sample text with ___parameter___ to replace'
    toggles.parameter = '=value='
    test = Configuration.expand_text(text, toggles)
    assert test == 'this is some sample text with =value= to replace'


@pytest.mark.slow
def test_initialize():
    Configuration.initialize()
    assert builtins.toggles.dry_run is False
    assert builtins.toggles.aws_account is not None
    assert builtins.toggles.aws_environment is not None
    assert builtins.toggles.aws_region is not None

    Configuration.initialize(dry_run=True)
    assert builtins.toggles.dry_run is True

    with pytest.raises(FileNotFoundError):
        Configuration.initialize(stream='this*file*does*not*exist')


def test_set_default_values(toggles):
    Configuration.set_default_values()
    assert toggles.application_ami_id is None
    assert toggles.application_disk_size is None
    assert toggles.application_inbound_ports == [443]
    assert toggles.application_instance_type == 't3.large'
    assert toggles.application_internet_facing is False
    assert toggles.application_operating_system is None
    assert toggles.application_setup_document == 'install_application_server'
    assert toggles.application_trusted_peer == '0.0.0.0/0'
    assert toggles.bucket_name is None
    assert toggles.bucket_encryption_key is None
    assert toggles.cockpit_text_label == 'Cluster Monitoring'
    assert toggles.database_ami_id is None
    assert toggles.database_disk_size is None
    assert toggles.database_instance_type == 't3.large'
    assert toggles.database_operating_system is None
    assert toggles.database_setup_document == 'install_database_server'
    assert toggles.infrastructure_vpc_id is None


def test_set_from_environment(toggles):
    environ = dict(
        active_directory_domain_credentials="where-my-secret-is",
        TRUSTED_PEER='4.3.2.1/32',
        NOT_MAPPED_VARIABLE="what'up Doc?",
        NONE_VARIABLE=None,
        NULL_VARIABLE='')

    Configuration.set_from_environment(environ=environ)
    assert toggles.__dict__.get('active_directory_domain_credentials') is None
    assert toggles.application_trusted_peer == '4.3.2.1/32'

    mapping = dict(
        active_directory_domain_credentials='active_directory_domain_credentials',
        inexistant_variable="*THIS*DOES*NOT*EXIST*IN*ENVIRONMENT",
        none_variable='NONE_VARIABLE',
        null_variable='NULL_VARIABLE')
    Configuration.set_from_environment(environ=environ, mapping=mapping)
    assert toggles.active_directory_domain_credentials == "where-my-secret-is"
    with pytest.raises(Exception):
        assert toggles.inexistant_variable is None
    with pytest.raises(Exception):
        assert toggles.none_variable is None
    assert toggles.null_variable == ''


def test_set_from_settings(toggles):
    settings = dict(active_directory=dict(specific_parameter="foo bar"))
    Configuration.set_from_settings(settings)
    assert toggles.active_directory_specific_parameter == "foo bar"
    with pytest.raises(Exception):
        assert toggles.inexistant_toggle is None


@pytest.mark.slow
def test_set_from_yaml(toggles):
    os.environ.pop('TRUSTED_PEER', None)

    Configuration.set_from_yaml(BytesIO(b'a: b\nc: d\n'))
    assert toggles.a == 'b'  # 1
    assert toggles.c == 'd'  # 2

    Configuration.set_from_yaml('settings_sample.yaml')
    assert toggles.application_inbound_ports == [80, 443]
    assert len(toggles.__dict__.keys()) < 10  # assets are not listed

    Configuration.set_from_yaml('tests/settings/assets_fixture.yaml')
    assert toggles.bucket_name == 'name-of-an-existing-bucket'
    assert toggles.bucket_encryption_key == 'alias/EncryptionOperationKey'

    Configuration.set_from_yaml('tests/settings/infrastructure_fixture_default.yaml')
    assert toggles.infrastructure_vpc_id == 'default'

    Configuration.set_from_yaml('tests/settings/infrastructure_fixture.yaml')
    assert toggles.infrastructure_vpc_id == 'id-of-existing-vpc'
    assert toggles.infrastructure_private_production_subnet_id == 'id-of-existing-subnet-2'

    Configuration.set_from_yaml('tests/settings/servers.yaml')
    assert toggles.application_ami_id == 'ami-0e4ec44f0007f4ab2'
    assert toggles.application_disk_size == 10
    assert toggles.application_inbound_ports == [12, 34]
    assert toggles.application_instance_type == 'c5.large'
    assert toggles.application_internet_facing is False
    assert toggles.application_setup_document == '../tests/documents/custom_application_server_setup'
    assert toggles.database_ami_id == 'ami-0e4ec44f0007f4ab2'
    assert toggles.database_disk_size == 10
    assert toggles.database_instance_type == 'c5.large'
    assert toggles.database_setup_document == '../tests/documents/custom_database_server_setup'

    Configuration.set_from_yaml('tests/settings/servers_pl.yaml')
    assert toggles.application_trusted_peer == 'pl-1234'
    assert toggles.application_internet_facing is True
