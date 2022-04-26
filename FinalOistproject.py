import os
import logging
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
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from functools import partial

   
def twitter(search):
    global errorlabel
    if errorlabel:
        errorlabel.destroy()
    search = search.get()
    with open('searchlog.txt', 'a+') as f:
        f.write(search)
        f.write('\n')
        f.close()
    #api keys provided by twitter
    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    access_key= config.access_key
    access_secret = config.access_secret
    tweet_num = 8
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
        twitinfo.to_csv('twitter.csv', mode='a+',encoding='utf-8')
        print (twitinfo)
        dfgui.show(twitinfo)
        
    else:
        errorlabel = Label(tk, text="No data available for search, please retry", bg='#ffffff')
        errorlabel.place(x=65, y=300)
        with open('errorlogs.txt', 'a+') as f:
            f.write("No data available for ")
            f.write(search)
            f.write('\n')
            f.close()
def youtube(search):
    global errorlabel
    if errorlabel:
        errorlabel.destroy()
    search = search.get()
    with open('searchlog.txt', 'a+') as f:
        f.write(search)
        f.write('\n')
        f.close()
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
                maxResults=8
                ).execute()
                #grabs the comments and places them in list
                for item in video_response['items']:
                    comment = str(item['snippet']['topLevelComment']['snippet']['textDisplay'])
                    rows.append([
                            items['snippet']['channelTitle'],
                            items['snippet']['title'],
                            items['snippet']['description'],comment])
        except:
            with open('errorlogs.txt', 'a+') as f:
                f.write(search)
                f.write(" ,video has comments disabled")
                f.write('\n')
            f.close()
            print(search," video has comments disabled")
            
    if len(rows):
        #coverts into an csv and gui
        ytinfo = pd.DataFrame(rows, columns = ["Channel Name", "Title", "Description", "Comment" ])
        ytinfo.to_csv('youtube.csv',mode='a+', encoding='utf-8')
        print(ytinfo)
        dfgui.show(ytinfo)
    else:
        errorlabel = Label(tk, text="No data available for search, please retry", bg='#ffffff')
        errorlabel.place(x=65, y=300)
        with open('errorlogs.txt', 'a+') as f:
            f.write("No data available for ")
            f.write(search)
            f.write('\n')
        f.close()
def csv():
    filetypes = (
        ('csv files', '*.csv'),
        ('All files', '*.csv*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    if filename:
        openedCSV = pd.read_csv(filename)
        if ("twitter.csv" in str(filename)):
            new = openedCSV[~openedCSV['Nr of retweets'].isin(['Nr of retweets'])]
            dfgui.show(new)
        elif("youtube.csv" in str(filename)):
            new = openedCSV[~openedCSV['Channel Name'].isin(['Channel Name'])]
            dfgui.show(new)
        else:
            dfgui.show(openedCSV)
def viewHistory():
    tk = Tk()
    tk.geometry("600x500")
    tk.title("History file")
    txtarea = Text(tk, width=600, height=500, bg='#f1f3f7')
    txtarea.place(x=0, y=0)
    try:
        tf = open("searchlog.txt", "r")
        txtarea.insert(END, tf.read())
        tf.close()
    except:
        print("searchlog file doesn't exist yet")
def clearHistory():
    with open("searchlog.txt", "w") as tf:
        tf.write("")
        tf.close()
def on_click(event):
    if searchEntry.cget('fg') == 'grey':
       searchEntry.delete(0, "end")
       searchEntry.insert(0, '')

    
#building gui
tk = Tk()
tk.geometry("720x405")
tk.title("BuzzHunt")
tk['bg']='#ffffff'

try:
    photo = PhotoImage(file = "images/buzz.png")
    logo1 = PhotoImage(file = "images/logo1.png")
    logo2 = PhotoImage(file = "images/logo2.png")
    chooseOne = PhotoImage(file = "images/chooseOne.png")
    ytButton = PhotoImage(file = "images/ytbutton.png")
    twButton = PhotoImage(file = "images/twbutton.png")
    csvButton = PhotoImage(file = "images/csvbutton.png")
    cHistory = PhotoImage(file = "images/clearHistory.png")
    vHistory = PhotoImage(file = "images/viewHistory.png")
except:
    print("Images not found")
tk.iconphoto(False, photo)

label1 = Label(image = logo1, bg='#ffffff').place(x=300, y=0)  
label2 = Label(image = logo2, bg='#ffffff').place(x=0, y=0)
label3 = Label(image = chooseOne, bg='#ffffff').place(x=65, y=210)
search = StringVar()
errorlabel = None
searchEntry = Entry(tk, textvariable=search, bg='#f9f9f9', width = 25)
searchEntry.place(x=66, y=180)
searchEntry.insert(0, 'Search..')
searchEntry.bind('<FocusIn>', on_click)
searchEntry.config(fg = 'grey')


youtube = partial(youtube, search)
twitter = partial(twitter, search)
b1 = Button(tk, text="On Twitter", command=twitter, bg='#00acee', image=twButton,highlightthickness = 0, bd = 0).place(x=160, y=240)
b2 = Button(tk, text="On YouTube", command=youtube, bg='#c4302b', image=ytButton,highlightthickness = 0, bd = 0).place(x=65, y=240)
b3 = Button(tk, text="Open CSV File", command=csv, bg='#7289DA', image=csvButton,highlightthickness = 0, bd = 0).place(x=255, y=240)
b4 = Button(tk, text="View History", command=viewHistory, bg='#ffffff',image=vHistory, highlightthickness=0, bd=0).place(x=65, y=360)
b5 = Button(tk, text="Clear History", command=clearHistory, bg='#ffffff', image=cHistory, highlightthickness=0, bd=0).place(x=171, y=360)
tk.mainloop()    
