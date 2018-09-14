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
    import generate_training_dataset
    parameters = generate_training_dataset.ReadParameters(args)     
    generate_training_dataset.Main(parameters)

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
    #format_limtox1_0_to_limtox2_0(gold_anwser_file, random_retrieval_file)
    generate_training_dataset(gold_anwser_file, quantity_gold_answer,random_retrieval_file, quantity_random_answer, dataset_output_file)
    curated_training_dataset(dataset_output_file)
    
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['dataset_output_file']=Config.get('MAIN', 'dataset_output_file')
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
    total_articles_errors = 0
    total_articles_deleted = 0
    with open(random_retrieval_file+".tmp",'w') as new_random_file:
        with open(random_retrieval_file,'r') as random_file:
            for line in random_file:
                try:
                    data = re.split(r'\t+', line)
                    if(len(data)==4):
                        if any(data[1] in s for s in gold_ids_list):
                            logging.info("delete from random " + data[1])
                            total_articles_deleted = total_articles_deleted + 1
                        else:
                            new_random_file.write(line)
                            new_random_file.flush()
                    else:
                        logging.info("this record is wrong " + line)
                except Exception as inst:
                    total_articles_errors = total_articles_errors + 1
                    #logging.error("The article with id : " + id + " could not be processed. Cause:  " +  str(inst))
                    logging.error("Error reading article the cause probably: contained an invalid character ")       
        random_file.close()
    new_random_file.close()  
    os.remove(random_retrieval_file) 
    os.rename(random_retrieval_file+".tmp", random_retrieval_file)  
    logging.info("Total articles with character invalid: "  +  str(total_articles_errors))
    logging.info("Total articles deleted from random: "  +  str(total_articles_deleted))
    logging.info(" End of process") 
       
def generate_training_dataset(gold_answer_file, quantity_gold_answer,random_retrieval_file, quantity_random_answer, dataset_output_file):
    logging.info(" Generating DataSet for Training")
    subprocess.check_call("./trainning_test_split.bash %s %s %s %s %s" % (gold_answer_file, str(quantity_gold_answer), random_retrieval_file, str(quantity_random_answer), dataset_output_file),   shell=True)
    logging.info(" End DataSet Training Generator")  
    


def format_limtox1_0_to_limtox2_0(gold_anwser_file, random_retrieval_file):
    logging.info(" Format files form limtox 1.0 to limtox 2.0")
    with open(gold_anwser_file+".tmp",'w') as new_gold_anwser_file:
        with open(gold_anwser_file,'r') as gold_file:
            for line in gold_file:
                line = 'hepatotoxicity' + '\t' + line
                new_gold_anwser_file.write(line)
                new_gold_anwser_file.flush()
        gold_file.close()
    new_gold_anwser_file.close()
    os.remove(gold_anwser_file) 
    os.rename(gold_anwser_file+".tmp", gold_anwser_file) 
    with open(random_retrieval_file+".tmp",'w') as new_random_retrieval_file:
        with open(random_retrieval_file,'r') as random_file:
            for line in random_file:
                line = 'random' + '\t' + line
                new_random_retrieval_file.write(line)
                new_random_retrieval_file.flush()
        random_file.close()
    new_random_retrieval_file.close()
    os.remove(random_retrieval_file) 
    os.rename(random_retrieval_file+".tmp", random_retrieval_file) 
    logging.info(" End of process") 


def curated_training_dataset(dataset_output_file):
    logging.info("Curated File " + dataset_output_file)
    with open(dataset_output_file+".tmp",'w') as new_dataset_output_file:
        with open(dataset_output_file,'r') as dataset_file:
            for line in dataset_file:
                data = re.split(r'\t+', line)
                if(len(data)==4):
                    new_dataset_output_file.write(line)
                    new_dataset_output_file.flush()
        dataset_file.close()
    new_dataset_output_file.close()
    os.remove(dataset_output_file) 
    os.rename(dataset_output_file+".tmp", dataset_output_file) 
    logging.info(" End of process")     
