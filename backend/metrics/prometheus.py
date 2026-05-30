from prometheus_client import Counter, Histogram

# Metrics definition
REQUEST_COUNT = Counter(
    "request_count",
    "Total number of requests received",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Time taken for the ONNX model to run inference in seconds",
    ["model_version"]
)

PREDICTION_COUNT = Counter(
    "prediction_count",
    "Total number of predictions made per class",
    ["predicted_class"]
)
