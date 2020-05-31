
# Splitistic

API wykonane z wykorzystaniem Django Rest Framework.
W momencie gdy dzieli się mieszkanie zdarzają  się zakupy, które trzeba wykonać dla wszystkich. Po kilku takich zakupach traci się rachubę kto jest komu winien ile pieniędzy. Tutaj z pomocą przychodzi Splitistic. API pozwala na wprowadzanie danych dotyczących zakupów takich jak, cena oraz dla kogo zostały one zrobione. Dzięki czemu, potem przy użyciu jednego żądania wszystkie problemy z tym kto ma komu oddać ile pieniędzy zostaną natychmiast rozwiązane. 

## API Requests

 - /login/ - autoryzacja użytkowników
 - /zakup/
	 -  POST 

    ```
    {
        "opis": banana < opis zakupu >,
        "cena": 25.40 < cena zakupy >,
        "dla_kogo": < lista id dla kogo zakup był zrobiony > 
        [
            1,
            2,
            3,
            4
	    ]
    }
    ```
    - GET - purchase list
	```
	[
		{
	    "id": 1,
	    "data": "2019-12-07T15:26:37.557683Z",
	    "opis": "jajka",
	    "cena": 200,
	    "kto_kupil": 1,
	    "dla_kogo": [
	        1,
	        2,
	        3,
	        4
	    ]
	},
	{
	    "id": 2,
	    "data": "2019-12-07T15:27:48.710730Z",
	    "opis": "banan",
	    "cena": 400,
	    "kto_kupil": 2,
	    "dla_kogo": [
	        1,
	        2,
	        3,
	        4
		]
	}]
	```
	- DELETE /zakup/&lt;id> - usunięcie wybranego wpisu, trzeba być osobą, która wykonała zakup
- /graph/ 
	- GET - otrzymanie danych z relacjami kto  jest komu winien pieniądze
```
[
    {
        "kto": 1,
        "komu": 3,
        "ile": 600.0
    },
    {
        "kto": 2,
        "komu": 1,
        "ile": 100.0
    },
    {
        "kto": 3,
        "komu": "",
        "ile": ""
    },
    {
        "kto": 4,
        "komu": 1,
        "ile": 200.0
    }
]
```
- /uzytkownik/
	- GET - lista użytkowników w sytemie
```
[
    {
        "id": 1,
        "imie": "Marcin"
    },
    {
        "id": 2,
        "imie": "Dawid"
    },
    {
        "id": 3,
        "imie": "Rafal"
    },
    {
        "id": 4,
        "imie": "Tomek"
    }
]
```
- /users/changepassword/ (widok dostępny po zalogowaniu)
	- POST - zmiana obecnego hasła użytkownika
```
{
	"old password": xxxxx <stare hasło>
	"new password": yyyyy <nowe hasło>
}
```
- /users/changeusername/ (widok dostępny po zalogowaniu)
	- POST - zmiana obecnej nazwy użytkownika
```
{
	"new username": Jacek <nowa nazwa użytkownika>
}
```
