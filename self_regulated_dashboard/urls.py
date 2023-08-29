from django.urls import path
from .views import self_regulated_dashboard_report

urlpatterns = [
    path('self_regulated_dashboard/', view=self_regulated_dashboard_report.as_view(), name='self_regulated_dashboard'),
    # 其他路徑
]
