from flask import Flask, redirect, url_for, request, render_template
import tweepy as tw
import datetime
import re
import bs4
import requests
import json

app = Flask(__name__)

consumer_key= 'RcNjffhjgsMb7zbC8xt0YzxBO'
consumer_secret= 'o5N6pblbpMXY5I2Xyr9DwafU7tEdT8emkFdYXsoDg2OlCS9p4n'
access_token= '23436854-O6yEOHmjk9bPITfS65vUVuLITSXv9bnbkPA7EBEV3'
access_token_secret= 'zomrcG2Y0q59Dl5fTfZIIVAziyePQktmyvrFFyUCKTJ1j'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


def clean_input(tag):
    tag=tag.replace(" ","")
    if tag.startswith('#'):
        return tag[1:].lower()
    else:
        return tag.lower()
    
def get_date(months):
    x = datetime.datetime.now()
    if x.month-months<1:
        year=x.year-1
        month=12+ (x.month-months)
        return str(year)+'-'+str(month)+'-'+str(x.day)
    else:
        y=x.month-months
        return str(x.year)+'-'+str(y)+'-'+str(x.day)
    
def return_all_hashtags(tweets, tag):
    all_hashtags=[]
    for tweet in tweets:
        for word in tweet.split():
            
            if word.startswith('#'):
                word = re.sub(r'[^\w\s]','',word)
                if word.lower() != tag.lower():
                    all_hashtags.append('#'+word.lower())
    return all_hashtags

instagram_root = "https://www.instagram.com"
def extract_shared_data(doc):
        for script_tag in doc.find_all("script"):
            if script_tag.text.startswith("window._sharedData ="):
                shared_data = re.sub("^window\._sharedData = ", "", script_tag.text)
                shared_data = re.sub(";$", "", shared_data)
                shared_data = json.loads(shared_data)
                return shared_data

# retrieve twitter hashtags.

def get_tags_frequency(tag):
    search_word=clean_input(tag)
    date_since=1
    tweets = tw.Cursor(api.search,
              q='#'+search_word,
              lang="en",
              since=date_since).items(200)
    tweets_list=[]
    for tweet in tweets:
        tweets_list.append(tweet.text)
#retrieve instagram posts list

    url_string = "https://www.instagram.com/explore/tags/%s/" % search_word
    response = bs4.BeautifulSoup(requests.get(url_string).text, "html.parser")

#extract post list:
    shared_data = extract_shared_data(response)
    media=shared_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']

    posts=[]
    for post in media:
        if post['node']['edge_media_to_caption']['edges'] !=[]:
            posts.append(post['node']['edge_media_to_caption']['edges'][0]['node']['text'])

    all_tags= return_all_hashtags(tweets_list+posts, tag)

    frequency={}
    for item in set(all_tags):
        frequency[item]=all_tags.count(item)

    sorted_list= sorted(frequency.items(), key=lambda item: item[1], reverse= True)

    if len(sorted_list)>200:
        sorted_list=sorted_list[:100]

    return sorted_list



@app.route('/', methods = ['POST', 'GET'])
def search():
	if request.method == 'POST':
		tag = request.form['tag']
		final_list=get_tags_frequency(tag)
		return render_template('search.htm', tagslist=final_list)
	else:
		return render_template('search.htm')

if __name__ == '__main__':
   app.run()
   app.run(debug=true)