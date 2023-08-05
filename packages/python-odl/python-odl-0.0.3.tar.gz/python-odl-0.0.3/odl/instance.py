"""
This is the ODLInstance module. This has the classes to handle a OpenDayLight
instance. When we talk "instance", we are referring to ODL daemon that is
running on your infrastructure.

This code was tested with ODL Lithium release and uses the REST API provided by
restconf endpoints.
"""

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

from odl.flow import ODLFlow
from odl.node import ODLNode
from odl.table import ODLTable
from odl.topology import ODLTopology

from odl.exceptions import *

#from odl import log

import json
import sys
import requests


class ODLInstance(object):
    """
    This is the first class that you should instanciate in your code. This
    represents the ODL Instance, and any request it will be done on this class.

    You need to specify the server that you are trying to connect and your
    credentials.

    """
    def __init__(self, server, credentials):
        self.server = server
        self.credentials = credentials
        self.headers = { 'Content-type' : 'application/json' }
        self.topology = ODLTopology(self.server, self.credentials, self)

        self.update_xml()

    def to_dict(self):
        """
        This method return a dictionary with important attributes of a ODL
        Instance. This is useful and is a preparation to export data to JSON
        format.
        """
        # TODO: Split this method into small methods

        # All switches nodes in dict format
        base = {'nodes': {} }
        for node in self.get_nodes().values():
            base['nodes'][node.id] = node.to_dict()

        # These nodes and links are from ODL topology plugin.
        topology_nodes = self.topology.get_nodes()
        topology_links = self.topology.get_links()

        # if a node is not in base['nodes'], then append.
        for node in topology_nodes.values():
            node_id = node['node-id']
            if ((node_id.split(":")[0] == "host") and
                (not base['nodes'].has_key(node_id))):
                node['type'] = 'host'
                base['nodes'][node_id] = node

        # create links (base['links'] = [] with source and target
        base['links'] = []

        for node in topology_nodes.values():
            node_id = node['node-id']
            node_type = node_id.split(":")[0]
            if (node_type == "openflow"):
                # Get the termination points. Here we have Switch to port links
                try:
                    for tp in node['termination-point']:
                        tp_id = tp['tp-id']
                        node_object = self.get_node_by_id(node_id)
                        connector = node_object.get_connector_by_id(tp_id)
                        base['nodes'][tp_id] = connector.to_dict()
                        base['links'].append({'source': node_id,
                                              'target': tp_id,
                                              'type': 'port'})
                except KeyError as e:
                    pass

            elif (node_type == "host"):
                # Get the attachment points. Here we have Host to port links
                for ap in node['host-tracker-service:attachment-points']:
                    tp_id = ap['tp-id']
                    base['links'].append({'source': node_id,
                                          'target': tp_id,
                                          'type': 'host'})


        # Create the port 2 port links
        for link in topology_links.values():
            source = link['source']['source-tp']
            target = link['destination']['dest-tp']
            s_type = source.split(":")[0]
            t_type = target.split(":")[0]
            if ((s_type == "openflow") and (t_type == "openflow")):
                # This is a link between two ports (switch - switch)
                base['links'].append({'source': source,
                                      'target': target,
                                      'type': 'link'})
        ## Now, creat our port-switch links
        #for node in base['nodes']:
        #    id = node.keys()[0]
        #    connectors = node[id]['connectors']
        #    for connector in connectors:
        #        connector_id = connector.keys()[0]
        #        connector_nodes.append({connector_id: connector[connector_id]})
        #        port = connector[connector_id]['port_number']
        #        base['links'].append({'source': id, 'target': connector_id})
        #
        ## Extends nodes to include the connector_nodes
        #base['nodes'].extend(connector_nodes)

        return base

    def request(self, method, endpoint, auth, data=None, content=None):
        """
        Tries to connect to the endpoint using a given method
        PUT, GET or DELETE. Return the response code.
        """
        if content:
            headers = {'Content-type': content}
        else:
            headers = self.headers

        if method == "GET":
            try:
                response = requests.get(endpoint,
                                        headers = headers,
                                        auth = auth)
            except requests.exceptions.RequestException as e:
                raise ODLErrorOnGET(e)
        elif method == "PUT":
            try:
                response = requests.put(endpoint,
                                        headers = headers,
                                        data = data,
                                        auth = auth)
            except requests.exceptions.RequestException as e:
                raise ODLErrorOnPUT(e)
        elif method == "DELETE":
            try:
                response = requests.delete(endpoint,
                                           headers = headers,
                                           auth = auth)
            except requests.exceptions.RequestException as e:
                raise ODLErrorOnDELETE(e)
        else:
            raise NotImplemented("Method %s not implemented." % method)

        if response.status_code == 404:
            raise ODL404("Endpoint not found: %s" % self.server + endpoint)

        # Consider any status other than 2xx an error
        if not response.status_code // 100 == 2:
            raise UnexpectedResponse(format(response))

        #log.info("ODLInstance: %s %s" % (method, endpoint))
        return response

    def get(self, endpoint):
        """
        Requests a GET to endpoint and returns the json.
        """
        response = self.request(method = "GET",
                                endpoint = self.server + endpoint,
                                auth = self.credentials)
        return json.loads(response.text)

    def put(self, endpoint, data, content="application/json"):
        """
        Sends data via PUT to endpoint.
        """
        response = self.request(method = "PUT",
                                endpoint = self.server + endpoint,
                                data = data,
                                auth = self.credentials,
                                content = content)

    def delete(self, endpoint):
        """
        Sends a DELETE to endpoint.
        """
        response = self.request(method = "DELETE",
                                endpoint = self.server + endpoint,
                                auth = self.credentials)

    def update_xml(self):
        endpoint = "/restconf/operational/opendaylight-inventory:nodes/"
        # Default xml is operational
        self.xml = self.get(endpoint)
        config_endpoint = "/restconf/config/opendaylight-inventory:nodes/"
        try:
            self.config_xml = self.get(config_endpoint)
        except ODL404:
            self.config_xml = {}

    def get_nodes(self):
        nodes = self.xml['nodes']['node']
        result = {}
        for node in nodes:
            obj = ODLNode(node, self)
            result[obj.id] = obj
        return result

    def get_node_by_id(self, id):
        nodes = self.get_nodes()
        try:
            return nodes[id]
        except KeyError:
            raise NodeNotFound("Node %s not found" % id)

    def get_connector_by_id(self, id):
        nodes = self.get_nodes()
        for node in nodes.values():
            connector = node.get_connector_by_id(id)
            if connector and connector.id == id:
                return connector
        return None
