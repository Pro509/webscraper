import requests
from random import randint
from time import sleep
from bs4 import BeautifulSoup as soup

city_url = "https://www.tripadvisor.com/Hotels-g293916-Bangkok-Hotels.html"
tripadvisor_url = "https://www.tripadvisor.com"
city_page = requests.get(city_url)
print("status", city_page.status_code)

bs_obj = soup(city_page.content, 'html.parser')

def makeReviewPageLinks(bs_obj, reviews = 10):
    """ TripAdvisor specific review page links for city hotels """
    hotel_links = []
    for link in bs_obj.findAll('a', {'class': 'review_count'}):
        # print(type(link))
        # print(link, '\n')
        link_suffix = link['href']
        hotel = tripadvisor_url + link_suffix
        hotel_links.append(hotel)
        for i in range(5,reviews+1,5):
            next_page = hotel[:(hotel.find('Reviews')+7)]
                        + f'-or{i}' + 
                        hotel[:(hotel.find('Reviews')+7)]
            hotel_links.append(next_page)
        print("Done")

    return hotel_links

for link in hotel_links[:3]:
    review_page = requests.get(link)
    sleep(randint(1,5))
    reviews = soup(review_page.content, 'html.parser')


