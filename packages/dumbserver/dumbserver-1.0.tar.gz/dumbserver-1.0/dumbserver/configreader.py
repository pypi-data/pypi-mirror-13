#!/usr/bin/env python
    
def readFileContents(filename):
    return readYamlFileContents(filename)
    # if filename.endswith(".yml") or filename.endswith(".yaml"):
    #     return readYamlFileContents(filename)
    # else:
    #     raise ValueError("Unsupported file type for file {"+ filename +"}. Currently supports only YAML format")

def readYamlFileContents(filename):
    import yaml
    contents = {}
    with open(filename, 'r') as stream:
        contents = yaml.load(stream)
    return contents