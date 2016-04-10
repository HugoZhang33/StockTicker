web: gunicorn StockTicker.wsgi --log-file -
worker: celery -A StockTicker worker -B --loglevel=info