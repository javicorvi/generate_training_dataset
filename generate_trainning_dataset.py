import sys
import subprocess 
import os
import argparse
import ConfigParser
import re
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser=argparse.ArgumentParser()
parser.add_argument('-p', help='Path Parameters')
args=parser.parse_args()
parameters={}
if __name__ == '__main__':
    import generate_trainning_dataset
    parameters = generate_trainning_dataset.ReadParameters(args)     
    generate_trainning_dataset.Main(parameters)

def Main(parameters):
    dataset_output_file=parameters['dataset_output_file']
    gold_anwser_file = parameters['gold_anwser_file']
    random_retrieval_file= parameters['random_retrieval_file']
    quantity_gold_answer=parameters['quantity_gold_answer']
    quantity_random_answer=parameters['quantity_random_answer']
    
    if not os.path.exists(gold_anwser_file):
        print("The Gold Anwser File not exist: " +  gold_anwser_file)
        logging.error("The Gold Anwser File not exist: " +  gold_anwser_file)
        sys.exit(1)
    if not os.path.exists(random_retrieval_file):
        print("The Random File not exist : " + random_retrieval_file)
        logging.error("The Random File not exist : " + random_retrieval_file)
        sys.exit(1)
    
    remove_goldanswer_articles_from_random(gold_anwser_file, random_retrieval_file)
    #generate_training_dataset(gold_anwser_file, quantity_gold_answer,random_retrieval_file, quantity_random_answer, dataset_output_file)
  
    
    
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['dataset_output_file']=Config.get('MAIN', 'dataset_output_file')
        parameters['gold_answer_folder']=Config.get('MAIN', 'gold_answer_folder')
        parameters['random_retrieval_folder']=Config.get('MAIN', 'random_retrieval_folder')
        parameters['gold_anwser_file']=Config.get('MAIN', 'gold_anwser_file')
        parameters['random_retrieval_file']=Config.get('MAIN', 'random_retrieval_file')
        parameters['quantity_gold_answer']=Config.get('MAIN', 'quantity_gold_answer')
        parameters['quantity_random_answer']=Config.get('MAIN', 'quantity_random_answer')
    else:
        logging.error("Please send the correct parameters config.properties --help ")
        sys.exit(1)
    return parameters   

def remove_goldanswer_articles_from_random(gold_anwser_file, random_retrieval_file):
    logging.info(" Remove random articles included into the gold answer dataset")
    gold_ids_list=[]
    with open(gold_anwser_file,'r') as gold_file:
        for line in gold_file:
            data = re.split(r'\t+', line)
            gold_ids_list.append(data[1])
    gold_file.close()
    print gold_ids_list
    with open(random_retrieval_file+".tmp",'w') as new_random_file:
        with open(random_retrieval_file,'r') as random_file:
            for line in random_file:
                data = re.split(r'\t+', line)
                if any(data[1] in s for s in gold_ids_list):
                    logging.info("delete from random " + data[1])
                else:
                    new_random_file.write(line)
                    new_random_file.flush()
        random_file.close()
    new_random_file.close()  
    os.remove(random_retrieval_file) 
    os.rename(random_retrieval_file+".tmp", random_retrieval_file)  
    logging.info(" End of process")        
def generate_training_dataset(gold_answer_file, quantity_gold_answer,random_retrieval_file, quantity_random_answer, dataset_output_file):
    logging.info(" Generating DataSet for Training")
    subprocess.check_call("./trainning_test_split.bash %s %s %s %s %s" % (gold_answer_file, str(quantity_gold_answer), random_retrieval_file, str(quantity_random_answer), dataset_output_file),   shell=True)
    logging.info(" End DataSet Training Generator")        
