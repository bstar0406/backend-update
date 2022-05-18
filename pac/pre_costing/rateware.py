from lxml import etree as ET
from zeep import Client
from zeep.helpers import serialize_object
import json
from pac.settings.settings import RATEWARE_HEADER
from pac.pre_costing.requestlog import create_request_log
from pac.pre_costing.models import RequestLog

# TODO:
# 1. User authentication expiration
# 2. Rate expiration period
# 3. Error handling


def rateware_client(wsdl_url="http://applications.smc3.com/AdminManager/services/RateWareXL?wsdl"):
    try:
        client = Client(wsdl_url)
    except:
        return
    return client


def is_ready():
    client = rateware_client()
    if client:
        is_ready = client.service.isReady(_soapheaders=RATEWARE_HEADER)
        return is_ready


def available_tariffs():
    client = rateware_client()
    if client:
        available_tariffs = client.service.AvailableTariffs(_soapheaders=RATEWARE_HEADER)
        return available_tariffs


def error_code_lookup(error_code):
    client = rateware_client()
    if client:
        response = client.service.ErrorCodeLookup(error_code, _soapheaders=RATEWARE_HEADER)
        return response


def ltl_rate_shipment_multiple(ltl_rate_shipment_request_list):
    client = rateware_client()
    if client:
        array_of_ltl_tate_shipment_request_type = client.get_type('ns2:ArrayOfLTLRateShipmentRequest')
        ltl_tate_shipment_request_type = client.get_type('ns2:LTLRateShipmentRequest')

        array_of_ltl_request_detail = client.get_type('ns2:ArrayOfLTLRequestDetail')
        ltl_request_detail = client.get_type('ns2:LTLRequestDetail')

        request = array_of_ltl_tate_shipment_request_type()
        for ltl_rate_ship_request in ltl_rate_shipment_request_list:
            ship_request = ltl_tate_shipment_request_type()
            ship_request.details = array_of_ltl_request_detail()

            # MAp input keys to dat structure
            for key in ship_request.__values__.keys():
                if key in ltl_rate_ship_request:
                    if key == 'details':
                        for details_key in ltl_rate_ship_request[key]:
                            request_detail = ltl_request_detail()
                            request_detail['nmfcClass'] = details_key['nmfcClass']
                            request_detail['weight'] = details_key['weight']
                            ship_request[key]['LTLRequestDetail'].append(request_detail)
                    else:
                        ship_request[key] = ltl_rate_ship_request[key]

            request['LTLRateShipmentRequest'].append(ship_request)

        response = client.service.LTLRateShipmentMultiple(request, _soapheaders=RATEWARE_HEADER)
        return response


def zeep_raw_xml(node):
    return ET.tostring(node, encoding='unicode')


def rateware_request(request_name, args={}):
    client = rateware_client()
    if client:
        response = getattr(client.service, request_name)(**args, _soapheaders=RATEWARE_HEADER)
        node = client.create_message(client.service, request_name)
        request = zeep_raw_xml(node)
        request_log = create_request_log(
            data={"response": json.dumps(serialize_object(response)),
                  "request": request, "system": RequestLog.RATEWARE})
        return response, request_log.reference_id
