# hh2mc

Адаптер для проксирования запросов из HTTP-заголовков в формат memcached.

Принимет HTTP-запросы, где в  HTTP-заголовках (Memcached-Key, Memcached-Value, Memcached-Time) указываются значения передаваемые в memcached.
Ответ из memcached так же возвращаетя в HTTP-заголовках.
Метод GET для запроса значений, POST для записи значений в memcached.
Позврашаются коды HTTP-статуса: 200 - при удачных запросах/записях данных, 400-599 - при не нахождении значений, и др. ошибках.

Изначально предназначалось для возможности записи из nginx в memcached значений сесионной информации.

Написано на Python-е, компилируется [py2bin](https://github.com/editorbank/py2bin)-ом в единый независимый от установок Python-а бинарный файл.
Бинарный файл заварачивается в Docker-образ на основе чистой Ubuntu.

## Требования к среде сборки

* ОС Linux семейства Ubuntu
* Установленный Docker или Podman

## Настройка

Среду поддержки образов можно указать в переменой `docker` указав в значении `podman` или `docker` в файлах `config.sh` и `py2bin.sh`.
Там же можно указать имя контейнера и образ.

## Сборка

Для (пере)сборки образа выполните команду:

```bash
./build.sh
```

## Проверка

Получившийся образ можно увидеть командой

```bash
docker images -f reference=hh2mc
```

Запустить образ для подсказки использования

```bash
docker run -it --rm --name hh2mc docker.io/editorbank/hh2mc:latest /hh2mc.bin --help
```

## Запуск в отдельных контейнерах

Запускаем образы в разных контейнерах на хостовой машине с полученим запросов по порту 8080 и перенаправлением в memcached на порт 8211 в другой.
Где 192.168.0.198 - это внешний адрес хостовой машины, если указать 127.0.0.1 или 0.0.0.0, то запрос из контейнера не выйдет.

```bash
docker run -d --rm -p 8211:8211 --name mc docker.io/library/memcached:latest memcached -p 8211
docker run -d --rm -p 8080:8080 --name hh2mc docker.io/editorbank/hh2mc:latest /hh2mc.bin 0.0.0.0:8080 192.168.0.198:8211
```

Проверяем, тут `localhost` или `192.168.0.198` уже не принципиально.

```bash
curl -D- -X GET localhost:8080 -H "Memcached-Key: kkk" ;\
curl -D- -X POST localhost:8080 -H "Memcached-Key: kkk" -H "Memcached-Value: vvv" ;\
curl -D- -X GET localhost:8080 -H "Memcached-Key: kkk"
```

Ниже ответ. В первом запросе ключ `kkk` небыл найден, вторым мы его добавили, третим получили его значение `vvv`.

```bash
HTTP/1.0 404 Not Found
Server: SimpleHTTP/0.6 Python/3.10.6
Date: Sun, 04 Jun 2023 03:41:44 GMT
Content-Length: 0

HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.10.6
Date: Sun, 04 Jun 2023 03:41:44 GMT
Content-Length: 0

HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.10.6
Date: Sun, 04 Jun 2023 03:41:44 GMT
Memcached-Value: vvv
Content-Length: 0

```

Тушим контейнеры

```bash
docker stop -i mc hh2mc
```

## Локальный запуск при разработке

```bash
apt install -y python3.10-venv python3.10-pip && python3 -m venv venv
bash -c "source venv/bin/activate && pip install -r ./requirement.txt"
bash -c "source venv/bin/activate && python ./hh2mc.py 127.0.0.1:8080 127.0.0.1:8211"
```
