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

from odl.connector import ODLConnector
from odl.table import ODLTable
from odl.exceptions import TableNotFound, ConnectorNotFound

class ODLNode(object):
    """
    This class represents a node (or a switch) in OpenDayLight.
    """
    def __init__(self, xml, odl_instance):
        self.xml = xml
        self.odl_instance = odl_instance

    def __repr__(self):
        return "<ODLNode: %s>" % self.id

    @property
    def id(self):
        return self.xml['id']

    @property
    def description(self):
        try:
            return self.xml['flow-node-inventory:description']
        except KeyError as e:
            return None

    @property
    def ip_address(self):
        try:
            return self.xml['flow-node-inventory:ip-address']
        except KeyError as e:
            return None

    @property
    def manufacturer(self):
        try:
            return self.xml['flow-node-inventory:manufacturer']
        except KeyError as e:
            return None

    @property
    def serial_number(self):
        return self.xml['flow-node-inventory:serial-number']

    @property
    def hardware(self):
        try:
            return self.xml['flow-node-inventory:hardware']
        except KeyError as e:
            return None

    @property
    def software(self):
        try:
            return self.xml['flow-node-inventory:software']
        except KeyError as e:
            return None

    def to_dict(self):
        tables = self.get_tables().values()
        conns = self.get_connectors().values()
        base = {
                'id': self.id,
                'description': self.description,
                'ip_address': self.ip_address,
                'manufacturer': self.manufacturer,
                'hardware': self.hardware,
                'type': 'switch',
                'software': self.software,
                'tables': { table.id: table.to_dict() for table in tables},
                'connectors': {conn.id: conn.to_dict() for conn in conns}}

        return base

    def get_config_xml(self):
        config_nodes = self.odl_instance.config_xml['nodes']['node']
        for node in config_nodes:
            if node['id'] == self.id:
                return node
        return {}

    def get_tables(self):
        """
        Return a dict with all tables of this node.
        """
        tables = self.xml['flow-node-inventory:table']
        result = {}
        for table in tables:
            obj = ODLTable(table, self)
            result[obj.id] = obj
        return result

    def get_table_by_id(self, id):
        """
        Return a table based on id.
        """
        tables = self.get_tables()
        try:
            return tables[int(id)]
        except KeyError:
            raise TableNotFound("Table %s not found" % id)

    def get_connectors(self):
        """
        Return a dict with all connectors of this node.
        """
        try:
            connectors = self.xml['node-connector']
        except KeyError:
            print "Error, switch without connectors"
            print self.id, self.description, self.ip_address
            return {}
        result = {}
        for connector in connectors:
            obj = ODLConnector(connector, self)
            result[obj.id] = obj
        return result

    def get_connector_by_id(self, id):
        """
        Return a connector based on id.
        """
        connectors = self.get_connectors()
        try:
            return connectors[id]
        except KeyError:
            raise ConnectorNotFound("Connector %s not found" % id)

    def clear_flows(self):
        pass

    def delete_config_flows_by_name(self, name):
        """
        Return a list of config flows based on name.
        """
        tables = self.get_tables()
        for table in tables.values():
            flows = table.get_config_flows_by_name(name)
            for flow in flows:
                flow.delete()

    def add_flow(self, flow):
        pass
