# from lxml import etree as ET
from django.conf import settings
import requests
# import json

# from pac.pre_costing.requestlog import create_request_log
# from pac.pre_costing.models import RequestLog
from pac.rrf.models import RequestStatus


def _get_email_template(template_name):
    # TODO: Implement template table
    return ("Test Subject", 'Test Email Template!  Placeholder: [[test]]')


def _replace_template_placeholders(subject, template, placeholder_data):
    for key in placeholder_data:
        subject.replace(key, placeholder_data[key])
        template.replace(key, placeholder_data[key])


def send_email_template(template_name, to_users=[], cc=[], placeholder_data={}):
    # Get To Emails
    to_emails = [x.user_email for x in to_users]

    # Get Template
    template_subject = _get_email_template(template_name)
    subject = template_subject[0]
    template = template_subject[1]

    # Replace Placeholders
    _replace_template_placeholders(subject, template, placeholder_data)

    # Send Email
    send_email_simple(subject=subject, body=template, to=to_emails, cc=cc)


def send_email_workflow(request_status_name, users=[], placeholder_data={}):
    # TODO: Remove hardcoded mapping and query Template table by status
    status_template_map = {
        'Pending Credit Approval': "PendingCreditApproval",
        'Pending EPT Approval': 'PendingEPTApproval',
        'Cost+ Declined': 'Cost+Declined',
        'Credit Declined': 'CreditDeclined',
        'Pending Sales Approval': 'PendingSalesApproval',
        'Pending Cost+ Approval': 'PendingCost+Approval',
        'Pending DRM Approval': 'PendingDRMApproval',
        'Pending PC Approval': 'PendingPCApproval',
        'Pending PCR Approval': 'PendingPCRApproval',
        'Pending GRI Customer Response': 'PendingGRICustomerResponse'
    }

    status_cc_map = {
        'Pending Credit Approval': ['day&rosscreditapp@dayandrossinc.ca'],
        'Pending EPT Approval': ['day&rosscreditapp@dayandrossinc.ca']
    }

    cc_list = []
    if request_status_name in status_cc_map:
        cc_list = status_cc_map[request_status_name]

    if request_status_name in status_template_map:
        send_email_template(status_template_map[request_status_name], users, cc_list, placeholder_data)


def send_email_comment(request_number, comment_tag):
    # TODO: Remove hardcoded mapping and query table by status
    template_name = f'comment_{comment_tag}'

    comment_email_required_by_tag = {
        'rebates': [['request_status', 'credit_analyst']],
        'commissions': [['request_status', 'credit_analyst']]
    }

    if comment_tag.lower() in comment_email_required_by_tag:
        notification_users = comment_email_required_by_tag[comment_tag.lower()]

        users = []
        for user_select in notification_users:
            if user_select[0] == 'request_status':
                request_status = RequestStatus.objects.filter(
                    request__request_number=request_number
                ).select_related(
                    user_select[1]
                ).first()

                if request_status:
                    user = getattr(request_status, user_select[1])

                    if user:
                        users.append(user)

        send_email_template(template_name, users)


def send_email_simple(subject, body=None, html_body=None, to=[], cc=[]):
    # base_url = "https://api.smtp2go.com/v3/"
    base_url = settings.SMTP2GO_BASE_URL
    relative_path = "email/send"
    # api_key = "api-40246460336B11E6AA53F23C91285F72"
    api_key = settings.SMTP2GO_API_KEY
    from_email = settings.SMTP2GO_FROM_EMAIL

    payload = {
        "api_key": api_key,
        "to": to,
        "cc": cc,
        "sender": from_email,
        "subject": subject,
        "text_body": body,
        "html_body": html_body
    }

    print('Sending Email')
    print(payload)

    ret = requests.post(base_url + relative_path, json=payload)

    if ret.status_code == requests.codes.ok:
        print("Email sent successfully")
        return True
    else:
        print("Email Failed")
        ret_json = ret.json()

        print(ret_json)
