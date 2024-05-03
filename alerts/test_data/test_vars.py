"""Test variables."""

import pandas as pd

OUTPUT_AFTER_PROCESSING_XML = {'created_at': '2024-04-24T06:32:48.156Z',
                               'last_updated': '2024-04-24T06:59:20.130Z',
                               'operator_ref': ['VT'],
                               'operator_name': ['Avanti West Coast'],
                               'incident_number': 'DBE6100D741A4833932F597AFAFBDF86',
                               'start_time': '2024-04-24T07:32:00.000+01:00',
                               'end_time': None, 'planned': 'false',
                               'cleared': 'false', 'info_link': 'Link',
                               'routes_affected': 'Routes', 'incident_priority': '1',
                               'summary': 'Major disruption at Birmingham New Street expected until 12:00'}

OUTPUT_AFTER_REPLACE = {'created_at': ['2024-04-24T06:32:48.156Z'],
                        'last_updated': ['2024-04-24T06:59:20.130Z'],
                        'operator_ref': ['VT'],
                        'operator_name': ['Avanti West Coast'],
                        'incident_number': ['DBE6100D741A4833932F597AFAFBDF86'],
                        'start_time': ['2024-04-24T07:32:00.000+01:00'],
                        'end_time': [None], 'planned': ['false'],
                        'info_link': ['Link'],
                        'routes_affected': ['Routes'],
                        'incident_priority': ['1'],
                        'summary':
                        ['Major disruption at Birmingham New Street expected until 12:00'],
                        'description': ['A description.']}

TIMESTAMP_WITH_END_TIME = {
    'created_at': ['2024-04-05T14:46:53.097Z'],
    'last_updated': ['2024-04-05T14:46:53.097Z'],
    'start_time': ['2024-04-27T00:00:00.000+01:00'],
    'end_time': ['2024-04-28T23:59:00.000+01:00']
}

TIMESTAMP_WITHOUT_END_TIME = {
    'created_at': ['2024-04-05T14:46:53.097Z'],
    'last_updated': ['2024-04-05T14:46:53.097Z'],
    'start_time': ['2024-04-27T00:00:00.000+01:00'],
    'end_time': [None]
}

TIMESTAMP_OUTPUT_1 = {'created_at':
                      [pd.Timestamp(
                          '2024-04-05 15:46:53.097000+0100',
                          tz='Europe/London')],
                      'last_updated':
                      [pd.Timestamp(
                          '2024-04-05 15:46:53.097000+0100',
                          tz='Europe/London')],
                      'start_time':
                      [pd.Timestamp('2024-04-27 00:00:00+0100',
                                    tz='Europe/London')],
                      'end_time':
                      [pd.Timestamp('2024-04-28 23:59:00+0100',
                                    tz='Europe/London')]}


TIMESTAMP_OUTPUT_2 = {'created_at':
                      [pd.Timestamp(
                          '2024-04-05 15:46:53.097000+0100',
                          tz='Europe/London')],
                      'last_updated':
                      [pd.Timestamp(
                          '2024-04-05 15:46:53.097000+0100',
                          tz='Europe/London')],
                      'start_time':
                      [pd.Timestamp('2024-04-27 00:00:00+0100',
                                    tz='Europe/London')],
                      'end_time': [None]}
