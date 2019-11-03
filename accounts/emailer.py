from clients.models import ClientEmails
import requests
from datetime import datetime
from zpractice_citus import settings


def send_email(to_email, subject, body, sent_by):
    from_email = sent_by.customer.username+"@zpractice.com"
    print(body)
    result = requests.post(
            "https://api.mailgun.net/v3/mg.zpractice.com/messages",
            auth=("api", settings.MAILGUN_API_key),
            data={"from": "{} <{}@zpractice.com>".format(sent_by.customer.username, sent_by.customer.username),
                  "to": [to_email, "admin@zpractice.com"],
                  "subject": subject,
                  "text": body})


def send_team_member_credential_email(team_member, password, requester):
    import codecs
    email_body = open("templates/email_default/team_signup", "r", 'uft-8').read()
    subject = "You are invited to join the Zpractice team"
    from customers.models import Customer
    parsed_email_text = str(email_body).replace('{{owner}}', " " + requester.get_full_name() + " ")
    parsed_email_text = parsed_email_text.replace('{{domain}}', " " + team_member.customer.get_primary_domain().domain + " ")
    parsed_email_text = parsed_email_text.replace('{{username}}', " " + team_member.username)
    parsed_email_text = parsed_email_text.replace('{{password}}', " " + password + " ")
    soupified_email = BeautifulSoup(parsed_email_text, features="html.parser")
    send_email(to_email=team_member.email, subject=subject, body=soupified_email, sent_by=requester)
