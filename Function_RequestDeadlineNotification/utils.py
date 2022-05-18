import holidays
import numpy
import datetime
from pandas.tseries.offsets import BDay, CustomBusinessDay
from pandas.tseries.holiday import (Holiday, AbstractHolidayCalendar, nearest_workday, MO, Day)

from django.db.models import Q, F

from pac.rrf.models import RequestQueue
from pac.notifications import NotificationManager

# Batch is intended to run at 3am daily.
# Batch picks up records that have not been actioned on since 8am previous business day.

# Requirement to handle Canadian Federal holidays + 11/11


class RequestDeadlineNotification:
    def __init__(self):
        self.overdue_priority_request_queues = []
        # today = datetime.date(2021, 10, 12)
        today = datetime.datetime.today()

        # Load holidays into an AbstractHolidayCalendar
        rules = []
        for date in holidays.Canada(years=[today.year - 1, today.year]).items():
            rules.append(Holiday(date[1], year=date[0].year, month=date[0].month, day=date[0].day))
        holiday_calendar_canada = AbstractHolidayCalendar(rules=rules)

        # Calculate the cutoff date for requests
        self.request_priority_cutoff_datetime = (today
                                                 - CustomBusinessDay(1, calendar=holiday_calendar_canada)
                                                 + datetime.timedelta(hours=8))
        self.request_normal_cutoff_datetime = (today
                                               - CustomBusinessDay(6, calendar=holiday_calendar_canada)
                                               + datetime.timedelta(hours=17))

    def load_overdue_requests(self, debug=False):
        print('Begin Loading Overdue Requests')

        self.overdue_priority_request_queues = self._load_requests(True, self.request_priority_cutoff_datetime)
        self.overdue_normal_request_queues = self._load_requests(False, self.request_normal_cutoff_datetime)

        print('Done Loading Overdue Requests')

    def send_overdue_request_notifications(self, debug=False):
        print('Begin Sending Overdue Request Notifications')

        # Request notifications split to allow differeent messages based on request priority

        # High Priority Requests
        for actionable_request_queue in self.overdue_priority_request_queues:
            self._send_request_notification(actionable_request_queue,
                                f"RRF {actionable_request_queue.request_id} is overdue and must be actioned")

        # Normal Priority Requests
        for actionable_request_queue in self.overdue_normal_request_queues:
            self._send_request_notification(actionable_request_queue,
                                f"RRF {actionable_request_queue.request_id} is overdue and must be actioned")

        print('Done Sending Overdue Request Notificationss')

    def _load_requests(self, is_priority, cutoff_date):
        if is_priority:
            q_filter_priority = Q(request__request_information__priority=True)
        else:
            q_filter_priority = (Q(request__request_information__priority=False)
                                 | Q(request__request_information__priority=None))

        return_list = list(RequestQueue.objects.filter(
            completed_on=None,
            is_actionable=True,
            request__is_active=True,
            request__uni_type=None  # TODO: Confirm only RRF Requests?
        ).filter(
            Q(assigned_on__lte=cutoff_date),
            q_filter_priority
        ).select_related(
            'user',
        ).annotate(
            request_uni_type=F('request__uni_type')
        ))

        return return_list

    def _send_request_notification(self, actionable_request_queue, message):
        NotificationManager.send_notification(
            user=actionable_request_queue.user,
            message=message,
            meta={
                'route': {
                    'id': actionable_request_queue.request_id,
                    'route_type': actionable_request_queue.request_uni_type or 'REQUEST'
                }
            })
