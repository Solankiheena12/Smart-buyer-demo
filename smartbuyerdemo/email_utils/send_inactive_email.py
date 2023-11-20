import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
from django.template.loader import render_to_string
from employee.models import Employee
from user.models import User
from django.db.models import Q
from django.shortcuts import HttpResponse


def send_inactive_email(subject, template, data):
    context = {}

    employee_email = data.get("email", "")
    employee = Employee.objects.filter(email=employee_email).first()

    context.update(
        employe_id=employee.employe_id,
        employee_name=employee.first_name,
        employee_last_name=employee.last_name,
        designation=employee.designation,
        email=employee.email,
    )

    html_body = render_to_string(template, context)
    super_admin_email = config("INIT_EMAIL")

    recipient_email = employee_email
    

    msg = MIMEMultipart()
    msg.set_unixfrom("author")
    msg["From"] = "SmartBuyer <" + config("ADMIN_EMAIL") + ">"
    msg["To"] = recipient_email

    msg["Subject"] = subject

    part2 = MIMEText(html_body, "html")
    msg.attach(part2)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url = os.path.join(BASE_DIR, "static/images/smartbuyerlogo.png")
    img_data = open(url, "rb").read()
    msImage = MIMEImage(img_data)
    msImage.add_header("Content-ID", "<image1>")
    msg.attach(msImage)

    try:
        mail_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        mail_server.ehlo()
        mail_server.login(config("ADMIN_EMAIL"), config("EMAIL_PASSWORD"))

        recipients = [msg["To"], super_admin_email]
        
        mail_server.sendmail(config("ADMIN_EMAIL"), recipients, msg.as_string())
        mail_server.quit()
    except Exception as e:
        
        return HttpResponse("An error occurred while sending the email.", status=500)

    return HttpResponse("Mail Send", status=200)
