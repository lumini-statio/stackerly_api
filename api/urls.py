from django.urls import path
from rest_framework.routers import DefaultRouter
from api.views import *

router = DefaultRouter()

# viewsets routes
router.register('box', BalanceBoxViewSet, 'box')
router.register('location', LocationViewSet, 'location')
router.register('order', OrderViewSet, 'order')
router.register('product', ProductViewSet, 'product')
router.register('product-state', ProductStateViewSet, 'product-state')
router.register('profit', ProfitLossRecordViewSet, 'profit')
router.register('purchase', PurchaseViewSet, 'purchase')
router.register('store', StoreViewSet, 'store')
router.register('user-purchase', UserPurchaseViewSet, 'user-purchase')

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
]

urlpatterns += router.urls
