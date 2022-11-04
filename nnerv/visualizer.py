import spacy
import argparse
import json
import sqlite3
import os

from rich import print as rprint
from rich.console import Console
from rich.text import Text    

import shutup
shutup.please()

from nnerv.doi2metadata import doi2metadata

def rich_print(doi,title,abstract,annotations):
    
    console = Console()
    doi_rich = Text()
    title_rich = Text()
    abstract_rich = Text()
    abstract_rich.append("Abstract: ", style="on blue")
    
    if len(annotations)>1:
        abstract_rich.append(abstract[:int(annotations[0]['start_char'])])
        for i in range(len(annotations)-1):
            abstract_rich.append(abstract[int(annotations[i]['start_char']):int(annotations[i]['end_char'])]+' ', style="bold red")
            abstract_rich.append('('+annotations[i]['label']+')',style="on red")
            abstract_rich.append(abstract[int(annotations[i]['end_char']):int(annotations[i+1]['start_char'])])
        
        abstract_rich.append(abstract[int(annotations[-1]['start_char']):int(annotations[-1]['end_char'])]+' ', style="bold red")
        abstract_rich.append('('+annotations[-1]['label']+')',style="on red")
        abstract_rich.append(abstract[int(annotations[-1]['end_char']):])
        
    elif len(annotations)==1:
        abstract_rich.append(abstract[:int(annotations[0]['start_char'])])
        abstract_rich.append(abstract[int(annotations[0]['start_char']):int(annotations[0]['end_char'])]+' ', style="bold red")
        abstract_rich.append('('+annotations[0]['label']+')',style="on red")
        abstract_rich.append(abstract[int(annotations[0]['end_char']):])
        
    elif len(annotations)==0:
        abstract_rich.append(abstract)
        
    rprint('[on blue]DOI:[/] [u green]https://doi.org/'+doi+'[/]')
    rprint('[on blue]Title:[/] [bold green]'+title+'[/]')
    
    console.print(abstract_rich)

def output_json(output_path,doi,title,abstract,annotations):
    write_dict={
            'doi':doi,
            'title':title,
            'abstract':abstract,
            'annotations':annotations,
    }
    
    with open(output_path,'a') as f:
        f.write(json.dumps(write_dict) + "\n")
        
def doc2annotations(doc):
    return [{'text': ent.text, 'label': ent.label_, 'start_char': ent.start_char, 'end_char': ent.end_char} for ent in doc.ents]

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
        
    return conn
    
def has_db(db_path,doi,model):

    if not os.path.isfile(db_path):
        return False
    
    conn = create_connection(db_path)
    with conn:
        try:
            sql = 'SELECT * FROM nnerv WHERE doi=? AND model=?'
            cur = conn.cursor()
            cur.execute(sql, (doi,model))
            rows = cur.fetchall()
            
            if rows:
                doi,model,title,abstract,annotations_raw=rows[0]
                annotations=json.loads(annotations_raw)
                return doi,title,abstract,annotations
            else:
                return False
        except sqlite3.OperationalError as e:
            if 'no such table' in str(e):
                return False
            else:
                print(e)
        except Exception as e:
            print(e)
    
    
def output_db(db_path,doi,model_load,title,abstract,annotations):
    
    data=(
        doi,model_load,title,abstract,
        json.dumps(annotations)
    )

    conn = create_connection(db_path) 
    try:
        cur = conn.cursor()
        sql='SELECT * FROM nnerv'
        cur.execute(sql)
    except sqlite3.OperationalError as e:
        if 'no such table' in str(e):
            sql='CREATE TABLE nnerv (doi text,model text,title text, abstract text, annotations json)'
            cur.execute(sql)
        else:
            print(e)
    except Exception as e:
        print(e)
    
    with conn:
        try:
            sql = ''' INSERT INTO nnerv(doi,model,title,abstract,annotations)
                VALUES(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, data)
            conn.commit()
        except Exception as e:
            print(e)
            
def main(doi,model_input,output=None,database=None,silent=False):

    if model_input:
        model=model_input[0]
    else:
        model='./scibert_uncased_best/'
    
    if database:
        db_return=has_db(database[0],doi,model)
        if db_return:
            doi,title,abstract,annotations=db_return
        else:
            nlp = spacy.load(model)
            title,abstract=doi2metadata(doi)
            doc=nlp(abstract)
            annotations=doc2annotations(doc)
            output_db(database[0],doi,model,title,abstract,annotations)    
    else:
        nlp = spacy.load(model)
        title,abstract=doi2metadata(doi)
        doc=nlp(abstract)
        annotations=doc2annotations(doc)
    
    if not silent:
        rich_print(doi,title,abstract,annotations)
    
    if output:
        output_json(output[0],doi,title,abstract,annotations)
