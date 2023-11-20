import os
import smtplib
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jwt
from decouple import config
from django.shortcuts import HttpResponse
from django.template.loader import render_to_string

from user.models import User


def send_confirm_mail(subject, template, data):
    context = {"name": data["name"], "email": data["email"]}

    html_body = render_to_string(template, context)
    recipient_email = data["email"]

    msg = MIMEMultipart()
    msg["From"] = "SmartBuyer <" + config("ADMIN_EMAIL") + ">"
    msg["To"] = recipient_email
    msg["Subject"] = subject

    part2 = MIMEText(html_body, "html")
    msg.attach(part2)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    url = os.path.join(BASE_DIR, "static/images/smartbuyerlogo.png")
    with open(url, "rb") as image_file:
        img_data = image_file.read()
    msImage = MIMEImage(img_data)
    msImage.add_header("Content-ID", "<image1>")
    msg.attach(msImage)

    if template == "password-changed-confirmation.html":
        # Attach additional image if needed
        url = os.path.join(BASE_DIR, "static/images/checked.png")
        img_data1 = open(url, "rb").read()
        msImage1 = MIMEImage(img_data1)
        msImage1.add_header("Content-ID", "<image2>")

    try:
        mail_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        mail_server.ehlo()
        mail_server.login(config("ADMIN_EMAIL"), config("EMAIL_PASSWORD"))
        mail_server.sendmail(config("ADMIN_EMAIL"), msg["To"], msg.as_string())
        mail_server.quit()
        return HttpResponse("Mail Sent", status=200)
    except Exception as e:
        return HttpResponse(f"Mail could not be sent: {str(e)}", status=500)


def send_success_mail(subject, template, data):
    name = data.get("name", "")
    email = data.get("email", "")
    company = data.get("company", "")

    user = User.objects.filter(email=email).first()

    context = {
        "name": name,
        "email": user.email,
        "company": company,
    }

    html_body = render_to_string(template, context)
    recipient_email = data["email"]
    super_admin_email = config("INIT_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = "SmartBuyer <" + config("ADMIN_EMAIL") + ">"
    msg["To"] = ", ".join([super_admin_email, recipient_email])

    msg["Subject"] = subject

    part2 = MIMEText(html_body, "html")
    msg.attach(part2)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    url = os.path.join(BASE_DIR, "static/images/smartbuyerlogo.png")
    with open(url, "rb") as image_file:
        img_data = image_file.read()
    msImage = MIMEImage(img_data)
    msImage.add_header("Content-ID", "<image1>")
    msg.attach(msImage)

    if template == "register-success.html":
        # Attach additional image if needed
        url = os.path.join(BASE_DIR, "static/images/checked.png")
        img_data1 = open(url, "rb").read()
        msImage1 = MIMEImage(img_data1)
        msImage1.add_header("Content-ID", "<image2>")

    try:
        mail_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        mail_server.ehlo()
        mail_server.login(config("ADMIN_EMAIL"), config("EMAIL_PASSWORD"))

        mail_server.sendmail(
            config("ADMIN_EMAIL"), msg["To"].split(", "), msg.as_string()
        )

        mail_server.quit()

        return HttpResponse("Mail Sent", status=200)

    except Exception as e:
        return HttpResponse(f"Mail could not be sent: {str(e)}", status=500)
