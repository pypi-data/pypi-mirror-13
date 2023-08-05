========
mailsend
========

This is a fork of
`Rick Harris's tinysmtp package <http://github.com/rconradharris/tinysmtp>`_
with a few fixes and Python 3 compatibility.

Example::

    with Mail().connect() as mail:
        msg = Message(
            'alice@example.com', 'Subject', ['bob@example.com'], body='body')
        mail.send(msg)


Connections may be configured from a URL specified in an environment variable::

  export MAILSEND_URL="smtp+tls://user:password@server.example.org/"


Or as individual variables::

  export MAILSEND_HOSTNAME=server.example.org
  export MAILSEND_PORT=25


Or in code::

    mail = Mail('smtp://server.example.org/')
    mail2 = Mail('server.example.org',
                 port=25,
                 ssl=True,
                 username='x',
                 password='x')


Call ``mail.send`` to send a message::

    mail = Mail('smtp://server.example.org/')
    mail.send(sender='alice@example.com',
              recipients=['bob@example.com', 'charlie@example.com'],
              body='Hello everyone!',
              html='<p>Hello everyone!</p>',
              subject='Hello')

Or use the message class to construct messages piecemeal::

    msg = Message('alice@example.com', 'Hello!')
    msg.body = 'Hello'
    msg.recipients = ['bob@example.com']
    msg.cc = ['charlie@example.org']
    msg.bcc = ['dina@example.org']

    mail = Mail('smtp://server.example.org/')
    mail.send(msg)

To send multiple messages in a single connection, use ``Mail.connect``::

    with mail.connect() as conn:
        conn.send(msg1)
        conn.send(msg2)
