from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Notification


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """
    Get user's notifications with optional type filtering
    """
    user = request.user

    # Get filter parameters
    notification_type = request.GET.get('type', '').strip()
    limit = request.GET.get('limit', '50')
    offset = request.GET.get('offset', '0')

    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        limit = 50
        offset = 0

    # Build query
    notifications_query = Notification.objects.filter(user=user)

    # Apply type filter if provided
    if notification_type:
        notifications_query = notifications_query.filter(type=notification_type)

    # Order by most recent first
    notifications_query = notifications_query.order_by('-created_at')

    # Get total count
    total_count = notifications_query.count()

    # Apply pagination
    notifications = notifications_query[offset:offset + limit]

    # Build response
    notifications_list = []
    for notification in notifications:
        notifications_list.append({
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "full_details": notification.full_details,
            "metadata": notification.metadata,
            "read": notification.read,
            "created_at": notification.created_at.isoformat(),
        })

    return Response({
        "success": True,
        "notifications": notifications_list,
        "total_count": total_count,
        "unread_count": Notification.objects.filter(user=user, read=False).count(),
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.read = True
        notification.save(update_fields=['read'])

        return Response({
            "success": True,
            "message": "Notification marked as read"
        })
    except Notification.DoesNotExist:
        return Response({
            "success": False,
            "error": "Notification not found"
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all user's notifications as read
    """
    updated_count = Notification.objects.filter(
        user=request.user,
        read=False
    ).update(read=True)

    return Response({
        "success": True,
        "message": f"{updated_count} notifications marked as read",
        "updated_count": updated_count
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recent_notifications(request):
    """
    Get 3 most recent notifications for dropdown
    """
    user = request.user

    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:3]

    notifications_list = []
    for notification in notifications:
        notifications_list.append({
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "read": notification.read,
            "created_at": notification.created_at.isoformat(),
        })

    unread_count = Notification.objects.filter(user=user, read=False).count()

    return Response({
        "success": True,
        "notifications": notifications_list,
        "unread_count": unread_count,
    })
