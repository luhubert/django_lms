from django.shortcuts import render
from django.views import View

# Create your views here.
class co_regulated_dashboard_report(View):
    def get(self, request):
        return render(request, 'app/co_regulated_dashboard.html')