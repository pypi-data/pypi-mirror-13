# This file has been generated at Fri Jul 24 16:30:27 2015

from openalea.core import CompositeNodeFactory as CNF

__name__ = '__my package__'

__editable__ = True
__description__ = ''
__license__ = ''
__url__ = ''
__alias__ = []
__version__ = ''
__authors__ = ''
__institutes__ = ''
__icon__ = ''

__all__ = ['test']


test = CNF(name='test',
           description='simple workflow to execute',
           category='experimental hardcore',
           doc='',
           inputs=[
               {'desc': '', 'interface': None, 'name': 'IN1', 'value': None},
               {'desc': '', 'interface': None, 'name': 'IN2', 'value': None}],
           outputs=[
               {'desc': '', 'interface': None, 'name': 'OUT1'},
               {'desc': '', 'interface': None, 'name': 'OUT2'}],
           elt_factory={2: ('scifloware', 'simple_test')},
           elt_connections={42766488L: (2, 0, '__out__', 0),
                            42766512L: ('__in__', 1, '__out__', 1),
                            42766632L: ('__in__', 0, 2, 0),
                            42766633L: ('__in__', 1, 2, 1)},
           elt_data={2: {'block': False,
                         'caption': 'toto',
                         'delay': 0,
                         'hide': True,
                         'id': 2,
                         'lazy': True,
                         'port_hide_changed': set([]),
                         'posx': -167,
                         'posy': -136,
                         'priority': 0,
                         'use_user_color': False,
                         'user_application': None,
                         'user_color': None},
                     '__in__': {'block': False,
                                'caption': 'In',
                                'delay': 0,
                                'hide': True,
                                'id': 0,
                                'lazy': True,
                                'port_hide_changed': set([]),
                                'posx': 25,
                                'posy': -102,
                                'priority': 0,
                                'use_user_color': False,
                                'user_application': None,
                                'user_color': None},
                     '__out__': {'block': False,
                                 'caption': 'Out',
                                 'delay': 0,
                                 'hide': True,
                                 'id': 1,
                                 'lazy': True,
                                 'port_hide_changed': set([]),
                                 'posx': -81,
                                 'posy': 120,
                                 'priority': 0,
                                 'use_user_color': False,
                                 'user_application': None,
                                 'user_color': None}
                     },
           elt_value={2: [(0, 1), (1, 2)],
                      '__in__': [],
                      '__out__': []},
           elt_ad_hoc={2: {'position': [-167, -136],
                           'userColor': None,
                           'useUserColor': False},
                       '__in__': {
                           'position': [25, -102],
                           'userColor': None,
                           'useUserColor': False},
                       '__out__': {
                           'position': [-81, 120],
                           'userColor': None,
                           'useUserColor': False}
                       },
           lazy=True,
           eval_algo='LambdaEvaluation',
           )
