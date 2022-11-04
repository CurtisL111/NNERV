# Nanoparticle Named Entity Recognition Visualizer

# Introduction

This script can extract, save, and visualize nanoparticle entities. The system consists of three components, get metadata by DOI, annotate the text with trained model and output the result.

The trained model can be downloaded from release.

# Usage
- Specify PubMed E-utilities API key in doi2metadata.py, you can find the instructions here https://www.ncbi.nlm.nih.gov/books/NBK25497/

- Specify desired default model path in visualizer.py
 
- ```chmod nerv```, make ```nerv``` executable 

- ```./nerv -h ``` 

```usage: nerv [-h] [-s] -d DOI [-m MODEL] [-o OUTPUT] [-db DATABASE]

Nanoparticle NER Visualizer

optional arguments:
  -h, --help            show this help message and exit
  -s, --silent          omit command line output
  -d DOI, --doi DOI     DOI to analyze
  -m MODEL, --model MODEL
                        path or name of spaCy model
  -o OUTPUT, --output OUTPUT
                        output JSONL file path
  -db DATABASE, --database DATABASE
                        store to an SQLite database```