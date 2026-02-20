# THEOS Deployment Guide

Complete guide for deploying THEOS in production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Integration](#integration)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Scaling](#scaling)

---

## Pre-Deployment Checklist

Before deploying THEOS to production, ensure:

### Code Quality

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code formatting: `black --check code/`
- [ ] Import sorting: `isort --check-only code/`
- [ ] Linting: `flake8 code/`
- [ ] Type checking: `mypy code/`
- [ ] No security vulnerabilities: `bandit code/`

### Documentation

- [ ] README is up-to-date
- [ ] API documentation is complete
- [ ] Examples are working
- [ ] Configuration is documented
- [ ] Deployment guide is reviewed

### Testing

- [ ] Unit tests pass (58/58)
- [ ] Integration tests pass
- [ ] Performance benchmarks acceptable
- [ ] Edge cases tested
- [ ] Error handling verified

### Security

- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] Error messages don't leak information
- [ ] Audit logging enabled
- [ ] Access control configured

### Performance

- [ ] Latency acceptable (< 200ms)
- [ ] Memory usage acceptable (< 100KB)
- [ ] Throughput meets requirements
- [ ] Scaling strategy defined
- [ ] Monitoring configured

### Operations

- [ ] Deployment procedure documented
- [ ] Rollback procedure documented
- [ ] Monitoring alerts configured
- [ ] Logging configured
- [ ] Backup strategy defined

---

## Installation Methods

### Method 1: Direct Installation

For simple deployments:

```bash
# Clone repository
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "from code.theos_governor import THEOSGovernor; print('✓ THEOS installed')"
```

### Method 2: Virtual Environment

For isolated environments:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install THEOS
git clone https://github.com/Frederick-Stalnecker/THEOS.git
cd THEOS
pip install -r requirements.txt

# Verify
pytest tests/ -v
```

### Method 3: Docker

For containerized deployments:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy code
COPY code/ code/
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Run tests
RUN pytest tests/ -v

# Default command
CMD ["python3", "-c", "from code.theos_governor import THEOSGovernor; print('THEOS ready')"]
```

Build and run:

```bash
docker build -t theos:1.0 .
docker run theos:1.0
```

### Method 4: PyPI (Future)

When published to PyPI:

```bash
pip install theos
```

---

## Configuration

### Environment Variables

Set these environment variables for production:

```bash
# Logging
export THEOS_LOG_LEVEL=INFO
export THEOS_LOG_FILE=/var/log/theos.log

# Performance
export THEOS_MAX_WORKERS=4
export THEOS_CACHE_SIZE=1000

# Safety
export THEOS_RISK_THRESHOLD=0.35
export THEOS_SIMILARITY_THRESHOLD=0.90

# Monitoring
export THEOS_METRICS_ENABLED=true
export THEOS_METRICS_PORT=8000
```

### Configuration File

Create a configuration file:

```yaml
# config.yaml
theos:
  governor:
    max_cycles: 3
    similarity_threshold: 0.90
    risk_threshold: 0.35
    initial_contradiction_budget: 1.0
  
  performance:
    max_workers: 4
    cache_size: 1000
    timeout_seconds: 5
  
  logging:
    level: INFO
    format: json
    file: /var/log/theos.log
  
  monitoring:
    enabled: true
    metrics_port: 8000
    health_check_interval: 60
```

Load configuration:

```python
import yaml
from code.theos_governor import GovernorConfig, THEOSGovernor

with open('config.yaml') as f:
    config_data = yaml.safe_load(f)

config = GovernorConfig(**config_data['theos']['governor'])
governor = THEOSGovernor(config=config)
```

---

## Integration

### Web API Integration

Integrate THEOS with a web API:

```python
from fastapi import FastAPI
from code.theos_governor import THEOSGovernor, EngineOutput

app = FastAPI()
governor = THEOSGovernor()

@app.post("/evaluate")
async def evaluate_decision(left: dict, right: dict):
    """Evaluate a decision."""
    
    left_output = EngineOutput(**left)
    right_output = EngineOutput(**right)
    
    evaluation = governor.evaluate_cycle(left_output, right_output, 1.0, 1)
    
    return {
        "decision": evaluation.decision,
        "similarity": evaluation.similarity_score,
        "risk": evaluation.risk_score,
        "quality": evaluation.composite_quality
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### Database Integration

Store decisions in a database:

```python
import sqlite3
from datetime import datetime

def store_decision(decision_id: str, evaluation: dict):
    """Store decision in database."""
    
    conn = sqlite3.connect('theos_decisions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO decisions (id, timestamp, similarity, risk, quality, decision)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        decision_id,
        datetime.utcnow(),
        evaluation['similarity'],
        evaluation['risk'],
        evaluation['quality'],
        evaluation['decision']
    ))
    
    conn.commit()
    conn.close()
```

### Message Queue Integration

Process decisions asynchronously:

```python
import json
from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'decisions',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def process_decisions():
    """Process decisions from queue."""
    
    for message in consumer:
        decision = message.value
        
        governor = THEOSGovernor()
        left = EngineOutput(**decision['left'])
        right = EngineOutput(**decision['right'])
        
        evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
        
        producer.send('results', {
            'id': decision['id'],
            'evaluation': evaluation.__dict__
        })
