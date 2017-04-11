import os
import glob
import json
import requests
import subprocess
from collections import defaultdict
files =  glob.glob("gold_standard/text_en/*.txt")

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

#print text_counts
#print summary_counts

ratio=[]
ratio=[round(1.0*summary_count/text_count, 2) for text_count, summary_count in zip(text_counts, summary_counts)]

print ratio
files =  glob.glob("gold_standard/text_en/*.txt")
summaryfiles = glob.glob("gold_standard/summary_en/*.txt")
i = 0

if not os.path.exists("gold_standard/my_summary/"):
    os.makedirs("gold_standard/my_summary/")

for fil, sumfile in zip(files, summaryfiles):
	
	with open(fil,  'r') as f:
	    read_data = f.read()
	url = "http://precis.herokuapp.com/summary"
	payload = {"ratio":ratio[i],"text":read_data}
	headers = {'content-type': 'application/json'}
	response=requests.post(url, data=json.dumps(payload), headers=headers)
	mysum=response.json()
	summary = mysum["summary"]
	summary  = summary.encode('ascii','ignore')
	filename = "gold_standard/my_summary/" + sumfile.split("/")[2].split("_")[0] + "_summary.txt"
	with open(filename, 'w+') as fi:
		fi.write(summary)
	i+=1
	print i

if not os.path.exists("gold_standard/sumy_summary/"):
    os.makedirs("gold_standard/sumy_summary/")
i=0
for fil, sumfile in zip(files, summaryfiles):
	len=str(int(ratio[i]*100)) + "%"
        result = subprocess.check_output("sumy text-rank --length=" + len + " --file=" + fil, shell=True)
	filename = "gold_standard/sumy_summary/" + sumfile.split("/")[2].split("_")[0] + "_summary.txt"
	with open(filename, 'w+') as fi:
        	fi.write(result)
        i+=1
        print i
