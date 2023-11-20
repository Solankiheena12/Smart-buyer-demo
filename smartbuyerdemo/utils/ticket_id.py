from datetime import date
import string
import secrets


def generate_ticket_id():
    N = 4
    res = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for i in range(N)
    )
    today = date.today()
    month = today.month
    year = str(today.year)
    ticket = "{}{}{}".format(str(res), month, year[2:])
    return ticket
