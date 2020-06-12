from rest_framework import serializers
from wydatki.models import Zakup, Uzytkownik, User
from django.utils   import timezone
import datetime
 
# serializacja zakupów
class ZakupSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
 
    class Meta:
        model = Zakup
        fields = '__all__'
        # pole jest wypelniane automatycznie
        read_only_fields = ('kto_kupil',)
 
    # przekonwertuj date do odpowiedniego formatu
    def get_data(self, obj):
        datetime_str = str(obj.data)
        old_format = '%Y-%m-%d %H:%M:%S.%f+00:00'
        new_format = '%d-%m-%Y %H:%M'
        new_datetime_str = datetime.datetime.strptime(datetime_str, old_format).strftime(new_format)
        return(new_datetime_str)
 
    # przy tworzeniu zakupu automatycznie dodaj kto_kupil
    def create(self, validated_data):
        uzytkownik = self.context['request'].user.uzytkownik
        validated_data['kto_kupil'] = uzytkownik
        return super().create(validated_data)
 
class Zakup2Serializer(serializers.ModelSerializer):
 
    class Meta:
        model = Zakup
        fields = ['id', 'cena', 'kto_kupil', 'dla_kogo']
   
           
class Uzytkownik2Serializer(serializers.ModelSerializer):
    zakupy = Zakup2Serializer(many=True, read_only=True)
    ile_wydal = serializers.SerializerMethodField()
 
    class Meta:
        model = Uzytkownik
        fields = ['id', 'imie', 'zakupy', 'ile_wydal']
 
    def get_ile_wydal(self, obj):
        wydatki = {
            1 : 0,
            2 : 0,
            3 : 0,
            4 : 0
        }
 
        for zakup in obj.zakupy.all():
            for osoba in zakup.dla_kogo.all():
                wydatki[osoba.id] += (zakup.cena / zakup.dla_kogo.count())
 
        return wydatki
 
    def to_representation(self, instance):
        data = super(Uzytkownik2Serializer, self).to_representation(instance)
        #instance_type = data["type"]
 
        data.pop("zakupy")
 
        return data        
 
# serializacja uzytkownikow
class UzytkownikSerializer(serializers.ModelSerializer):
   
    username = serializers.SerializerMethodField()
 
    class Meta:
        model = Uzytkownik
        fields = ('id', 'imie', 'username')
 
    def get_username(self, obj):
        return obj.user.username
 
class UserSerializer(serializers.ModelSerializer):
    uzytkownik = UzytkownikSerializer()
    password = serializers.CharField(write_only=True)
 
    def create(self, validated_data):
        uzytkownik_data = validated_data.pop('uzytkownik')
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        Uzytkownik.objects.create(user=user, **uzytkownik_data)
        user.save()
        return user
 
    def update(self, instance, validated_data):
        uzytkownik = validated_data.get('uzytkownik')
        instance.uzytkownik.imie = uzytkownik.get('imie')
        instance.username = validated_data.get('username')
       
        instance.uzytkownik.save()
        instance.save()
        return instance
 
    class Meta:
        model = User
        fields = ['id', 'uzytkownik', 'username', 'password']
 
class ChangePasswordSerializer(serializers.Serializer):
    model = User
 
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
 
class ChangeUsernameSerializer(serializers.Serializer):
    model = User
 
    new_username = serializers.CharField(required=True)
