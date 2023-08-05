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

import json
import sys

import networkx as nx

class ODLTopology(object):
    def __init__(self, server, credentials, odl_instance):
        self.server = server
        self.credentials = credentials
        self.odl_instance = odl_instance
        self.headers = { 'Content-type' : 'application/json' }

    def get_topology(self):
        endpoint = "/restconf/operational/network-topology:network-topology/"

        result = self.odl_instance.get(endpoint)

        return result['network-topology']['topology'][0]

    def get_nodes(self):
        topology = self.get_topology()
        nodes = topology['node']
        result = {}
        for node in nodes:
            node['id'] = node['node-id']
            result[node['node-id']] = node

        return result

    def get_links(self):
        topology = self.get_topology()
        try:
            links = topology['link']
        except KeyError as e:
            links = []

        result = {}
        for link in links:
            result[link['link-id']] = link

        return result

    def get_networkx_graph(self):
        graph = nx.Graph()

        data = self.odl_instance.to_dict()

        # When adding an edge to the graph the node it will be added
        # automatically.
        for link in data['links']:
            graph.add_edge(link['source'], link['target'])

        return graph
