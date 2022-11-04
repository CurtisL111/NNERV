import requests
import xmltodict

def doi2metadata(doi):
    api_key='your_pubmed_apikey'
    try:
        #clean doi input
        doi=doi.strip()
        
        #get PMID by DOI
        url='http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?api_key=%s&db=pubmed&WebEnv=1&usehistory=y&term=%s'%(api_key,doi)
        
        r=requests.get(url)
        dict_data = xmltodict.parse(r.content)
        
        pmid=dict_data['eSearchResult']['WebEnv']
        
        #get abstract/title by PMID
        url='http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key=%s&db=pubmed&retmode=XML&rettype=abstract&query_key=1&WebEnv=%s'%(api_key,pmid)
        
        r=requests.get(url)
        dict_data = xmltodict.parse(r.content)
        
        title=dict_data['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['Article']['ArticleTitle']
        
        #sometimes this section would be a dict/ordered dict
        if type(title) is str:
            title=title
        else:
            title=title['#text']
        
        abstract=dict_data['PubmedArticleSet']['PubmedArticle']['MedlineCitation']['Article']['Abstract']['AbstractText']
        
        if type(abstract) is str:
            abstract=abstract
        else:
            abstract=abstract['#text']
        
        #print(abstract)
        
        return title,abstract
    except Exception as e:
        print(e)
        return 'This DOI is invalid or some error occurred...',''

if __name__ == "__main__":
    doi=input('DOI: ')
    doi2metadata(doi)