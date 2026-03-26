from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, DealerViewSet, OrderViewSet, InventoryViewSet

from django.urls import path
from .views import DealerRegisterView
 

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('dealers', DealerViewSet)
router.register('orders', OrderViewSet)
router.register('inventory', InventoryViewSet)

urlpatterns = router.urls

# ✅ Add this separately (IMPORTANT)
urlpatterns += [
    path('register/', DealerRegisterView.as_view()),
]

