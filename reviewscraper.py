import requests
from random import randint
from time import sleep
from bs4 import BeautifulSoup as soup

city_url = "https://www.tripadvisor.com/Hotels-g293916-Bangkok-Hotels.html"
tripadvisor_url = "https://www.tripadvisor.com"
reviews = 15
city_page = requests.get(city_url)
print("status", city_page.status_code)

bs_obj = soup(city_page.content, 'html.parser')

def makeReviewPageLinks(bs_obj, reviews = 10):
    """ TripAdvisor review pages links for city-specific hotels """
    hotel_links = []
    for link in bs_obj.findAll('a', {'class': 'review_count'}):
        # print(type(link))
        # print(link, '\n')
        link_suffix = link['href']
        hotel = tripadvisor_url + link_suffix
        hotel_links.append(hotel)
        for i in range(5,reviews+1,5):
            next_page = hotel[:(hotel.find('Reviews')+7)]+ f'-or{i}' + hotel[(hotel.find('Reviews')+7):]
            hotel_links.append(next_page)
        print("Done")

    return hotel_links


city_dict = dict()

hotel_links = makeReviewPageLinks(bs_obj, reviews)

for link in hotel_links[0:int(reviews/3)]: #
    print(link, '\n')
    review_page = requests.get(link)
    sleep(randint(1,4))
    reviews = soup(review_page.content, 'html.parser')
    hotel_name = reviews.find('h1').get_text()
    city_dict[hotel_name] = {'reviews': {}}
    counter = 1 #number of reviews counter
    print(hotel_name)
    
    for r in reviews.findAll('q'):
        review_text = r.span.text.strip()
        city_dict[hotel_name]['reviews'].update({f'{counter}': {'review': review_text, 'stars': None}})
        counter += 1
        # print(review_text, '\n')


import json
print()
print(json.dumps(city_dict, indent=4, sort_keys=True))


