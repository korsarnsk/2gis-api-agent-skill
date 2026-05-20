# 2GIS API Tools — Справочник для Hermes Agent

## Конфигурация

### Настройка ключа

Ключ API хранится в переменной окружения или передаётся параметром:

```bash
# Вариант 1: переменная окружения
export TWOGIS_API_KEY="your_key_here"

# Вариант 2: параметр при вызове
python3 scripts/2gis_call.py --key "your_key_here" --api places --params '{...}'
```

Если ключ не предоставлен, агент должен запросить его у пользователя перед первым вызовом.

---

## Tool Definitions для Hermes Agent

Ниже — описания инструментов в формате, совместимом с tool-calling агентами. Каждый tool вызывает `scripts/2gis_call.py` с соответствующими параметрами.

### search_places
**Описание:** Поиск организаций, зданий и мест в каталоге 2ГИС
**Когда использовать:** Пользователь ищет компании, рестораны, магазины, здания, адреса
**Параметры:**
- `query` (string, обязательный) — текст поиска
- `point` (string) — центр поиска "lon,lat"
- `radius` (int) — радиус в метрах
- `type` (string) — фильтр типа (branch, building, street, station, parking)
- `fields` (string) — доп. поля через запятую
- `page_size` (int) — кол-во результатов (1-50)

**Пример вызова:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api places \
  --params '{"q":"пиццерия","point":"37.6173,55.7558","radius":2000,"fields":"items.point,items.contact_groups,items.schedule","page_size":10}'
```

### get_item_by_id
**Описание:** Получить полную информацию об объекте по его ID
**Когда использовать:** Нужны детали об объекте, найденном ранее через search/suggest
**Параметры:**
- `id` (string, обязательный) — ID объекта из каталога
- `fields` (string) — доп. поля

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api byid \
  --params '{"id":"4504127908435201","fields":"items.point,items.links,items.contact_groups"}'
```

### geocode
**Описание:** Геокодирование — адрес в координаты или координаты в адрес
**Когда использовать:** Нужно узнать координаты адреса или адрес по координатам
**Параметры (прямое):**
- `q` (string) — адрес
**Параметры (обратное):**
- `lat` (float) — широта
- `lon` (float) — долгота
**Общие:**
- `fields` (string) — доп. поля

**Примеры:**
```bash
# Прямое
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api geocode \
  --params '{"q":"Новосибирск, Красный проспект, 1","fields":"items.point,items.address"}'

# Обратное
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api geocode \
  --params '{"lat":55.0302,"lon":82.9204,"fields":"items.point,items.address"}'
```

### suggest
**Описание:** Автодополнение — подсказки по частичному вводу
**Когда использовать:** Интерактивный поиск, нужны быстрые подсказки
**Параметры:**
- `q` (string, обязательный) — частичный текст
- `point` (string) — "lon,lat"
- `region_id` (string) — ID региона
- `suggest_type` (string) — "default" или "route_endpoint"

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api suggest \
  --params '{"q":"сбер","point":"37.6173,55.7558"}'
```

### get_regions
**Описание:** Список регионов 2ГИС
**Когда использовать:** Нужен region_id для ограничения поиска
**Параметры:**
- `q` (string) — фильтр по названию

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api regions \
  --params '{"q":"Москва"}'
```

### build_route
**Описание:** Построение маршрута между точками
**Когда использовать:** Нужен маршрут с расстоянием, временем, геометрией
**Параметры:**
- `points` (array, обязательный) — массив точек `[{"type":"walking","x":lon,"y":lat}, ...]`
- `type` (string) — тип маршрута: jam, statistic, shortest, pedestrian, bicycle, taxi, emergency, truck_jam
- `locale` (string) — язык
- `alternative` (int) — кол-во альтернатив

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api routing \
  --params '{"points":[{"type":"walking","x":37.617,"y":55.755},{"type":"walking","x":37.658,"y":55.764}],"type":"jam","locale":"ru"}'
```

### build_public_transport_route
**Описание:** Маршрут на общественном транспорте
**Когда использовать:** Пользователь хочет добраться на автобусе/метро/трамвае
**Параметры:**
- `source` (object) — `{"point":{"lat":...,"lon":...}}`
- `target` (object) — `{"point":{"lat":...,"lon":...}}`
- `transport` (array) — `["bus","trolleybus","tram","metro"]`

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api public_transport \
  --params '{"source":{"point":{"lat":55.798,"lon":37.697}},"target":{"point":{"lat":55.821,"lon":37.641}},"transport":["bus","metro","tram"]}'
```

