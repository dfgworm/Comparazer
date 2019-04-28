import scrapy
from re import compile,sub

allow=compile(r"^http")
deny=compile(r"ask\.com")
deny2=compile(r"askmediagroup")

class EntityExtractor(scrapy.Spider):
	name = "Extractor"
	
	quality="Best" #Best/Worst
	entType="book characters"
	entLabel='PERSON' #PERSON/ORG
	
	def start_requests(self):
		askcomurls = []
		
		askcompagesToScrap=10
		
		ent=sub(r"\s+","+",self.entType)
		for i in range(1,askcompagesToScrap+1):
			askcomurls.append("https://www.ask.com/web?q="+self.quality+"+"+ent+"&o=0&qo=pagination&qsrc=998&page="+str(i))
		for url in askcomurls:
			yield scrapy.Request(url=url, callback=self.askcom_parser)
	
	def askcom_parser(self, response):
		list=response.xpath("//a/@href").getall()
		for i in list:
			if (allow.search(i)!=None and deny.search(i)==None and deny2.search(i)==None):
				yield scrapy.Request(response.urljoin(i), callback=self.get_body)
	
	def get_body(self, response):
		string=" ".join(response.xpath("body//p/descendant-or-self::text()").getall())
		yield {"text":string}
	
	