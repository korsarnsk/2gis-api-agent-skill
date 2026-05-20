# 2GIS API — Полный каталог публичных эндпоинтов

Документация: https://docs.2gis.com/

Все API требуют параметр `key` — ключ доступа, получаемый в Platform Manager (https://platform.2gis.com/).

---

## Содержание

1. [Search APIs](#1-search-apis)
   - 1.1 Places API
   - 1.2 Places ById
   - 1.3 Places BySite
   - 1.4 Geocoder API
   - 1.5 Geocoder ByIP
   - 1.6 Suggest API
   - 1.7 Markers API
   - 1.8 Regions API
2. [Navigation APIs](#2-navigation-apis)
   - 2.1 Routing API (новый единый)
   - 2.2 Directions API (deprecated)
   - 2.3 Public Transport API
   - 2.4 Distance Matrix API
   - 2.5 Distance Matrix Async API
   - 2.6 TSP / VRP API
   - 2.7 Isochrone API
   - 2.8 Map Matching API
   - 2.9 Route Planner API
   - 2.10 Pairs Directions API (deprecated)
   - 2.11 Truck Directions API (deprecated)
   - 2.12 Truck Passes API
3. [Maps APIs](#3-maps-apis)
   - 3.1 Static API

---

## 1. Search APIs

Базовый URL: `https://catalog.api.2gis.com`

Общий формат ответа:
```json
{
  "meta": {"api_version": "...", "code": 200, "issue_date": "..."},
  "result": {"items": [...], "total": N}
}
```

### 1.1 Places API — Поиск организаций, зданий и мест

**Эндпоинт:** `GET /3.0/items`

**Назначение:** Полнотекстовый поиск по каталогу 2ГИС — организации, здания, улицы, остановки, парковки.

**Ключевые параметры:**
- `key` (обязательный) — API-ключ
- `q` (обязательный) — поисковый запрос
- `point` — центр поиска, формат `lon,lat`
- `radius` — радиус поиска в метрах (макс. 50000)
- `region_id` — ID региона 2ГИС для ограничения поиска
- `type` — фильтр типа: `branch`, `building`, `street`, `adm_div`, `station`, `parking`, `gate`, `road`, `attraction`, `crossroad`, `coordinates`
- `fields` — доп. поля: `items.point`, `items.address`, `items.contact_groups`, `items.schedule`, `items.reviews`, `items.links`, `items.rubrics`, `items.flags`, `items.floors`, `items.capacity`, `items.structure_info` и др.
- `page`, `page_size` — пагинация (макс. page_size=50)
- `sort` — сортировка: `relevance` (по умолчанию) или `distance`
- `locale` — язык: `ru_RU`, `en_US`, `ar_AE` и др.

**Пример:**
```
GET https://catalog.api.2gis.com/3.0/items?q=кофейня&point=82.9346,55.0415&radius=1000&fields=items.point,items.contact_groups&key=API_KEY
```

### 1.2 Places ById — Получение объекта по ID

**Эндпоинт:** `GET /3.0/items/byid`

**Назначение:** Получить полную информацию об объекте каталога по его уникальному ID.

**Параметры:**
- `key` (обязательный)
- `id` (обязательный) — ID объекта (из поиска Places / Suggest)
- `fields` — доп. поля (аналогично Places API)

**Пример:**
```
GET https://catalog.api.2gis.com/3.0/items/byid?id=4504127908435201&fields=items.point,items.links&key=API_KEY
```

### 1.3 Places BySite — Поиск по домену сайта

**Эндпоинт:** `GET /3.0/items/bysite` *(платный)*

**Назначение:** Найти филиалы организации по адресу её веб-сайта.

**Параметры:**
- `key`, `url` (домен/сайт), `fields`

### 1.4 Geocoder API — Геокодирование

**Эндпоинт:** `GET /3.0/items/geocode`

**Назначение:** Прямое геокодирование (адрес → координаты) и обратное (координаты → адрес).

**Параметры:**
- `key` (обязательный)
- `q` — адрес для прямого геокодирования
- `lat`, `lon` — координаты для обратного геокодирования
- `fields` — доп. поля: `items.point`, `items.address`, `items.geometry.selection` и др.
- `radius` — радиус поиска (для обратного)
- `type` — тип объекта
- `locale`

**Примеры:**
```bash
# Прямое геокодирование
GET https://catalog.api.2gis.com/3.0/items/geocode?q=Москва, Садовническая, 25&fields=items.point&key=API_KEY

# Обратное геокодирование
GET https://catalog.api.2gis.com/3.0/items/geocode?lat=55.751508&lon=37.615666&fields=items.point&key=API_KEY
```

### 1.5 Geocoder ByIP — Геолокация по IP

**Эндпоинт:** `GET /3.0/items/geocode/byip`

**Назначение:** Определить местоположение по IP-адресу (только cloud).

**Параметры:**
- `key` (обязательный)
- `ip` — IP-адрес (если не указан, определяется автоматически)
- `fields`

### 1.6 Suggest API — Автодополнение

**Эндпоинт:** `GET /3.0/suggest`

**Назначение:** Подсказки при вводе текста в поисковое поле. Оптимизирован для быстрого ввода.

**Параметры:**
- `key` (обязательный)
- `q` (обязательный) — частичный текст запроса
- `point` — `lon,lat` для учёта местоположения
- `region_id` — ID региона
- `locale`
- `suggest_type` — `default` или `route_endpoint` (подсказки для точки маршрута)
- `fields`

**Пример:**
```
GET https://catalog.api.2gis.com/3.0/suggest?q=каф&point=82.9346,55.0415&key=API_KEY
```

**Ответ содержит:**
- `type: "user_query"` — текстовые подсказки
- `type: "branch"`, `"building"`, и др. — объекты из каталога

### 1.7 Markers API — Маркеры для карты

**Эндпоинт:** `GET /3.0/markers`

**Назначение:** Поиск объектов для отображения маркеров на карте. Возвращает только объекты с координатами.

**Параметры:** аналогичны Places API (`q`, `point`, `radius`, `type`, `key`)

### 1.8 Regions API — Регионы 2ГИС

**Эндпоинт:** `GET /3.0/regions`

**Назначение:** Получить список регионов (агломераций) 2ГИС для ограничения поисковых запросов.

**Параметры:**
- `key` (обязательный)
- `q` — фильтр по названию
- `locale`

**Пример:**
```
GET https://catalog.api.2gis.com/3.0/regions?q=Москва&key=API_KEY
```

---

## 2. Navigation APIs

Базовый URL: `https://routing.api.2gis.com`

### 2.1 Routing API (единый, рекомендуемый)

**Эндпоинт:** `POST /routing/7.0.0/global`

**Назначение:** Единый API для построения маршрутов всех типов транспорта. Заменяет Directions API, Truck Directions API, Public Transport API.

**Типы транспорта:** car, pedestrian, bicycle, taxi, scooter, emergency, truck, public_transport

**Тело запроса (для авто/пешеход/велосипед):**
```json
{
  "locale": "ru",
  "points": [
    {"type": "walking", "x": 82.93057, "y": 54.943207},
    {"type": "walking", "x": 82.945039, "y": 55.033879}
  ],
  "type": "jam"
}
```

**Типы маршрута (параметр `type`):**
- `jam` — с текущими пробками
- `statistic` — со статистическими пробками (+ `utc` timestamp)
- `shortest` — кратчайший по расстоянию
- `pedestrian` — пешеходный
- `bicycle` — велосипедный
- `taxi` — для такси (с учётом выделенных полос)
- `emergency` — для экстренных служб
- `truck_jam` / `truck_statistic` — для грузовиков

**Тело запроса (для общественного транспорта):**
```json
{
  "source": {"point": {"lat": 55.798227, "lon": 37.697461}},
  "target": {"point": {"lat": 55.821029, "lon": 37.641507}},
  "transport": ["bus", "trolleybus", "tram", "metro", "suburban_train"]
}
```

**Ответ содержит:** total_distance, total_duration, maneuvers[], geometry (WKT LINESTRING)

**Дополнительные опции:**
- `options: ["pedestrian_instructions"]` — пошаговые инструкции
- `use_indoor: true` — маршрут внутри зданий
- `alternative: N` — кол-во альтернативных маршрутов (до 3)
- `filters` — исключение типов дорог
- `avoid` — полигоны зон объезда

### 2.2 Directions API (deprecated)

**Эндпоинт:** `POST /carrouting/6.0.0/global`

Формат аналогичен Routing API. Рекомендуется мигрировать на Routing API 7.0.

### 2.3 Public Transport API

**Эндпоинт:** `POST /public_transport/2.0`

**Назначение:** Построение маршрутов на общественном транспорте с расписанием.

**Параметры:**
```json
{
  "source": {"point": {"lat": 55.798227, "lon": 37.697461}},
  "target": {"point": {"lat": 55.821029, "lon": 37.641507}},
  "transport": ["bus", "trolleybus", "tram", "metro"],
  "begin_time": "2025-01-15T08:00:00",
  "locale": "ru"
}
```

**Типы транспорта:** `bus`, `trolleybus`, `tram`, `metro`, `light_metro`, `suburban_train`, `funicular`, `monorail`, `water_transport`, `cable_car`

**Ответ:** маршруты с пересадками, остановками, расписанием, временем в пути, пешеходными сегментами.

### 2.4 Distance Matrix API (синхронный)

**Эндпоинт:** `POST /get_dist_matrix?version=2.0`

**Назначение:** Матрица расстояний и времени для пар точек.

**Параметры:**
```json
{
  "points": [
    {"lat": 54.997, "lon": 82.795},
    {"lat": 54.999, "lon": 82.921},
    {"lat": 55.045, "lon": 82.981}
  ],
  "sources": [0],
  "targets": [1, 2],
  "type": "jam"
}
```

**Ограничения:** до 25 точек в sources или targets, расстояние между точками ≤ 2000 км.

**Ответ:** массив `routes[]` с `distance` (метры) и `duration` (секунды) для каждой пары.

### 2.5 Distance Matrix Async API

**Эндпоинты:**
- `POST /async_matrix/create` — создание задачи
- `GET /async_matrix/result/{task_id}` — получение результата

**Назначение:** Для больших матриц (>25 точек). Асинхронный режим.

### 2.6 TSP / VRP API — Задача коммивояжёра

**Эндпоинты:**
- `POST /logistics/vrp/1.1.0/create` — создание задачи
- `GET /logistics/vrp/1.1.0/status/{task_id}` — статус
- `GET /logistics/vrp/1.1.0/result/{task_id}` — результат

**Назначение:** Оптимальный обход до 200 точек до 50 курьерами с учётом временных окон, грузоподъёмности, типов транспорта.

**Параметры:**
```json
{
  "start_time": "2025-05-12T04:05:00Z",
  "agents": [
    {
      "agent_id": 0,
      "start_waypoint_id": 0,
      "work_time_window": {"start": 28800, "end": 64800},
      "capacity": 200
    }
  ],
  "waypoints": [
    {"waypoint_id": 0, "point": {"lat": 55.0, "lon": 82.9}},
    {"waypoint_id": 1, "point": {"lat": 55.1, "lon": 82.8}, "service_time": 600, "delivery_value": 50}
  ],
  "routing_options": {
    "transport": "driving"
  }
}
```

**Типы транспорта для routing_options:** `driving`, `walking`, `bicycle`, `scooter`, `truck`

### 2.7 Isochrone API — Зоны доступности

**Эндпоинт:** `POST /isochrone/2.0.0`

**Назначение:** Построение изохрон — зон, достижимых за указанное время.

**Параметры:**
```json
{
  "start": {"lat": 55.0, "lon": 82.9},
  "durations": [600, 1200, 1800],
  "reverse": false,
  "transport": "walking"
}
```

**Транспорт:** `driving`, `walking`, `bicycle`, `public_transport`, `taxi`

**durations** — массив длительностей в секундах (до 5 значений, макс. 3600 каждое).

**reverse:** `false` = от точки, `true` = к точке.

**Ответ:** геометрия полигонов в WKT для каждого интервала.

### 2.8 Map Matching API — Привязка трека к дорогам

**Эндпоинт:** `POST /map_matching/1.0.0`

**Назначение:** Восстановление автомобильного маршрута из GPS-точек с привязкой к дорожной сети.

**Параметры:**
```json
{
  "query": [
    {"lon": 82.914948, "lat": 55.051097, "utc": 1623878771, "speed": 41, "azimuth": 171},
    {"lon": 82.914914, "lat": 55.051196, "utc": 1623878773, "speed": 42, "azimuth": 171}
  ]
}
```

Каждая точка: `lon`, `lat` (обязательные), `utc` (Unix timestamp), `speed` (км/ч), `azimuth` (градусы).

**Ответ:** distance, duration, edges[] с геометрией, query[] с скорректированными координатами.

### 2.9 Route Planner API — Объезд всех дорог

**Эндпоинт:** `POST /route_planner/1.0`

**Назначение:** Построение маршрута через все дороги внутри полигона (для уборочной техники, инспекции и т.д.)

### 2.10 Pairs Directions API (deprecated)

**Эндпоинт:** `POST /get_pairs/1.0/{routing_type}`

где `routing_type` = `driving`, `pedestrian`, `bicycle`, `taxi`

**Назначение:** Быстрое получение distance/duration между парами точек.

```json
{
  "points": [
    {"lon1": 82.933, "lat1": 55.102, "lon2": 82.958, "lat2": 55.032}
  ],
  "type": "jam",
  "output": "simple"
}
```

### 2.11 Truck Directions API (deprecated)

**Эндпоинт:** `POST /truck/6.0.0/global`

Аналог Directions, но для грузовиков. Рекомендуется использовать Routing API с type `truck_jam`.

### 2.12 Truck Passes API

**Эндпоинт:** `GET /truck_passes/1.0.0/global`

**Назначение:** Получить список зон пропусков для грузовиков. ID пропусков используются в Routing / TSP для грузовых маршрутов.

---

## 3. Maps APIs

### 3.1 Static API — Статичная карта

**Базовый URL:** `https://static-maps-api.2gis.com/1.0`

**Назначение:** Генерация PNG-изображения карты по параметрам в URL.

**Параметры (в URL):**
- `key` (обязательный)
- `center` — центр карты: `lon,lat`
- `zoom` — уровень масштабирования (1-18)
- `size` — размер изображения: `WxH` (макс. 1280x1024)
- `markers` — маркеры на карте
- `path` — линии/полигоны на карте

**Пример:**
```
https://static-maps-api.2gis.com/1.0?center=82.9346,55.0415&zoom=14&size=600x400&key=API_KEY
```

---

## Общие заметки

### Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успех |
| 400 | Ошибка параметров запроса |
| 403 | Невалидный ключ или недостаточные права |
| 404 | Объект не найден |
| 408 | Таймаут |
| 422 | Невозможно построить маршрут |
| 429 | Превышен лимит запросов |
| 500 | Ошибка сервера |

### Формат координат

- **Search APIs:** `point=lon,lat` (долгота, широта через запятую)
- **Navigation APIs (body):** `"x": lon, "y": lat` или `"lon": ..., "lat": ...`
- **Geometry:** WKT формат, например `LINESTRING(lon1 lat1, lon2 lat2)`

### Лимиты demo-ключа

Demo-ключ имеет ограниченное количество запросов и действует 1 месяц. Для продуктивного использования нужна платная подписка через Platform Manager.
