from django.urls import path
from .views import co_regulated_dashboard_report

urlpatterns = [
    path('co_regulated_dashboard/', view=co_regulated_dashboard_report.as_view(), name='co_regulated_dashboard'),
    # 其他路徑
]
