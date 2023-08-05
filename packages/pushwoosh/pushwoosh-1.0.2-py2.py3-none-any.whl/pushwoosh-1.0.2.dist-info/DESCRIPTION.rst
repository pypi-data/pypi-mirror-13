Python Pushwoosh client
=======================

A simple client for the Pushwoosh push notification service.

Example::

    from pushwoosh import Pushwoosh

    text = 'Hello there'
    conditions = ['UserId', 'EQ', 1]
    message = {
        'text': text,
        'conditions': conditions
    }
    push = Pushwoosh(API_TOKEN, APP_CODE, False)
    push.create_message([message])


