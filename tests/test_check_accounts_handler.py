#!/usr/bin/env python3
"""
Copyright Reply.com or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
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

from boto3.session import Session
import json
from moto import mock_organizations, mock_ssm
import os
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from code.check_accounts_handler import handle_event, validate_tags
import code.check_accounts_handler as to_be_mocked

# pytestmark = pytest.mark.wip


def create_account(name, ou, session, tags={}):
    result = session.client('organizations').create_account(Email=f"{name}@acme.com",
                                                            AccountName=f"{name}")
    my_id = result["CreateAccountStatus"]["AccountId"]
    session.client('organizations').tag_resource(ResourceId=my_id,
                                                 Tags=[dict(Key='account:holder', Value=f"{name}@acme.com")])
    session.client('organizations').tag_resource(ResourceId=my_id,
                                                 Tags=[dict(Key=k, Value=v) for k, v in tags.items()])
    my_ou = session.client('organizations').list_parents(ChildId=my_id)["Parents"][0]["Id"]
    session.client('organizations').move_account(AccountId=my_id, SourceParentId=my_ou, DestinationParentId=ou)
    return my_id


def create_organizational_unit(parent, name, session):
    result = session.client('organizations').create_organizational_unit(ParentId=parent, Name=name)
    return result["OrganizationalUnit"]["Id"]


def given_some_context():
    environment = os.environ['ENVIRONMENT_IDENTIFIER']

    session = Session(aws_access_key_id='testing',
                      aws_secret_access_key='testing',
                      aws_session_token='testing',
                      region_name='eu-west-1')

    context = SimpleNamespace(session=session)
    context.root_id = session.client('organizations').create_organization(FeatureSet="ALL")["Organization"]["MasterAccountId"]

    context.committed_ou = create_organizational_unit(parent=context.root_id, name='committed', session=session)
    context.crm_account = create_account(name='crm', ou=context.committed_ou, session=session, tags=dict(CostCenter='CRM', Sponsor='CSO'))
    context.erp_account = create_account(name='erp', ou=context.committed_ou, session=session, tags=dict(CostCenter='ERP', Sponsor='COO'))

    context.sandbox_ou = create_organizational_unit(parent=context.root_id, name='sandbox', session=session)
    context.alice_account = create_account(name='alice', ou=context.sandbox_ou, session=session)
    context.bob_account = create_account(name='bob', ou=context.sandbox_ou, session=session)

    context.settings_crm_account = {
        'account_tags': {'CostCenter': 'crm', 'Sponsor': 'Claudio Roger Marciano'},
        'identifier': context.crm_account,
        'note': 'the production account for our CRM system',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'disabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=f"/{environment}/Accounts/{context.crm_account}",
                                        Value=json.dumps(context.settings_crm_account),
                                        Type='String')

    context.settings_erp_account = {
        'account_tags': {'CostCenter': 'erp', 'Sponsor': 'Eric Roger Plea'},
        'identifier': context.erp_account,
        'note': 'the production account for our ERP system',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'disabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=f"/{environment}/Accounts/{context.erp_account}",
                                        Value=json.dumps(context.settings_erp_account),
                                        Type='String')

    context.settings_committed_ou = {
        'account_tags': {'CostCenter': 'committed', 'Sponsor': 'CFO'},
        'identifier': context.committed_ou,
        'note': 'the collection of production accounts for actual business',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'disabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=f"/{environment}/OrganizationalUnits/{context.committed_ou}",
                                        Value=json.dumps(context.settings_committed_ou),
                                        Type='String')

    context.settings_sandbox_ou = {
        'account_tags': {'CostCenter': 'sandbox', 'Sponsor': 'CTO'},
        'identifier': context.sandbox_ou,
        'note': 'the collection of sandbox accounts for individual innovation',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'enabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    session.client('ssm').put_parameter(Name=f"/{environment}/OrganizationalUnits/{context.sandbox_ou}",
                                        Value=json.dumps(context.settings_sandbox_ou),
                                        Type='String')

    return context


@pytest.mark.integration_tests
@patch.dict(os.environ, dict(ENVIRONMENT_IDENTIFIER='Fake',
                             ORGANIZATIONAL_UNITS_PARAMETER="SomeParameter",
                             VERBOSITY='DEBUG'))
@mock_organizations
@mock_ssm
def test_handle_event(monkeypatch):

    context = given_some_context()

    processed = set()

    def process(details, *arg, **kwargs):
        processed.add(details.id)

    monkeypatch.setattr(to_be_mocked, 'validate_tags', process)

    result = handle_event(event=None, context=None, session=context.session)
    assert result == '[OK]'
    assert processed == {context.crm_account, context.erp_account, context.alice_account, context.bob_account}


@pytest.mark.unit_tests
def test_validate_tags():
    valid_tags = SimpleNamespace(id='123456789012',
                                 tags={'account:holder': 'a@b.com', 'account:state': 'released'})
    validate_tags(item=valid_tags)


@pytest.mark.unit_tests
def test_validate_tags_on_absent_holder():
    absent_holder = SimpleNamespace(id='123456789012',
                                    tags={'account:state': 'released'})
    with pytest.raises(ValueError):
        validate_tags(item=absent_holder)


@pytest.mark.unit_tests
def test_validate_tags_on_invalid_holder():
    invalid_holder = SimpleNamespace(id='123456789012',
                                     tags={'account:holder': 'a_b.com', 'account:state': 'released'})
    with pytest.raises(ValueError):
        validate_tags(item=invalid_holder)


@pytest.mark.unit_tests
def test_validate_tags_on_absent_state():
    absent_state = SimpleNamespace(id='123456789012',
                                   tags={'account:holder': 'a@b.com'})
    with pytest.raises(ValueError):
        validate_tags(item=absent_state)


@pytest.mark.unit_tests
def test_validate_tags_on_invalid_state():
    invalid_state = SimpleNamespace(id='123456789012',
                                    tags={'account:holder': 'a@b.com', 'account:state': '*alien*'})
    with pytest.raises(ValueError):
        validate_tags(item=invalid_state)
