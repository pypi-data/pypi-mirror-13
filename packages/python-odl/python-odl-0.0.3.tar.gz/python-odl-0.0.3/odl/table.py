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
#          - Artur Baruchi <abaruchi AT ncc DOT unesp DOT br>
#
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from odl.flow import ODLFlow
from odl.exceptions import ODL404, FlowNotFound
from of.flow import GenericFlow
from jinja2 import Template

import json
import os

class ODLTable(object):
    """
    This class represents a switch table in OpenDayLight.
    """
    def __init__(self, xml, node):
        self.xml = xml
        self.config_table = {}
        self.node = node

        base = "/restconf/operational/opendaylight-inventory:nodes"
        self.endpoint = "%s/node/%s/table/%s/" % (base,
                                                  self.node.id,
                                                  self.id)

        self.config_endpoint = self.endpoint.replace("operational",
                                                     "config")

        # Update table json
        #self.update()

    def __repr__(self):
        return "<ODLTable: %s>" % self.id

    @property
    def id(self):
        return self.xml['id']

    def _get_aggregate_stats(self):
        """
        Return a dict with the aggregate statistics when exists, if not return
        an empty dict
        """
        try:
            key = 'opendaylight-flow-statistics:aggregate-flow-statistics'
            return self.xml[key]
        except KeyError:
            return {}

    def get_config_xml(self):
        try:
            config_tables = self.node.get_config_xml()['flow-node-inventory:table']
            for table in config_tables:
                if table['id'] == self.id:
                    return table
            return {}
        except KeyError:
            return {}

    def to_dict(self):
        base = {'id':self.id,
                'flows': {flow.id: flow.to_dict() for flow in self.get_all_flows().values()}}
        return base

    def update(self):
        """
        Queries the server and retrieve a updated table.
        """
        odl_instance = self.node.odl_instance
        result = odl_instance.get(self.endpoint)
        self.xml = result['flow-node-inventory:table'][0]

        try:
            result = odl_instance.get(self.config_endpoint)
            self.config_table = result['flow-node-inventory:table'][0]
        except ODL404 as e:
            pass

    def get_operational_flows(self):
        """
        Return a dict with all flows in operational endpoint (in this table).
        """
        try:
            flows = self.xml['flow']
        except KeyError:
            flows = []

        result = {}
        for flow in flows:
            obj = ODLFlow(flow, self)
            result[obj.id] = obj
        return result

    def get_aggregate_byte(self):
        """
        Return the number of aggregate byte count for a table
        """
        stats = self._get_aggregate_stats()
        try:
            return stats['byte-count']
        except KeyError:
            return None

    def get_aggregate_packets(self):
        """
        Returns the number of aggregate packets for a table
        """
        stats = self._get_aggregate_stats()
        try:
            return stats['packet-count']
        except KeyError:
            return None

    def get_config_flows(self):
        """
        Return a dict with all flows in config endpoint (in this table).
        """
        try:
            flows = self.get_config_xml()['flow']
        except KeyError:
            flows = []

        result = {}
        for flow in flows:
            obj = ODLFlow(flow, self)
            result[obj.id] = obj
        return result

    def get_all_flows(self):
        """
        Return a list with operational and config flows. Operational flows has
        the flag active to true.
        """
        operational = self.get_operational_flows()
        all_flows = self.get_config_flows()
        for flow in operational.values():
            if not all_flows.has_key(flow.id):
                flow.active = True
                all_flows[flow.id] = flow
            else:
                all_flows[flow.id].active = True
        return all_flows

    def get_flow_by_id(self, id):
        """
        Return a flow from this table, based on id.
        """
        # For now, this is only used in config context.
        flows = self.get_config_flows()
        try:
            return flows[id]
        except KeyError:
            raise FlowNotFound("Flow id %s not found" % id)

    def get_flow_by_clean_id(self, clean_id):
        flows = self.get_config_flows()
        for flow in flows.values():
            if flow.clean_id == clean_id:
                return flow

        # Try to get in operational flows
        flows = self.get_operational_flows()
        for flow in flows.values():
            print flow.clean_id, clean_id
            if flow.clean_id == clean_id:
                return flow

    def get_config_flows_by_name(self, name):
        """
        Return a list of config flows based on name.
        """
        result = []
        flows = self.get_config_flows()
        for flow in flows.values():
            if flow.name == name:
                result.append(flow)

        return result

    def put_flow_from_data(self, data, flow):
        """
        Insert a flow in this table (config endpoint) based on raw xml data.
        """
        odl_instance = self.node.odl_instance
        endpoint = self.config_endpoint + 'flow/' + str(flow.id)
        return odl_instance.put(endpoint,
                                data=data,
                                content="application/xml")

    def put_flow_from_template(self, filename, flow):
        """
        This methods reads a XML jinja2 template and parse-it before sending to
        ODL.
        """
        with open(filename, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow)
            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def l2output(self, flow_name, connector_id, source, destination, template_dir):
        """
        This methods insert a flow using source MAC address and destination MAC
        address as match fields.

        connector_id must be a valid ID of the node of this table.
        """
        tpl = os.path.join(template_dir, 'l2output.tpl')

        connector = self.node.get_connector_by_id(connector_id)

        flow = GenericFlow(name = flow_name, table = self)

        with open(tpl, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow,
                                     source = source,
                                     destination = destination,
                                     connector = connector)

            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def l3output(self, flow_name, connector_id, source, destination, template_dir):
        """
        This methods insert a flow using source address and destination address
        as match fields (both in ipv4).

        connector_id must be a valid ID of the node of this table.
        """
        tpl = os.path.join(template_dir, 'l3output.tpl')

        connector = self.node.get_connector_by_id(connector_id)

        flow = GenericFlow(name = flow_name, table = self)

        with open(tpl, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow,
                                     source = source,
                                     destination = destination,
                                     connector = connector)

            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def install_flow(self, priority, name, eth_type, eth_source,
                     eth_destination,  ipv4_source, ipv4_destination,
                     connector_id, template_dir):

        tpl = os.path.join(template_dir, 'complete.tpl')
        flow = GenericFlow(name = name,
                           table = self,
                           priority = priority)

        with open(tpl, 'r') as f:
            template = Template(f.read())
            parsed = template.render(flow = flow,
                                     eth_type = eth_type,
                                     eth_source = eth_source,
                                     eth_destination = eth_destination,
                                     ipv4_source = ipv4_source,
                                     ipv4_destination = ipv4_destination,
                                     connector_id = connector_id)

            print parsed
            return self.put_flow_from_data(data = parsed,
                                           flow = flow)

    def delete_low_priority_flows(self, priority = 100):
        """
        This method will delete all flows on this table (config endpoint), but
        only with low priority. Default is 100.
        """
        flows = self.get_config_flows()
        for flow in flows.values():
            if flow.priority <= priority:
                flow.delete()

    def delete_flows(self):
        """
        Delete all flows in this table (config endpoint).
        """
        flows = self.get_config_flows()
        for flow in flows.values():
           flow.delete()
