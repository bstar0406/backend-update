from pac.pre_costing.serializers import RequestLogSerializer


def create_request_log(data):
    serializer = RequestLogSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
        return instance
