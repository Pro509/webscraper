import os
import requests
import json
from random import randint, shuffle
from time import sleep, time
from bs4 import BeautifulSoup as soup
from progress.bar import IncrementalBar

def StrToInt(text):
    return int(text.replace(',',''))

def bubbleRatingVal(tags):
    rating = [value for element in tags.find_all(class_=True) 
        for value in element["class"]]
    rating = rating[1]
    return int(rating[(rating.find('_')+1):(rating.find('_')+3)])

def getAvgRating(reviews_page):
    '''Gets the average rating of the hotel based on all reviews'''
    rating_obj = reviews_page.find('div', {'class':'kVNDLtqL'}).get_text()
    # Test: print(rating_obj) = '4.5Excellent2,385 reviews'
    Avg_rating = int(float(rating_obj[:3])*10)
    return Avg_rating

def makeReviewPageLinks(bs_obj, reviews = 10, nofHotels = 10):
    """ TripAdvisor review pages links for city-specific hotels """
    tripadvisor_url = "https://www.tripadvisor.com"
    hotel_links = []
    hotelsReviews = bs_obj.findAll('a', {'class': 'review_count'})
    for link in hotelsReviews:
        review_count = StrToInt(link.get_text().split()[0])
        if review_count >= reviews:
            pass
        else:
            hotelsReviews.remove(link)

    bar = IncrementalBar('Generating Hotel Links', max = nofHotels)
    for link in hotelsReviews[:nofHotels]:
        # print(type(link))
        # print(review_count, '\n')
        link_suffix = link['href']
        hotelLink = tripadvisor_url + link_suffix
        hotel_links.append(hotelLink)
        for i in range(5,reviews-4,5):
            next_page = hotelLink[:(hotelLink.find('Reviews')+7)]+ f'-or{i}' + hotelLink[(hotelLink.find('Reviews')+7):]
            hotel_links.append(next_page)

        bar.next()
    bar.finish()
    return hotel_links

def get(link):
    '''Converting URL to beautiful soup object: Forceful and ensures task completion'''
    r = None
    try:
        r = requests.get(link, timeout=5).text
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
    # continue in a retry loop
        print(f"Faced {e}, retrying")
        sleep(1)
        get(link)
    # except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        # when catastrophic error. bail.
        # raise SystemExit(e)
    
    # Making BeautifulSoup Object
    if r is not None: 
        r_bs_obj = soup(r, 'html.parser')
        if r_bs_obj is not None:
            return r_bs_obj
        else:
            sleep(0.5)
            get(link)
    else:
        get(link)
    
def reviewExtract(hotel_links):
    city_dict = dict()
    # Status checking setup
    start = time()
    bar = IncrementalBar('Extracting Hotel Reviews', max = len(hotel_links), suffix='%(percent)d%%')
    
    for link in hotel_links:
        sleep(randint(1,3))
        # print(link)
        reviews = get(link)   # deprecated from review_page to reviews
        sleep(1)
        # print(type(reviews), link)
        if reviews is not None:
            pass
        else:
            print(f"\nNoneType response found in:\n{link}, retrying")
            reviews = get(link)
            # reviews = soup(reviews.content, 'html.parser')

        # Saving hotel name to append page reviews appropriately
        try:
            hotel_name = reviews.find('h1')
            hotel_name = hotel_name.get_text()
        except AttributeError:
            print(f"No heading found in:\n{link}")
        
        # Setting review index numbers
        if hotel_name in city_dict:
            ids = city_dict[hotel_name]['reviews'].keys()
            counter = int(list(ids)[-1]) + 1
        else:
            hotel_rating = getAvgRating(reviews)
            city_dict[hotel_name] = {'avg_rating': hotel_rating,'reviews': {}}
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
    end = time()
    bar.finish()
    print(f"{((end-start)/60):.2f} mins taken")
    return city_dict

if __name__=="__main__":
    city_url = input("City URL: ")
    reviews_demand = int(input("No. of reviews (in multiples of 5): "))
    nofHotels = int(input("Hotels: "))
    fileName = input("Output file Name: ")

    city_page = requests.get(city_url)
    bs_obj = soup(city_page.content, 'html.parser')

    print(f"URL Status: {city_page.status_code}")
    
    hotel_links = makeReviewPageLinks(bs_obj, reviews=reviews_demand, nofHotels=nofHotels)
    data = reviewExtract(hotel_links)

    # Export reviews to JSON file
    with open(os.path.join('test output', f'{fileName}.json'), 'w') as outfile:
        json.dump(data, outfile, indent=4)

