from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView,CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from .models import Zakup, Uzytkownik, User
from .serializers import *
from math import ceil
from .permissions import IsOwnerOrReadOnly, IsUserOrReadOnly
import itertools
import math

class ZakupView(viewsets.ModelViewSet):
	queryset = Zakup.objects.all()
	serializer_class = ZakupSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly,
							IsOwnerOrReadOnly
	]


class UzytkownikView(viewsets.ModelViewSet):
	queryset = Uzytkownik.objects.all()
	serializer_class = UzytkownikSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserList(ListAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class UserDetail(RetrieveAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class UserCreate(CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserUpdate(UpdateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly,
							IsUserOrReadOnly]	

class ChangePasswordView(UpdateAPIView):
	serializer_class = ChangePasswordSerializer
	model = User
	permission_classes = (permissions.IsAuthenticated,
							IsUserOrReadOnly)
	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)

		if serializer.is_valid():
			if not self.object.check_password(serializer.data.get("old_password")):
				return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
			# set_password also hashes the password that the user will get
			self.object.set_password(serializer.data.get("new_password"))
			self.object.save()
			response = {
				'status': 'success',
				'code': status.HTTP_200_OK,
				'message': 'Password updated successfully',
				'data': []           
			}
			return Response(response)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangeUsername(UpdateAPIView):
	serializer_class = ChangeUsernameSerializer
	model = User
	permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly)

	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)

		if serializer.is_valid():
			self.object.username = serializer.data.get("new_username")
			self.object.save()
			response = {
				'status': 'success',
				'code': status.HTTP_200_OK,
				'message': 'Username updated successfully',
				'data': []           
			}
			return Response(response)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserView(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class Graph2View(APIView):

	def get(self, request):

		data = Uzytkownik2Serializer(Uzytkownik.objects.all(), many=True).data

		# konwersja do tabelki
		tabelka = []
		wynik = {}
		lenght = len(data)
		for ob in data:
			row = []
			if ob['id'] == lenght:
				temp = str(str(1) + ' placi ' + str(ob['id']))
			else:
				temp = str(str(int(ob['id'])+1) + ' placi ' + str(ob['id']))
			wynik[temp] = 0
			for key in ob['ile_wydal'].keys():   
				row.append(ob['ile_wydal'][key])  
			tabelka.append(row)

		# optymalizacja v1 - po przekatnej
		for y in range(0, len(tabelka), 1):
			for x in range(0, len(tabelka), 1):
				if tabelka[x][y] != 0 or tabelka[y][x] != 0:
					if x == y:
						x += 1
					else:
						if tabelka[x][y] > tabelka[y][x]:
							#print(str(tabelka[x][y]) + ' - ' + str(tabelka[y][x]) + '  ' + str(x) + ',' + str(y))
							tabelka[x][y] -= tabelka[y][x]        
							tabelka[y][x] = 0
						else:
							#print(str(tabelka[y][x]) + ' - ' + str(tabelka[x][y])+ '  ' + str(x) + ',' + str(y))
							tabelka[y][x] -= tabelka[x][y]
							tabelka[x][y] = 0

		# optymalizacja v2 - graf
		max_przeskok = ceil(len(data) / 2)
		ids = [1,2,3,4]
		for x in range(0, len(tabelka), 1):
			for y in range(0, len(tabelka), 1):
				if x == y:
					y += 1
				else:
					if tabelka[x][y] != 0:
						skoki = abs(x-y)
						# print(skoki)
						if skoki <= max_przeskok:
							for i in range(0, skoki):
								# print(str(ids[y-i]) + ' placi ' + str(ids[y-i-1]) + ' ' + str(tabelka[x][y]))                        
								wynik[str(ids[y-i]) + ' placi ' + str(ids[y-i-1])] += tabelka[x][y]
						else:
							# print(str(ids[y]) + ' placi ' + str(ids[y-1]) + ' ' +str(tabelka[x][y])) 
							wynik[str(ids[y]) + ' placi ' + str(ids[y-1])] += tabelka[x][y]

		# optymalizacja v3 - minimum
		minimum = min(wynik.values())
		for key in wynik.keys():

			wynik[key] -= minimum

		return Response(wynik)

class GraphView(APIView):

	def get(self, request):
		# query zwracajace wszystkie zakupy
		data = Zakup2Serializer(Zakup.objects.all(), many=True).data
		# id : [ile wydal, ile_powinien]
		bilans = {
			1 : [0, 0],
			2 : [0, 0],
			3 : [0, 0],
			4 : [0, 0],
		}
		lenght = len(bilans)
		# zrob bilans
		for zakup in data:
			dla_ilu = len(zakup["dla_kogo"])
			bilans[zakup["kto_kupil"]][0] += (zakup["cena"])
			for osoba in zakup["dla_kogo"]:
				bilans[osoba][1] += math.floor(zakup["cena"] / dla_ilu)
		# zoptymalizuj
		# zrob array
		# 0 0 0 0	<- ile wydal
		# 0 0 0 0	<- ile powinien
		# 0 0 0 0	<- dlug
		wydal = 4 * [0]
		powinien = 4 * [0]
		dlug = 4 * [0]
		for key, item in bilans.items():
			wydal[key - 1] = item[0]
			powinien[key - 1] = item[1]
			dlug[key - 1] = powinien[key - 1] - wydal[key - 1]
		smallest = 99999999 # duza wartosc poczatkowa
		# po pierwsze znajdz optymalna kolejnosc
		# w ktorej przekazywane sa pieniadze 
		# od osoby z lewej do prawej

		# wszystkie mozliwe permutacje (1,2,3,4)
		for perm in itertools.permutations([0,1,2,3]):
			# stworz nowa liste
			test = []
			for item in perm:
				test.append(dlug[item])

			accu = 4 * [0]
			accu[0] = test[0]
			minimum = test[0]
			# accu -> akumulacja dlugow
			for i in range(1, len(accu)):
				accu[i] = accu[i-1] + test[i]
				minimum = min(minimum, accu[i])
			# policz sume oddawania pieniedzy
			sum = 0
			for t in range(4):
				accu[t] -= minimum
				sum += accu[t]
			# znajdz minimalna sume
			if sum < smallest:
				# zapisz najlepsza kolejnosc
				# oraz najlepsza akumulacje długu
				best_row = perm
				best_accu = accu
				smallest = sum
		# najlepsza kolejnosc
		best_order = []
		# znajdz ile transakcji mozna pominac
		# 1. porownuj array czy nastepna osoba jest
		# 	 winna wiecej niz poprzednia 
		# 2. jezeli tak to odejmij czesc dlugu i 
		#    transakcja moze byc pominieta do kolejnej
		#    osoby
		# 3. przesun odpowiednio ilosc pieniedzy ktore
		#    musza oddac  
		for guy in best_row:
			best_order.append(guy + 1)

		temp_accu = best_accu[-1:] + best_accu[:-1]
		pay_to_n = lenght * [0]
		# porownaj kolejne dlugi wobec nastepnej osoby
		# jezeli jest mniejszy niz kolejny to:
		# pay_to_n[osoba] = 1 czyli mozna pominac
		# transakcje i przeniesc ja do kolejnej osoby
		for i in range(0, lenght):
			if i == lenght-1:
				if temp_accu[i] < temp_accu[0]:
					pay_to_n[i] = 1
			else:
				if temp_accu[i] < temp_accu[i+1]:
					pay_to_n[i] = 1
		# utworz listy 
		pays_to = lenght * [0]	# placi n-tej osobie
		amount = lenght * [0]	# ilosc pieniedzy
		temp_sum = 0			# suma kolejnych '1' w pay_to_n 

		# znajdz cykle
		indices = []
		cycles = []
		for i, el in enumerate(pay_to_n):
			tmp = []
			if el:
				tmp.append(i)
				for j in range(1, lenght):
					if pay_to_n[(i+j) % lenght] == 1:
						tmp.append((i+j)%lenght)
					else:
						if len(tmp) > len(indices) and len(tmp) > 1:
							indices = tmp
							cycles.append(tmp)                    
						break
		if not cycles:
			for i, el in enumerate(pay_to_n):
				if el:
					cycles.append([i])		

		for cycle in cycles:
			if len(cycle) < 2:
				for guy in cycle:
					pays_to[guy] = (best_order[(guy + 1) % lenght])
					amount[guy] = best_accu[guy]
			else:
				for i, guy in enumerate(cycle):
					pays_to[guy] = best_order[((cycle[-1]) + 1 )% lenght]
					if i == 0:
						amount[guy] = best_accu[guy]
					else:
						amount[guy] = best_accu[guy] - best_accu[cycle[(i - 1)]]
			
		for i, el in enumerate(best_accu):
			if el != 0 and pays_to[i] == 0:
				amount[i] = el
				pays_to[i] = best_order[(i + 1)%lenght]


				
		# ###############################################################
		# for i,el in enumerate(pay_to_n):
		# 	# jezeli w pay_to_n jest '0' -> brak transakcji
		# 	if el == 0:
		# 		if temp_sum > 0:
		# 			# jezeli byl to koniec ciągu jedynek
		# 			# wszystkie poprzednie osoby musza zaplacic
		# 			# aktualnej osobie
		# 			for x in range(1, temp_sum+1):
		# 				pays_to[i - x]= best_order[i]
		# 		# kolejne jedynki = 0
		# 		temp_sum = 0
		# 		pays_to[i] = best_order[(i+1)%lenght]
		# 		amount[i] = best_accu[i]
		# 	# jezeli w pay_to_n '1'
		# 	else:
		# 		# pierwsza '1'
		# 		if temp_sum == 0 :
		# 			amount[i] = best_accu[i]
		# 		else:
		# 			for x in range(1, temp_sum+1):
		# 				amount[i] = best_accu[i]- best_accu[i - x] 
		# 		# przypadek gdy jest to ostatnia osoba
		# 		# musi zaplacic 1 osobie
		# 		if i == lenght - 1:
		# 			pays_to[i] = best_order[(i+1)%lenght]
		# 			for x in range(1, temp_sum+1):
		# 				pays_to[i - x] = best_order[0]
		# 			amount[i] = best_accu[i] - best_accu[i - 1] 
		# 		# liczba kolejnych '1' + 1
		# 		temp_sum += 1
		# 	if amount[i] == 0:
		# 		pays_to[i] = 0
		# ###############################################################
		# koncowa lista do zwrocenia na stronie
		final =[
			{
				'kto' : '',
				'komu': '',
				'ile' : ''
			},
			{
				'kto' : '',
				'komu': '',
				'ile' : ''
			},
			{
				'kto' : '',
				'komu': '',
				'ile' : ''
			},
			{
				'kto' : '',
				'komu': '',
				'ile' : ''
			}
			]

		# print(f"{best_order} order")
		# print(f'{pay_to_n} pay_to_n')
		# print(f'{pays_to} pays_to')
		# print(f'{amount} amount')
		# print(f'{best_accu} accu')
		# uzupelnij koncowa liste poprawnie
		for i, guy in enumerate(best_order):
			final[guy - 1]["kto"] = guy
			# gdy dlug jest 0 zostaw puste pola
			if amount[i] != 0:
				final[guy - 1]["komu"] = pays_to[i]
				final[guy - 1 ]["ile"] = amount[i]
		# zwroc
		return Response(final)
