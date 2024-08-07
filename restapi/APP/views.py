from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TokenUserAuthenticationSerializer, CreateAccountSerializer

class ObtainAuthTokenView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TokenUserAuthenticationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CreateAccountView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateAccountSerializer(data=request.data)
        if serializer.is_valid():
            create_result = serializer.create(serializer.validated_data)
            return Response(create_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)