#!/bin/sh

algolist="text-rank lex-rank edmundson lsa sum-basic kl"

python summary_getter.py


for algo in $algolist
do
	python sumy_summary_getter.py $algo	
	search_dir="gold_standard/summary_en"

	#echo "FILENAME, MY_ALGO, OTHER_ALGO"

	count=0.0
	my_average=0.0
	sumy_average=0.0
	echo $algo
	for entry in "$search_dir"/*
	do
	  count=`echo $count + 1.0 |bc`
	  filename="$(echo $entry | awk -F'\\/' '{print $3}' | awk -F'\\_' '{print $1}')"
	  actual_summary=$search_dir"/"$filename"_summary.txt"
	  my_summary="gold_standard/my_summary/"$filename"_summary.txt"
	  sumy_summary="gold_standard/sumy_summary/"$filename"_summary.txt"
	  result_my_summary="$(/usr/bin/python -m sumy.evaluation $algo $actual_summary --file=$my_summary --format=plaintext | grep 'Rouge-1' | awk -F':' '{print $2}')"
	  my_average=`echo $my_average + $result_my_summary | bc`
	  result_sumy_summary="$(/usr/bin/python -m sumy.evaluation $algo $actual_summary --file=$sumy_summary --format=plaintext | grep 'Rouge-1' | awk -F':' '{print $2}')"
	  sumy_average=`echo $sumy_average + $result_sumy_summary | bc`
	  echo $filename, $result_my_summary, $result_sumy_summary
	done
	echo $algo
	python -c "print 'Precis Average Rouge-1 score', $my_average/$count"
	python -c "print 'Average Rouge-1 score', $sumy_average/$count"	
done