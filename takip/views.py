from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, date
import calendar
import json
from takip.forms import OgrenciGirisForm
from takip.models import Student, DailyReading

# -------------------- ÖĞRENCİ --------------------
def ogrenci_giris(request):
    if request.method == 'POST':
        form = OgrenciGirisForm(request.POST)
        if form.is_valid():
            sinif = form.cleaned_data['sinif']
            numara = form.cleaned_data['numara']
            if not numara.startswith('12'):
                messages.error(request, 'Numara 12 ile başlamalıdır.')
                return redirect('ogrenci_giris')
            real_no = numara[2:]
            try:
                student = Student.objects.get(student_no=real_no, classroom=sinif)
                request.session['student_id'] = student.id
                return redirect('ogrenci_panel')
            except Student.DoesNotExist:
                messages.error(request, 'Numara veya sınıf hatalı.')
    else:
        form = OgrenciGirisForm()
    return render(request, 'takip/ogrenci_giris.html', {'form': form})

"""def ogrenci_panel(request):
    if 'student_id' not in request.session:
        return redirect('ogrenci_giris')
    student = Student.objects.get(id=request.session['student_id'])
    sinif_ogrencileri = Student.objects.filter(classroom=student.classroom).order_by('student_no')
    bugun = timezone.now().date()
    tarihler = [bugun - timedelta(days=i) for i in range(15)]
    tarihler.sort()
    okuma_dict = {}
    for ogr in sinif_ogrencileri:
        okuma_dict[ogr.id] = {}
        for tarih in tarihler:
            dr, _ = DailyReading.objects.get_or_create(student=ogr, date=tarih)
            okuma_dict[ogr.id][tarih] = dr.completed
    context = {
        'student': student,
        'sinif_ogrencileri': sinif_ogrencileri,
        'tarihler': tarihler,
        'bugun': bugun,
        'okuma_dict': okuma_dict,
    }
    return render(request, 'takip/ogrenci_panel.html', context)"""
def ogrenci_panel(request):
    if 'student_id' not in request.session:
        return redirect('ogrenci_giris')
    student = Student.objects.get(id=request.session['student_id'])
    sinif_ogrencileri = Student.objects.filter(classroom=student.classroom).order_by('student_no')
    bugun = timezone.now().date()
    # Ayın ilk ve son günü
    ay_ilk = date(bugun.year, bugun.month, 1)
    ay_son = date(bugun.year, bugun.month, calendar.monthrange(bugun.year, bugun.month)[1])
    gun_adi_map = {0: 'Pzt', 1: 'Sal', 2: 'Çar', 3: 'Per', 4: 'Cum', 5: 'Cmt', 6: 'Paz'}
    tarihler = []
    gun = ay_ilk
    while gun <= ay_son:
        weekday = gun.weekday()
        gun_adi = gun_adi_map[weekday]
        tarihler.append({'tarih': gun, 'gun_adi': gun_adi})
        gun += timedelta(days=1)
    okuma_dict = {}
    for ogr in sinif_ogrencileri:
        okuma_dict[ogr.id] = {}
        for gun_bilgisi in tarihler:
            tarih = gun_bilgisi['tarih']
            dr, _ = DailyReading.objects.get_or_create(student=ogr, date=tarih)
            okuma_dict[ogr.id][tarih] = dr.completed
    context = {
        'student': student,
        'sinif_ogrencileri': sinif_ogrencileri,
        'tarihler': tarihler,
        'bugun': bugun,
        'okuma_dict': okuma_dict,
    }
    return render(request, 'takip/ogrenci_panel.html', context)
