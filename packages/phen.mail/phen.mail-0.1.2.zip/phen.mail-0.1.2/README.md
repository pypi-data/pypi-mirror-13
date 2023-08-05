Mail Services Plugin
====================

> *Note:* this is alpha software, use it only if willing to help debug it.

This plugin provides full mail services:

* relay: signs mail messages (DKIM) and transports them to other servers
* relay through smarthost: forwards the messages to the configured SMTP
  server to do the relaying
* delivery: receives and filters messages, then delivers them to Phen
  mailboxes, to other plugins, or to external agents (e.g. dovecot LDA)
* fetching: retrieves messages from other servers
* access: serves messages through IMAP4, POP3, or direct shell management

When used in conjunction with Phen's DNS plugin, outgoing mail passes
common anti-spam tests. The module dkimpy (python-dkim in Debian) is
required for DKIM signatures.

Other plugins can easily send mail using the `send_mail` method.


Server Configuration
--------------------

> *Note:* all configuration files are in JSON format, but allow
> hash (#) comments.

Edit the file `/[device-identity]/system/mail/mail.jcfg` using the
reference below:
```
{
  "sender-domain": "example.com",
  "receivers": [                      # DNS MX records (requires dns plugin)
    [0, "mail1.example.com"],         # priority, server name
    [5, "mail2.example.com"],
  ],
  "domains": {
    "example.com": {
      "postmaster": ":alice",
      "abuse": ":alice",
      "alice": "/[user-identity]/path/to/mail-folder",
      "bob": "-disabled account",
      "carol": ">external-MDA-command parameters [hashed-passphrase]"
      "dan": ">forward@domain.org [hashed-passphrase]"
      "robot": ".plugin-name parameters"
    }
  },
  "relay": {
    "dkim-key": "/[device-identity]/system/mail/dkim.key",  # default
    "queue-folder": "/[device-identity]/system/mail/queue"  # default
  },
  # if instead of relaying by yourself you prefer/need a smarthost:
  # "hosted": {
  #   "server": "smtp.example.com",
  #   "port": 587,                                          # default
  #   "username": "user@example.com",
  #   "password": "KTgyfDNrNH0kbCkCKgMtAi4D",
  #   "require-tls": false
  # },

  "imap": true,
  "pop": {"port": 111, "disable-ssl": true}
}
```

Remember that mail servers are required by RFC822 6.3, RFC1123 5.2.7,
and RFC2821 4.5.1 to have a valid `postmaster` address, and by RFC2142
Section 2 to have a valid `abuse` address.

You only have to specify configuration sections if you want to change a
default value. For instance, the `relay` section in the reference above
could be replaced with `"relay": true`.

The first character of the user definition string sets the action to
take when receiving or relaying mails:

* **-** disables the service to the user
* **/** indicates the path to the mail folder, where the user can specify
  preferences in the `mail.jcfg` file
* **:** specifies an alias to another username (with @domain if not the same)
* **>** forwards the email to an external mail delivery agent, or to another
  mail server if a mail address is specified; if the last argument is a
  sha256 hashed passphrase, the user can relay messages using the mail address
  as username
* **.** delivers the message to a Phen plugin; the mail plugin itself replies
  messages with an aknowledgment echo

> *Note:* the IMAP server only works with Evolution so far. Thunderbird and
> Geary still can't retrieve messages correctly.


User Configuration
------------------

Reference `/[user-identity]/mail/mail.jcfg`:
```
{
  "passphrase": "sha256-passphrase",
  "pop3pwd": "obscured-passphrase",
  "external-MDA": "command parameters",
  "authorization": "admin sign allowing the external-MDA command",
  "delivery": "path-to-custom-folder",    # default: mail-foder/delivery
  "filters": "path-to-custom-file"        # default: mail-foder/filters.jcfg
}
```

The passphrase is used for SMTP and IMAP authentication, and its hash
can be calculated with Phen's shell command `sha256`:
```
admin:iYPM7:/[iYPM7]$ sha256
Type in your pass phrase:
08fc92f4ad885e06491aa5b19435849eb62232a056dd840a53fee62a5507b654
```

The POP implementation requires the unhashed storage of the passphrase,
so to avoid using clear-text you can use the shell command `obscure`:
```
admin:iYPM7:/[iYPM7]$ obscure
Type in your pass phrase:
KTgyfDNrNH0kbCkCKgMtAi4D
```

Identities that don't belong to the *admin* account must have *admin*
authorization to use the host system's resources, such as using and external
MDA or executing a code filter.

Example filter configuration file:
```
{
  "filters": [
    {"type": "py", "code": "file:test-filter.py"},
    {"type": "match", "content": "[3ug-l]", "action": "accept:Lists/3ug-l"}
  ]
}
```

Example code filter:
```python
try:
    cnt = int(msg["Subject"].split()[-1])
    if cnt % 2:
       accept("odd")
    accept("even")
except:
    pass
```


### Fetcher Configuration

Example `/[user-identity]/system/config/mail-fetcher.jcfg`:
```
{
  "mail-folders": {
    "mail": "/[user-identity]/mail"
  },
  "accounts": [
    {
      "server": "imap.example.com",
      "protocol": "imap",             # imap / imaps
      "username": "alice",
      "passphrase": "KTgyfDNrNH0kbCkCKgMtAi4D",
      "period": "5 min",
      "first-time": "download-all",   # default is "ignore-all"
      "boxes": [
        {"Inbox": "filter"},
        "SomeList",                   # same as {"SomeList": "filter"}
        {"SomeOtherList": "accept:mail:Lists/SomeOther"},
        {"Spam": "delete"}
      ]
    }
  ]
}
```

The above `mail-folders` section is the default, and can be ommited if
unchanged.

> *Note:* protocols pop / pops not available yet.


Immediate ToDo List
-------------------
* better user documentation (some features are not currently described)
* developer documentation
* fetching through POP
* continous fetching through IMAP (don't disconnect, go IDLEing)
* Python3 support
* tests
* optimizations (lots of room for improvement here)


Future Plans
------------
* Gateway for using Phen's internal messaging mechanism
* Long term storage in a `phen.db` database.
* Keyword search using Woosh.
* Interaction with Notmuch.
