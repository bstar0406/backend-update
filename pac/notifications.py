from pac.models import Notification
from pac.rrf.models import Request


class NotificationManager:

    @staticmethod
    def send_notification(user, message, meta):

        Notification.objects.create(user=user, message=message, meta=meta)

    @staticmethod
    def send_notification_request(user, message, request):
        meta = {
            'route': {
                'id': request.request_id,
                'route_type': request.uni_type or 'REQUEST'
            }
        }

        NotificationManager.send_notification(user, message, meta)

    @staticmethod
    def send_notification_request_number(user, message, request_number):
        request = Request.objects.filter(request_number=request_number).first()

        if request:
            NotificationManager.send_notification_request(user, message, request)
