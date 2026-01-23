# SentinelMap

**Automated Traffic Infrastructure Mapping from Dashcam Footage**

An end-to-end data pipeline that transforms raw dashcam videos into validated traffic sign maps using computer vision, stream processing, and geospatial analytics.

---

## 💡 Motivation

Keeping digital maps up-to-date is a constant challenge. Traditional map updates rely on manual surveys or expensive LiDAR vehicles. **SentinelMap** demonstrates how commodity dashcam footage can automatically validate and update traffic infrastructure data at scale.

**Key Insight**: Millions of dashcams are already recording the roads. By combining object detection (YOLOv8) with GPS telemetry and comparing against OpenStreetMap ground truth, we can identify map discrepancies, new infrastructure, and outdated data — all from video footage that's already being captured.

---

## ✨ Key Features

🎯 **Computer Vision Detection**  
YOLOv8 detects traffic signs (lights, stop signs) from dashcam video with hardware acceleration (Apple M4 MPS)

🌍 **GPS Extraction**  
Extracts binary GPS metadata from video files using exiftool (VIOFO A119 V3 support)

⚡ **Stream Processing**  
High-throughput Kafka producer (Go) streams detections to Confluent Cloud with exactly-once semantics

❄️ **Geospatial Analytics**  
Snowflake spatial queries (ST_DISTANCE) match detections against OpenStreetMap nodes within configurable thresholds

📊 **Data Quality Validation**  
dbt transformation layer with automated tests ensures data integrity and classification accuracy

📈 **Real-time Dashboard**  
Interactive Streamlit visualization shows detection heatmaps, verification trends, and map discrepancies

---

## 🎯 Dashboard Overview

The Streamlit dashboard provides real-time insights into detection quality and map validation:

<p align="center">
  <img src="modules/dashboard/streamlit-screenshot.png" width="49%" alt="Detection Heatmap" />
  <img src="modules/dashboard/streamlit-screenshot-2.png" width="49%" alt="Analytics Charts" />
</p>

### Dashboard Metrics Explained

**Verification Rate**: Percentage of detections matched to OpenStreetMap nodes within 10 meters with correct classification  
- 🟢 **VERIFIED**: Detection matched to OSM node (≤10m, same type)
- 🟠 **NEW_DISCOVERY**: No OSM match found (>10m away) — potential map update candidate
- 🔴 **CLASS_MISMATCH**: Location matched (≤10m) but wrong type (e.g., stop sign vs traffic light) — data quality issue

**Detection Heatmap**: Geographic density visualization showing where traffic signs were detected  

**30-Day Trend**: Historical verification rate to track data quality over time  

**Class Breakdown**: Distribution of traffic lights vs stop signs by verification status

**Run the dashboard locally**:
```bash
cd modules/dashboard
pip install -r requirements.txt
cp .env.example .env  # Add your Snowflake credentials
streamlit run app.py
```

---

## 🏗️ Architecture

SentinelMap uses a modular pipeline architecture inspired by production-grade mapping systems:

```
📹 Dashcam Video (MP4)
    ↓
🤖 Perception Layer (Python + YOLOv8)
   • Object detection with confidence scoring
   • GPS metadata extraction (exiftool)
   • ROI patch generation (256×256)
    ↓
📊 CSV Detections
   • Frame number, timestamp, bounding box
   • Confidence score, class name (traffic light / stop sign)
   • Vehicle GPS coordinates, heading
    ↓
🚀 Ingestion Layer (Go + Kafka)
   • High-throughput streaming (goroutine-based parallelism)
   • Exactly-once semantics (idempotent producer)
   • Real-time metrics (throughput, success rate)
    ↓
☁️ Confluent Cloud Kafka
   • Stream buffer and topic partitioning
   • Auto-scaling and replication
    ↓
❄️ Snowflake Data Warehouse
   • Snowpipe Streaming (real-time ingestion)
   • GEOGRAPHY type for spatial queries
   • ST_DISTANCE for proximity matching
    ↓
📈 Analytics Layer (dbt)
   • Staging: Raw data normalization
   • Core: Spatial joins with OSM ground truth
   • Marts: Aggregated metrics and review queues
    ↓
🗺️ Streamlit Dashboard
   • Detection heatmap (PyDeck)
   • Verification metrics and trends
   • Class distribution analytics
```

