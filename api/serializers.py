from rest_framework.serializers import ModelSerializer
from api.models import (BalanceBox, CustomUser,
                        Location, Order, Product,
                        ProductState, ProfitLossRecord, Purchase,
                        Store, UserPurchase)


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class BalanceBoxSerializer(ModelSerializer):
    class Meta:
        model = BalanceBox
        fields = '__all__'


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductStateSerializer(ModelSerializer):
    class Meta:
        model = ProductState
        fields = '__all__'


class ProfitLossRecordSerializer(ModelSerializer):
    class Meta:
        model = ProfitLossRecord
        fields = '__all__'


class PurchaseSerializer(ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class StoreSerializer(ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class UserPurchaseSerializer(ModelSerializer):
    class Meta:
        model = UserPurchase
        fields = '__all__'
