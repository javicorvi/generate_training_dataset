#!/bin/bash

classes_folder=$1
quantity_for_class=$2
dataset_output_file=$3

#echo "$classes_folder"
#echo "$quantity_for_class"
#echo "$dataset_output_file"

declare -a classes_folders=( "$(tr "," "\n" <<< "$classes_folder")" )
declare -a quantity_classes=( "$(tr "," "\n" <<< "$quantity_for_class")" )
echo "${classes_folders}"
echo "${quantity_classes[2]}"

for ((i=0;i<${#classes_folders[@]};++i)); do
	echo "javi"
    echo "${classes_folders[i]}"
    echo "${quantity_classes[i]}"
    #shuf -n "${quantity_classes[i]}" "${classes_folders[i]}" > "${classes_folders[i]}""tmp"
done



