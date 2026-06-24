from django.urls import path
from takip import views

urlpatterns = [
    path('', views.ana_sayfa, name='ana_sayfa'),  # ANA SAYFA EKLENDİ
    path('ogrenci-giris/', views.ogrenci_giris, name='ogrenci_giris'),
    path('ogrenci-panel/', views.ogrenci_panel, name='ogrenci_panel'),
    path('ogretmen-giris/', views.ogretmen_giris, name='ogretmen_giris'),
    path('ogretmen-panel/', views.ogretmen_panel, name='ogretmen_panel'),
    path('api/tik-ekle/', views.ajax_tik_ekle, name='ajax_tik_ekle'),
    path('api/tik-ogretmen/', views.ajax_tik_ogretmen, name='ajax_tik_ogretmen'),
    path('cikis/', views.cikis, name='cikis'),
]