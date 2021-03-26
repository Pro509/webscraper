import requests
import json
from random import randint
from time import sleep
from bs4 import BeautifulSoup as soup

city_url = "https://www.tripadvisor.com/Hotels-g293916-Bangkok-Hotels.html"
tripadvisor_url = "https://www.tripadvisor.com"
reviews = 15
city_page = requests.get(city_url)
print("status", city_page.status_code)

bs_obj = soup(city_page.content, 'html.parser')

def StrToInt(text):
    return int(text.replace(',',''))

def bubbleRatingVal(tags):
    rating = [value for element in tags.find_all(class_=True) 
        for value in element["class"]]
    rating = rating[1]
    return int(rating[(rating.find('_')+1):(rating.find('_')+3)])

def makeReviewPageLinks(bs_obj, reviews = 10):
    """ TripAdvisor review pages links for city-specific hotels """
    hotel_links = []
    for link in bs_obj.findAll('a', {'class': 'review_count'}):
        # print(type(link))
        review_count = StrToInt(link.get_text().split()[0])

        if review_count >= 100:
            # print(review_count, '\n')
            link_suffix = link['href']
            hotel = tripadvisor_url + link_suffix
            hotel_links.append(hotel)
            for i in range(5,reviews-4,5):
                next_page = hotel[:(hotel.find('Reviews')+7)]+ f'-or{i}' + hotel[(hotel.find('Reviews')+7):]
                hotel_links.append(next_page)
        else:
            pass

    return hotel_links

def getAvgReview():
    pass

city_dict = dict()

hotel_links = makeReviewPageLinks(bs_obj, reviews)


for link in hotel_links[:int(reviews/3)]:
    # print(link)
    review_page = requests.get(link)
    sleep(randint(1,4))
    reviews = soup(review_page.content, 'html.parser')

    # Saving hotel name to append page reviews appropriately
    hotel_name = reviews.find('h1').get_text()
    if hotel_name in city_dict:
        ids = city_dict[hotel_name]['reviews'].keys()
        counter = int(list(ids)[-1]) + 1
    else:
        city_dict[hotel_name] = {'reviews': {}}
        counter = 1
    print(hotel_name, '\n')
    
    for r in reviews.findAll('div', {'data-test-target':'HR_CC_CARD'}):
        # print(r,'\n')
        review_text = r.find('q').get_text() #r.span.text.strip()
        bubble = r.find('div', {'data-test-target':'review-rating'})
        rating = bubbleRatingVal(bubble)
        # print(rating)
        city_dict[hotel_name]['reviews'].update({f'{counter}': {'review_text': review_text, 'rating': rating}})
        counter += 1
        # print(review_text, '\n')



# print()
# print(json.dumps(city_dict, indent=4, sort_keys=True))

with open('data.json', 'w') as outfile:
    json.dump(city_dict, outfile, indent=4)

