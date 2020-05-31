from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# model uzytkownika
class Uzytkownik(models.Model):
    imie = models.CharField(max_length=20 ,blank=False)
    # relacja do wbudowanej klasy User w Django
    # aby umozliwic autoryzacje
    user = models.OneToOneField(User, on_delete=models.CASCADE)

# model zakupu
class Zakup(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=150, blank=True, default='')
    cena = models.IntegerField()
    # pola kto_kupil oraz dla_kogo sa w relacji z konkretnymi uzytkownikami
    kto_kupil = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name="zakupy")
    dla_kogo = models.ManyToManyField(Uzytkownik, related_name="dla_kogo", blank=True)

    class Meta:
        # sortuj od najnowszego
        ordering = ['-data', 'opis', 'cena']