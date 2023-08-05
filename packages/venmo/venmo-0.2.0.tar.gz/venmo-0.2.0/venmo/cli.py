#!/usr/bin/env python

"""
Venmo CLI.

Pay or charge people via the Venmo API:

    venmo pay 19495551234 23.19 "Thanks for the beer <3"
    venmo charge 19495551234 23.19 "That beer wasn't free!"

Refresh your venmo access token:

    venmo refresh-token
"""

import argparse
import urllib

import requests

from venmo import settings, oauth


def pay(args):
    _pay_or_charge(args)


def charge(args):
    args.amount = "-" + args.amount
    _pay_or_charge(args)


def _pay_or_charge(args):
    params = {
        'note': args.note,
        'phone': args.phone,
        'amount': args.amount,
        'access_token': oauth.get_access_token(),
        'audience': 'private',
    }
    response = requests.post(
        _payments_url_with_params(params)
    ).json()
    _log_response(response)


def _payments_url_with_params(params):
    return "{payments_base_url}?{params}".format(
        payments_base_url=settings.PAYMENTS_BASE_URL,
        params=urllib.urlencode(params),
    )


def _log_response(response):
    if 'error' in response:
        message = response['error']['message']
        code = response['error']['code']
        print 'message="{}" code={}'.format(message, code)
        return

    payment = response['data']['payment']
    target = payment['target']

    payment_action = payment['action']
    if payment_action == 'charge':
        payment_action = 'charged'
    if payment_action == 'pay':
        payment_action = 'paid'

    amount = payment['amount']
    if target['type'] == 'user':
        user = "{first_name} {last_name}".format(
            first_name=target['user']['first_name'],
            last_name=target['user']['last_name'],
        )
    else:
        user = target[target['type']],
    note = payment['note']

    print 'Successfully {payment_action} {user} ${amount} for "{note}"'.format(
        payment_action=payment_action,
        user=user,
        amount=amount,
        note=note,
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers()

    for action in ["pay", "charge"]:
        subparser = subparsers.add_parser(action)
        subparser.add_argument("phone", help="who to {}".format(action))
        subparser.add_argument("amount", help="how much to pay or charge")
        subparser.add_argument("note", help="what the request is for")
        subparser.set_defaults(func=globals()[action])

    parser_refresh_token = subparsers.add_parser('refresh-token')
    parser_refresh_token.set_defaults(func=oauth.refresh_token)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
