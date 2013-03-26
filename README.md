<pre>

To get this to work in your environment with the development server:

1. git clone https://github.com/mitchgt/prepay.git
2. update settings.py with your db info and ROOT_PATH
3. manage.py syncdb
4. manage.py collectstatic
5. manage.py runserver

To get it to work with apache, here's what I added to my httpd.conf:

# config for prepay django app
WSGIScriptAlias /prepay /Users/mike/emory/cs370/prepay/prepay/wsgi.py
<Directory "/Users/mike/emory/cs370/prepay">
    AllowOverride None
    Options None
    Order allow,deny
    Allow from all
</Directory>

To serve static files from Apache instead of django:

Alias /prepay/css /Users/mike/emory/cs370/prepay/static/css
Alias /prepay/js /Users/mike/emory/cs370/prepay/static/js
Alias /prepay/img /Users/mike/emory/cs370/prepay/static/img

(Todo: add settings.py change for when serving static from apache)

</pre>