from django.shortcuts import render

# Create your views here.
def show_login(request):
    return render(request, "html.html")
def show_register(request):
    return render(request, "html2.html")
def show_landing(request):
    return render(request, "html3.html")