from requests import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_comments(request):
    user_id = self.kwargs.get("entity_id")
    return Comment.objects.filter(entity_id=user_id)

    return Response(None, status=status.HTTP_200_OK)
