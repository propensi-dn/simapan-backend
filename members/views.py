from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import MemberRegisterSerializer
from .models import Member

class MemberRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]  # untuk file upload

    def post(self, request):
        serializer = MemberRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Registrasi berhasil. Data sedang menunggu verifikasi.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MemberStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Email wajib diisi'}, status=400)
        try:
            member = Member.objects.get(user__email=email)
            return Response({'email': email, 'status': member.status})
        except Member.DoesNotExist:
            return Response({'error': 'Email tidak ditemukan'}, status=404)
