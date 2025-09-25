from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from django.shortcuts import get_object_or_404

from api.serializers import *
from api.models import *


# Create your views here.
@api_view(['POST'])
def login(request):
    user = get_object_or_404(CustomUser, username=request.data['username'])
    
    if not user.check_password(request.data['password']):
        return Response({"error": "Invalid Password"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = CustomUserSerializer(instance=user)
    
    return Response({
        "token": token.key,
        "user": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    serializer: ModelSerializer = CustomUserSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
    
        user = CustomUser.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()
        
        token = Token.objects.create(user=user)
        
        return Response({
            'token': token.key,
            'user': serializer.data,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = CustomUserSerializer(instance=request.user)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


class BalanceBoxViewSet(ModelViewSet):
    queryset = BalanceBox.objects.all()
    serializer_class = BalanceBoxSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ProductStateViewSet(ModelViewSet):
    queryset = ProductState.objects.all()
    serializer_class = ProductStateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ProfitLossRecordViewSet(ModelViewSet):
    queryset = ProfitLossRecord.objects.all()
    serializer_class = ProfitLossRecordSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class UserPurchaseViewSet(ModelViewSet):
    queryset = UserPurchase.objects.all()
    serializer_class = UserPurchaseSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
