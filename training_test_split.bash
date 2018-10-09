gold_answer_file=$1
quantity_gold_answer=$2
random_retrieval_file=$3
quantity_random_answer=$4
dataset_output_file=$5

echo $gold_answer_file
echo $quantity_gold_answer

total=$(($quantity_gold_answer + $quantity_random_answer))
echo $total

shuf -n $quantity_gold_answer $gold_answer_file > $gold_answer_file$"tmp"
shuf -n $quantity_random_answer $random_retrieval_file > $random_retrieval_file$"tmp"
cat $gold_answer_file$"tmp" $random_retrieval_file$"tmp" > $dataset_output_file$"tmp"
shuf -n $total $dataset_output_file$"tmp" > $dataset_output_file

rm $gold_answer_file$"tmp"
rm $random_retrieval_file$"tmp"
rm $dataset_output_file$"tmp"