---
name: 2gis-api
description: >
  Skill для работы с публичными API 2ГИС (2GIS). Используй этот skill всякий раз, когда пользователь
  упоминает 2ГИС, 2GIS, DoubleGIS, или хочет работать с геокодированием, поиском организаций/зданий,
  построением маршрутов, матрицами расстояний, изохронами, задачей коммивояжёра (TSP/VRP),
  общественным транспортом, статическими картами, map matching — через API 2ГИС.
  Также используй при упоминании catalog.api.2gis.com, routing.api.2gis.com, static-maps-api.2gis.com,
  или любых эндпоинтов 2GIS API. Skill содержит полный каталог публичных API, готовые tools
  для вызовов, и инструкции по прототипированию. Используй даже если пользователь просто говорит
  "поиск организаций", "построй маршрут", "геокодирование" в контексте 2GIS-данных.
---

# 2GIS API Skill

Этот skill предоставляет полный справочник публичных API 2ГИС и набор инструментов для их вызова.

## Настройка API-ключа

Перед выполнением любых вызовов необходим API-ключ. Спроси пользователя:

> Для работы с 2GIS API нужен ключ доступа. Укажи свой API-ключ (получить можно на https://platform.2gis.com/).

Ключ передаётся как параметр `key` в query string для всех запросов.

## Каталог публичных API

Полный справочник по каждому API — в файле `references/api-catalog.md`. Ниже — краткая карта:

### Search APIs (базовый URL: `https://catalog.api.2gis.com`)

| API | Эндпоинт | Назначение |
|-----|----------|------------|
| **Places API** | `GET /3.0/items` | Поиск организаций, зданий, мест по тексту/координатам |
| **Places ById** | `GET /3.0/items/byid` | Получение объекта по ID |
| **Geocoder API** | `GET /3.0/items/geocode` | Прямое/обратное геокодирование |
| **Geocoder ByIP** | `GET /3.0/items/geocode/byip` | Геолокация по IP |
| **Suggest API** | `GET /3.0/suggest` | Автодополнение (подсказки) |
| **Markers API** | `GET /3.0/markers` | Поиск маркеров для карты |
| **Regions API** | `GET /3.0/regions` | Список регионов 2ГИС |

### Navigation APIs (базовый URL: `https://routing.api.2gis.com`)

| API | Эндпоинт | Назначение |
|-----|----------|------------|
| **Routing API** | `POST /routing/7.0.0/global` | Единый роутинг (авто, пешеход, велосипед, такси, скутер, ОТ) |
| **Directions API** *(deprecated)* | `POST /carrouting/6.0.0/global` | Построение автомаршрутов |
| **Public Transport** | `POST /public_transport/2.0` | Маршруты общественного транспорта |
| **Distance Matrix** | `POST /get_dist_matrix` | Матрица расстояний (синхронный режим) |
| **Distance Matrix Async** | `POST /async_matrix/create` | Матрица расстояний (асинхронный режим) |
| **TSP / VRP** | `POST /logistics/vrp/1.1.0/create` | Задача коммивояжёра |
| **TSP Status** | `GET /logistics/vrp/1.1.0/result` | Проверка статуса TSP-задачи |
| **Isochrone API** | `POST /isochrone/2.0.0` | Зоны доступности (изохроны) |
| **Map Matching** | `POST /map_matching/1.0.0` | Привязка GPS-трека к дорогам |
| **Route Planner** | `POST /route_planner/1.0` | Маршрут через все дороги внутри полигона |
| **Pairs Directions** *(deprecated)* | `POST /get_pairs/1.0/{type}` | Расстояние между парами точек |
| **Truck Passes** | `GET /truck_passes/1.0.0/global` | Зоны пропусков для грузовиков |

### Maps APIs

| API | Базовый URL | Назначение |
|-----|-------------|------------|
| **Static API** | `https://static-maps-api.2gis.com/1.0` | Генерация статичного изображения карты |

## Как использовать

1. **Прочитай `references/api-catalog.md`** — там подробности по каждому API: параметры, формат ответа, примеры curl.
2. **Используй `scripts/2gis_call.py`** — готовый скрипт для вызова любого эндпоинта из терминала.
3. **Для прототипирования** запускай скрипт через bash_tool, подставляя ключ пользователя.

## Быстрый старт: вызов API

```bash
# Поиск организации
python3 /path/to/scripts/2gis_call.py \
  --key "USER_API_KEY" \
  --api places \
  --params '{"q": "кофейня", "point": "82.9346,55.0415", "radius": 1000}'

# Геокодирование
python3 /path/to/scripts/2gis_call.py \
  --key "USER_API_KEY" \
  --api geocode \
  --params '{"q": "Москва, Садовническая, 25"}'

# Построение маршрута
python3 /path/to/scripts/2gis_call.py \
  --key "USER_API_KEY" \
  --api routing \
  --params '{"points": [{"type":"walking","x":82.93057,"y":54.943207},{"type":"walking","x":82.945039,"y":55.033879}]}'
```

## Рекомендации для агента

- Всегда проверяй наличие ключа перед вызовом
- Для навигационных API используй POST-запросы с JSON-телом
- Для поисковых API используй GET-запросы с query-параметрами
- Обрабатывай `meta.code` в ответе: 200 = OK, 403 = невалидный ключ, 400 = ошибка параметров
- Координаты: `lon` (долгота), `lat` (широта) — не перепутай порядок!
- Для Places/Geocoder: параметр `fields` позволяет запросить дополнительные данные
- Для Routing: поле `type` задаёт тип маршрута (jam, statistic, shortest, pedestrian, bicycle и т.д.)
