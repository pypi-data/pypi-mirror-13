#!/usr/bin/env python
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#          - Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from odl.exceptions import ODL404, FlowNotFound

import re

class ODLFlow(object):
    """
    This class represents a switch table in OpenDayLight.
    """
    def __init__(self, xml, table):
        self.xml = xml
        self.table = table
        self.active = False

    def __repr__(self):
        return "<ODLFlow: %s>" % self.id

    @property
    def id(self):
        return self.xml['id']

    @property
    def clean_id(self):
        return str(re.sub(r'#|\$|-|\*','', self.id))


    @property
    def priority(self):
        return self.xml['priority']

    @property
    def idle_timeout(self):
        try:
            return self.xml['idle-timeout']
        except KeyError:
            return {}

    @property
    def name(self):
        try:
            return self.xml['flow-name']
        except KeyError:
            return ""

    @property
    def hard_timeout(self):
        try:
            return self.xml['hard-timeout']
        except KeyError:
            return {}

    @property
    def cookie(self):
        try:
            return self.xml['cookie']
        except KeyError:
            return {}

    def _get_flow_stats(self):
        """
        Return a dict with the flow statics when exists, if not return a empty
        dict.
        """
        try:
            return self.xml['opendaylight-flow-statistics:flow-statistics']
        except KeyError:
            return {}

    def _get_match(self):
        """
        Return the match fields of this flow.
        """
        try:
            return self.xml['match']
        except KeyError:
            return {}

    def _get_ethernet_match(self):
        """
        Return the ethernet match of this flow.
        """
        match = self._get_match()
        try:
            return match['ethernet-match']
        except KeyError:
            return {}

    def get_ethernet_type(self):
        ethernet_match = self._get_ethernet_match()
        try:
            return ethernet_match['ethernet-type']['type']
        except KeyError:
            return "*"

    def get_ethernet_source(self):
        ethernet_match = self._get_ethernet_match()
        try:
            return ethernet_match['ethernet-source']['address']
        except KeyError:
            return "*"

    def get_ethernet_destination(self):
        ethernet_match = self._get_ethernet_match()
        try:
            return ethernet_match['ethernet-destination']['address']
        except KeyError:
            return "*"

    def get_ipv4_source(self):
        match = self._get_match()
        try:
            return match['ipv4-source']
        except KeyError:
            return "*"

    def get_ipv4_destination(self):
        match = self._get_match()
        try:
            return match['ipv4-destination']
        except KeyError:
            return "*"

    def get_actions(self):
        try:
            actions = self.xml['instructions'].values()[0]
        except KeyError as e:
            actions = []

        result = []
        for action in actions:
            try:
                apply_action = action['apply-actions']['action'][0]
            except KeyError as e:
                continue
            action_type = apply_action.keys()[0]
            if action_type == 'output-action':
                value = apply_action[action_type]['output-node-connector']
                result.append({'type': action_type,
                               'value': value})

        return result

    def to_dict(self):
        base = {'priority': self.priority,
                'idle_timeout': self.idle_timeout,
                'hard_timeout': self.hard_timeout,
                'cookie': self.cookie,
                'name': self.name,
                'id': self.id,
                'node_id': self.table.node.id,
                'active': self.active,
                'table_id': self.table.id,
                'clean_id': self.clean_id,
                'ethernet_match': {'type': self.get_ethernet_type(),
                                   'source': self.get_ethernet_source(),
                                   'destination': self.get_ethernet_destination()},
                'ipv4_source': self.get_ipv4_source(),
                'ipv4_destination': self.get_ipv4_destination(),
                'actions': self.get_actions(),
                'stats': {'bytes': self.get_byte_count(),
                          'packets': self.get_packet_count()}}
        return base

    def get_long_id(self):
        """
        Return a long ID number.
        """
        return "%s-%s-%s-%s-%s-%s" % (self.table.node.id,
                                      self.table.id,
                                      self.id,
                                      self.priority,
                                      self.idle_timeout,
                                      self.hard_timeout)

    def get_stats_seconds(self):
        """
        Return the number of seconds in flow stats.
        """
        stats = self._get_flow_stats()
        try:
            return stats['duration']['second']
        except KeyError:
            return 0

    def get_byte_count(self):
        """
        Return the number of bytes that matches with this flow.
        """
        stats = self._get_flow_stats()
        try:
            return stats['byte-count']
        except KeyError:
            return None

    def get_packet_count(self):
        """
        Return the number of packets that matches with this flow.
        """
        stats = self._get_flow_stats()
        try:
            return stats['packet-count']
        except KeyError:
            return None

    def delete(self):
        """
        Delete a flow from config endpoint. We cannot delete flows in
        operational endpoint only.
        """
        odl_instance = self.table.node.odl_instance
        endpoint = self.table.config_endpoint + 'flow/' + self.id

        try:
            odl_instance.delete(endpoint)
        except ODL404:
            raise FlowNotFound("Flow id %s not found" % self.id)
