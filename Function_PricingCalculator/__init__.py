import logging
import os
import json
import time
import azure.functions as func

# Load Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pac.settings.settings')  # nopep8
from django.core.wsgi import get_wsgi_application  # nopep8
application = get_wsgi_application()  # nopep8
# Change to django.setup() instead of wsgi

from pac.rrf.models import Request, RequestStatus, RequestStatusType  # nopep8
from pac.rrf.workflow import WorkflowManager
from pac.notifications import NotificationManager

from .utils import RequestCalculator


def main(msg: func.ServiceBusMessage):
    debug_logging = True

    logging.info('Python ServiceBus queue trigger processed message: %s', msg.get_body().decode('utf-8'))
    logging.info(f'Debug logging: {debug_logging}')

    message = json.loads(msg.get_body().decode('utf-8'))
    request_id = message.get('request_id')
    return_request_status = message.get('return_request_status')
    request_rating_filters = message.get('request_rating_filters')

    if not request_id:
        logging.info('request_id must be provided')
    else:
        try:
            # Run Pricing Calculator
            start_time = time.time()
            calc = RequestCalculator(request_id, request_rating_filters)
            calc.pre_run_clear_data(debug_logging)
            calc.pre_run_validate_data(debug_logging)
            calc.request_setup(debug_logging)
            calc.calculate_lane_density(debug_logging)
            calc.calculate_line_haul_cost(debug_logging)
            calc.calculate_dock_cost(debug_logging)
            calc.calculate_pickup_cost(debug_logging)
            calc.calculate_delivery_cost(debug_logging)
            calc.calculate_fak_rate(debug_logging)
            calc.calculate_splits_all(debug_logging)
            calc.calculate_margin(debug_logging)
            calc.calculate_profitability(debug_logging)
            calc.calculate_rates(debug_logging)
            calc.save_data()

            logging.info("--- Calculator completed in %s seconds ---" % (time.time() - start_time))
        except Exception as e:
            logging.info(f"Engine Error: {e}")
            notification_message = f"Request {request_id} - Pricing Engine has thrown an exception and could not complete"
        else:
            notification_message = f"Request {request_id} - Pricing Engine processing is complete"
        finally:
            logging.info("--- Beginning Workflow Reassign ---")
            
            # Return Workflow to return_request_status
            request_instance = Request.objects.filter(
                request_id=request_id
            ).select_related(
                'request_information__customer__account',
                'request_information__request_type'
            ).first()

            request_status_instance = RequestStatus.objects.filter(request=request_instance).first()

            current_request_status_type_instance = RequestStatusType.objects.filter(
                request_status_type_name="With Pricing Engine").first()

            next_request_status_type_instance = RequestStatusType.objects.filter(
                request_status_type_id=return_request_status).first()

            workflow_manager = WorkflowManager(request_status=request_status_instance,
                                               request=request_instance,
                                               current_request_status_type=current_request_status_type_instance,
                                               next_request_status_type=next_request_status_type_instance,
                                               pricing_engine_rating_filters=None)

            if current_request_status_type_instance:
                workflow_manager.close_request_queue()
            if next_request_status_type_instance:
                actionable_users = workflow_manager.generate_request_queue()

            for user in actionable_users:
                NotificationManager.send_notification(user, notification_message, meta=None)

            logging.info(f"--- Request Workflow Reassigned to Status {return_request_status} ---")

    logging.info('done')
