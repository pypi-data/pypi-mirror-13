#!/usr/bin/env python

import re,os

import treelib_adapter as Tree
import arguments as Arguments
from constants import ROOT, PORT
from constants import QUERY_DELIMITER as query_delimiter
from constants import HEADER_DELIMITER as header_delimiter
from constants import EXP_REQUEST, EXP_RESPONSE, EXP_METHOD, EXP_PATH, EXP_QUERY, EXP_HEADERS, EXP_BODY, EXP_STATUS_CODE

class Request:
    def __init__(self, port, method, path, query, headers, body):
        self.port = port
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body
    
    def toString(self):
        request = "PORT: "+self.port + ">> " + self.method.upper()+" " + self.path
        if not self.path:
            request += "/"
        if self.query:
            request += "?"+self.query
        if self.headers:
            request += " | HEADERS: "+self.headers
        if self.body:
            request += " | BODY: "+self.body
        return request

def createTree():
    return Tree.createTree()
    
def addNodeToTree(tree, content, nodeId, parentId, nodeInfo):
    return Tree.addNodeToTree(tree, content, nodeId, parentId, nodeInfo)

def addLeafNodeToTree(tree, content, nodeId, parentId, nodeInfo):
    return Tree.addLeafNodeToTree(tree, content, nodeId, parentId, nodeInfo)
    
def display(tree):
    Tree.display(tree)

def getNodeFromTreeById(node_id, tree):
    return Tree.getNodeFromTreeById(node_id, tree)

def getTagForNode(node):
    return Tree.getTagForNode(node)
    
def getIdForNode(node):
    return Tree.getIdForNode(node)

def getDirectChildrenForNode(node, tree, nodeInfo=None):
    return Tree.getDirectChildrenForNode(node, tree, nodeInfo)
    
def populateExpectations(tree, file_name, port_number, expectations):
    if not tree:
        tree = createTree()
    tree = addNodeToTree(tree, port_number, port_number, ROOT, PORT)
    
    for expectation in expectations:
        request_parameters = expectations.get(expectation).get(EXP_REQUEST)
        if request_parameters is None:
            request_parameters = {}
        parent = port_number
    
        method = request_parameters.get(EXP_METHOD)
        if method is None:
            method = "GET"
        node_id = parent+":"+method
        tree = addNodeToTree(tree, method, node_id, parent, EXP_METHOD)
        parent = node_id
        
        path = request_parameters.get(EXP_PATH)
        if path is None:
            path = "/"
        node_id = parent+">"+path
        tree = addNodeToTree(tree, path, node_id, parent, EXP_PATH)
        parent = node_id
        
        queryList = request_parameters.get(EXP_QUERY)
        if queryList is not None:
            queryList.sort()
            query = query_delimiter.join(queryList)
            node_id = parent+"?"+query
            tree = addNodeToTree(tree, query, node_id, parent, EXP_QUERY)
            parent = node_id

        headersList = request_parameters.get(EXP_HEADERS)
        if headersList is not None:
            headersList.sort()
            headers = header_delimiter.join(headersList)
            node_id = parent+"|"+headers
            tree = addNodeToTree(tree, headers, node_id, parent, EXP_HEADERS)
            parent = node_id
        
        requestBody = request_parameters.get(EXP_BODY)
        if requestBody is not None:
            node_id = parent+"|"+requestBody
            tree = addNodeToTree(tree, requestBody, node_id, parent, EXP_BODY)
            parent = node_id

        response = expectations.get(expectation).get(EXP_RESPONSE)
        if response is None:
            response = {EXP_STATUS_CODE:200}
            
        tree = addLeafNodeToTree(tree, response, file_name+":"+port_number+"/"+expectation, parent, EXP_RESPONSE)
    return tree

def forwardMatchNodes(nodes, value):
    matching_nodes = []
    for node in nodes:
        if re.match('^'+getTagForNode(node)+'$', value, re.IGNORECASE):
            matching_nodes.append(node)
    return matching_nodes

