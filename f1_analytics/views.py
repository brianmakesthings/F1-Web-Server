from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from visualizations.visualizations import plot_driver_lap_times
from f1_analytics.events_drivers import get_event_lists, event_to_drivers_csv
from io import StringIO

# Create your views here.
def index(request):
    return render(request, "analytics/index.html")


def lap_times(request):
    form_data = {
        "year": request.GET.get("year"),
        "event": request.GET.get("event"),
        "drivers": request.GET.getlist("drivers[]"),
        "absolute_compound": request.GET.get("absolute_compound", False) == "on",
    }
    for key in form_data:
        if form_data[key] is None:
            return render(request, "analytics/lap_times.html", {"image": ""})
    lap_time_lineplot = plot_driver_lap_times(
        year=int(form_data["year"]),
        event=form_data["event"],
        drivers=form_data["drivers"],
        y="sLapTime",
        upper_bound=10,
        absolute_compound=False,
    )
    imgdata = StringIO()
    lap_time_lineplot.savefig(imgdata, format="svg")
    imgdata.seek(0)
    svg_data = imgdata.getvalue()
    return render(request, "analytics/lap_times.html", {"image": svg_data})

def events(request):
    year = request.GET.get("year", "2021")
    events = get_event_lists(int(year))
    return JsonResponse({"events": events})

def drivers(request):
    year = request.GET.get("year", "2021")
    event = request.GET.get("event", "Bahrain Grand Prix")
    drivers = event_to_drivers_csv(int(year), event)
    return JsonResponse({"drivers":drivers})