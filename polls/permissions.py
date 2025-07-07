from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Consente accesso in scrittura solo al proprietario dell'oggetto.
    """

    def has_object_permission(self, request, view, obj):
        # Le richieste SAFE (GET, HEAD, OPTIONS) sono sempre permesse
        if request.method in permissions.SAFE_METHODS:
            return True
        # Altrimenti solo se è il creatore
        return obj.created_by == request.user
