alerta-mailer
=============

This integration can be used to send emails for alerts received by Alerta.

It is specifically designed to reduce the number of unnecessary emails by ensuring that alerts meet the following criteria:

  * must not be a duplicate alert (ie. ``repeat != True``)
  * must have status of ``open`` or ``closed``
  * must have a current severity *OR* previous severity of ``critical`` or ``major``
  * must not have been cleared down within 30 seconds (to prevent flapping alerts spamming)

To achieve the above, alerts are actually held for a minimum of 30 seconds before they generate emails.

If you are using Google Gmail as the SMTP server. You will need to create an application-specific password.

You can skip the use of an SMTP server using the option 'skip_mta'. Note that in most cases is recommended to
use an SMTP outbound server as the MTA, but if you know what you're doing you can use skip_mta and then alerta-mailer
will resolve the proper destination MX DNS record for each address and attempt to deliver the email directly. Some
email systems may detect certain email patterns to black-list you, such as sending email using a hostname such as
'localhost'. You may need to set the 'mail_localhost' option or set a proper FQDN in your server to avoid this.

You can also use IP-authentication in your own SMTP server (by only white-listing the alerta server IP), in such
cases you should not set the 'smtp_password' option to skip authentication altogether.

Application-specific passwords
https://support.google.com/accounts/answer/185833?hl=en


Installation
------------

    $ python setup.py install

Configuration
-------------

Settings are changed using an ini-style configuration file that is also used for the ``alerta`` cli.

A section called ``[alerta-mailer]`` is used to clearly define which settings apply to the mailer script.

```
[alerta-mailer]
key = demo-key
mail_to = john.doe@gmail.com,jane.doe@gmail.com
mail_from = your.email@gmail.com
amqp_url = redis://localhost:6379/
dashboard_url = http://localhost:8000
smtp_password = okvqhitqomebufyv
debug = True
skip_mta = False
email_type = text
```

Notifications by different groups of server can be enabled using the section
called ``[notifications]`` see the example above.

```
[notifications]
rules = notification1, notification2

[notification1]
field = alert.resource
regex = db-\w+
contacts = dba@lists.mycompany.com, dev@lists.mycompany.com

[notification2]
field = alert.resource
regex = web-\w+
contacts = dev@lists.mycompany.com 
```

field is a reference to the alert object, regex is a valid python regexp and
contacts are a list (comma separated) of mails who will receive an e-mail if
the regular expression matches.

Environment Variables
---------------------

``SMTP_PASSWORD`` - can be used instead of smtp_password in the configuration file.

Email Format
------------

The format for emails uses a templating engine called Jinja2.

The variable email_type can have 2 possible values:

- html: for just html emails, will fallback to text for text clients (mutt,
  etc) 
- text: for just plain text emails

Deployment
----------

    $ export SMTP_PASSWORD=okvqhitqomebufyv
    $ alerta-mailer

Dependencies
------------

The Alerta server *MUST* have the AMQP plugin enabled and configured. See [default settings](https://github.com/guardian/alerta/blob/master/alerta/settings.py#L57)
