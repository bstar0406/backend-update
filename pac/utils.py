from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser

from pac.models import Comment
from pac.rrf.models import Request, RequestStatus
from pac.serializers import CommentSerializer
from pac.settings import settings

from pac.email.send_email import send_email_comment
from pac.notifications import NotificationManager


def save_attachments_to_storage(request, *args, **kwargs):
    attachments = []
    # saving files
    files = request.FILES.getlist('files')
    for f in files:
        attached_file = default_storage.save(f.name, f)
        attachments.append(attached_file)
    return attachments


def get_attachment_from_storage(container, file_name, *args, **kwargs):
    attached_file = default_storage.open(container, file_name)

    return attached_file
    # attachments = []
    # saving files
    # files = request.FILES.getlist('files')
    # for f in files:
    #     attached_file = default_storage.save(f.name, f)
    #     attachments.append(attached_file)
    # return attachments


def save_comment(request, entity_id):
    comment_notification_by_category = {
        'Rebates': [['request_status', 'credit_analyst']],
        'Commissions': [['request_status', 'credit_analyst']]
    }

    attachments = save_attachments_to_storage(request)

    # workaround to work locally without JWT, only for debugging
    if settings.DEBUG:
        user_name = "Anonymous User" if isinstance(request.user, AnonymousUser) else request.user.user_name

    # resolving request number, will work only for comments for RRF
    # be careful, this makes whole Comment functionality working only with RRFs
    # entity_id = request_id_to_request_number(entity_id)

    # entity_id = request.data["entity_id"]
    comment_serializer = CommentSerializer(data=request.data,
                                           many=False,
                                           context={
                                               "attachments": attachments,
                                               "entity_uuid": entity_id,
                                               "username": user_name
                                           })

    if comment_serializer.is_valid():
        # Save comment
        saved_comment = comment_serializer.save()

        # Send notification if tag requires notifications
        if saved_comment.tag in comment_notification_by_category:
            notification_users=comment_notification_by_category[saved_comment.tag]

            # users=[]
            for user_select in notification_users:
                if user_select[0] == 'request_status':
                    request_status=RequestStatus.objects.filter(
                        request__request_number=entity_id
                    ).select_related(
                        user_select[1]
                    ).first()

                    if request_status:
                        user=getattr(request_status, user_select[1])

                        if user:
                            # users.append(user)
                            NotificationManager.send_notification_request_number(
                                user,
                                f"A {saved_comment.tag} comment has been left on a Request that requires attention",
                                entity_id
                            )

        return saved_comment


    raise NameError('There is a problem while saving comment.{}'.format(comment_serializer.errors))


def update_comment(request, comment_id):
    comment=Comment.objects.get(id=comment_id)

    data=JSONParser().parse(request)
    serializer=CommentSerializer(comment,
                                   data=data,
                                   context={
                                       "attachments": data.get("attachments")
                                   },
                                   partial=True)
    if serializer.is_valid():
        serializer.save()
        return serializer
    raise ValidationError


def get_comments(entity_id):
    comments=Comment.objects.filter(entity_uuid=entity_id).order_by("created_on")
    serializer=CommentSerializer(comments, many=True)
    return serializer


def delete_comment(comment_id):
    try:
        comment=Comment.objects.get(id=comment_id)
        comment.delete()
        return
    except Comment.DoesNotExist as error:
        raise RuntimeError('Comment not found') from error


# temporarily disabled as changed approach
def request_id_to_request_number(request_id):
    if len(request_id) >= 32:
        return request_id
    try:
        # return Request.objects.get(request_id=request_id).request_number
        return Request.objects.values_list('request_number', flat=True).get(request_id=request_id)
    except Request.DoesNotExist:
        return request_id
