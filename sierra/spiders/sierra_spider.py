import scrapy
import scrapy
import json
import re


class SierraSpiderSpider(scrapy.Spider):
    name = "sierra_spider"
    
    custom_settings = {
		'FEEDS': {
			'sierra.csv': {
				'format': 'csv',
				'encoding': 'utf-8-sig',
				'overwrite': True,
			},
		},
	}
    
    def start_requests(self):
        # Recent change (2022-03), supplier introduced separate B2B shop
        yield scrapy.Request('https://www.sierra.com/', callback=self.parse_category)

    def parse_category(self,response):

        categories=response.xpath("//div[contains(@class,'categories-title')]/following-sibling::a/@href").extract()
        for category in categories:
            category=f'https://www.sierra.com{category}'
            print(category)
            yield scrapy.Request(category, callback=self.parse_category_page)
            break

    def parse_category_page(self,response):

        product_links=response.xpath('//a[@class="display-block text-truncate js-productThumbnail"]/@href').extract()
        for product_link in product_links:
            product_link=f'https://www.sierra.com{product_link}'
            print(product_link)
            yield scrapy.Request(product_link, callback=self.scrape_product_page)
            # break
            
        # nextpage=response.xpath('//a[@aria-label="Go to Next Page"]/@href').get()
        # if nextpage:
        #     nextpage=f'https://www.sierra.com{nextpage}'
        #     yield scrapy.Request(nextpage, callback=self.parse_category_page)

    def scrape_product_page(self,response):

        script_data = response.xpath("//script[contains(text(),'ecommerce')]/text()").get()
        
        if script_data:
            # Extract the JSON part of the script using regex
            json_data = re.findall(r'({"products".+dimension20":[^\]]+]})', script_data)
            if json_data:
                # json_text = 
                data=json_data[0]
                # Remove dataLayer.push({ }) parts to extract only JSON
                # json_text = json_text.replace('dataLayer.push(', '').replace(');', '')
                # data = json.loads(data)
                product_info = json.loads(data)
                product_data= {
                    'id': product_info['products'][0]['id'],
                    'name': product_info['products'][0]['name'],
                    'brand': product_info['products'][0]['brand'],
                    'category': product_info['products'][0]['category'],
                    'variant': product_info['products'][0]['variant'],
                    'price': product_info['products'][0]['price'],
                    'rrPrice': product_info['products'][0]['rrPrice'],
                    'discountPrice': product_info['products'][0]['discountPrice'],
                    'discount': product_info['products'][0]['discount'],
                    'productParentStock': product_info['products'][0]['productParentStock'],
                    'productChildStock': product_info['products'][0]['productChildStock'],
                    'product_url':response.url
                }
                techs=response.xpath("//h3[contains(text(),'Specs')]/following-sibling::div/ul/li/text()").extract()
                tech_dict={}
                for tech in techs:
                    data=tech.split(':')
                    if len(data)>1:
                        key=data[0]
                        value=data[1]
                        tech_dict[key]=value
                product_data['techs'] = tech_dict                   
                yield product_data
                                    
                
              