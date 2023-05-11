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

from boto3.session import Session
import json
import logging
from types import SimpleNamespace


def create_account(name, ou, session, tags={}):
    result = session.client('organizations').create_account(Email=f"{name}@example.com", AccountName=f"{name}")
    my_id = result["CreateAccountStatus"]["AccountId"]
    session.client('organizations').tag_resource(ResourceId=my_id, Tags=[dict(Key='account-holder', Value=f"{name}@example.com")])
    session.client('organizations').tag_resource(ResourceId=my_id, Tags=[dict(Key=k, Value=tags[k]) for k in tags.keys()])
    my_ou = session.client('organizations').list_parents(ChildId=my_id)["Parents"][0]["Id"]
    session.client('organizations').move_account(AccountId=my_id, SourceParentId=my_ou, DestinationParentId=ou)
    return my_id


def create_organizational_unit(parent, name, session):
    result = session.client('organizations').create_organizational_unit(ParentId=parent, Name=name)
    return result["OrganizationalUnit"]["Id"]


def put_parameter(name, value, session):
    logging.debug(f"Putting parameter {name}")
    session.client('ssm').put_parameter(Name=name,
                                        Value=json.dumps(value),
                                        Type='String')


def given_a_small_setup(environment='Spa'):

    session = Session()

    context = SimpleNamespace(session=session)

    context.root_id = session.client('organizations').create_organization(FeatureSet="ALL")["Organization"]["MasterAccountId"]

    result = session.client('organizations').create_account(Email="aws@example.com", AccountName="Example Corporation")
    context.root_account = result["CreateAccountStatus"]["AccountId"]

    context.committed_ou = create_organizational_unit(parent=context.root_id, name='committed', session=session)
    context.crm_account = create_account(name='crm', ou=context.committed_ou, session=session, tags={'account-state': 'vanilla'})
    context.erp_account = create_account(name='erp', ou=context.committed_ou, session=session, tags={'account-state': 'assigned'})

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
    put_parameter(name=f"/{environment}/Accounts/{context.crm_account}",
                  value=context.settings_crm_account,
                  session=session)

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
    put_parameter(name=f"/{environment}/Accounts/{context.erp_account}",
                  value=context.settings_erp_account,
                  session=session)

    context.sandbox_ou_name = 'Sandbox'
    context.sandbox_ou = create_organizational_unit(parent=context.root_id, name=context.sandbox_ou_name, session=session)
    context.alice_account = create_account(name='alice', ou=context.sandbox_ou, session=session, tags={'account-state': 'released'})
    context.bob_account = create_account(name='bob', ou=context.sandbox_ou, session=session, tags={'account-state': 'expired'})

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
    put_parameter(name=f"/{environment}/OrganizationalUnits/{context.sandbox_ou}",
                  value=context.settings_sandbox_ou,
                  session=session)

    # following entities exit in the organization but are not in scope of settings
    context.unmanaged_ou = create_organizational_unit(parent=context.root_id, name='unmanaged', session=session)
    context.unmanaged_account = create_account(name='unmanaged', ou=context.unmanaged_ou, session=session, tags={})

    context.settings_alien_ou = {
        'account_tags': {'CostCenter': 'alien', 'Sponsor': 'whoKnows'},
        'identifier': 'ou-alien',
        'note': 'this OU is configured but does not exist in the organization',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'disabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    put_parameter(name=f"/{environment}/OrganizationalUnits/ou-alien",
                  value=context.settings_alien_ou,
                  session=session)

    context.settings_alien_account = {
        'account_tags': {'CostCenter': 'alien', 'Sponsor': 'whoKnows'},
        'identifier': '210987654321',
        'note': 'this account is configured but does not exist in the organization',
        'preparation': {
            'feature': 'enabled',
            'variables': {'HELLO': 'WORLD'}
        },
        'purge': {
            'feature': 'enabled',
            'variables': {'DRY_RUN': 'TRUE'}
        }
    }
    put_parameter(name=f"/{environment}/Accounts/210987654321",
                  value=context.settings_alien_account,
                  session=session)

    return context
