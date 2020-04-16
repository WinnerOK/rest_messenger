from rest_framework.response import Response
from rest_framework.views import APIView


class PingView(APIView):
    """
    Be sure, API is alive.
    """
    def get(self, request):
        return Response({"pong": True})
