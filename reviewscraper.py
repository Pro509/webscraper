import requests
import json
from random import randint
from time import sleep
from bs4 import BeautifulSoup as soup
from progress.bar import IncrementalBar

def StrToInt(text):
    return int(text.replace(',',''))

def bubbleRatingVal(tags):
    rating = [value for element in tags.find_all(class_=True) 
        for value in element["class"]]
    rating = rating[1]
    return int(rating[(rating.find('_')+1):(rating.find('_')+3)])

def makeReviewPageLinks(bs_obj, reviews = 10):
    """ TripAdvisor review pages links for city-specific hotels """
    tripadvisor_url = "https://www.tripadvisor.com"
    hotel_links = []
    hotelsReviews = bs_obj.findAll('a', {'class': 'review_count'})
    bar = IncrementalBar('Generating Hotel Links', max = len(hotelsReviews))
    for link in hotelsReviews:
        # print(type(link))
        review_count = StrToInt(link.get_text().split()[0])

        if review_count >= 100:
            # print(review_count, '\n')
            link_suffix = link['href']
            hotelLink = tripadvisor_url + link_suffix
            hotel_links.append(hotelLink)
            for i in range(5,reviews-4,5):
                next_page = hotelLink[:(hotelLink.find('Reviews')+7)]+ f'-or{i}' + hotelLink[(hotelLink.find('Reviews')+7):]
                hotel_links.append(next_page)
        else:
            hotelsReviews.remove(link)

        bar.next()
    bar.finish()
    return hotel_links

def getAvgReview():
    pass

def reviewExtract(hotel_links):
    city_dict = dict()
    bar = IncrementalBar('Extracting Hotel Reviews', max = len(hotel_links), suffix='%(percent)d%%')
    for link in hotel_links:
        # print(link)
        review_page = requests.get(link)
        sleep(randint(1,2))
        reviews = soup(review_page.content, 'html.parser')

        # Saving hotel name to append page reviews appropriately
        hotel_name = reviews.find('h1').get_text()
        if hotel_name in city_dict:
            ids = city_dict[hotel_name]['reviews'].keys()
            counter = int(list(ids)[-1]) + 1
        else:
            city_dict[hotel_name] = {'reviews': {}}
            counter = 1
        # print(hotel_name, '\n')
        
        for r in reviews.findAll('div', {'data-test-target':'HR_CC_CARD'}):
            # print(r,'\n')
            review_text = r.find('q').get_text() #r.span.text.strip()
            bubble = r.find('div', {'data-test-target':'review-rating'})
            rating = bubbleRatingVal(bubble)
            # print(rating)
            city_dict[hotel_name]['reviews'].update({f'{counter}': {'review_text': review_text, 'rating': rating}})
            counter += 1
            # print(review_text, '\n')
        bar.next()
    bar.finish()
    return city_dict

if __name__=="__main__":
    city_url = input("City URL: ")
    reviews = int(input("No. of reviews (in multiples of 5): "))
    fileName = input("Output file Name: ")
    city_page = requests.get(city_url)
    print(f"Your Page Status: {city_page.status_code}")
    bs_obj = soup(city_page.content, 'html.parser')

    hotel_links = makeReviewPageLinks(bs_obj, reviews)
    data = reviewExtract(hotel_links)

    with open(f'{fileName}.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

