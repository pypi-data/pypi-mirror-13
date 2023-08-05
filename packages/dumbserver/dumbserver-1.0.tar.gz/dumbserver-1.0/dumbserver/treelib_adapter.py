#!/usr/bin/env python

from treelib import Node, Tree

from constants import ROOT as root

def createTree():
    tree = Tree()
    tree.create_node(root,root)
    return tree

def addNodeToTree(tree, tag, nodeId, parentId, nodeInfo):
    if not tree.contains(nodeId):
        tree.create_node(tag, nodeId, parent=parentId, data=nodeInfo)
    return tree

def addLeafNodeToTree(tree, tag, nodeId, parentId, nodeInfo):
    parent_node = getNodeFromTreeById(parentId, tree)
    children = getDirectChildrenForNode(parent_node, tree, "response")
    if not children:
        tree.create_node(tag, nodeId, parent=parentId, data=nodeInfo)
        return tree
    else:
        duplicates = [getIdForNode(child) for child in children]
        duplicates.append(nodeId)
        raise ValueError("Error: Duplicate entry in expectations found: " + str(duplicates))

def display(tree):
    tree.show()

def getNodeFromTreeById(nodeId, tree):
    return tree.get_node(nodeId)

def isLeafNode(node):
    return node.is_leaf()
    
def getTagForNode(node):
    return node.tag

def getIdForNode(node):
    return node.identifier

def getInfoForNode(node):
    return node.data
    
def getAllChildrenForNode(node, tree):
    childrenNodeIds, children = tree.is_branch(getIdForNode(node)), []
    for childNodeId in childrenNodeIds:
        children.append(getNodeFromTreeById(childNodeId, tree))
    return children

def getDirectChildrenForNode(node, tree, nodeInfo=None):
    children = []
    for node in getAllChildrenForNode(node, tree):
        if nodeInfo:
            if getInfoForNode(node) == nodeInfo:
                children.append(node)
    return children