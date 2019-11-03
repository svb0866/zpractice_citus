import os

import requests
from datetime import datetime
from zpractice_citus import settings
import html2text

def send_email(to_email, subject, body, sent_by):
    from_email = sent_by.customer.username+"@zpractice.com"
    from clients.models import ClientEmails
    result = requests.post(
        "https://api.mailgun.net/v3/mg.zpractice.com/messages",
        auth=("api", settings.MAILGUN_API_key),
        data={"from": "{} <{}@zpractice.com>".format(sent_by.customer.username, sent_by.customer.username),
              "to": [to_email, "admin@zpractice.com"],
              "subject": subject,
              "text": body}
    )

    ClientEmails(subject=subject, email=body, sent_from_email=from_email, sent_to_email=to_email,
                 sent_by=sent_by.username, status=result.status_code).save()


def parse_email(email_text, appointment, requesting_user, old_date=None, old_time=None):
    parsed_email_text = str(email_text).replace('{{client_name}}', " "+appointment.__str__()+" ")
    parsed_email_text = parsed_email_text.replace('{{assigned_clinician}}', " "+appointment.assigned_to.__str__()+" ")
    parsed_email_text = parsed_email_text.replace('{{appointment_date_time}}',
                                                  " "+appointment.get_human_readable_datetime()+" ")
    parsed_email_text = parsed_email_text.replace('{{your_name}}', " "+requesting_user.__str__()+" ")
    if old_date or old_time:
        old_datetime = datetime.combine(old_date, old_time)
        old_datetime = " "+old_datetime.strftime("%d %b %Y, %I:%M %p")+" "
        parsed_email_text = parsed_email_text.replace(' {{old_appointment_date_time}}', old_datetime)
        parsed_email_text = parsed_email_text.replace(' {{new_appointment_date_time}}', " "+appointment.get_human_readable_datetime()+" ")

    formatted_text = html2text.html2text(parsed_email_text)
    return formatted_text


def send_appointment_created_email(appointment, requesting_user):
    subject = "New Appointment for " + appointment.client.__str__()
    parsed_email_body = parse_email(requesting_user.emailtemplates.new_appointment, appointment, requesting_user)
    send_email(to_email='svb0866@gmail.com', subject=subject,
               body=parsed_email_body, sent_by=requesting_user)


def send_appointment_reschedule_email(appointment, old_date, old_time, requesting_user):
    subject = "Appointment Rescheduled for " + appointment.client.__str__()
    parsed_email_body = parse_email(requesting_user.emailtemplates.appointment_reschedule,
                                    appointment, requesting_user, old_date, old_time,)
    send_email(to_email='svb0866@gmail.com', subject=subject,
               body=parsed_email_body, sent_by=requesting_user)


def send_appointment_canceled_email(appointment, requesting_user):
    subject = "Appointment Canceled for " + appointment.client.__str__()
    parsed_email_body = parse_email(requesting_user.emailtemplates, appointment, requesting_user)
    send_email(to_email='svb0866@gmail.com', subject=subject,
               body=parsed_email_body, sent_by=requesting_user)


def send_client_credential_email(client_obj, password, requester):
    import codecs
    email_body = codecs.open(
        os.path.join(settings.BASE_DIR, "templates/email_default/client_onboarding.html"), "r", 'utf-8').read()
    subject = "Your access credential to the client Portal of "+requester.customer.__str__()
    parsed_email_text = str(email_body).replace('{{client_name}}', " " + client_obj.__str__())
    parsed_email_text = parsed_email_text.replace('{{your_name}}', " " + requester.__str__())
    parsed_email_text = parsed_email_text.replace('{{access_credential}}', " " + "Portal : " +
                                                  "Login_url" + "<br/>" +
                                                  "Username : "+client_obj.primary_email + "<br/>" +
                                                  "Password : "+password+"<br/>")

    send_email(to_email=client_obj.primary_email, subject=subject, body=html2text.html2text(parsed_email_text), sent_by=requester)




