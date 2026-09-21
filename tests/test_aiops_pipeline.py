import json
import subprocess
import sys

from src.aiops_pipeline import load_data, run_pipeline
from src.anomaly_detector import AnomalyDetector
from src.event_consumer import EventConsumer
from src.event_producer import EventProducer
from src.event_topic import EventTopic


def test_normal_record_is_not_anomaly():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:00:00",
        "service": "payment-service",
        "response_time_ms": 120,
        "cpu_percent": 42,
        "memory_percent": 51,
        "log_level": "INFO",
        "message": "Payment request processed successfully"
    }

    assert detector.detect(record) is None


def test_anomalous_record_is_detected():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:05:00",
        "service": "payment-service",
        "response_time_ms": 610,
        "cpu_percent": 75,
        "memory_percent": 70,
        "log_level": "ERROR",
        "message": "Payment service timeout"
    }

    event = detector.detect(record)

    assert event is not None
    assert event["type"] == "ANOMALY"
    assert "High response time" in event["reasons"]
    assert "Error log detected" in event["reasons"]


def test_warning_log_is_not_an_error():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:05:00",
        "service": "auth-service",
        "response_time_ms": 200,
        "cpu_percent": 50,
        "memory_percent": 55,
        "log_level": "WARNING",
        "message": "Token refresh warning"
    }

    assert detector.detect(record) is None


def test_high_cpu_and_memory_are_flagged():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:20:00",
        "service": "inventory-service",
        "response_time_ms": 210,
        "cpu_percent": 85,
        "memory_percent": 90,
        "log_level": "INFO",
        "message": "High resource usage"
    }

    event = detector.detect(record)

    assert event is not None
    assert "High CPU utilization" in event["reasons"]
    assert "High memory utilization" in event["reasons"]


def test_producer_publishes_event():
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)

    event = {
        "type": "ANOMALY",
        "service": "payment-service"
    }

    assert producer.publish(event)
    assert len(topic.get_messages()) == 1


def test_consumer_receives_event():
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)
    consumer = EventConsumer(topic)

    event = {
        "type": "ANOMALY",
        "service": "payment-service"
    }

    producer.publish(event)

    messages = consumer.consume()

    assert len(messages) == 1