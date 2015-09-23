#!/usr/bin/python
#
# eddb.io station database
#

import cPickle
import os
from os.path import dirname, join, normpath
import sys
from sys import platform

class EDDB:

    def __init__(self):
        self.system_ids  = cPickle.load(open(join(self.respath(), 'systems.p'),  'rb'))
        self.station_ids = cPickle.load(open(join(self.respath(), 'stations.p'), 'rb'))

    # system_name -> system_id or 0
    def system(self, system_name):
        return self.system_ids.get(system_name, 0)	# return 0 on failure (0 is not a valid id)

    # (system_name, station_name) -> (station_id, has_shipyard) or None
    def station(self, system_name, station_name):
        return self.station_ids.get((self.system_ids.get(system_name), station_name))

    def respath(self):
        if getattr(sys, 'frozen', False):
            if platform=='darwin':
                return normpath(join(dirname(sys.executable), os.pardir, 'Resources'))
            else:
                return dirname(sys.executable)
        elif __file__:
            return dirname(__file__)
        else:
            return '.'


# build system & station database from files systems.json and stations_lite.json from http://eddb.io/api
if __name__ == "__main__":
    import json

    # system_name by system_id
    systems  = dict([(x['id'], str(x['name'])) for x in json.loads(open('systems.json').read())])

    stations = json.loads(open('stations_lite.json').read())

    # check that all populated systems have known coordinates
    coords = dict([(x['id'], x['x'] or x['y'] or x['z']) for x in json.loads(open('systems.json').read())])
    for x in stations:
        assert x['system_id'] == 17072 or coords[x['system_id']], (x['system_id'], systems[x['system_id']])

    # system_id by system_name - populated systems only
    system_ids = dict([(systems[x['system_id']], x['system_id']) for x in stations])
    cPickle.dump(system_ids,  open('systems.p',  'wb'), protocol = cPickle.HIGHEST_PROTOCOL)

    # station_id by (system_id, station_name)
    station_ids = dict([((x['system_id'], str(x['name'])), (x['id'],bool(x['has_shipyard']))) for x in stations])
    cPickle.dump(station_ids, open('stations.p', 'wb'), protocol = cPickle.HIGHEST_PROTOCOL)
