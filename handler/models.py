from __future__ import unicode_literals

from django.db import models

class User(models.Model):
	phone_number = models.CharField(max_length=50, unique=True)

class Stock(models.Model):
	symbol = models.CharField(max_length=20, unique=True)
	price = models.CharField(max_length=10)
	open_price = models.CharField(max_length=10)
	pre_close_price = models.CharField(max_length=10)
	high_price = models.CharField(max_length=10)
	low_price = models.CharField(max_length=10)

class Subscription(models.Model):
	user = models.ForeignKey(User)
	stock = models.ForeignKey(Stock)
	status = models.BooleanField(default=True)
