from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from visualizations.visualizations import plot_driver_lap_times, tyre_usage_pie
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
        "y-data": request.GET.get("y-data", "sLapTime"),
    }
    context = {
        "image": "",
        "y_options": ["DeltaToRep", "DeltaToFastest", "PctFromRep", "PctFromFastest", "DeltaToLapRep", "PctFromLapRep", "sLapTime", "sDeltaToRep", "sDeltaToFastest", "sDeltaToLapRep"],
    }
    for key in form_data:
        if form_data[key] is None:
            return render(request, "analytics/lap_times.html", context)
    lap_time_lineplot = plot_driver_lap_times(
        year=int(form_data["year"]),
        event=form_data["event"],
        drivers=form_data["drivers"],
        y=form_data["y-data"],
        upper_bound=10,
        absolute_compound=form_data["absolute_compound"],
    )
    imgdata = StringIO()
    lap_time_lineplot.savefig(imgdata, format="svg")
    imgdata.seek(0)
    context["image"]= imgdata.getvalue()
    return render(request, "analytics/lap_times.html", context)

def tyre_usage(request):
    form_data = {
        "year": request.GET.get("year"),
        "events": request.GET.getlist("events[]"),
        # "drivers": request.GET.getlist("drivers[]"),
        "slick_only": request.GET.get("slick_only", False) == "on",
        "absolute_compound": request.GET.get("absolute_compound", False) == "on",
    }
    context = {
        "image": "",
    }
    for key in form_data:
        if form_data[key] is None:
            return render(request, "analytics/tyre_usage.html", context)
    lap_time_lineplot = tyre_usage_pie(
        year=int(form_data["year"]),
        events=form_data["events"],
        drivers=None,
        absolute_compound=form_data["absolute_compound"],
        slick_only=form_data["slick_only"],
    )
    imgdata = StringIO()
    lap_time_lineplot.savefig(imgdata, format="svg")
    imgdata.seek(0)
    context["image"]= imgdata.getvalue()
    return render(request, "analytics/tyre_usage.html", context)


def events(request):
    year = request.GET.get("year")
    if year is None:
        return HttpResponseBadRequest('Missing params')
    events = get_event_lists(int(year))
    return JsonResponse({"events": events})

def drivers(request):
    year = request.GET.get("year")
    event = request.GET.get("event")
    if year is None or event is None:
        return HttpResponseBadRequest('Missing params')
    drivers = event_to_drivers_csv(int(year), event)
    return JsonResponse({"drivers":drivers})