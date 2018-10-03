
[![Join the chat at https://gitter.im/UtiloBot/Lobby](https://badges.gitter.im/UtiloBot/Lobby.svg)](https://gitter.im/UtiloBot/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
# UtiloBot
It is bot for [telegram.org](//telegram.org) that saves files sent to his server and provides you short download link and a deletion link. It can also download videos from youtube and perform youtube search too.

## How to use it 
Go to [telegram.me/UtiloBot](//telegram.me/UtiloBot) on web or search for UtiloBot on your telegram app and start the conversation.  

## Utilo Commands 
You can use the following commands after you found the UtiloBot on telegram
1. /**start** - Shows the default welcome message
2. /**youtube** - To download youtube video via URL or first search youtube and then download video
3. /**joke** - Get a random hilarious joke
4. /**facebook** - To subscribe to facebook pages
5. /**twitter** - To subscribe to twitter handles
6. /**mysubscription** - Lets you know all your Facebook and Twitter subscription.
7. /**mail** - To send an E-mail to someone without using your email id.
8. /**help** - To know more.  

Apart from these commands, if you send any file to Utilo, he will upload that file and send you a short URL to download and delete the file.


## Using the Source Code  

1. Get the telegram bot api and save it in file named `ACCESS_TOKEN`
2. Get a bitly access token and save it to `BITLY_ACCESS_TOKEN`
3. Get a facbook app access token and save it to `FB_ACCESS_TOKEN`
4. Get twitter credentials and save them to `TWITTER_CONFIG.json` as follows :
```
{
    "access_token" : " ",
    "access_token_secret" : " ",
    "consumer_key" : " ",
    "consumer_secret" : " "
}
```
5. Save your E-mail credentials in `EMAIL_CONFIG.json` as follows :
    `{"email":" ","pass":" "}`
6. Make two folders in the repository - FB, Twitter and inside, make a folder `pages_json`.

## Screeshots

### Using Youtube search 
![demo](http://i.imgur.com/WhZqPiq.gif)

### Using Youtube download
<img src = "http://i.imgur.com/BzHMyp8.png" height="600" width="374">

### Using file link generators
<img src = "http://i.imgur.com/rxXnQ47.png" height="600" width="374">
<img src = "http://i.imgur.com/33et3QM.png" height="600" width="374">
<img src = "http://i.imgur.com/PxuyCJe.png" height="600" width="374">

### Getting Jokes 
<img src = "http://i.imgur.com/SjcsCQz.png" height="600" width="374">

### Sending Mail 
<img src = "http://i.imgur.com/lBUXNIF.png" height="600" width="374">

