"""
Prints stats on what percentage of try pushes are being scheduled with various
different mechanisms over the last week. The date range can be modified the
same as the `hours_on_try` recipe.

.. code-block:: bash

    adr try_usage

`View Results <https://mozilla.github.io/active-data-recipes/#try-usage>`__
"""
from __future__ import print_function, absolute_import

from collections import defaultdict, OrderedDict

from ..recipe import RecipeParser
from ..query import run_query


def subcommand(name):
    return {
        name: {
            'test': 'Pushed via `mach try {}`'.format(name),
            'method': 'mach try {}'.format(name),
        }
    }


def run(args, config):
    parser = RecipeParser('date')
    args = parser.parse_args(args)

    query_args = vars(args)
    data = next(run_query('try_commit_messages', config, **query_args))['data']

    count = defaultdict(int)
    count['total'] = len(data['message'])

    users = defaultdict(set)
    users['total'] = set(data['user'])

    # Order is important as the search stops after the first successful test.
    d = OrderedDict()
    d.update(subcommand('syntax'))
    d['vanilla'] = {
        'test': 'try:',
        'method': 'vanilla try syntax',
    }
    d.update(subcommand('fuzzy'))
    d.update(subcommand('again'))
    d.update(subcommand('empty'))
    d.update(subcommand('release'))
    d['other'] = {
        'test': '',
        'method': 'other',
    }
    d['total'] = {
        'test': None,
        'method': 'total',
    }

    data = zip(data['user'], data['message'])
    for user, message in data:
        for k, v in d.items():
            if v['test'] in message:
                count[k] += 1
                users[k].add(user)
                break

    def fmt(key):
        percent = round(float(count[key]) / count['total'] * 100, 1)
        return [d[key]['method'], count[key], percent, len(users[key]), round(float(count[key]) / len(users[key]), 2)]  # noqa

    data = [['Method', 'Pushes', 'Percent', 'Users', 'Push / User']]
    for k, v in sorted(count.items(), key=lambda t: t[1], reverse=True):
        data.append(fmt(k))
    return data
