from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a job application to edit or delete it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the job application's user matches the requesting user
        return obj.user == request.user