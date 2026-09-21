import json
import runpy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from aiops_pipeline import load_data, run_pipeline
from anomaly_detector import AnomalyDetector
from calculations import area_of_circle, get_nth_fibonacci
from event_producer import EventProducer
from event_topic import EventTopic


def test_calculation_validation_and_iteration_paths():
    with pytest.raises(ValueError, match="Radius cannot be negative"):
        area_of_circle(-1)

    with pytest.raises(ValueError, match="n cannot be negative"):
        get_nth_fibonacci(-1)

    assert get_nth_fibonacci(10) == 55


def test_detector_reports_each_anomaly_reason():
    record = {
        "timestamp": "2026-09-20T10:00:00",
        "service": "billing-service",
        "response_time_ms": 501,
        "cpu_percent": 81,
        "memory_percent": 81,
        "log_level": "WARNING",
    }

    detector = AnomalyDetector()
    event = detector.detect(record)
    error_event = detector.detect({**record, "log_level": "ERROR"})

    assert {"High response time", "High CPU utilization", "High memory utilization"} <= set(event["reasons"])
    assert "Error log detected" in event["reasons"] or "Error log detected" in error_event["reasons"]
    assert event["source"] is record


def test_event_producer_rejects_empty_events_and_topic_can_clear():
    topic = EventTopic("events")
    producer = EventProducer(topic)

    assert producer.publish(None) is False
    producer.publish({"type": "ANOMALY"})
    assert topic.get_messages() == [{"type": "ANOMALY"}]

    topic.clear()
    assert topic.get_messages() == []


def test_pipeline_loads_data_and_processes_records(tmp_path):
    data = [
        {
            "timestamp": "2026-09-20T10:00:00",
            "service": "billing-service",
            "response_time_ms": 700,
            "cpu_percent": 10,
            "memory_percent": 10,
            "log_level": "INFO",
        },
        {
            "timestamp": "2026-09-20T10:01:00",
            "service": "billing-service",
            "response_time_ms": 100,
            "cpu_percent": 10,
            "memory_percent": 10,
            "log_level": "INFO",
        },
    ]
    data_file = tmp_path / "service_data.json"
    data_file.write_text(json.dumps(data), encoding="utf-8")

    assert load_data(data_file) == data
    result = run_pipeline(data_file)

    assert result["records_processed"] == 2
    assert len(result["anomalies_detected"]) == 1
    assert isinstance(result["events_consumed"], list)


def test_pipeline_script_entry_point(monkeypatch, capsys):
    monkeypatch.setattr(
        "event_consumer.EventConsumer.consume",
        lambda self: [{
            "service": "billing-service",
            "timestamp": "2026-09-20T10:00:00",
            "type": "ANOMALY",
            "reasons": ["High response time"],
        }],
    )

    runpy.run_module("aiops_pipeline", run_name="__main__")

    output = capsys.readouterr().out
    assert "Service: billing-service" in output
    assert "Reasons: High response time" in output