### calculate_distance_matrix
**Описание:** Матрица расстояний между точками
**Когда использовать:** Сравнение расстояний от/до нескольких точек, логистика
**Параметры:**
- `points` (array) — все точки `[{"lat":...,"lon":...}, ...]`
- `sources` (array) — индексы начальных точек
- `targets` (array) — индексы конечных точек
- `type` (string) — jam/statistic/shortest

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api dist_matrix \
  --params '{"points":[{"lat":55.0,"lon":82.8},{"lat":55.1,"lon":82.9},{"lat":55.2,"lon":83.0}],"sources":[0],"targets":[1,2],"type":"jam"}'
```

### build_isochrone
**Описание:** Построение зон доступности (изохрон)
**Когда использовать:** Нужно узнать, какая территория доступна за N минут
**Параметры:**
- `start` (object) — `{"lat":...,"lon":...}`
- `durations` (array) — секунды `[600, 1200, 1800]`
- `transport` (string) — driving/walking/bicycle/public_transport
- `reverse` (bool) — false=от точки, true=к точке

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api isochrone \
  --params '{"start":{"lat":55.753,"lon":37.620},"durations":[600,1200],"transport":"walking","reverse":false}'
```

### solve_tsp
**Описание:** Решение задачи коммивояжёра (TSP/VRP)
**Когда использовать:** Оптимальный обход точек курьерами
**Шаги:**
1. Создать задачу (tsp_create)
2. Проверять статус (tsp_status)
3. Получить результат (tsp_result)

**Пример создания:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api tsp_create \
  --params '{
    "start_time":"2025-06-01T08:00:00Z",
    "agents":[{"agent_id":0,"start_waypoint_id":0,"work_time_window":{"start":28800,"end":64800}}],
    "waypoints":[
      {"waypoint_id":0,"point":{"lat":55.753,"lon":37.620}},
      {"waypoint_id":1,"point":{"lat":55.760,"lon":37.630},"service_time":600},
      {"waypoint_id":2,"point":{"lat":55.770,"lon":37.640},"service_time":600}
    ]
  }'
```

### match_gps_track
**Описание:** Привязка GPS-трека к дорогам
**Когда использовать:** Есть последовательность GPS-точек, нужно восстановить маршрут
**Параметры:**
- `query` (array) — точки с `lon`, `lat`, `utc`, `speed`, `azimuth`

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api map_matching \
  --params '{"query":[{"lon":82.914948,"lat":55.051097,"utc":1623878771,"speed":41,"azimuth":171},{"lon":82.914914,"lat":55.051196,"utc":1623878773,"speed":42,"azimuth":171}]}'
```

### get_static_map
**Описание:** Получить статичное изображение карты
**Когда использовать:** Нужна картинка карты для вставки в документ/отчёт
**Параметры:**
- `center` (string) — "lon,lat"
- `zoom` (int) — 1-18
- `size` (string) — "WxH"

**Пример:**
```bash
python3 scripts/2gis_call.py --key "$TWOGIS_API_KEY" --api static_map \
  --params '{"center":"37.620,55.753","zoom":"14","size":"600x400"}' \
  --output map.png
```

---

## Типичные сценарии

### Сценарий 1: Найти ближайшие кафе и построить маршрут
1. `search_places` — найти кафе рядом
2. Выбрать подходящее из результатов
3. `build_route` — построить маршрут до него

### Сценарий 2: Геокодировать адреса и построить матрицу расстояний
1. `geocode` — получить координаты для каждого адреса
2. `calculate_distance_matrix` — посчитать расстояния между ними

### Сценарий 3: Оптимизация доставки
1. `geocode` — геокодировать адреса доставки
2. `solve_tsp` — найти оптимальный маршрут для курьеров
3. `build_route` — построить детальный маршрут по решению TSP

### Сценарий 4: Анализ доступности локации
1. `geocode` — найти координаты точки
2. `build_isochrone` — построить зоны 5/10/15/20 минут
3. `search_places` — найти объекты внутри зон
