from django.shortcuts import render


def tableau_report(request):
    return render(request, 'tableau.html')