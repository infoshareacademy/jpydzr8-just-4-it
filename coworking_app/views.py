from django.shortcuts import render

def coworking_view(request):
    context = {
        "workspace_name": "Skyline Workspace"
    }
    return render(request, "coworking_app/coworking.html", context)
