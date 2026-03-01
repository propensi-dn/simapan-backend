from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import LoginSerializer, LogoutSerializer


class LoginView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		tokens = serializer.validated_data['tokens']

		return Response(
			{
				'access': tokens['access'],
				'refresh': tokens['refresh'],
				'role': user.role,
				'email': user.email,
			},
			status=status.HTTP_200_OK,
		)


class LogoutView(APIView):
	def post(self, request):
		serializer = LogoutSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		refresh_token = serializer.validated_data['refresh']
		token = RefreshToken(refresh_token)
		token.blacklist()

		return Response({'message': 'Logout berhasil'}, status=status.HTTP_200_OK)

# Create your views here.
