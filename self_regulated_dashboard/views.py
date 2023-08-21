from django.shortcuts import render
from django.views import View

class self_regulated_dashboard_report(View):
    def get(self, request):
        return render(request, 'app/self_regulated_dashboard.html')