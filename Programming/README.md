# Прграммная часть проекта "Танковый Бой"
### [**Сервер**](./Server) *(Язык программирования - JavaScript)*
Служит связующим звеном, которое хранит и обрабатывает данные (запросы), получаемые от всех подключенных устройств.\
Располагается на удаленном сервере. 

### [**Клиент**](./Client) *(Язык программирования - Python)*
Графическая среда для управления танками.\
Позволяет отправлять требуемые запросы действий серверу.

### [**Контроллер**](./Arduino/) *(Языки программирования - Python, C++)*
Программа для управления интерактивным полем.

### [**ИИ "Даня"**](./Client) *(Язык программирования - Python)*
Анализирует обстановку на игровом поле, вычисляет и совершает оптимальный ход.

### [**Шея**](./Neck) *(Язык программирования - Python)*
Графическая среда для ручного внесения препятствий и танков на поле.

### [**Голова**](./Head) *(Язык программирования - Python)*
Программа для распознания и отслеживания объектов на поле.

### [**Библиотеки**](./Libraries) *(Язык программирования - Python)*
Хранилище требуемых библиотек для Python-программ.

>### **Информация для подключения по TCP-IP**
>Подключение к удаленному серверу по протоколу TCP-IP происходит по адресу `play.aniby.net` с портом `3030`.