import sys
import subprocess 
import xml.etree.ElementTree as ET
import os, fnmatch
import argparse
import ConfigParser
import httplib, urllib

import codecs
parser=argparse.ArgumentParser()
parser.add_argument('-p', help='Path Parameters')
args=parser.parse_args()
parameters={}
if __name__ == '__main__':
    import generate_trainning_dataset
    parameters = generate_trainning_dataset.ReadParameters(args)     
    generate_trainning_dataset.Main(parameters)

def Main(parameters):
    dest=parameters['output_directory']
    gold_answer_folder=parameters['gold_answer_folder']
    gold_anwser_file=parameters['gold_anwser_file']
    random_retrieval_folder = parameters['random_retrieval_folder']
    random_retrieval_file = parameters['random_retrieval_file']
    pubmed_search_query= parameters['pubmed_search_query']
    gold_anwser_result_file=parameters['gold_anwser_result_file']
    gold_anwser_file_classifier_format=parameters['gold_anwser_file_classifier_format']
    random_retrieval_file_classifier_format=parameters['random_retrieval_file_classifier_format']
    gold_answer_classification_label=parameters['gold_answer_classification_label']
    negative_classification_label=parameters['negative_classification_label']
    num_gold_answer = parameters['num_gold_answer']
    num_rand_answer = parameters['num_rand_answer']
    output_data_set_file=parameters['output_data_set_file']
    
    if not os.path.exists(gold_answer_folder):
        os.makedirs(gold_answer_folder)
    if not os.path.exists(random_retrieval_folder):
        os.makedirs(random_retrieval_folder)
    
    download_goldanswer(pubmed_search_query, gold_anwser_file_classifier_format, gold_answer_classification_label, 200)
    
    remove_goldanswer_articles_from_random(gold_anwser_file, random_retrieval_folder)
    
    generate_random_result_file(random_retrieval_folder, random_retrieval_file)
    
    standardization_for_classification(gold_anwser_file, gold_anwser_file_classifier_format, gold_answer_classification_label)
    
    standardization_for_classification(random_retrieval_file, random_retrieval_file_classifier_format,negative_classification_label)
    
    generate_training_dataset(gold_anwser_file_classifier_format, num_gold_answer,random_retrieval_file_classifier_format, num_rand_answer, output_data_set_file)
    
    
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['output_directory']=Config.get('MAIN', 'output_directory')
        parameters['gold_answer_folder']=Config.get('MAIN', 'gold_answer_folder')
        parameters['gold_anwser_file']=Config.get('MAIN', 'gold_anwser_file')
        parameters['random_retrieval_folder']=Config.get('MAIN', 'random_retrieval_folder')
        parameters['random_retrieval_file']=Config.get('MAIN', 'random_retrieval_file')
        parameters['pubmed_search_query']=Config.get('MAIN', 'pubmed_search_query')
        parameters['gold_anwser_result_file']=Config.get('MAIN', 'gold_anwser_result_file')
        parameters['gold_anwser_file_classifier_format']=Config.get('MAIN', 'gold_anwser_file_classifier_format')
        parameters['random_retrieval_file_classifier_format']=Config.get('MAIN', 'random_retrieval_file_classifier_format')
        parameters['gold_answer_classification_label']=Config.get('MAIN', 'gold_answer_classification_label')
        parameters['negative_classification_label']=Config.get('MAIN', 'negative_classification_label')
        parameters['num_gold_answer']=Config.get('MAIN', 'num_gold_answer')
        parameters['num_rand_answer']=Config.get('MAIN', 'num_rand_answer')
        parameters['output_data_set_file']=Config.get('MAIN', 'output_data_set_file')
    else:
        print("Please send the correct parameters config.properties --help ")
        sys.exit(1)
    return parameters   

def remove_goldanswer_articles_from_random(idgold_anwser_file, random_retrieval_folder):
    result_file_name="./pmidlist.csv"
    with open(result_file_name,'w') as result_file:  
        i=0
        docXml = ET.parse(gold_anwser_file)
        for article in docXml.findall("PubmedArticle"):
            pmid = article.find("MedlineCitation").find("PMID").text
            if(os.path.exists(random_retrieval_folder + "/PMID"+pmid+".xml")):
                #remove from random folder.
                os.remove(random_retrieval_folder + "/PMID"+pmid+".xml")
            result_file.write(pmid+"\n")
            result_file.flush()
            print i        
        result_file.close()

'''                                  
def remove_goldanswer_articles_from_random(gold_anwser_file, random_retrieval_folder):
    result_file_name="./pmidlist.csv"
    with open(result_file_name,'w') as result_file:  
        i=0
        docXml = ET.parse(gold_anwser_file)
        for article in docXml.findall("PubmedArticle"):
            pmid = article.find("MedlineCitation").find("PMID").text
            if(os.path.exists(random_retrieval_folder + "/PMID"+pmid+".xml")):
                #remove from random folder.
                os.remove(random_retrieval_folder + "/PMID"+pmid+".xml")
            result_file.write(pmid+"\n")
            result_file.flush()
            print i        
        result_file.close()
'''        
def generate_random_result_file(random_retrieval_folder, result_file_name):
    listOfFiles = os.listdir(random_retrieval_folder)  
    pattern = "PMID*.xml"
    with open(result_file_name,'w') as result_file:  
        header='<?xml version="1.0" ?> <!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st June 2018//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_180601.dtd">  <PubmedArticleSet>'
        result_file.write(header)
        result_file.flush()
        i=0
        for entry in listOfFiles:  
            if fnmatch.fnmatch(entry, pattern):
                with open(random_retrieval_folder + entry,'r') as xml_file:    
                    print ("Parsing " + entry)
                    docXml = ET.parse(xml_file)
                    article = docXml.find("PubmedArticle")
                    artstr = ET.tostring(article, method='xml')
                    result_file.write(artstr)
                    result_file.flush()
                    i=i+1
                    print i        
        footer='</PubmedArticleSet>'
        result_file.write(footer)
        result_file.flush()
        result_file.close() 

