#!/usr/bin/env python3
"""
2GIS API Caller — универсальный инструмент для вызова публичных API 2ГИС.

Использование:
    python3 2gis_call.py --key API_KEY --api places --params '{"q":"кофейня","point":"82.9346,55.0415"}'
    python3 2gis_call.py --key API_KEY --api geocode --params '{"q":"Москва, Тверская, 1"}'
    python3 2gis_call.py --key API_KEY --api routing --params '{"points":[...]}'

Список доступных API (--api):
  Search:    places, byid, geocode, geocode_byip, suggest, markers, regions
  Nav:       routing, directions, public_transport, dist_matrix, dist_matrix_async_create,
             dist_matrix_async_result, tsp_create, tsp_status, tsp_result,
             isochrone, map_matching, route_planner, pairs, truck_passes
  Maps:      static_map
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error

# ─── API Definitions ──────────────────────────────────────────────────────────

CATALOG_BASE = "https://catalog.api.2gis.com"
ROUTING_BASE = "https://routing.api.2gis.com"
STATIC_BASE = "https://static-maps-api.2gis.com/1.0"

API_REGISTRY = {
    # ── Search APIs (GET) ──
    "places": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/items",
        "required": ["q"],
        "description": "Поиск организаций, зданий и мест",
    },
    "byid": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/items/byid",
        "required": ["id"],
        "description": "Получить объект по ID",
    },
    "geocode": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/items/geocode",
        "required": [],  # q OR (lat+lon)
        "description": "Прямое/обратное геокодирование",
    },
    "geocode_byip": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/items/geocode/byip",
        "required": [],
        "description": "Геолокация по IP-адресу",
    },
    "suggest": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/suggest",
        "required": ["q"],
        "description": "Автодополнение (подсказки)",
    },
    "markers": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/markers",
        "required": ["q"],
        "description": "Маркеры для карты",
    },
    "regions": {
        "method": "GET",
        "url": f"{CATALOG_BASE}/3.0/regions",
        "required": [],
        "description": "Список регионов 2ГИС",
    },
    # ── Navigation APIs (POST) ──
    "routing": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/routing/7.0.0/global",
        "required": ["points"],
        "description": "Единый роутинг (авто, пешеход, велосипед, такси и др.)",
    },
    "directions": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/carrouting/6.0.0/global",
        "required": ["points"],
        "description": "Построение маршрутов (deprecated, используй routing)",
    },
    "public_transport": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/public_transport/2.0",
        "required": ["source", "target", "transport"],
        "description": "Маршруты общественного транспорта",
    },
    "dist_matrix": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/get_dist_matrix",
        "url_params": {"version": "2.0"},
        "required": ["points", "sources", "targets"],
        "description": "Матрица расстояний (синхронная)",
    },
    "dist_matrix_async_create": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/async_matrix/create",
        "required": ["points", "sources", "targets"],
        "description": "Матрица расстояний — создание асинхронной задачи",
    },
    "dist_matrix_async_result": {
        "method": "GET",
        "url": f"{ROUTING_BASE}/async_matrix/result",
        "required": ["task_id"],
        "description": "Матрица расстояний — результат асинхронной задачи",
    },
    "tsp_create": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/logistics/vrp/1.1.0/create",
        "required": ["waypoints"],
        "description": "TSP/VRP — создание задачи",
    },
    "tsp_status": {
        "method": "GET",
        "url": f"{ROUTING_BASE}/logistics/vrp/1.1.0/status",
        "required": ["task_id"],
        "description": "TSP/VRP — проверка статуса",
    },
    "tsp_result": {
        "method": "GET",
        "url": f"{ROUTING_BASE}/logistics/vrp/1.1.0/result",
        "required": ["task_id"],
        "description": "TSP/VRP — получение результата",
    },
    "isochrone": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/isochrone/2.0.0",
        "required": ["start", "durations"],
        "description": "Построение изохрон (зон доступности)",
    },
    "map_matching": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/map_matching/1.0.0",
        "required": ["query"],
        "description": "Привязка GPS-трека к дорожной сети",
    },
    "route_planner": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/route_planner/1.0",
        "required": [],
        "description": "Маршрут через все дороги внутри полигона",
    },
    "pairs": {
        "method": "POST",
        "url": f"{ROUTING_BASE}/get_pairs/1.0/driving",
        "required": ["points"],
        "description": "Расстояния между парами точек (deprecated)",
    },
    "truck_passes": {
        "method": "GET",
        "url": f"{ROUTING_BASE}/truck_passes/1.0.0/global",
        "required": [],
        "description": "Зоны пропусков для грузовиков",
    },
    # ── Maps APIs ──
    "static_map": {
        "method": "GET",
        "url": STATIC_BASE,
        "required": ["center", "zoom", "size"],
        "description": "Статичное изображение карты",
        "binary": True,
    },
}


def list_apis():
    """Вывести список всех доступных API."""
    print("Доступные API 2ГИС:\n")
    print(f"{'Имя':<30} {'Метод':<6} {'Описание'}")
    print("-" * 80)
    for name, cfg in API_REGISTRY.items():
        print(f"{name:<30} {cfg['method']:<6} {cfg['description']}")


def call_api(api_name: str, api_key: str, params: dict, routing_type: str = None) -> dict | bytes:
    """
    Вызвать 2GIS API.

    Args:
        api_name: имя API из реестра
        api_key: ключ доступа
        params: параметры запроса (dict)
        routing_type: для pairs API — тип маршрута (driving/pedestrian/bicycle/taxi)

    Returns:
        dict с JSON-ответом или bytes для binary-ответов (static_map)
    """
    if api_name not in API_REGISTRY:
        raise ValueError(f"Неизвестный API: {api_name}. Используй --list для списка.")

    cfg = API_REGISTRY[api_name]
    method = cfg["method"]
    url = cfg["url"]
    is_binary = cfg.get("binary", False)

    # Для pairs — подставляем routing_type в URL
    if api_name == "pairs" and routing_type:
        url = f"{ROUTING_BASE}/get_pairs/1.0/{routing_type}"

    # Для task-based GET-эндпоинтов, подставляем task_id в URL
    if api_name in ("tsp_status", "tsp_result", "dist_matrix_async_result"):
        task_id = params.pop("task_id", None)
        if task_id:
            url = f"{url}/{task_id}"

    # Формируем query string
    query_params = {"key": api_key}
    if "url_params" in cfg:
        query_params.update(cfg["url_params"])

    if method == "GET":
        query_params.update(params)
        full_url = f"{url}?{urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)}"
        req = urllib.request.Request(full_url, method="GET")
    else:
        full_url = f"{url}?{urllib.parse.urlencode(query_params)}"
        body = json.dumps(params, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            full_url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if is_binary:
                return raw
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {"error": {"code": e.code, "message": error_body}}
    except urllib.error.URLError as e:
        return {"error": {"message": str(e.reason)}}


def main():
    parser = argparse.ArgumentParser(
        description="2GIS API Caller — вызов публичных API 2ГИС",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--key", help="API-ключ 2ГИС")
    parser.add_argument("--api", help="Имя API (см. --list)")
    parser.add_argument(
        "--params",
        default="{}",
        help='JSON-строка с параметрами, например \'{"q":"кофейня","point":"82.9,55.0"}\'',
    )
    parser.add_argument("--routing-type", default=None, help="Для pairs: driving/pedestrian/bicycle/taxi")
    parser.add_argument("--list", action="store_true", help="Показать все доступные API")
    parser.add_argument("--output", default=None, help="Путь для сохранения binary-ответа (static_map)")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-print JSON")

    args = parser.parse_args()

    if args.list:
        list_apis()
        sys.exit(0)

    if not args.key:
        print("Ошибка: укажи --key API_KEY", file=sys.stderr)
        sys.exit(1)

    if not args.api:
        print("Ошибка: укажи --api <name>. Используй --list для списка.", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга --params: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_api(args.api, args.key, params, args.routing_type)

    if isinstance(result, bytes):
        out_path = args.output or f"{args.api}_output.png"
        with open(out_path, "wb") as f:
            f.write(result)
        print(f"Сохранено: {out_path} ({len(result)} байт)")
    else:
        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
