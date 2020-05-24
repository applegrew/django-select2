# Sample App

Before you start, make sure you have Redis installed, since
we need if for caching purposes.

```
# Debian
sudo apt-get install redis-server -y
# macOS
brew install redis
```

Now, to run the sample app, please execute:

```
git clone https://github.com/codingjoe/django-select2.git
cd django-select2/example
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
# follow the instructions to create a superuser
python3 manage.py runserver
# follow the instructions and open your browser
```
