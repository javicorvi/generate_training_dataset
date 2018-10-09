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
    import generate_multiclass_training_dataset
    parameters = generate_multiclass_training_dataset.ReadParameters(args)     
    generate_multiclass_training_dataset.Main(parameters)

def Main(parameters):
    dataset_output_file=parameters['dataset_output_file']
    work_dir = parameters['work_dir']
    classes = parameters['classes']
    quantity_for_class= parameters['quantity_for_class']
    classes_folder=parameters['classes_folder']
    
    validate_parameters(dataset_output_file, work_dir,classes, quantity_for_class, classes_folder)
    
    classes_folder_=classes_folder.split(",")
    classes_=classes.split(",")
    quantity_for_class_=quantity_for_class.split(",")
    quantity_for_class_ = [  int(f) for f in quantity_for_class_]
    
    classes_folder_ = [ work_dir + "/" + f for f in classes_folder_]
    
    '''for clas in classes_folder_[:len(classes_folder_)-1]:
        remove_goldanswer_articles_from_random(clas, classes_folder_[len(classes_folder_)-1])
    '''
    
    random_folder = classes_folder_[len(classes_folder_)-1]
    random_quantity = quantity_for_class_[len(quantity_for_class_)-1]
    i=0
    for clas, quantity in zip(classes_folder_, quantity_for_class_):
        generate_training_dataset(clas, quantity, random_folder, random_quantity, dataset_output_file+"_"+str(i))
        random_quantity = random_quantity + quantity
        random_folder = dataset_output_file+"_"+i
        i=i+1
    #generate_training_dataset(classes_folder, quantity_for_class, dataset_output_file)
    
    #format_limtox1_0_to_limtox2_0(gold_anwser_file, random_retrieval_file)
    #
    #curated_training_dataset(dataset_output_file)
    
def generate_training_dataset(gold_answer_file, quantity_gold_answer,random_retrieval_file, quantity_random_answer, dataset_output_file):
    logging.info(" Generating DataSet for Training")
    subprocess.check_call("./training_test_split.bash %s %s %s %s %s" % (gold_answer_file, str(quantity_gold_answer), random_retrieval_file, str(quantity_random_answer), dataset_output_file),   shell=True)
    logging.info(" End DataSet Training Generator")  
    
    
def validate_parameters(dataset_output_file, work_dir, classes, quantity_for_class, classes_folder):
    ''' if not os.path.exists(gold_anwser_file):
        print("The Gold Anwser File not exist: " +  gold_anwser_file)
        logging.error("The Gold Anwser File not exist: " +  gold_anwser_file)
        sys.exit(1)
    if not os.path.exists(random_retrieval_file):
        print("The Random File not exist : " + random_retrieval_file)
        logging.error("The Random File not exist : " + random_retrieval_file)
        sys.exit(1)'''
    print "validate"
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['dataset_output_file']=Config.get('MAIN', 'dataset_output_file')
        parameters['work_dir']=Config.get('MAIN', 'work_dir')
        parameters['classes']=Config.get('MAIN', 'classes')
        parameters['quantity_for_class']=Config.get('MAIN', 'quantity_for_class')
        parameters['classes_folder']=Config.get('MAIN', 'classes_folder')
    else:
        logging.error("Please send the correct parameters config.properties --help ")
        sys.exit(1)
    return parameters   

def remove_goldanswer_articles_from_random(gold_anwser_file, random_retrieval_file):
    logging.info(" Remove random articles included into the gold answer dataset for class : " + gold_anwser_file)
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
       
def generate_training_dataset_multiclass(classes_folder, quantity_for_class, dataset_output_file):
    logging.info(" Generating DataSet for Training")
    subprocess.check_call("./training_multiclass_dataset_split.bash %s %s %s " % (classes_folder, quantity_for_class, dataset_output_file),   shell=True)
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
