import os
import config
import googleapiclient.discovery
import googleapiclient.errors
import tweepy
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import dfgui
import csv
from tkinter import *
from functools import partial

   
def twitter(search):
    global errorlabel
    if errorlabel:
        errorlabel.destroy()
    search = search.get()
    #api keys provided by twitter
    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    access_key= config.access_key
    access_secret = config.access_secret
    tweet_num = 5
    tweets = []
    data = []
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    #getting results from search  
    results = tweepy.Cursor(api.search_tweets,q=search+ " -filter:retweets",
                               lang="en").items(tweet_num)
    #filling up data into lists
    for status in results:
      if status.lang == 'en':
        data = {'User': status.user.name,
            'Account name': '@'+status.user.screen_name, 
            'Tweet': status.text, 
            'Time': status.created_at,
            'Nr of retweets': status.retweet_count,
            'Nr of favorited': status.favorite_count}
        tweets.append(data)
    if len(data):
        #coverting that data into a csv and gui
        twitinfo = pd.DataFrame(tweets)  
        twitinfo.head()
        twitinfo.to_csv('twitter.csv', encoding='utf-8')
        print (twitinfo)
        dfgui.show(twitinfo)
    else:
        errorlabel = Label(tk, text="No data available for search, please retry")
        errorlabel.place(x=160, y=430)
def youtube(search):
    global errorlabel
    if errorlabel:
        errorlabel.destroy()
    search = search.get()
    rows = []
    videoID = []
    SCOPES = 'https://www.googleapis.com/auth/youtube.force-ssl'
    api_service_name = "youtube"
    api_version = "v3"
    API_KEY = config.API_KEY
    youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = API_KEY)
    #searching for video
    request = youtube.search().list(
            part="id,snippet",
            type='video',
            q=search,
            videoDuration='any',
            videoDefinition='any',
            maxResults=1,
            fields="nextPageToken,items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))"
    )
    response = request.execute()
    #for each video found looks through comments
    for items in response['items']:
        videoID.append(items['id']['videoId'])
        try:
            for item in videoID:
                video_response=youtube.commentThreads().list(
                part='id,snippet,replies',
                videoId=item,
                maxResults=6
                ).execute()
                #grabs the comments and places them in list
                for item in video_response['items']:
                    comment = str(item['snippet']['topLevelComment']['snippet']['textDisplay'])
                    rows.append([
                            items['snippet']['channelTitle'],
                            items['snippet']['title'],
                            items['snippet']['description'],comment])
        except:
            print("Video has comments disabled")
            
    if len(rows):
        #coverts into an csv and gui
        ytinfo = pd.DataFrame(rows, columns = ["Channel Name", "Title", "Description", "Comment" ])
        ytinfo.to_csv('youtube.csv', encoding='utf-8')
        print(ytinfo)
        dfgui.show(ytinfo)
    else:
        errorlabel = Label(tk, text="No data available for search, please retry")
        errorlabel.place(x=160, y=430)
        
    
#building gui
tk = Tk()
tk.geometry("600x500")
tk.title("Please Choose")
searchLabel = Label(tk, text="Search for Data:").place(x=140, y=150)
search = StringVar()
errorlabel = None
searchEntry = Entry(tk, textvariable=search).place(x=230, y=150)
youtube = partial(youtube, search)
twitter = partial(twitter, search)
b1 = Button(tk, text="On Twitter", command=twitter).place(x=180, y=200)
b2 = Button(tk, text="On YouTube", command=youtube).place(x=280, y=200)
tk.mainloop()     
