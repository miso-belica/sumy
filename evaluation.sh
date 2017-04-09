#!/bin/sh

python summary_getter.py

search_dir="gold_standard/summary_en"

echo "FILENAME, MY_ALGO, OTHER_ALGO"
for entry in "$search_dir"/*
do
  filename="$(echo $entry | awk -F'\\/' '{print $3}' | awk -F'\\_' '{print $1}')"
  actual_summary=$search_dir"/"$filename"_summary.txt"
  my_summary="gold_standard/my_summary/"$filename"_summary.txt"
  sumy_summary="gold_standard/sumy_summary/"$filename"_summary.txt"
  result_my_summary="$(/usr/local/bin/python -m sumy.evaluation text-rank $actual_summary --file=$my_summary --format=plaintext | grep 'Rouge-1' | awk -F':' '{print $2}')"
  result_sumy_summary="$(/usr/local/bin/python -m sumy.evaluation text-rank $actual_summary --file=$sumy_summary --format=plaintext | grep 'Rouge-1' | awk -F':' '{print $2}')"
  echo $filename, $result_my_summary, $result_sumy_summary
done
