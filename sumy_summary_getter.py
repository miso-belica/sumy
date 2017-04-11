import os
import glob
import json
import requests
import subprocess
import sys

files =  glob.glob("gold_standard/text_en/*.txt")
#print sys.argv[1]
text_counts=[]
for fil in files:
	with open(fil,  'r') as f:
	    read_data = f.read()
	text_counts.append(len(read_data.split()))

files =  glob.glob("gold_standard/summary_en/*.txt")
summary_counts=[]
for fil in files:
	with open(fil,  'r') as f:
	    read_data = f.read()
	summary_counts.append(len(read_data.split()))


ratio=[]
ratio=[round(1.0*summary_count/text_count, 2) for text_count, summary_count in zip(text_counts, summary_counts)]

files =  glob.glob("gold_standard/text_en/*.txt")
summaryfiles = glob.glob("gold_standard/summary_en/*.txt")


if not os.path.exists("gold_standard/sumy_summary/"):
    os.makedirs("gold_standard/sumy_summary/")
i=0
for fil, sumfile in zip(files, summaryfiles):
	len=str(int(ratio[i]*100)) + "%"
        result = subprocess.check_output("sumy "+sys.argv[1]+" --length=" + len + " --file=" + fil, shell=True)
	filename = "gold_standard/sumy_summary/" + sumfile.split("/")[2].split("_")[0] + "_summary.txt"
	with open(filename, 'w+') as fi:
        	fi.write(result)
        i+=1
        print i