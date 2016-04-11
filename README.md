# StockTicker
This project functions as an Stock Ticker where a mobile phone user can send a text message with command followed by stock symbols and it will return the stock info scraped from Yahoo.

Commands:  
 #0 for stock price (can only type stock symbols without #0)  
 #1 for more information   
 #2 for daily update subscription  
 #3 for daily update unsubscription  
 #4 for unsubscribe all  
 #5 for show all subscriptions  
 #6 for help information
 
Example:  
'#1 FB GOOG' would return more information about the stock of Facebook and Google

## Stack
1. Django
2. Postgres
3. Twilio
4. Redis
5. Celery

## Prerequisites
1. Setuptools, Pip, and Virtualenv installed.
2. A Twilio account with a provisioned phone number.
3. A Heroku account
4. The Heroku Toolbelt installed locally

## Download and Deploy on Heroku
```
$ git clone https://github.com/HugoZhang33/StockTicker.git
```

```
$ virtualenv venv
$ source venv/bin/activate
```
```
$ pip install -r requirements.txt
```
```
$ heroku login 
```
```
$ heroku create 
```
```
$ git add .
$ git commit -m "Deploy"
$ git push heroku master
```
<https://devcenter.heroku.com/articles/getting-started-with-python#introduction> for more detail about Heroku
