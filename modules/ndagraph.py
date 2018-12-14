#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# ndagraph.py

# Import Modules
import pydot
import re

def networkgraph(topologyfile,topologyname, networkgraphlist, fullinventorylist, l2interfacelist, l3interfacelist):
	# Create lists
	duplicatelink = []
	dupdetect = []
	# Pydot base configuration
	graph = pydot.Dot(graph_type='digraph')	
	# Create all primary network devices
	for device in networkgraphlist:
		# Get device information
		devicehostname = device['hostname']
		deviceipaddress = device['ip']
		# Duplicate detect
		for dupdev in dupdetect:
			if dupdev == devicehostname:
				continue
		# Get device model
		stackv = 0
		stackinv = []
		devicemodellist = filter(lambda x: x['Hostname'] == devicehostname, fullinventorylist)
		# Chassis
		for modeldict in devicemodellist:
			if re.match('.*[Cc]hassis$',modeldict['Description']):
				if modeldict['Stack Number'] == '':
					devicemodel = modeldict['Product ID']
					break
				else:
					stackv = 1
					stackinv.append('(' + modeldict['Stack Number'] + ') ' +  modeldict['Product ID'])
		if stackv == 1:
			# convert list of switches (if stacked) into a format for the label
			devicemodel = '\n'.join(stackinv)
		# Create device label
		devicelabel = devicehostname + '\n' + devicemodel + '\n' + 'ip:' + deviceipaddress
		# Add node to graph	
		node = pydot.Node(devicehostname, label=(devicelabel))
		graph.add_node(node)
		dupdetect.append(devicehostname)
	# Create all secondary network devices
	for device in networkgraphlist:
		deviceneighborlist = device['neighbors']
		for neighbor in deviceneighborlist:
			deviceneighbor = neighbor['neighbor']
			sourceinterface = neighbor['sourceinterface']
			destinationinterface = neighbor['destinationinterface']
			deviceneighborip = neighbor['ip']
			deviceneighbordevice = neighbor['device']
			# Create secondary devices and attach information about them
			skipcreation = 0
			# Dup Detect
			for dupdev in dupdetect:
				if dupdev == deviceneighbor:
					skipcreation = 1
					break
			if skipcreation == 0:
				devicelabel = deviceneighbor + '\n' + deviceneighbordevice + '\n' + 'ip:' + deviceneighborip
				node = pydot.Node(deviceneighbor, label=(devicelabel))
				graph.add_node(node)
				dupdetect.append(deviceneighbor)
	# Create all network device relationships
	for device in networkgraphlist:
		devicehostname = device['hostname']
		deviceneighborlist = device['neighbors']
		for neighbor in deviceneighborlist:
			deviceneighbor = neighbor['neighbor']
			sourceinterface = neighbor['sourceinterface']
			destinationinterface = neighbor['destinationinterface']
			deviceneighborip = neighbor['ip']
			deviceneighbordevice = neighbor['device']
			# Bidirectional link detection
			bidilinksource = filter(lambda x: x['source'] == deviceneighbor, duplicatelink)
			bidilinkdest = filter(lambda x: x['destination'] == devicehostname, bidilinksource)
			# if no bidirectional link found, create link
			if bidilinkdest == []:
				# Add link to duplicate list
				duplicatedict = {}
				duplicatedict['source'] = devicehostname
				duplicatedict['destination'] = deviceneighbor
				duplicatelink.append(duplicatedict)
				# Add edge node
				edge = pydot.Edge(devicehostname,deviceneighbor,color='#FF0000',label=('s:' + sourceinterface + '\n' + 'd:' + destinationinterface), fontcolor='#0000FF', fontsize=8)
				graph.add_edge(edge)
	# Create final drawing
	graph.write_pdf(topologyfile)
			