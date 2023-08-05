#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2014, vdnguyen <vanduc.nguyen@savoirfairelinux.com>

from __future__ import unicode_literals, division

import codecs
import json
import urllib
import sys

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from shinkenplugins.old import BasePlugin
from shinkenplugins.perfdata import PerfData
from shinkenplugins.states import STATES


class Plugin(BasePlugin):
    NAME = 'check-snow-clearance'
    VERSION = '0.1'
    DESCRIPTION = 'check the number of clear street'
    AUTHOR = 'vdnguyen'
    EMAIL = 'vanduc.nguyen@savoirfairelinux.com'

    ARGS = [('h', 'help', 'display plugin help', False),
            ('v', 'version', 'display plugin version number', False),
            ('w', 'warning', 'Limit to result in a warning state', True),
            ('c', 'critical', 'Limit to result in a critical state', True),
            ('l', 'boroughs_list', 'List of all boroughs', False),
            ('b', 'borough', 'Borough to check', True),
            ]

    @staticmethod
    def get_boroughs_list():
        # get list of all boroughs
        url = "http://infoneige.ca/vdm/stats.json"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        boroughs = data["avancement"]
        boroughs_list = []

        for i in boroughs:
            borough = i["arrondissment"].replace(' ', '')
            boroughs_list.append(borough)

        return boroughs_list

    def check_args(self, args):
        boroughs_list = Plugin.get_boroughs_list()
        # if -l in args print list of valid boroughs

        if "boroughs_list" in args:
            # Handle show region list
            output = "\n".join(boroughs_list)
            # Exit showing region list
            self.exit(STATES.UNKNOWN, 'boroughs:\n' + output)

        if "borough" not in args:
            self.exit(STATES.UNKNOWN, 'Borough argument is missing')
        # check if user enter the valid borough
        if args['borough'].decode("utf8") not in boroughs_list:
            # Handle show region list
            output = "\n".join(boroughs_list) + "\n" + "Borough %r unknown" % args['borough']
            # Exit showing region list
            self.exit(STATES.UNKNOWN, 'boroughs:\n' + output)

        # Check critical argument
        if 'critical' not in args:
            self.exit(STATES.UNKNOWN, 'Critical argument is missing')
        # Check warning argument
        if 'warning' not in args:
            self.exit(STATES.UNKNOWN, 'Warning argument is missing')

        if args.get("warning"):
            warning = args.get("warning")
            if not warning.isdigit():
                self.exit(STATES.UNKNOWN, "Enter warning argument in integer")

        # handle non digital critical argument
        if args.get("critical"):
            warning = args.get("critical")
            if not warning.isdigit():
                self.exit(STATES.UNKNOWN, "Enter critical argument in integer")

        return True, None

    def run(self, args):
        clearance_percent = 0
        planned_percent = 0
        in_action_percent = 0
        without_info_percent = 0
        state = None
        message = None

        # get json data from "http://infoneige.ca/vdm/stats.json"
        url = "http://infoneige.ca/vdm/stats.json"
        response = urllib.urlopen(url)
        json_data = json.loads(response.read())
        # get warning and critical from args
        warning = float(args["warning"])
        critical = float(args["critical"])
        # get borough from args to compare to get the right borough
        input_borough = args["borough"]
        input_borough = input_borough.decode("utf8")

        borough = json_data["avancement"]
        for i in borough:
            if input_borough == i["arrondissment"].replace(' ', ''):
                # get all data
                non_clear = float(i[u"enneigé"])
                clear = float(i[u"déneigé"])
                planned = float(i[u"planifié"])
                in_action = float(i[u"en cours"])
                without_info = float(i[u"pas d info"])
                # calculate the total of streets sides in one borough
                total = non_clear + clear + planned + in_action
                # calculate the total included without info
                total_without_info = total + without_info
                # calculate all data in percentage
                if total:
                    clearance_percent = (clear / total) * 100.0
                    planned_percent = (planned / total) * 100.0
                    in_action_percent = (in_action / total) * 100.0
                else:
                    clearance_percent = 100
                    planned_percent = 0
                    in_action_percent = 0
                if total_without_info:
                    without_info_percent = (without_info / total_without_info) * 100.0
                else:
                    without_info_percent = 100

                if clearance_percent < critical:
                    message = ("CRITICAL: %0.1f%% in '%s' is clear"
                               % (clearance_percent, input_borough))
                    state = STATES.CRITICAL
                elif clearance_percent <= warning:
                    message = ("WARNING: %0.1f%% in '%s' is clear"
                               % (clearance_percent, input_borough))
                    state = STATES.WARNING
                else:
                    message = ("OK: %0.1f%% in '%s' is clear"
                               % (clearance_percent, input_borough))
                    state = STATES.OK

        clearance_percent = "%0.1f" % clearance_percent
        planned_percent = "%0.1f" % planned_percent
        in_action_percent = "%0.1f" % in_action_percent
        without_info_percent = "%0.1f" % without_info_percent

        p1 = PerfData("clearance_percent",
                      clearance_percent,
                      unit="%",
                      warn=warning,
                      crit=critical,
                      min_="0.0",
                      max_=100.0)
        p2 = PerfData("planned_percent",
                      planned_percent,
                      unit="%",
                      warn=warning,
                      crit=critical,
                      min_="0.0",
                      max_=100.0)
        p3 = PerfData("in_action_percent",
                      in_action_percent,
                      unit="%",
                      warn=warning,
                      crit=critical,
                      min_="0.0",
                      max_=100.0)
        p4 = PerfData("without_info_percent",
                      without_info_percent,
                      unit="%",
                      warn=warning,
                      crit=critical,
                      min_="0.0",
                      max_=100.0)

        self.exit(state, message, p1, p2, p3, p4)


def main(argv=None):
    Plugin()


if __name__ == "__main__":
    main()
