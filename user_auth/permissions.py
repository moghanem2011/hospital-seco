from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status


class Permission(BasePermission):
    message = "You are not authorized to perform this action"
    group_name = ""


    def handle_permission_denied(self, request):
        """
        If request is unauthorized, return a `PermissionDenied` response.
        """
        data = {'success':False ,'detail': self.__class__.message}
        return Response(data, status=status.HTTP_403_FORBIDDEN)


    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.groups.filter(name=self.__class__.group_name).exists()
        
        return self.handle_permission_denied(request)
        # return False


     
class ReciptionPermission(Permission):
   group_name = "reciption"
     

class PharmacyPermission(Permission):
    group_name = "pharmacy"


class DoctorPermission(Permission):
    group_name = "doctor"


class PatientPermission(Permission):
    group_name = "patient"