def ajax_tik_ekle(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if 'student_id' not in request.session:
            return JsonResponse({'status': 'error', 'message': 'Oturum yok'}, status=403)
        student = Student.objects.get(id=request.session['student_id'])
        data = json.loads(request.body)
        ogr_id = data.get('ogr_id')
        tarih_str = data.get('tarih')
        if not ogr_id or not tarih_str:
            return JsonResponse({'status': 'error', 'message': 'Eksik parametre'})
        if int(ogr_id) != student.id:
            return JsonResponse({'status': 'error', 'message': 'Başkasına tik atamazsınız'})
        tarih = timezone.datetime.strptime(tarih_str, '%Y-%m-%d').date()
        bugun = timezone.now().date()
        if tarih != bugun:
            return JsonResponse({'status': 'error', 'message': 'Sadece bugün için tik atabilirsiniz'})
        dr, _ = DailyReading.objects.get_or_create(student=student, date=tarih)
        if dr.completed:
            return JsonResponse({'status': 'error', 'message': 'Bugün zaten tik attınız'})
        dr.completed = True
        dr.save()
        return JsonResponse({'status': 'success', 'message': 'Tik başarıyla eklendi'})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'}, status=400)

# -------------------- ÖĞRETMEN --------------------
def ogretmen_giris(request):
    if request.user.is_authenticated:
        return redirect('ogretmen_panel')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            auth_login(request, user)
            return redirect('ogretmen_panel')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre veya yetki yok')
    return render(request, 'takip/ogretmen_giris.html')

@login_required
def ogretmen_panel(request):
    if not request.user.is_superuser:
        return redirect('ogretmen_giris')
    siniflar = Student.objects.values_list('classroom', flat=True).distinct().order_by('classroom')
    secilen_sinif = request.GET.get('sinif')
    if not secilen_sinif and siniflar:
        secilen_sinif = siniflar[0]
    if secilen_sinif:
        ogrenciler = Student.objects.filter(classroom=secilen_sinif).order_by('student_no')
    else:
        ogrenciler = Student.objects.none()

    bugun = timezone.now().date()
    ay_ilk = date(bugun.year, bugun.month, 1)
    ay_son = date(bugun.year, bugun.month, calendar.monthrange(bugun.year, bugun.month)[1])
    gun_adi_map = {0: 'Pzt', 1: 'Sal', 2: 'Çar', 3: 'Per', 4: 'Cum', 5: 'Cmt', 6: 'Paz'}
    tarihler = []
    gun = ay_ilk
    while gun <= ay_son:
        weekday = gun.weekday()
        gun_adi = gun_adi_map[weekday]
        tarihler.append({'tarih': gun, 'gun_adi': gun_adi})
        gun += timedelta(days=1)

    okuma_dict = {}
    for ogr in ogrenciler:
        okuma_dict[ogr.id] = {}
        for gun_bilgisi in tarihler:
            tarih = gun_bilgisi['tarih']
            dr, _ = DailyReading.objects.get_or_create(student=ogr, date=tarih)
            okuma_dict[ogr.id][tarih] = dr.completed

    context = {
        'siniflar': siniflar,
        'secilen_sinif': secilen_sinif,
        'ogrenciler': ogrenciler,
        'tarihler': tarihler,
        'bugun': bugun,
        'okuma_dict': okuma_dict,
    }
    return render(request, 'takip/ogretmen_panel.html', context)

@login_required
def ajax_tik_ogretmen(request):
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ogr_id = data.get('ogr_id')
            tarih_str = data.get('tarih')
            completed = data.get('completed')
            if not ogr_id or not tarih_str or completed is None:
                return JsonResponse({'status': 'error', 'message': 'Eksik parametre'})
            student = Student.objects.get(id=ogr_id)
            tarih = timezone.datetime.strptime(tarih_str, '%Y-%m-%d').date()
            dr, _ = DailyReading.objects.get_or_create(student=student, date=tarih)
            dr.completed = completed
            dr.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'}, status=400)


def ana_sayfa(request):
    return render(request, 'takip/ana_sayfa.html')


def cikis(request):
    if 'student_id' in request.session:
        del request.session['student_id']
    auth_logout(request)
    return redirect('/')