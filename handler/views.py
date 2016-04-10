# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import *

from twilio.rest import TwilioRestClient
import twilio.twiml

from yahoo_finance import Share

@csrf_exempt
@require_http_methods(["POST"])
def reply_sms(request):
	"""
	Reply to incoming messages
	"""
	text = request.POST.get("Body", "").strip().upper()
	phone_number = request.POST.get("From", "")
	command, symbols = split_text(text)
	message = execute_command(command, symbols, phone_number)
	resp = twilio.twiml.Response()
	resp.message(message)
	return HttpResponse(str(resp))

def split_text(text):
	"""
	Split text into stock symbols and optional command 
	@Return (command, symbols)
	"""
	commands = ['#0', '#1', '#2', '#3', '#4', '#5', '#6']
	if text[0:2] in commands:
		return (text[0:2], text[2:].split())
	else:
		return ('#0', text.split())

def execute_command(command, symbols, phone_number):
	"""
	@Param 'command'：	
					#0 for stock price
					#1 for more information
					#2 for daily update subscription
					#3 for daily update unsubscription
					#4 for unsubscribe all
					#5 for show all subscriptions
					#6 for help information
	@Return str

	"""
	if command == '#0':
		return get_stock_info(symbols, False)
	elif command == '#1':
		return get_stock_info(symbols, True)
	elif command == '#2': # return status message
		return subscribe_stocks(symbols, phone_number)
	elif command == '#3':
		return unsubscribe_stocks(symbols, phone_number)
	elif command == '#4':
		return unsubscribe_all(phone_number)
	elif command == '#5':
		return show_subscriptions(phone_number)
	else:
		return help_info()

def get_stock_info(symbols, moreInfo=False):
	""" 
	Scrape stock info from Yahoo finance
	@Param 'moreInfo': False for getting price, True for getting more information
	@Return 'message': "symbol: Price-number, Open Price-number, Pre Close Price-number, High Price-number, 
						Low price-number"
	"""
	message = ''
	for symbol in symbols:
		try:
			stock = Share(symbol)
			price = stock.get_price()
		except AttributeError:
			price = None
		
		if price == None: # Stock symbol not exists, replace with an alert message
			message += '#' + symbol + ': ' + 'The stock symbol does not exit' + '\n'
		elif moreInfo: 
			message += '#%s: Price-%s, Open Price-%s, Pre Close Price-%s, High Price-%s, Low price-%s\n' \
						% (symbol, price, stock.get_open(), stock.get_prev_close(), stock.get_days_high(), stock.get_days_low())
		else:
			message += '#' + symbol + ': ' + price + '\n'

	alert_message = 'Please type #1 followed by stock symbols to get more information' if moreInfo == True else \
					'Please type #0 followed by stock symbols to get stock price'
	return message if message != '' else alert_message

def help_info():
	return  "Command #0, #1, #2, #3 are followed by stock symbols, like '#1 FB GOOG' would return more information about the stock of Facebook and Google\n\n" \
			+ "#0 for stock price (can only type stock symbols without #0)\n" \
			+ "#1 for more information\n" \
			+ "#2 for daily update subscription\n" \
			+ "#3 for daily update unsubscription\n" \
			+ "#4 for unsubscribe all\n" \
			+ "#5 for show all subscriptions\n" \
			+ "#6 for help information"

def subscribe_stocks(symbols, phone_number):
	"""
	@Param 'symbols': a list of symbol
	@Return str
	"""
	error_message = ''
	message = ''

	# Check user
	try:
		user = User.objects.get(phone_number=phone_number)
	except User.DoesNotExist:
		user = User(phone_number=phone_number)
		user.save()

	subscription_list = []

	for symbol in symbols:
		# Check stock
		try:
			stock = Stock.objects.get(symbol=symbol)
		except Stock.DoesNotExist:
			# Validate stock symbol
			try:
				s = Share(symbol)
				price = s.get_price()
			except AttributeError:
				price = None
			
			if price == None:
				error_message += '#' + symbol + ', '
				continue

			stock = Stock(symbol=symbol, price=price)
			stock.save()
		
		message += '#' + symbol + ', '
			 
		# Check subscription
		try:
			subscription = Subscription.objects.get(user=user, stock=stock)
			subscription.status = True
			subscription.save()
		except Subscription.DoesNotExist:
			subscription_list.append(Subscription(user=user, stock=stock))

	# Save all new subscription into database
	Subscription.objects.bulk_create(subscription_list)

	error_message += '' if error_message == '' else 'are not valid stock symbol'
	message += 'are subscribed\n' if message != '' else 'Please type #2 followed by valid stock symbols to subscribe stock\n'
	return message + error_message
			
def unsubscribe_stocks(symbols, phone_number):
	"""
	@Param 'symbols': a list of symbol
	@Return str
	"""
	message = ''
	try:
		user = User.objects.get(phone_number=phone_number)
	except User.DoesNotExist:
		message = 'You don\'t subscribe any stock information'
	else:
		for symbol in symbols:
			try:
				stock = Stock.objects.get(symbol=symbol)
			except Stock.DoesNotExist:
				continue
			
			try:
				s = Subscription.objects.get(user=user, stock=stock)
				s.status = False
				s.save()
				message += '#' + symbol + ', '
			except Subscription.DoesNotExist:
				pass
	return 'Successfully Unsubscribe' + message if message != '' else 'Please type #3 followed by valid stock symbols to unsubscribe stock'

def unsubscribe_all(phone_number):
	message = ''
	try:
		user = User(phone_number=phone_number)
	except User.DoesNotExist:
		message = 'You don\'t subscribe any stock information'
	else:
		Subscription.objects.filter(user__phone_number=user.phone_number).update(status=False)
		message = 'Successfully Unsubscribe All'
	return message

def show_subscriptions(phone_number):
	message = ''
	try:
		user = User(phone_number=phone_number)
	except User.DoesNotExist:
		return 'You don\'t subscribe any stock information'
	else:
		s_list = Subscription.objects.filter(user__phone_number=user.phone_number).filter(status=True)
		for s in s_list:
			message += '#' + s.stock.symbol + ', '
	return  'You have subscribed ' + message if message != '' else 'You don\'t subscribe any stock information'

