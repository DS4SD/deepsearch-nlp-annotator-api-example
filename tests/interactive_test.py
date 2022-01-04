# IBM Corpus Processing Service
# (C) Copyright IBM Corporation 2019, 2021
# ALL RIGHTS RESERVED

import os
import time
import json

import glob

import datetime
import textwrap
import requests

from tabulate import tabulate
from datetime import datetime

import argparse

from TestConfig import *
from TestFunctions import *

from alive_progress import alive_bar

def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--filename", default="./data/geography.txt",
                        required=False, help="filename with the input-data")

    parser.add_argument("--documents", default=None,
                        required=False, help="directory with CCS-documents")
                        
    parser.add_argument("--end_point", default="local_geo",
                        required=False, help="endpoint {}".format(str(list(end_points.keys()))))

    parser.add_argument("--inspect", default=True,
                        required=False, help="inspect output")

    parser.add_argument("--mode", default="default",
                        required=False, help="type of performance testing ('default', 'batch' or 'thread')")
    
    args = parser.parse_args()

    if args.end_point in end_points:
        end_point=end_points[args.end_point]
    else:
        print("invalid endpoint => aborting ...")
        exit(0)
        
    return end_point, args.filename, args.documents, args.inspect, args.mode

def get_text_from_txt_or_jsonl(filename):
    
    fr = open(filename)

    while True:

        line = fr.readline()
        
        if line==None:
            break

        try:
            data=["",""]

            if filename.endswith("txt"):
                data = [line, line]

            elif filename.endswith("jsonl"):
                _ = json.loads(line)

                if "main-text" in _:
                    data = [
                        _["description"]["title"],
                        _["main-text"][0]["text"],
                    ]
                elif "text" in _ and "_file" in _:
                    data = [
                        _["_file"]["filename"],
                        _["text"]
                    ]
                else:
                    data ["", ""]

            yield data
        except:
            break
            
    fr.close()

def get_text_from_json(filename):

    fr = open(filename)

    data = json.load(fr)

    for item in data["main-text"]:
        yield [item["text"], item["text"]]
    
    fr.close()    

def get_text(filename):    

    fr = open(filename)
    
    if(filename.endswith("txt") or
       filename.endswith("jsonl")):

        while True:

            line = fr.readline()
        
            if line==None:
                break

            try:
                data=["",""]
                
                if filename.endswith("txt"):
                    data = [line, line]

                elif filename.endswith("jsonl"):
                    _ = json.loads(line)
                    
                    if "main-text" in _:
                        data = [
                            _["description"]["title"],
                            _["main-text"][0]["text"],
                        ]
                    elif "text" in _ and "_file" in _:
                        data = [
                            _["_file"]["filename"],
                            _["text"]
                        ]
                else:
                    data ["", ""]

                yield data
            except:
                break
    else:
        doc = json.load(fr)

        for item in doc.get("main-text",[]):
            if "text" in item:
                yield [item["text"], item["text"]]
    
    fr.close()    
            
def display(text, ents, rels, ent_names, rel_names):

    wrapper = textwrap.TextWrapper(width=48)
    
    names={}
    for name in ent_names:
        names[name]=0
    
    print("text: \033[1;33;40m", text)
    print("\033[0;37;40m")
    
    data=[]
    for key,val in ents.items():

        if "statement" in key:
            continue
        
        for ent in val:

            name = ent["match"]
            
            orig=""
            if "original" in ent:
                orig = ent["original"]
                
            ref = ent["type"]+"."+str(names[ent["type"]])
            
            model = ent.get("model", "-")
            
            data.append([ref,
                         wrapper.fill(text=name),
                         wrapper.fill(text=orig),
                         ent["range"], model])
            
            names[ent["type"]] += 1

    print("\033[1;32;40mEntities: ")
    print("\033[0;37;40m")
    
    data = sorted(data, key=lambda x:x[3][0])
    print(tabulate(data, headers=["ref", "match", "original", "range", "model"]))

    print(" ")
    
    for key,val in rels.items():

        if(len(val["data"])>0):
            print("\033[1;32;40mRelationships: {}".format(key))
            print("\033[0;37;40m")

            for row in val["data"]:
                for ent in data:
                    if ent[0]==row[0]:
                        row.append(ent[1])

                row.append(" -> ")
                        
                for ent in data:
                    if ent[0]==row[1]:
                        row.append(ent[1])


            print(tabulate(val["data"], headers=val["header"]+[val["header"][0], "   ", val["header"][1]]))
            print("    ")
    print("\n")

    data=[]
    for key,val in ents.items():

        if "statement" not in key:
            continue

        for ent in val:

            state = ent["subtype"]
            
            subj = ent["subject"]

            name_ = "null"
            type_ = "-"
            if subj!=None:
                name_ = subj["name"]
                type_ = subj["type"]
                
            data.append([state, name_, type_, "", "", "", ""])

            for pred in ent["predicates"]:
                data.append(["", "", "",
                             pred["key"]["name"], pred["key"]["type"],
                             pred["value"]["name"], pred["value"]["type"]])

    if len(data)>0:
        print("\033[1;32;40mStatements: ")
        print("\033[0;37;40m")
        print(tabulate(data, headers=["statement", "subject", "type", "key", "key-type", "value", "value-type"]))
        print("    ")
        print("\n")                
    
    ans = input("continue? [(y)es/(n)o]")
    if ans=='n':
        exit(0)
        
    else:
        return
        

