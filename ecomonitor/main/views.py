from django.shortcuts import render, redirect, get_object_or_404
from .models import Enterprise, Pollutant, Record

def home(request):
    # Отримання даних для відображення у таблицях
    enterprises = Enterprise.objects.all()
    pollutants = Pollutant.objects.all()
    records = Record.objects.select_related('enterprise', 'pollutant').all()

    # Обробка параметрів сортування
    sort_by = request.GET.get('sort_by')
    order = request.GET.get('order')
    # Пошук
    search_query = request.GET.get('search_query')
    if search_query:
        try:
            search_year = int(search_query)
            records = records.filter(year=search_year)
        except ValueError: (
            records) = records.filter(enterprise__enterprise_name__icontains=search_query)
    # Сортування
    if sort_by and order:
        if order == 'asc': records = records.order_by(sort_by)
        elif order == 'desc': records = records.order_by(f'-{sort_by}')


    if request.method == 'POST':
        # Додати підприємство
        if 'new-enterprise-name' in request.POST:
            name = request.POST['new-enterprise-name']
            address = request.POST['new-enterprise-address']
            activity = request.POST['new-enterprise-activity']
            Enterprise.objects.create(
                enterprise_name=name,
                address=address,
                type_enterprise=activity
            )
            return redirect('home')

        # Додати забруднюючу речовину
        elif 'new-pollutant-name' in request.POST:
            name = request.POST['new-pollutant-name']
            hazard_class = request.POST['new-hazard-class']
            gdk = request.POST['new-mpc']
            tax_rate = request.POST.get('new-tax-rate', 0.0)
            cancer_risk_type = request.POST['new-cancer-risk']
            rfc = request.POST['new-rfc']

            Pollutant.objects.create(
                pollutant_name=name,
                danger_class=hazard_class,
                GDK=gdk,
                tax_rate=tax_rate,
                cancer_risk_type=cancer_risk_type,
                rfc=rfc
            )
            return redirect('home')


        # Додати викиди
        elif 'object-name-input' in request.POST:
            enterprise_id = request.POST['object-name-input']
            pollutant_id = request.POST['pollutant-name-input']
            year = request.POST['report-year-input']
            record_type = request.POST['report-type-input']
            volume = float(request.POST['emission-volume-input'])

            enterprise = get_object_or_404(Enterprise, id=enterprise_id)
            pollutant = get_object_or_404(Pollutant, id=pollutant_id)

            record = Record.objects.create(
                enterprise=enterprise,
                pollutant=pollutant,
                year=year,
                type=record_type,
                volume=volume
            )
            record.calculate_risk()  # Обчислення ризиків
            return redirect('home')

    return render(request, 'main/home.html', {
        'enterprises': enterprises,
        'pollutants': pollutants,
        'records': records
    }) #n

def delete_enterprise(request, id):
    enterprise = get_object_or_404(Enterprise, id=id)
    enterprise.delete()
    return redirect('home')

def delete_pollutant(request, id):
    pollutant = get_object_or_404(Pollutant, id=id)
    pollutant.delete()
    return redirect('home')

def delete_record(request, id):
    record = get_object_or_404(Record, id=id)
    record.delete()
    return redirect('home')

def edit_enterprise(request, id):
    enterprise = get_object_or_404(Enterprise, id=id)

    if request.method == 'POST':
        enterprise.enterprise_name = request.POST['edit-enterprise-name']
        enterprise.address = request.POST['edit-enterprise-address']
        enterprise.type_enterprise = request.POST['edit-enterprise-activity']
        enterprise.save()
        return redirect('home')

    enterprises = Enterprise.objects.all()
    pollutants = Pollutant.objects.all()
    records = Record.objects.all()

    return render(request, 'main/home.html', {
        'enterprises': enterprises,
        'pollutants': pollutants,
        'records': records,
        'enterprise_to_edit': enterprise
    })
def edit_pollutant(request, id):
    pollutant = get_object_or_404(Pollutant, id=id)
    if request.method == 'POST':
        pollutant.pollutant_name = request.POST['edit-pollutant-name']
        pollutant.danger_class = request.POST['edit-hazard-class']
        pollutant.GDK = request.POST['edit-mpc']
        pollutant.tax_rate = request.POST['edit-tax-rate']
        pollutant.cancer_risk_type = request.POST['edit-cancer-risk']
        pollutant.rfc = request.POST['edit-rfc']
        pollutant.save()
        return redirect('home')

    enterprises = Enterprise.objects.all()
    pollutants = Pollutant.objects.all()
    records = Record.objects.all()

    return render(request, 'main/home.html', {
        'enterprises': enterprises,
        'pollutants': pollutants,
        'records': records,
        'pollutant_to_edit': pollutant
    })


def edit_record(request, id):
    record = get_object_or_404(Record, id=id)

    if request.method == 'POST':
        record.enterprise_id = request.POST['edit-object-name']
        record.pollutant_id = request.POST['edit-pollutant-name']
        record.year = request.POST['edit-report-year']
        record.type = request.POST['edit-report-type']
        record.volume = float(request.POST['edit-emission-volume'])

        record.save()
        record.calculate_risk()  # Оновлення ризиків
        return redirect('home')

    enterprises = Enterprise.objects.all()
    pollutants = Pollutant.objects.all()
    records = Record.objects.all()

    return render(request, 'main/home.html', {
        'enterprises': enterprises,
        'pollutants': pollutants,
        'records': records,
        'record_to_edit': record
    })
