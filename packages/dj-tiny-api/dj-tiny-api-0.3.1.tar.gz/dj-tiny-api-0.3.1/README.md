# dj-tiny-api

A tiny toolkit to implement HTTP APIs using Django.

Basic Usage
===========

    # in views.py
    from dj_tiny_api import Endpoint


    @Endpoint(
        url=r'^api/v1/foo/?$',
        methods=['GET', 'POST'],
    )
    def foo_view()
        return {'foo': 'bar'}

    # this will return response with body
    {"data": {"foo": "bar"}, "error": null}