---

## 📂 Project Structure

```
sentinel-map/
├── modules/
│   ├── perception/              # YOLOv8 detection pipeline (Python)
│   ├── ingestion/               # Kafka producer (Go)
│   └── dashboard/               # Real-time visualization (Streamlit)
├── analytics/                   # dbt transformation layer
├── data/                        # Video input and CSV output
└── docs/                        # Architecture documentation
```

**[📖 Full documentation for each module](#-documentation)**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (perception layer)
- Go 1.20+ (ingestion layer)
- Snowflake account (analytics/dashboard)
- Confluent Cloud account (optional, for Kafka streaming)

### Running the Pipeline

**1. Process Video** (Perception Layer)
```bash
cd modules/perception
pip install -r requirements.txt

python detect_and_extract.py \
  --video ../../data/videos/sample.MP4 \
  --output-csv ../../data/detections/detections.csv \
  --device mps  # or 'cuda' for NVIDIA GPUs
```

**2. Stream to Kafka** (Ingestion Layer)
```bash
cd modules/ingestion
cp .env.example .env  # Add your Kafka credentials
make build

./bin/producer \
  -csv ../../data/detections/detections.csv \
  -vehicle vehicle-001
```

**3. Run Analytics** (dbt + Snowflake)
```bash
cd analytics
cp .env.example .env  # Add Snowflake credentials
dbt run  # Transforms raw data → fact tables → marts
```

**4. Launch Dashboard** (Streamlit)
```bash
cd modules/dashboard
cp .env.example .env  # Add Snowflake credentials
streamlit run app.py  # Opens at http://localhost:8501
```

---

## 📚 Documentation

- **[Perception Layer](modules/perception/README.md)** - YOLOv8 detection and GPS extraction
- **[Ingestion Layer](modules/ingestion/README.md)** - Kafka streaming producer
- **[Analytics Layer](analytics/README.md)** - dbt transformation models
- **[Dashboard](modules/dashboard/README.md)** - Streamlit visualization setup

---

## 🧪 Experimental Results

This is a proof-of-concept showcasing the technical pipeline. Results demonstrate feasibility but are not production-scale:

**Pipeline Validation**:
- ✅ End-to-end data flow operational (video → detection → Kafka → Snowflake → dashboard)
- ✅ High verification rate achieved against OpenStreetMap ground truth
- ✅ Real-time streaming and visualization functional
- ✅ Geospatial queries performing efficiently with ST_DISTANCE

**Technical Performance**:
- YOLOv8 inference: ~100 FPS on Apple M4 MPS
- Kafka throughput: Tested up to 650k messages/sec send rate
- Snowflake spatial joins: Processing time scales linearly with dataset size
- dbt transformation: 5 models, 16 data quality tests (100% pass rate)

**Known Limitations**:
- GPS extraction limited to VIOFO A119 V3 camera format
- OSM ground truth coverage limited to Toronto metropolitan area
- Requires manual threshold tuning for different geographic regions
- Dashboard refresh rate limited by Snowflake query performance

---

## 🛣️ Technology Stack

**Computer Vision**: Python, YOLOv8 (Ultralytics), OpenCV, PyTorch  
**Stream Processing**: Go, Kafka, Confluent Cloud  
**Data Warehouse**: Snowflake, Snowpipe Streaming, GEOGRAPHY type  
**Transformation**: dbt Core, SQL  
**Visualization**: Streamlit, PyDeck, Plotly  
**Hardware**: Apple M4 MacBook Pro (MPS acceleration)

---

## 🛣️ Future Enhancements

- [ ] Multi-camera support (GoPro, Garmin, generic NMEA GPS)
- [ ] Automated OSM changeset generation
- [ ] H3/S2 spatial indexing for faster queries
- [ ] Real-time anomaly detection (missing/moved signs)
- [ ] Mobile app integration for crowdsourced validation

---

## 🤝 Contributing

This is a portfolio project demonstrating production-grade data engineering. Contributions and feedback welcome!

---

## 📄 License

MIT License

---

## 📬 Contact

**Boyang Li**  
bryanli2009@live.ca | [LinkedIn](https://www.linkedin.com/in/boyang419/)

---

*Inspired by Lyft's Level 5 mapping platform and built with modern data engineering best practices.*
