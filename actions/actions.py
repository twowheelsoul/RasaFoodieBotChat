# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
#import zomatopy
import json
import pandas as pd

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
respEmailString = ""
def RestaurantSearch(City,Cuisine):
    TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
    return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]

def getStringfromDf(df):
    global respEmailString
    resp = ""

    for index, row in df.iterrows():
        respEmailString = respEmailString + '\n'+'Name: ' + row['Restaurant Name'] + '\n'+'Address :'+ ' ' + row['Address'] + '\n'+'Avg Cost for two is :' + str(row['Average Cost for two']) + '\n'+ 'Rating : '+ str(row['Aggregate rating'])+'\n\n'
    
    for index, row in df.head(5).iterrows():
        resp = resp + '\n'+'Name: ' + row['Restaurant Name'] + '\n'+'Address :'+ ' ' + row['Address'] + '\n'+'Avg Cost for two is :' + str(row['Average Cost for two']) + '\n'+ 'Rating : '+ str(row['Aggregate rating'])+'\n\n'
    
    return resp


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'

        
    def run(self, dispatcher, tracker, domain):        
        count = 0
        config={ "user_key":""} #Get your key from zomato api
        isCityValid = True

        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        price_dict = {'low':1,'medium':2,'high':3}
        cities=['Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur', 'BokaroSteelCity', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-VirarCity', 'Vijayawada', 'Visakhapatnam', 'Vellore', 'Warangal', 'Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune']

        cities_lower=[x.lower() for x in cities]
        if loc.lower() not in cities_lower:
            isCityValid = False
            dispatcher.utter_message("Sorry, we don’t operate in this city. Can you please specify some other location")

        results = RestaurantSearch(City=loc,Cuisine=cuisine)
        d = results#json.loads(results)
        response="Showing you top rated restaurants:"+"\n"
        if d.shape[0] == 0:
            response= "No restaurant found for your criteria"
            dispatcher.utter_message(response)
        else:
            sorted_restaurants = d.sort_values(by=['Aggregate rating'],ascending=False)   
            count  = 0
            if(price_dict.get(price) == 1) :
                resp_restaurant = sorted_restaurants[sorted_restaurants["Average Cost for two"] < 300].head(10)
                count = resp_restaurant.shape[0]
                response = getStringfromDf(resp_restaurant)
            if(price_dict.get(price) == 2) :
                resp_restaurant = sorted_restaurants[sorted_restaurants["Average Cost for two"].between(300,700)].head(10)
                count = resp_restaurant.shape[0]
                response = getStringfromDf(resp_restaurant)   
            if(price_dict.get(price) == 3) :
                resp_restaurant = sorted_restaurants[sorted_restaurants["Average Cost for two"] > 700].head(10)
                count = resp_restaurant.shape[0]
                response = getStringfromDf(resp_restaurant)

        if(count==0):
            response = "Sorry, No results found for your criteria. Would you like to search for some other restaurants?"
            if isCityValid :
                dispatcher.utter_message(response)
        else :
            response = "Top 5 " + cuisine + " restaurants in " + loc + " with " + price + " price range :" + "\n" + response + "\n \n" 
            if isCityValid :
                dispatcher.utter_message(response)

        global respEmailString

        responseEmail = "Top 10 " + cuisine + " restaurants in " + loc + " with " + price + " price range :" + "\n" + respEmailString + "\n \n" 

        if isCityValid:
            return [SlotSet('emailbody',responseEmail)]
        else :
            return [SlotSet('location',loc)]

        
class ActionSendEmail(Action):

    def name(self):
        return 'action_sendemail'

    def run(self, dispatcher, tracker, domain):
        from_user = 'upgardtestemail@gmail.com' # provide your google email id
        to_user = tracker.get_slot('email')
        password = 'upgrad1234#' # provide ur gmail password
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(from_user, password)
        subject = 'RASA Foodie Chat Bot: Top 10 Restaurants for you'
        msg = MIMEMultipart()
        msg['From'] = from_user
        msg['TO'] = to_user
        msg['Subject'] = subject
        body = tracker.get_slot('emailbody')
        body_header = '''Dear Customer, \n \n'''
        body_footer = '''\n\n Thanks & Regards \n It was pleasure serving You \n Please visit us again :)'''
        body = body_header+body+body_footer
        msg.attach(MIMEText(body,'plain'))
        text = msg.as_string()
        server.sendmail(from_user,to_user,text)
        server.close()
        
class ActionCheckLocation(Action):

    def name(self):
        return 'action_chklocation'

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        
        cities=['Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur', 'BokaroSteelCity', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-VirarCity', 'Vijayawada', 'Visakhapatnam', 'Vellore', 'Warangal', 'Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune']

        cities_lower=[x.lower() for x in cities]
        
        if loc.lower() not in cities_lower:
            dispatcher.utter_message("Sorry, we don’t operate in this city. Can you please specify some other location")
        return     