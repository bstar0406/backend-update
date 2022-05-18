import json
from datetime import datetime, timezone

from pac.notifications import NotificationManager
from pac.rrf.models import ImportFile, RequestSectionLaneImportQueue, RequestSectionLanePricingPointImportQueue, \
    RequestSectionLanePointType, RequestSectionLane
from pac.rrf.utils import to_int
from pac.rrf.validators import do_validate_lanes, resolve_lane_ids, do_validate_header, do_validate_pricing_point, \
    resolve_pricing_point_ids


def status_watcher():
    files = ImportFile.objects.filter(uni_status__in=['UNPROCESSED'])
    import_queue_dict = {"LANE": RequestSectionLaneImportQueue,
                         "PRICINGPOINT": RequestSectionLanePricingPointImportQueue}
    for file in files:
        # total records and header
        rec_count = file.record_count + 1
        status_array = list(
            import_queue_dict[file.uni_type].objects.values('id', 'uni_status').filter(file=file).filter(
                uni_status__in=['VALID', 'INVALID']))

        if rec_count == len(status_array):
            if any(d['uni_status'] == 'INVALID' for d in status_array):
                file.uni_status = 'INVALID'
                file.updated_on = datetime.now(tz=timezone.utc)
            else:
                file.uni_status = 'VALID'
                file.updated_on = datetime.now(tz=timezone.utc)

            file.save()
            # TODO - to configure message storage, to support internationalization
            NotificationManager.send_notification(file.created_by, f"File {file.file_name} validated.",
                                                  {'type': 'VALIDATION_COMPLETED_' + file.uni_status,
                                                   'request_section_id': file.request_section_id})
            print("all processed sending notification")


def validate():
    files = ImportFile.objects.filter(uni_status__in=['UNPROCESSED'])

    for file in files:
        try:
            if file.uni_type == 'LANE':
                validate_lanes(file)
            elif file.uni_type == 'PRICINGPOINT':
                validate_pricing_points(file)
        except Exception as e:
            # TODO change status to CRASHED, and send notification to user
            file.uni_status = 'CRASHED'
            ImportFile.save(file)


def validate_lanes(file):
    header = RequestSectionLaneImportQueue.objects.filter(
        uni_type='HEADER',
        file=file
    ).first()
    if header and header.uni_status == 'UNPROCESSED':
        do_validate_header(header, request_section_id=file.request_section_id)
        RequestSectionLaneImportQueue.objects.filter(id=header.id).update(uni_status=header.uni_status,
                                                                          status_message=json.dumps(
                                                                              header.status_message))
    lanes = list(
        RequestSectionLaneImportQueue.objects.filter(
            uni_status__in=['UNPROCESSED'],
            uni_type='DATA',
            file=file))

    location_hierarchy = dict(
        RequestSectionLanePointType.objects
            .order_by('request_section_lane_point_type_name')
            .values_list('request_section_lane_point_type_name', 'location_hierarchy')
            .distinct())
    existing_request_section_lanes = list(RequestSectionLane.objects.values('origin_code',
                                                                            'destination_code', 'is_between').filter(
        request_section_id=file.request_section_id))

    for lane in lanes:
        if do_validate_lanes(file, header, lane, location_hierarchy, lanes=lanes,
                             existing_request_section_lanes=existing_request_section_lanes) == 'VALID':
            resolve_lane_ids(lane)
            RequestSectionLaneImportQueue.objects.filter(id=lane.id).update(
                orig_group_type_id=lane.orig_group_type_id,
                origin_group_id=lane.origin_group_id,
                origin_point_type_id=lane.origin_point_type_id,
                origin_point_id=lane.origin_point_id,
                destination_group_type_id=lane.destination_group_type_id,
                destination_group_id=lane.destination_group_id,
                destination_point_type_id=lane.destination_point_type_id,
                destination_point_id=lane.destination_point_id,
                uni_status=lane.uni_status,
                updated_on=datetime.now(tz=timezone.utc),
                status_message=json.dumps(lane.status_message))

        else:
            RequestSectionLaneImportQueue.objects.filter(id=lane.id).update(
                uni_status=lane.uni_status,
                updated_on=datetime.now(tz=timezone.utc),
                status_message=json.dumps(
                    lane.status_message))

    file.save(update_fields=["duplicate_lane_count", "directional_lane_count", "between_lane_count"])


def validate_pricing_points(file):
    header = RequestSectionLanePricingPointImportQueue.objects.filter(
        uni_type='HEADER',
        file=file
    ).first()

    if header and header.uni_status == 'UNPROCESSED':
        do_validate_header(header, header_type='PP', request_section_id=file.request_section_id)
        status_message = json.dumps(header.status_message)
        RequestSectionLanePricingPointImportQueue.objects.filter(id=header.id).update(uni_status=header.uni_status,
                                                                                      status_message=status_message)
    if header and header.uni_status == 'VALID':
        pricing_points = list(
            RequestSectionLanePricingPointImportQueue.objects.filter(
                uni_status__in=['UNPROCESSED'],
                uni_type='DATA',
                file=file))

        if pricing_points:

            for pricing_point in pricing_points:
                request_section_lane_id = to_int(pricing_point.request_section_lane_id)

                if request_section_lane_id:
                    lane = RequestSectionLane.objects.filter(
                        request_section_lane_id=pricing_point.request_section_lane_id).first()
                else:
                    lane = None

                if do_validate_pricing_point(file, header, pricing_point, lane=lane, ) == 'VALID':
                    resolve_pricing_point_ids(pricing_point)
                    RequestSectionLanePricingPointImportQueue.objects.filter(id=pricing_point.id).update(
                        origin_postal_code_id=pricing_point.origin_postal_code_id,
                        destination_postal_code_id=pricing_point.destination_postal_code_id,
                        uni_status=pricing_point.uni_status,
                        status_message=json.dumps(pricing_point.status_message))
                else:
                    RequestSectionLanePricingPointImportQueue.objects.filter(id=pricing_point.id).update(
                        uni_status=pricing_point.uni_status,
                        updated_on=datetime.now(tz=timezone.utc),
                        status_message=json.dumps(
                            pricing_point.status_message))
    else:
        file.uni_status = 'INVALID'
        file.updated_on = datetime.now(tz=timezone.utc)
    file.save(update_fields=["uni_status", "updated_on"])
