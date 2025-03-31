# deploy.sh
flask db upgrade
gunicorn -b 0.0.0.0:$PORT app:app
