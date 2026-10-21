"""Office staff API views — own profile only (management lives on /users)."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsOfficeStaff
from officestaff.models import OfficeStaff


class OfficeStaffMeView(APIView):
    """GET /api/v1/office-staff/me/ — the authenticated office staff profile."""

    permission_classes = [IsOfficeStaff]

    def get(self, request):
        profile = OfficeStaff.objects.filter(user=request.user).first()
        data = {
            "email": request.user.email,
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None,
            "office_location": profile.office_location if profile else None,
            "joining_date": profile.joining_date if profile else None,
        }
        return Response(data)
