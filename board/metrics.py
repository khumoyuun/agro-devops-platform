from prometheus_client import Counter

agro_requests_total = Counter(
    "agro_requests_total",
    "Total HTTP requests to agro platform"
)


