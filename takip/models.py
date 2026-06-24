from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    student_no = models.CharField(max_length=10, unique=True, verbose_name="Öğrenci No")
    first_name = models.CharField(max_length=50, verbose_name="İsim")
    last_name = models.CharField(max_length=50, verbose_name="Soyisim")
    classroom = models.CharField(max_length=20, verbose_name="Sınıf")

    def __str__(self):
        return f"{self.student_no} - {self.first_name} {self.last_name}"

    def display_number(self):
        return f"12{self.student_no}"

class DailyReading(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_readings')
    date = models.DateField(verbose_name="Tarih")
    completed = models.BooleanField(default=False, verbose_name="Okuma Tamamlandı")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.date} - {'Tamamlandı' if self.completed else 'Bekliyor'}"