def download_goldanswer(pubmed_search_query, pubmed_result_output, classification_token, retmax=50000):   
    params = urllib.urlencode({'db':'pubmed','rettype':'xml','retmode':'xml','term': pubmed_search_query, 'retmax':str(retmax)})
    conn = httplib.HTTPSConnection("eutils.ncbi.nlm.nih.gov")
    conn.request("POST", "/entrez/eutils/esearch.fcgi", params )
    rpub = conn.getresponse()
    if not rpub.status == 200 :
        print "Error en la conexion: " + rpub.status + " " + rpub.reason 
        exit()
    response_pubmed = rpub.read()
    docXml = ET.fromstring(response_pubmed)
    with open(pubmed_result_output+"_id_list.txt",'w') as pmid_list_file: 
        with codecs.open(pubmed_result_output,'w',encoding='utf8') as txt_file:
            for f in docXml.find("IdList").findall("Id") :
                try:
                    print f.text
                    params = urllib.urlencode({'db':'pubmed','retmode':'xml','id':f.text})
                    conn2 = httplib.HTTPSConnection("eutils.ncbi.nlm.nih.gov")
                    conn2.request("POST", "/entrez/eutils/efetch.fcgi", params )
                    rf = conn2.getresponse()
                    if not rf.status == 200 :
                        print "Error en la conexion: " + rf.status + " " + rf.reason 
                        exit()
                    response_efetch = rf.read()
                    docXml_E = ET.fromstring(response_efetch) 
                    article = docXml_E.find("PubmedArticle")
                    if(article!=None):
                        pmid = article.find("MedlineCitation").find("PMID").text
                        art_txt = classification_token + "\t" + pmid + "\t"    
                        article_xml = article.find("MedlineCitation").find("Article")
                        abstract_xml = article_xml.find("Abstract")
                        if(abstract_xml!=None):
                            title_xml=article_xml.find("ArticleTitle")
                            if(title_xml!=None):
                                title = title_xml.text
                                if(title!=None):
                                    art_txt = art_txt + title.replace("\n"," ").replace("\t"," ").replace("\r"," ") + "\t" 
                                else:
                                    art_txt = art_txt + " " + "\t"     
                                abstract_xml = article_xml.find("Abstract")
                                if(abstract_xml!=None):
                                    abstract_text = abstract_xml.find("AbstractText")
                                    if(abstract_text!=None):
                                        abstract=abstract_text.text
                                        if(abstract!=None):
                                            art_txt = art_txt + abstract.replace("\n"," ").replace("\t"," ").replace("\r"," ") + "\n" 
                                            txt_file.write(art_txt)
                                            txt_file.flush()
                                            pmid_list_file.write(pmid+"\n")
                                            pmid_list_file.flush()   
                    rf.close
                    conn2.close()
                except Exception as inst:
                    print "Error Downloading " 
                    print inst    
            txt_file.close()
        pmid_list_file.close()        
    rpub.close
    conn.close()         
        

def standardization_for_classification(pubmed_result_file, pubmed_result_output,classification_token):
    if os.path.isfile(pubmed_result_file):
        with open(pubmed_result_file,'r') as xml_file:    
            with codecs.open(pubmed_result_output,'w',encoding='utf8') as txt_file:
                print ("Parsing " + pubmed_result_file)
                docXml = ET.parse(xml_file)
                for article in docXml.findall("PubmedArticle"):
                    try:
                        pmid = article.find("MedlineCitation").find("PMID").text
                        art_txt = classification_token + "\t" + pmid + "\t"    
                        article_xml = article.find("MedlineCitation").find("Article")
                        abstract_xml = article_xml.find("Abstract")
                        if(abstract_xml!=None):
                            title_xml=article_xml.find("ArticleTitle")
                            if(title_xml!=None):
                                title = title_xml.text
                                if(title!=None):
                                    art_txt = art_txt + title.replace("\n"," ").replace("\t"," ").replace("\r"," ") + "\t" 
                                else:
                                    art_txt = art_txt + " " + "\t"     
                            abstract_xml = article_xml.find("Abstract")
                            if(abstract_xml!=None):
                                abstract_text = abstract_xml.find("AbstractText")
                                if(abstract_text!=None):
                                    abstract=abstract_text.text
                                    if(abstract!=None):
                                        art_txt = art_txt + abstract.replace("\n"," ").replace("\t"," ").replace("\r"," ") + "\n" 
                                        txt_file.write(art_txt)
                                        txt_file.flush()
                    except Exception as inst:
                        print "Error Generando el JSON/TXT PMID " + pmid
                        print inst
                        x = inst.args
                        print x
                txt_file.flush()                     
                txt_file.close()    
            xml_file.close()                         
            
            
def generate_training_dataset(gold_answer_file_classifier_format, num_gold_answer,random_retrieval_file_classifier_format,num_rand_answer, output_data_set_file):
    subprocess.check_call("./trainning_test_split.bash %s %s %s %s %s" % (gold_answer_file_classifier_format, str(num_gold_answer), random_retrieval_file_classifier_format, str(num_rand_answer), output_data_set_file),   shell=True)
    