def reverseMatchNodes(nodes, value):
    matching_nodes = []
    for node in nodes:
        node_tag = getTagForNode(node)
        expected, actual, counter = node_tag.split(header_delimiter), value.split(header_delimiter), 0

        for exp in expected:
            matches = False
            for act in actual:
                if re.match('^'+exp+'$', act, re.IGNORECASE):
                    matches = True
                    break
            if matches:
                counter += 1
        
        if len(expected) == counter:
            matching_nodes.append(node)
    return matching_nodes

def getDirectChildrenForNodeList(nodes, tree, node_info):
    all_children = []
    for node in nodes:
        for children in getDirectChildrenForNode(node, tree, node_info):
            all_children.append(children)
    return all_children

def getNodesThatMatchRequestComponent(nodes, component, value, tree, reverse_match=False):
    nodes_for_matching = getDirectChildrenForNodeList(nodes, tree, component)
    
    if nodes_for_matching:
        nodes_that_match = []
        if reverse_match:
            nodes_that_match = reverseMatchNodes(nodes_for_matching, value)
        else:    
            nodes_that_match = forwardMatchNodes(nodes_for_matching, value)
        
        if nodes_that_match:
            nodes = nodes_that_match
        else:
            nodes = filter(lambda x:x not in set(nodes_that_match), nodes)
    return nodes

def getResponseFromExpectations(tree, request): 
    print "Finding response for request {" + request.toString() + "}"
    port, method, path, query, headers, body = request.port, request.method, request.path, request.query, request.headers, request.body
    query = query_delimiter.join(sorted(query.split(query_delimiter)))

    nodes = []
    if tree.contains(port):
        nodes = [getNodeFromTreeById(port, tree)]
    print "Port: ["+port+"] <> Nodes under observation: "+str([getIdForNode(node) for node in nodes])
    
    nodes = getNodesThatMatchRequestComponent(nodes, EXP_METHOD, method, tree)
    print "Method: ["+method+"] <> Nodes under observation: "+str([getIdForNode(node) for node in nodes])
    
    nodes = getNodesThatMatchRequestComponent(nodes, EXP_PATH, path, tree)
    print "Path: ["+path+"] <> Nodes under observation: "+str([getIdForNode(node) for node in nodes])
    
    nodes = getNodesThatMatchRequestComponent(nodes, EXP_QUERY, query, tree)
    print "Query: ["+query+"] <> Nodes under observation: "+str([getIdForNode(node) for node in nodes])
    
    nodes = getNodesThatMatchRequestComponent(nodes, EXP_HEADERS, headers, tree, True)
    print "Headers: ["+headers+"] <> Nodes under observation: "+str([getIdForNode(node) for node in nodes])
    
    nodes = getNodesThatMatchRequestComponent(nodes, EXP_BODY, body, tree)
    print "Body: ["+body+"] <> Nodes under observation: "+str([getIdForNode(node) for node in nodes])

    leaf_nodes = getDirectChildrenForNodeList(nodes, tree, EXP_RESPONSE)
    print "Response candidates: "+str([getIdForNode(node) for node in leaf_nodes])
    
    if len(leaf_nodes) == 1:
        print "Returning response: "+str(getIdForNode(leaf_nodes[0]))+" for request - {" + request.toString() + "}"
        
        response = getTagForNode(leaf_nodes[0])
        responseBody = response[EXP_BODY]
        if responseBody.endswith('.json'):
            basePath = os.path.dirname(getIdForNode(leaf_nodes[0]).split(':')[0])
            responseBody = Arguments.getPathForFile(responseBody,basePath)
            with open(responseBody, 'r') as response_file:
                responseBody = response_file.read()
        response[EXP_BODY] = responseBody
        return response
    elif len(leaf_nodes) < 1:
        raise ValueError("No match found for request - {" + request.toString() + "}")
    else:
        node_names = [getIdForNode(leaf_node) for leaf_node in leaf_nodes]
        raise ValueError("Multiple matches found for request - {" + request.toString() + "} >> Matching nodes: " + str(node_names))