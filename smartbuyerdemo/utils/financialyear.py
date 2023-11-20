# from datetime import date

# def GetCurrentFinancialYear():
#     current_month = date.today().month
#     current_year = date.today().year
#     last_year = str(current_year - 1)
#     next_year = str(current_year + 1)
#     if current_month <= 3:
#         return last_year[2:] + "/" + str(current_year)[2:]
#     else:
#         return str(current_year)[2:] + "/" + next_year[2:]

# def Increment_Invoice_Number():
#         last_invoice = Invoice.objects.all().order_by('invoice_id').last()
#         if not last_invoice:
#             return '01' + "-" + GetCurrentFinancialYear()
#         invoice_no = str(last_invoice)
#         invoice_str = invoice_no.split('-')[:1]
#         new_invoice_int = int(invoice_str[0])
#         new_invoice_str = str(new_invoice_int + 1)
#         if int(new_invoice_str)<10:
#             new_invoice_no = str("0" + new_invoice_str + "-" + GetCurrentFinancialYear())
#         else:
#             new_invoice_no = str(new_invoice_str + "-" + GetCurrentFinancialYear())
#         return new_invoice_no
