from scrapy.exceptions import DropItem
import spacy
import re
from functools import reduce
# Using Textblob as for it's simple sentiment analysis function
from textblob import TextBlob

nlp=spacy.load("en_core_web_lg")

# Regexp patterns for cleaning text
patterns=[]
#0
pattern=re.compile(r"(\s*'s\s*)|(\s*[^\w\s']+\s*)|(\s*\d+\s*)")
patterns.append(pattern)
#1
pattern=re.compile(r"(\\.){2,}|(\\r)+|(\\n)+|(\\t)+")
patterns.append(pattern)
#2
pattern=re.compile(r"[\[{(].*?[\]})]")
patterns.append(pattern)
#3
pattern=re.compile(r"[.?!,:;\"]+")
patterns.append(pattern)
#4
pattern=re.compile(r"\s{2,}")
patterns.append(pattern)
#5
patterns.append(re.compile(r"[|/\\]+"))
#6
patterns.append(re.compile(r"\s"))

class ComparazerPipeline(object):
	def process_item(self, item, spider):
		try:
			#process raw text to remove unnecessary parts
			string=item["text"]
			string=patterns[1].sub(" ",string)
			string=patterns[2].sub(" ",string)
			string=patterns[3].sub(lambda a: a.group(0)[0]+" ",string)
			string=patterns[4].sub(" ",string)
			if spider.name=="Extractor": item["text"]=string
			#extract needed entities
			string=nlp(string)
			entities=list(filter(lambda a: a.label_==spider.entLabel,string.ents))
			var=[patterns[5].split(u.lemma_) for u in entities]
			if len(var)==0:
				raise DropItem("No Entities")
			# Pipeline for Extractor, which extracts names from texts
			if spider.name=="Extractor":
				#filter and process names to remove unnecessary characters
				var=reduce(lambda a,b: a+b,var)
				var=map(lambda a: patterns[4].sub(" ",patterns[0].sub(" ",a)).strip(),var)
				var=filter(lambda a: len(patterns[6].findall(a))<4 and len(a)>3 and len(nlp(a).ents)==1 and nlp(a).ents[0].label_==spider.entLabel,var)
				var=list(var)
				if len(var)==0:
					raise DropItem("No Proper Entities")
				# export
				item["ents"]=var
				return item
			# Pipeline for Affirmator, which cleans, sorts and evaluates scores for names
			elif spider.name=="Affirmator":
				#filter and process names to remove unnecessary characters
				var=map(lambda a: patterns[4].sub(" ",patterns[0].sub(" ",a[0])).strip(),var)
				var=map(lambda a: a if len(patterns[6].findall(a))<4 and len(a)>3 and len(nlp(a).ents)==1 else False,var)
				var=dict(list((i,u.lower()) for i,u in enumerate(list(var)) if u!=False))
				#select only entities that are being evaluated
				for i in list(var.keys()):
					if var[i] in spider.names.keys(): var[i]=spider.names[var[i]]
					else:
						if var[i] in spider.extracts: var[i]=[var[i]]
						else:
							li=[]
							for u in spider.extracts:
								if (var[i] in u) or (u in var[i]): li.append(u)
							var[i]=li
							if len(li)<1: del var[i]
				if len(var)==0:
					raise DropItem("No Target Entities")
				#for each name take it's sentence and neighbouring sentences and evaluate sentiment
				#sentiment is then added to a this name's weight and name's count is incremented
				for i in var.keys():
					txt=entities[i].sent.text
					num=entities[i].sent[0].i-1
					if num>0: txt=string[num].sent.text+' '+txt
					num=entities[i].sent[-1].i+1
					if num<len(string): txt=txt+' '+string[num].sent.text
					sentiment=TextBlob(txt).sentiment.polarity
					for u in var[i]:
						if spider.weights.get(u)!=None:
							spider.weights[u]=spider.weights[u]+sentiment/len(var[i])
							spider.counts[u]=spider.counts[u]+1/len(var[i])
				raise DropItem("Succesfully analized")
		except UnicodeEncodeError:
			raise DropItem("UNICODE ERROR")
		
		
	def open_spider(self, spider):
		if spider.entLabel=='Detect':
			org=('company','organization')
			person=('person','human')
			org=list(map(lambda a: nlp(a),org))
			person=list(map(lambda a: nlp(a),person))
			num=0
			word=nlp(spider.entType)
			for a in org:
				num=num+word.similarity(a)
			for a in person:
				num=num-word.similarity(a)
			if num>0: spider.entLabel='ORG'
			else: spider.entLabel='PERSON'
			
	def close_spider(self, spider):
		if spider.name=="Affirmator":
			#sort names by weight/count, and write them to a file
			with open('weights'+'_'+re.sub(r'\s+','_',spider.entType)+'.txt','w', encoding="utf-8") as file:
				li=list(filter(lambda a: spider.counts[a]!=0,spider.weights.keys()))
				li.sort(key=lambda a: spider.weights[a]/spider.counts[a],reverse=True)
				for i in li:
					file.write(i+':'+str(spider.weights[i]/spider.counts[i]))
					file.write(':total:'+str(spider.weights[i]))
					file.write(':count:'+str(spider.counts[i])+'\n')
		elif spider.name=='Extractor':
			with open('entType.txt','w',encoding='utf-8') as file:
				file.write(list(nlp(spider.entType).noun_chunks)[0].lemma_+','+spider.entLabel)
	