import json
from django.conf import settings

from azure.servicebus import ServiceBusClient, ServiceBusMessage


class PricingEnginePayload():
    def __init__(self, request_id, return_request_status, request_rating_filters):
        self.request_id = request_id
        self.return_request_status = return_request_status
        self.request_rating_filters = request_rating_filters


def queue_pricing_engine(request_id, return_request_status, request_rating_filters) -> bool:
    print(f"Sending Request {request_id} to Pricing Engine")
    try:
        # create a Service Bus client using the connection string
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=settings.SERVICE_BUS_CONNECTION_STRING, logging_enable=True)
        with servicebus_client:
            # get a Queue Sender object to send messages to the queue
            sender = servicebus_client.get_queue_sender(queue_name=settings.SERVICE_BUS_QUEUE_PRICING_ENGINE)
            with sender:
                engine_payload = PricingEnginePayload(request_id, return_request_status, request_rating_filters)

                message = ServiceBusMessage(json.dumps(engine_payload.__dict__))
                sender.send_messages(message)
                print("Message Sent")

                return True
    except Exception as inst:
        print("queue_pricing_engine - An exception occurred")
        print(inst)

    return False
