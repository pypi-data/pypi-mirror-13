# Django GraphiQL [![PyPI version](https://badge.fury.io/py/django-graphiql.svg)](https://badge.fury.io/py/django-graphiql)

Django GraphiQL is a library for integrating [GraphiQL](https://github.com/graphql/graphiql) inside your Django project, so you can test your [GraphQL](https://github.com/graphql-python/graphql-core) schemas easily.

This library versioning go in partity with GraphiQL.

## Installing

For installing this library just run in your favorite shell:

```bash
pip install django-graphiql
```

## Configuring

In settings.py add `'django_graphiql'` into `INSTALLED_APPS`, so it will look like

```python
INSTALLED_APPS = [
    # ...
    'django_graphiql',
    # ...
]
```

And then, add into your urls.py:

```python
urlpatterns = [
    # Your other urls...
    url(r'^graphiql', include('django_graphiql.urls')),
]
```

If you want to configure the default query, just set `GRAPHIQL_DEFAULT_QUERY` in your settings
to the desired value.