def inspect_annotations(filename, deployment,
                        ent_names, rel_names,
                        max_docs=1000, batch_size=16):

    tic = datetime.now()
    
    texts=[]

    for i, data in enumerate(get_text(filename)):
        
        if data==["",""]:
            break
        
        texts.append(data[1])
            
        if(len(texts)==batch_size):
            res = get_entities(deployment, ent_names, texts)
            
            if res.status_code!=200:
                print(" ==> status-code [ents]: ", res.status_code, "\t", res)
                print("\t", data[0])
                exit(-1)

            response = res.json()
            ents = response["entities"]
                
            res = get_relationships(deployment, rel_names, texts, ents)
                
            if res.status_code!=200:
                print(" ==> status-code [rels]: ", res.status_code, "\t", res)
                print("\t", data[0])
                exit(-1)
                
            response = res.json()            
            rels = response["relationships"]                

            #print(json.dumps(response, indent=2))
            
            for i,text in enumerate(texts):
                display(text, ents[i], rels[i], ent_names, rel_names)
                
            texts=[]

        if i==max_docs:
            break
    
    toc = datetime.now()

    return toc-tic
    
def time_annotations(filename, deployment,
                     ent_names, rel_names,
                     max_docs=1000, batch_size=16):

    tic = datetime.now()
    
    texts=[]

    with alive_bar(max_docs) as bar:
    
        for i, data in enumerate(get_text(filename)):
        
            if data==["",""]:
                break
        
            texts.append(data[1])
            
            if(len(texts)==batch_size):
                res = get_entities(deployment, ent_names, texts)
            
                if res.status_code!=200:
                    print(" ==> status-code [ents]: ", res.status_code, "\t", res)
                    print("\t", data[0])
                    exit(-1)

                response = res.json()
                ents = response["entities"]
                
                res = get_relationships(deployment, rel_names, texts, ents)
                
                if res.status_code!=200:
                    print(" ==> status-code [rels]: ", res.status_code, "\t", res)
                    print("\t", data[0])
                    exit(-1)

                response = res.json()
                rels = response["relationships"]                
                
                texts=[]

            if i==max_docs:
                break

            bar()
    
    toc = datetime.now()

    return toc-tic

def run_thread_tests(filename, endpoint, max_docs=1024, batch_size=4):

    # init reader
    get_text(filename)

    headers=["#-threads", "batch-size", "#-text", "total-time", "time/text"]
    data=[]
    for nt in [1, 2, 4, 8, 16, 32]:
        
        tic = datetime.now()
        
        jobs=[]
        
        for l in range(0, nt):
            
            job = threading.Thread(target=time_annotations,
                                   args=(False, filename, endpoint,
                                         ent_names, rel_names,
                                         max_docs/nt, batch_size))
            jobs.append(job)
            
        for l in range(0, nt):
            jobs[l].start()

        for l in range(0, nt):
            jobs[l].join()
                
        toc = datetime.now()

        diff = toc-tic
        
        print(nt, "\t", diff, "\t", diff/max_docs)
        data.append([nt, batch_size, max_docs, diff, diff/max_docs])

    print(tabulate(data, headers))

    return headers, data

def run_batch_tests(filename, endpoint, ent_names, rel_names, max_docs=1024):

    headers=["batch-size", "#-text", "total-time", "time/text"]
    data=[]
    
    for bs in [1, 2, 4, 8, 16, 32, 64, 128]:

        diff = time_annotations(False, filename, deployment=endpoint,
                                ent_names=ent_names, rel_names=rel_names,
                                max_docs=max_docs, batch_size=bs)

        print(bs, "\t", diff, "\t", diff/max_docs)
        data.append([bs, max_docs, diff, diff/max_docs])

    print(tabulate(data, headers))

    return headers, data

if __name__ == "__main__":
    
    endpoint, filename, documents_dir, inspect, mode = parse_args()

    ent_names, rel_names = get_names(endpoint)

    print("entities: ", ent_names)
    print("relations: ", rel_names)

    ans = input("continue? [y/n]")
    if ans=='n':

        _ = input("entities: ")
        _ = _.replace("'", "\"")
        ent_names = json.loads(_)

        _ = input("realtions: ")
        _ = _.replace("'", "\"")
        rel_names = json.loads(_)

    if documents_dir!=None:

        documents = glob.glob(os.path.join(documents_dir, "*.json"))

        tic = datetime.now()
        
        doc_timings=[]
        
        for i,doc_file in enumerate(documents):
            print("document [{}/{}]: {}".format(str(i), len(documents), doc_file))

            with open(doc_file, "r") as fr:
                doc = json.load(fr)
                
                max_items = 0
                for item in doc.get("main-text", []):
                    if "text" in item:
                        max_items += 1
                        
            #print(" --> max-items: ", max_items)
                
            diff = time_annotations(doc_file, endpoint, ent_names, rel_names,
                                    max_docs=max_items, batch_size=1)

            #print(" --> total-time: ", diff)
            
            doc_timings.append([max_items, diff])

        toc = datetime.now()
        print(" --> total-time: ", (toc-tic))
            
    elif mode=="default" and inspect:

        inspect_annotations(filename, endpoint, ent_names, rel_names,
                            max_docs=10000, batch_size=1)
        
    elif mode=="default" and (not inspect):        

        diff = time_annotations(filename, endpoint, ent_names, rel_names,
                                max_docs=10000, batch_size=1)
        print("total-time: ", diff)

    elif mode=="thread":

        run_thread_tests(filename, endpoint, max_docs=1024, batch_size=4)        
        
    elif mode=="batch":

        run_batch_tests(filename, endpoint, ent_names, rel_names, max_docs=1024)
        
    else:
        print("unknown performance mode: ", mode)

