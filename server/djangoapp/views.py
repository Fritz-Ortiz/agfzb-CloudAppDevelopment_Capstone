from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf,get_dealer_from_cf_by_id, analyze_review_sentiments, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.



# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html',context)

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html',context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://fritzortiz27-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)
       


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    print("XXX IN GET DEALER DETAILS VIEW XXX")
    if request.method == "GET":
        context = {}
        
        reviews = get_dealer_reviews_from_cf("https://fritzortiz27-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews", dealer_id)
        analyzed_reviews = []
        print("XXX REVIEWS RECIEVED XXX")
        print(reviews)
        
        context["reviews"] = reviews
        dealer = get_dealer_from_cf_by_id(
            "https://fritzortiz27-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get", dealer_id)
        context["dealer"] = dealer
        print(" XXX CONTEXT XXX")
        print(context)
        print("XXX DONE WITH GET DEALER DETAILS VIEW XXX")
        return render(request, 'djangoapp/dealer_details.html', context)




# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id,):
    context = {}
    if request.method == "GET":
        url = "https://fritzortiz27-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_from_cf_by_id(url, dealer_id)
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars
        context["dealer"] = dealer
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        #info = request.POST.values()
        url = "https://fritzortiz27-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"      
        if 'purchase' in request.POST:
            was_purchased = True
        else:
            was_purchased = False
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        for car in cars:
            if car.id == int(request.POST['car']):
                review_car = car 

        #Creating review ID
        
        input_string = request.POST['content']
        # Convert string to a list of characters
        characters = list(input_string)

        # Use set to remove duplicates and sort the characters
        unique_characters = sorted(set(characters))

        # Concatenate the ASCII values as a string
        ascii_values_string = ''.join(str(ord(char)) for char in unique_characters)

        # Convert the concatenated string to an integer
        total = int(ascii_values_string) 

        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.POST['name']
        review["dealership"] = dealer_id
        review["review"] = request.POST['content']
        review["purchase"] = was_purchased
        review["purchase_date"] = request.POST['purchase_date']
        review["car_make"] = review_car.make.name
        review["car_model"] = review_car.name
        review["car_year"] = review_car.year.strftime("%Y")
        review["id"] = total
        json_payload = {}
        json_payload = review
        print("XXX JSON FOR REVIEW XXX")
        print(json_payload.values())
        response = post_request(url, json_payload)
        print("XXX RESPONSE XXX")
        print(response)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
