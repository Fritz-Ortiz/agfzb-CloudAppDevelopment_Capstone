import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {}".format(url))
    try:
        # Call the get method of the requests library with the URL and parameters
        if api_key:
            # Basic authentication GET
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # No authentication GET
            response = requests.get(url, params=kwargs)
        
        status_code = response.status_code
        #print("With status {}".format(status_code))
        
        json_data = response.json()
        return json_data
    
    except Exception as e:
        # If any error occurs
        print("Error:", e)
        return None


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(json_payload)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        print(json_data)
        return json_data
    except:
        print("Network exception occurred")


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):    
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    #print(json_result)
    
    if json_result:
        # Get the row list in JSON as dealers
        #dealers = json_result["rows"]
        
        
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                short_name=dealer_doc["short_name"],
                                st=dealer_doc["st"], zip=dealer_doc["zip"], state=dealer_doc["state"], _id=dealer_doc["_id"], _rev=dealer_doc["_rev"])
                                
            
            results.append(dealer_obj)

    return results





# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_from_cf_by_id(url, dealer_id):
    json_result = get_request(url, id=dealer_id)
    
    if json_result:
        dealer = json_result[0]
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                               id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], zip=dealer["zip"], _id=dealer["_id"], _rev=dealer["_rev"], state=dealer["state"])
    print(dealer_obj) 
    return dealer_obj  
     


def get_dealer_reviews_from_cf(url, dealer_id):
    
    json_result = get_request(url,id=dealer_id)
    #print(json_result)
    results = []
    if json_result:
        results = []
        
        reviews = json_result
        #print(reviews)
        
        for review in reviews:
            
            if review["purchase"]:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=str(review["purchase_date"]),
                    car_make=review["car_make"],
                    car_model=review["car_model"],
                    car_year=review["car_year"],
                    sentiment=analyze_review_sentiments(review["review"]),
                    id=review['id']
                )
            else:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=None,
                    car_make=None,
                    car_model=None,
                    car_year=None,
                    sentiment=analyze_review_sentiments(review["review"]),
                    id=review['id']
                )
            print("sentiment: XXXXXXXXXX BELOW THIS LINE XXXXXXXXXXXX")
            print(review_obj.sentiment)
            print(review_obj.review)
            
            results.append(review_obj.review)
            #print(results)
    return results




# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

   
def analyze_review_sentiments(dealer_review):
    API_KEY = "mZgf-pc4lsO3scdzMThaDn4x1Z1hWcpNDkbEvzkCC8Sv"
    NLU_URL = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/e031438f-f190-4d82-91f6-e3c7a600b8a4"
    authenticator = IAMAuthenticator(API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01', authenticator=authenticator)
    natural_language_understanding.set_service_url(NLU_URL)
    response = natural_language_understanding.analyze(text=dealer_review, features=Features(
        sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return(label)
    




    



