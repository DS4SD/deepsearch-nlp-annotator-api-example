# IBM Corpus Processing Service
# (C) Copyright IBM Corporation 2019, 2021
# ALL RIGHTS RESERVED

import json

import requests
import textwrap

def get_names(deployment):

    data = {
        "features": {
            "entity_names": True,
            "relationship_names": True,
            "property_names": True,
            "labels": True
        }
    }

    res = requests.post(url=deployment["url"],
                        headers=deployment["headers"],
                        json=data)

    if res.status_code!=200:
        print(res)
        exit(-1)

    resp = res.json()
    #print(json.dumps(resp, indent=2))
    
    return resp["entity_names"], resp["relationship_names"]
    
def get_entities(deployment, names, texts):

    data = {
        "find_entities": {
            "object_type": "text",
            "entity_names": names,
            "texts": texts
        }
    }

    res = requests.post(url=deployment["url"],
                        headers=deployment["headers"],                        
                        json=data)

    return res

def get_relationships(deployment, names, texts, entities):

    data = {
        "find_relationships": {        
            "object_type": "text",
            "relationship_names": names,
            "texts": texts,
            "entities": entities
        }
    }

    res = requests.post(url=deployment["url"],
                        headers=deployment["headers"],
                        json=data)

    return res    

