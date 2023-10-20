from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .models import Vehicle
from .serializers import VehicleSerializer


class GetVehicleApiView(GenericAPIView):
    """
    get vehicle by id
    """

    serializer_class = VehicleSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        vehicle = Vehicle.objects.filter(id=id).first()
        if vehicle is not None:
            serializer = VehicleSerializer(vehicle)
            return Response(serializer.data)
        message = {"detail": f"No vehicle with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class GetDriverVehiclesApiView(GenericAPIView):
    """
    get all vehicles owned by driver using id
    """

    serializer_class = VehicleSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwags):
        vehicles = Vehicle.objects.filter(owner__id=id)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


class VehicleApiView(GenericAPIView):
    """
    show all vehicles present
    """

    serializer_class = VehicleSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


class VehicleOwnerApiView(GenericAPIView):
    """
    get, add, update and delete vehicle as owner
    """

    serializer_class = VehicleSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        vehicles = Vehicle.objects.filter(owner=user)
        if vehicles.count() < 1:
            data = {"Vehicle": ["You do not have any yet"]}
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = user.user_owner.all().first()
        if not profile.is_approved:
            msg = "Your details have not been approved yet, contact admin"
            return Response(msg, status=status.HTTP_401_UNAUTHORIZED)
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        vehicle = Vehicle.objects.filter(id=id).first()
        if vehicle is not None:
            serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        message = {"detail": f"No vehicle with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class DeleteVehicleApiView(APIView):
    """
    delete vehicle, requires id
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            msg = "Vehicle id is required for this operation"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        vehicle = Vehicle.objects.filter(id=id).first()

        if not vehicle:
            msg = "Vehicle id doest not exist"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        vehicle.delete()
        msg = " Vehicle deleted successfully"
        return Response(msg, status=status.HTTP_202_ACCEPTED)
