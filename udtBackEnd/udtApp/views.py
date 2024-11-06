import json
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from .models import Device
import os
from django.http import FileResponse, Http404
from pathlib import Path
from datetime import datetime

def index(request):
    return render(request, 'udtApp/index.html', {'nbar': 'home'})

def monitor(request):
    # TODO: modify the grafana dashboard
    return render(request, 'udtApp/monitor.html', {'nbar': 'monitor'})

def entity(request, entity_id):
    device = Device.objects(_id__id=entity_id).first()
    print(device)
    if device:
    # return HttpResponse("This is the page where the entity %s is shown" % entity_id)
        return render(request, 'udtApp/entity.html', {'device': device})
        # return HttpResponse(device)
    else:
        return HttpResponse("No device found with this ID", status=404)

def entityList(request):
    # Prendi il parametro 'type' dalla querystring
    device_type = request.GET.get('type', '')

    device_types = sorted(Device.objects.distinct('_id.type'))
    print(device_types)
    # Filtro per il tipo di dispositivo, se specificato
    if device_type:
        # deviceList = Device.objects.filter(_id__type__exact=device_type)
        deviceList = Device.objects.filter(__raw__={'_id.type': {'$regex': f".*{device_type}$"}})
    else:
        deviceList = Device.objects.all()

    print(f"Devices count: {deviceList.count()}")
    paginator = Paginator(deviceList, 10)
    pageNumber = request.GET.get('page')

    page_obj = paginator.get_page(pageNumber)

    context = {
        'page_obj': page_obj,
        'device_types': device_types,
        'request': request,  # Necessario per mantenere il filtro durante la paginazione
    }

    if deviceList:
        return render(request, 'udtApp/entityList.html', context)
    else:
        return HttpResponse("There is no device inside the DB")

def simulation(request):

    # Getting the absolute path of the scenarioCollection folder
    current_dir = os.path.abspath(os.getcwd())
    current_path = Path(current_dir).resolve()
    project_root = current_path.parent
    base_dir = project_root / 'sumoenv' / 'joined' / 'scenarioCollection'
    if not os.path.exists(base_dir):
        base_dir = project_root / 'MOBIDT' / 'sumoenv' / 'joined' / 'scenarioCollection'
        if not os.path.exists(base_dir):
            return render(request, 'udtApp/emptyPage.html', {'item': 'Scenario folder'})

    # Get the selected type (in the page filter). Default is 'basic'
    selected_type = request.GET.get('type', 'basic')
    selected_date = request.GET.get('date', '').strip()
    if not selected_date:  # Se la data non è fornita, usa la data corrente
        selected_date = datetime.now().strftime('%Y-%m-%d')
    start_time = request.GET.get('start_time', '00:00').strip()  # rimuovere spazi bianchi
    end_time = request.GET.get('end_time', '23:00').strip()

    today = datetime.now().date()
    default_date = today.strftime('%Y-%m-%d')

    selected_start_datetime = datetime.strptime(f"{selected_date} {start_time}", '%Y-%m-%d %H:%M')
    selected_end_datetime = datetime.strptime(f"{selected_date} {end_time}", '%Y-%m-%d %H:%M')

    # List of folders containing 'basic' or 'congestioned' in the name
    folders = []
    for folder_name in os.listdir(base_dir):
        try:
            # La cartella ha una data nel formato YYYY-MM-DD_HH-MM-SS_tipo
            folder_datetime_str, folder_type = folder_name.rsplit('_', 1)
            folder_datetime = datetime.strptime(folder_datetime_str, '%Y-%m-%d_%H-%M-%S')

            # Verifica se la cartella è del tipo selezionato e se rientra nell'intervallo orario
            if (selected_type in folder_type) and (selected_start_datetime <= folder_datetime <= selected_end_datetime):
                folders.append(folder_name)
        except ValueError:
            # Se la cartella non ha il formato atteso, ignorala
            continue

    context = {
        'folders': folders,
        'selected_type': selected_type,
        'selected_date': selected_date,
        'selected_start_time': start_time,
        'selected_end_time': end_time,
        'default_date': default_date,
        'hours':  [f"{hour:02d}:00" for hour in range(24)],
    }
    return render(request, 'udtApp/simulation.html', context)


def serve_image(request, folder):

    current_dir = os.path.abspath(os.getcwd())
    current_path = Path(current_dir).resolve()
    project_root = current_path.parent
    base_dir = project_root / 'sumoenv' / 'joined' / 'scenarioCollection'
    folder_path = os.path.join(base_dir, folder)


    # Filter only .png files
    images = [img for img in os.listdir(folder_path) if img.endswith(".png")]

    # Get the selected type (in the page filter). Default is 'basic'
    selected_type = request.GET.get('type', 'basic')

    context = {
        'folder': folder,
        'images': images,
        'selected_type': selected_type,
        'base_dir': base_dir
    }
    return render(request, 'udtApp/simulationScenario.html', context)


