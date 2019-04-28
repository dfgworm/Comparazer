import scrapy
import re
import pandas as pd
from math import floor
from functools import reduce
allow=re.compile(r"^http")
deny=re.compile(r"ask\.com")
deny2=re.compile(r"askmediagroup")

class DataAffirmator(scrapy.Spider):
	name = "Affirmator"
	
	quality="Best" #Best/Worst
	entType=''
	entLabel=''
	#reading type of entity passed by Extractor
	with open('entType.txt','r',encoding='utf-8') as file:
		txt=file.read() 
		txt=txt.split(',')
		entType=txt[0]
		entLabel=txt[-1]
	minimumResults=20 #minimum amount of names to seek for
	def start_requests(self):
		#getting lists of names
		self.extracts=pd.read_csv('C:\\Users\\navi\\Dropbox\\Development\\Scrappy\\Comparazer\\Extractor.csv',encoding='utf-8',chunksize=1,iterator=True)
		self.extracts=list(map(lambda u: u['ents'].iloc[0].split(','),self.extracts)) 
		#entities from each text are in separate lists
		for i in range(len(self.extracts)):
			li=[]
			#removing repetitions from each individual list separately
			for e in self.extracts[i]: 
				if e.lower() not in map(lambda u: u.lower(),li):
					#check if one name is a part of any another
					for u in self.extracts[i]: 
						if e.lower() in u.lower() and e.lower()!=u.lower(): break
					else:
						li.append(e)
			self.extracts[i]=li
		self.shortcuts={}
		counts={}
		#saves a link between original name and it's lowercase copy
		for i in self.extracts: 
			#also counts occurences of the same name in different texts
			for u in i: 
				self.shortcuts[u.lower()]=self.shortcuts.get(u.lower()) or u
				counts[u.lower()]=(counts.get(u.lower()) or 0)+1
		
		self.extracts=self.shortcuts.keys()
		self.names={}
		#checks if a name is a part of other names and saves the list of these parents
		for e in self.extracts: 
			for u in self.extracts:
				#does not trigger if parent is less frequent than child
				if (e in u) and e!=u and counts[u]>=counts[e]: 
					self.names[e]=self.names.get(e) or []
					self.names[e].append(u)
		for e in list(self.names.keys()): #list of parents should only contain names with no parents
			while len(set(self.names.keys())&set(self.names[e]))>0:
				li=[]
				for num,u in enumerate(self.names[e]): li.append(self.names.get(u) or [u])
				self.names[e]=list(set(reduce(lambda a,b: a+b,li)))
		#spread number of occurences of children among their parents and delete them
		for e in self.names.keys(): 
			li=list(filter(lambda a: a not in self.names.keys(),self.names[e]))
			for u in li:
				counts[u]=counts[u]+counts[e]/len(li)
			del counts[e]
		#exclude results with low number of occurences
		#include more results if got too few
		m=4
		while m>1 and len(list(filter(lambda a: a>=m,counts.values())))<self.minimumResults:
			m=m-1
		self.extracts=[u for u in self.shortcuts.keys() if counts.get(u) and counts[u]>=m]
		self.weights={}
		self.counts={}
		for i in self.extracts:
			self.weights[i]=0
			self.counts[i]=0
		
		#write list of names with their number of occurences (mostly for debug)
		with open('names_'+re.sub(r'\s+','_',self.entType)+'.txt','w', encoding="utf-8") as file:
			for i in self.extracts: #
				file.write(i+':'+self.shortcuts[i]+':'+str(counts[i])+'\n')
		
		askcomurls = []
		askcompagesToScrap=1
		ent=re.sub(r"\s+","+",self.entType)
		#scrape all urls on a single page of askcom for each name
		for i in range(1,askcompagesToScrap+1):
			for j in self.extracts:
					url="https://www.ask.com/web?q="+j+"+"+ent+"&o=0&qo=pagination&qsrc=998&page="+str(i)
								
					yield scrapy.Request(url=url, callback=self.askcom_parser)
	def get_body(self, response):
		string=" ".join(response.xpath("body//p/descendant-or-self::text()").getall())
		yield {'text':string}
	def askcom_parser(self, response):
		list=response.xpath("//a/@href").getall()
		for i in list:
			if (allow.search(i)!=None and deny.search(i)==None and deny2.search(i)==None):
				yield scrapy.Request(response.urljoin(i), callback=self.get_body)
	