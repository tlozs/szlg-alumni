from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TokenUserAuthenticationSerializer, CreateAccountSerializer, EditProfileSerializer, CreatePostSerializer, GetUsersSerializer, GetPostsSerializer, DeletePostSerializer

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
    
class EditProfileView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EditProfileSerializer(data=request.data)
        if serializer.is_valid():
            edit_result = serializer.modify(serializer.validated_data)
            return Response(edit_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CreatePostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            create_result = serializer.create(serializer.validated_data)
            return Response(create_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetUsersView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = GetUsersSerializer(data=request.data)
        if serializer.is_valid():
            get_result = serializer.get_users(serializer.validated_data)
            return Response(get_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetMeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = GetUsersSerializer(data=request.data)
        if serializer.is_valid():
            get_result = serializer.get_me(serializer.validated_data)
            return Response(get_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUserView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        serializer = GetUsersSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            get_result = serializer.get_by_id(serializer.validated_data)
            return Response(get_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetPostsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = GetPostsSerializer(data=request.data)
        if serializer.is_valid():
            get_result = serializer.get_posts(serializer.validated_data)
            return Response(get_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DeletePostSerializer(data=request.data)
        if serializer.is_valid():
            delete_result = serializer.delete_post(serializer.validated_data)
            return Response(delete_result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)