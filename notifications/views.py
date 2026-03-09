from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer


class NotificationListView(APIView):
    """
    GET  /api/notifications/
        - Returns notifications for the logged-in user
        - Supports ?is_read=false for unread count (used by bell icon)

    DELETE /api/notifications/
        - Mark ALL notifications as read (bulk)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user)

        # Filter by read status — used by bell icon badge
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')

        # Filter by type — optional
        notif_type = request.query_params.get('type')
        if notif_type:
            qs = qs.filter(type=notif_type.upper())

        serializer = NotificationListSerializer(qs, many=True)
        return Response({
            'count':   qs.count(),
            'results': serializer.data,
        })

    def delete(self, request):
        """Mark all as read."""
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)

        return Response({'marked_read': updated}, status=status.HTTP_200_OK)


class NotificationDetailView(APIView):
    """
    GET   /api/notifications/{id}/   → detail notifikasi
    PATCH /api/notifications/{id}/   → mark as read
    """
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, user):
        try:
            return Notification.objects.get(pk=pk, recipient=user)
        except Notification.DoesNotExist:
            return None

    def get(self, request, pk):
        notif = self._get_object(pk, request.user)
        if not notif:
            return Response({'message': 'Notifikasi tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        # Auto mark as read when opened
        if not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=['is_read'])

        serializer = NotificationSerializer(notif)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Explicitly mark as read (for frontend bell dismiss)."""
        notif = self._get_object(pk, request.user)
        if not notif:
            return Response({'message': 'Notifikasi tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'message': 'Notifikasi ditandai sudah dibaca.'})


class UnreadCountView(APIView):
    """
    GET /api/notifications/unread-count/
    Lightweight endpoint — only returns the unread count for the bell badge.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return Response({'unread_count': count})