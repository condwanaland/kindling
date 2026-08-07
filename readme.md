Some scripts to automate part of my kindle workflow. 

I use Calibre to sort my books into a nice looking library. From there they need to be emailed to my kindle. 

Scripts here essentially

1. Find all epubs in my calibre library
1. Find which ones have been added since the last time the script was run
1. Email the new ones to my kindles email address

When prompted, use `y` to send to the usual Kindle address, `a` to send to the
alternate Kindle address, or `b` to send to both. A successful send through any
of these options updates the baseline so the same books are not offered again.

Still very much in progress but feel free to use for your own purposes. To make this run you'll need to update the working directory in `constants.py`. You'll also need a file called `auth_secrets.py` and fill it in with the following. If putting your code on github or somewhere public make sure to add `auth_secrets.py` to `.gitignore`.

```
class Creds:
    sender_email = "email_to_send_from"
    sender_pword = "email_password"
    recipient_email = "email_to_send_to"
    alternate_recipient_email = "alternate_email_to_send_to"
```

Depending on your email client you may need to allow access from the script. I use gmail, and therefore the password is an 'App Password' that is allowed to access without going through 2FA. You'll have to find what works for your client. 