```

---

## Monitoring

### Metrics to Monitor

Track these metrics in production:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Latency (p50) | < 150ms | > 200ms |
| Latency (p95) | < 200ms | > 300ms |
| Memory usage | < 50KB | > 100KB |
| Throughput | > 20 req/s | < 10 req/s |
| Error rate | < 0.1% | > 1% |
| Risk avg | 0.25-0.35 | > 0.40 |
| Convergence rate | > 80% | < 70% |

### Prometheus Integration

Expose metrics for Prometheus:

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
decision_counter = Counter('theos_decisions_total', 'Total decisions')
latency_histogram = Histogram('theos_latency_seconds', 'Decision latency')
memory_gauge = Gauge('theos_memory_bytes', 'Memory usage')
risk_gauge = Gauge('theos_risk_score', 'Risk score')

def evaluate_with_metrics(left, right):
    """Evaluate with metrics."""
    
    import time
    import psutil
    
    start = time.time()
    
    governor = THEOSGovernor()
    evaluation = governor.evaluate_cycle(left, right, 1.0, 1)
    
    latency = time.time() - start
    memory = psutil.Process().memory_info().rss
    
    decision_counter.inc()
    latency_histogram.observe(latency)
    memory_gauge.set(memory)
    risk_gauge.set(evaluation.risk_score)
    
    return evaluation

# Start metrics server
start_http_server(8000)
```

### Logging

Configure structured logging:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    """Format logs as JSON."""
    
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        }
        return json.dumps(log_data)

logger = logging.getLogger('theos')
handler = logging.FileHandler('/var/log/theos.log')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Log decisions
logger.info(f"Decision: {evaluation.decision}, Risk: {evaluation.risk_score:.2f}")
```

---

## Troubleshooting

### Issue: High Latency

**Symptoms:** Decisions taking > 200ms

**Diagnosis:**
1. Check text length (similarity computation scales linearly)
2. Check system load
3. Profile code with cProfile

**Solution:**
1. Reduce output text length
2. Use caching for similarity computations
3. Use parallel processing
4. Adjust configuration (fewer cycles, lower thresholds)

### Issue: High Memory Usage

**Symptoms:** Memory usage > 100KB

**Diagnosis:**
1. Check cycle count
2. Check wisdom record count
3. Check audit trail size

**Solution:**
1. Reduce max_cycles
2. Clear old wisdom records
3. Batch process instead of accumulating

### Issue: Low Convergence Rate

**Symptoms:** Many decisions don't converge

**Diagnosis:**
1. Engines are too different
2. Similarity threshold too high
3. Contradiction budget too low

**Solution:**
1. Improve engine outputs
2. Lower similarity threshold
3. Increase contradiction budget

### Issue: High Risk Scores

**Symptoms:** Many decisions exceed risk threshold

**Diagnosis:**
1. Engines are contradictory
2. Risk threshold too low
3. Engine outputs are poor quality

**Solution:**
1. Improve engine outputs
2. Increase risk threshold
3. Add more context to engines

---

## Scaling

### Horizontal Scaling

Scale across multiple machines:

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def distributed_evaluation(decisions: list, workers: list):
    """Distribute decisions across workers."""
    
    results = []
    
    for i, decision in enumerate(decisions):
        worker = workers[i % len(workers)]
        
        response = requests.post(
            f"http://{worker}/evaluate",
            json=decision
        )
        
        results.append(response.json())
    
    return results
```

### Vertical Scaling

Scale on single machine:

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_evaluation(decisions: list, workers: int = 4):
    """Process decisions in parallel."""
    
    def process_one(decision):
        governor = THEOSGovernor()
        left = EngineOutput(**decision['left'])
        right = EngineOutput(**decision['right'])
        return governor.evaluate_cycle(left, right, 1.0, 1)
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_one, decisions))
    
    return results
```

### Load Balancing

Use load balancer for multiple instances:

```
User Requests
    ↓
Load Balancer (nginx)
    ↓
    ├─ THEOS Instance 1
    ├─ THEOS Instance 2
    ├─ THEOS Instance 3
    └─ THEOS Instance 4
    ↓
Results
```

---

## Rollback Procedure

If deployment fails:

```bash
# Check current version
git log --oneline -1

# Rollback to previous version
git checkout <previous-commit>

# Restart services
systemctl restart theos

# Verify
curl http://localhost:8000/health
```

---

## Production Checklist

Before going live:

- [ ] All tests pass
- [ ] Performance benchmarks acceptable
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] Rollback procedure documented
- [ ] Scaling strategy tested
- [ ] Security review completed
- [ ] Documentation reviewed
- [ ] Team trained on operations

---

## Support

For deployment issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Check logs
3. Run diagnostics
4. Open GitHub issue with details

---

**Status:** Production Ready ✅  
**Last Updated:** February 19, 2026
