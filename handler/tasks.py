from __future__ import absolute_import
from .models import *
from django.conf import settings

from celery import shared_task

from twilio.rest import TwilioRestClient

from yahoo_finance import Share

@shared_task
def post():
	## Update stock info
	try:
		stock_list = Stock.objects.all()
		for stock in stock_list:
			try:
				s = Share(stock.symbol)
				stock.price = s.get_price()
				stock.open_price = s.get_open()
				stock.pre_close_price = s.get_prev_close()
				stock.high_price = s.get_days_high()
				stock.low_price = s.get_days_low()
				stock.save()
			except Exception, e:
				pass
	except Exception, e:
		pass

	## send message
	client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
	user_dir = {}
	try:
		subscription_list = Subscription.objects.filter(status=True)
		for s in subscription_list:
			meg = '#%s: Price-%s, Open Price-%s, Pre Close Price-%s, High Price-%s, Low price-%s\n' \
				 % (s.stock.symbol, s.stock.price, s.stock.open_price, s.stock.pre_close_price, s.stock.high_price, s.stock.low_price)
			
			phone_number = s.user.phone_number
			if phone_number in user_dir:
				user_dir[phone_number] += meg
			else:
				user_dir[phone_number] = meg

		for phone in user_dir:
			message = client.messages.create(to=phone, from_="+14123124628", body="Daily Update\n" + user_dir[phone])
	except Exception, e:
		pass
