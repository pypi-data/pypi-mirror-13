# django-blogposts
Simple django blogposts app.

installation

# first step
```
pip install django-blogposts
```

# second step
```
Add into settings.py INSTALL_APPS
'django_blogposts'
```

# third step
```
$ python manage.py collectstatic
$ python manage.py migrate
```

# fourth step
```
Add into urls.py

url(r'^blog/', include('django_blogposts.urls')),

```

# fifth step
```
all templates extends from base.html. If you doesn't have it, create it or override templates
```

# optionaly
```
you can use sitemap

from django_blogposts.sitemap import BlogPostSitemap
```

# dependencies
```
django
pillow
pytils
```
