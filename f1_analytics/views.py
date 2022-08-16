from django.shortcuts import render
from django.http import HttpResponse
from visualizations.visualizations import plot_driver_lap_times
from io import StringIO

# Create your views here.
def index(request):
    return render(request, "analytics/index.html")


def lap_times(request):
    form_data = {
        "year": request.GET.get("year", "2021"),
        "event": request.GET.get("event", "Hungary"),
        "drivers": request.GET.get("drivers", "[]"),
        "absolute_compound": request.GET.get("absolute_compound", False) == "on",
    }
    lap_time_lineplot = plot_driver_lap_times(
        year=int(form_data["year"]),
        event=form_data["event"],
        drivers=["VER", "LEC", "ALO"],
        y="sLapTime",
        upper_bound=10,
        absolute_compound=False,
    )
    imgdata = StringIO()
    lap_time_lineplot.savefig(imgdata, format="svg")
    imgdata.seek(0)
    svg_data = imgdata.getvalue()
    return render(request, "analytics/lap_times.html", {"image": svg_data})
