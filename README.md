# Manufacturing Sensor Big-Data Analytics

**Project title:** Manufacturing Sensor Big-Data Analytics: A Spark Streaming-Based Predictive Pipeline  
**Domain:** Big Data Analytics, Data Warehousing & Visualization

## Abstract

This mini project generates synthetic factory sensor telemetry, cleans and engineers sensor features, trains a Random Forest classifier, and displays estimated risk in a Streamlit maintenance dashboard. A separate Apache Spark Structured Streaming process ingests JSON files in micro-batches, applies validation and feature calculations, invokes the saved scikit-learn model, and stores output as Parquet and SQLite records. The project is designed for learning and local experimentation. Synthetic results are not evidence of real-world predictive accuracy.

**Keywords:** Manufacturing, sensors, Apache Spark, Structured Streaming, predictive maintenance, machine learning, IoT, data warehousing, visualization.

## What It Does

- Generates separate labeled training and unlabeled streaming samples with deterministic seeds.
- Validates required fields, deduplicates event IDs, replaces invalid sensor values with documented fixed operating setpoints, and engineers two deterministic sensor features.
- Trains and saves a stratified train/test Random Forest model; reports precision, recall, F1, confusion matrix, ROC-AUC, and feature importance.
- Stores readings, machine/time dimensions, and predictions in a local SQLite star schema; exports streamed records as Parquet.
- Presents eight dashboard sections, filters, charts, downloads, model evaluation, and separate Spark process status.
- Runs the dashboard and batch prototype without Java/Spark. The genuine streaming runner requires PySpark and Java.

Predicted risk is an estimate from the model, not a confirmed failure. The synthetic failure label is generated from an explicit probability rule based on temperature, vibration, and pressure. It is not an observation from a factory.

## Project Layout

```text
manufacturing-sensor-analytics/
  app.py
  config/settings.py
  data/                    # Created at runtime; ignored by Git
  scripts/                 # Data, model, database, and Spark commands
  src/                     # Generator, cleaning, model, warehouse, streaming
  tests/                   # Pytest checks
  docs/                    # Architecture and methodology
  requirements.txt
```

## Windows and VS Code Setup

Recommended: 64-bit Python 3.11 and a 64-bit Java 17 JDK. PySpark 3.5.3 supports Java 8, 11, and 17; Java 17 is recommended here. Spark requires a compatible Java runtime even though the dashboard-only mode does not. On Windows, Spark's local filesystem also requires Hadoop native files (`hadoop.dll` and `winutils.exe`); this project’s launcher discovers them at `%LOCALAPPDATA%\Programs\Hadoop\3.3.5` if present.

1. Install Python 3.11 and, for Spark, a Java 17 JDK. In VS Code choose **File > Open Folder** and open `manufacturing-sensor-analytics`.
2. Open **Terminal > New Terminal**. Confirm Python:

   ```powershell
   py -3.11 --version
   ```

   If `py` is not recognized, install Python from python.org, enable the Python Launcher/PATH options, restart VS Code, then retry.

3. Create and activate an isolated environment in PowerShell:

   ```powershell
   py -3.11 -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

   Select this environment in VS Code with **Ctrl+Shift+P > Python: Select Interpreter > .venv**.

4. Install dependencies and verify versions:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   java -version
   python -c "import pyspark; print('PySpark', pyspark.__version__)"
   ```

   If you only need the dashboard and batch prototype, the `pyspark` install is still in the shared requirements, but Java is not needed until Spark is started. If Java is installed but Spark reports it cannot find Java, set `JAVA_HOME` to the JDK folder and add `%JAVA_HOME%\bin` to PATH, then reopen VS Code.

5. **Windows Spark file access only:** install the Hadoop 3.3.5 Windows native files in `%LOCALAPPDATA%\Programs\Hadoop\3.3.5\bin`. The versions used here are community-built utilities from [cdarlint/winutils](https://github.com/cdarlint/winutils), not Apache-published Windows binaries. The project launcher discovers this path automatically.

   ```powershell
   $hadoopBin = Join-Path $env:LOCALAPPDATA 'Programs\Hadoop\3.3.5\bin'
   New-Item -ItemType Directory -Force -Path $hadoopBin
   Invoke-WebRequest 'https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.5/bin/hadoop.dll' -OutFile (Join-Path $hadoopBin 'hadoop.dll')
   Invoke-WebRequest 'https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.5/bin/winutils.exe' -OutFile (Join-Path $hadoopBin 'winutils.exe')
   ```

## Run the Prototype

From the project root, in the activated environment:

```powershell
python scripts/generate_data.py
python scripts/initialize_database.py
python scripts/train_model.py
python -m pytest -q
python -m streamlit run app.py
```

The first command creates 2,400 labeled training rows and a separate unlabeled JSON stream sample. `--rows` changes the training/sample size; `--seed` changes IDs and data. The database is initialized independently. Model metrics are measured on a stratified held-out portion of synthetic data only.

In the dashboard, **Create synthetic demo** generates a compact dataset, trains a model, and loads predictions into SQLite. This button is a local demo setup action, not a streaming simulation. The dashboard also opens with a clear empty state before data exists.

## Run Actual Spark Structured Streaming

Spark is a separate process from Streamlit. Start it in a second VS Code terminal, from the project root, after generating data and training the model:

```powershell
python scripts/run_streaming.py --interval "10 seconds"
```

This reads new JSON files from `data/streaming_input`, maintains a recovery checkpoint, writes prediction batches to `data/processed/stream_parquet`, updates SQLite and `data/stream_status.json`, and waits for more files. Keep this terminal open. To inject a fresh independent batch, open a third terminal and use a new seed each time:

```powershell
python scripts/generate_data.py --stream-only --rows 100 --seed 43
```

Then select **Streaming status** in Streamlit. Spark reports `STOPPED` if no active runner is reported; it does not animate or pretend to stream. Stop Spark with **Ctrl+C** in its terminal and Streamlit with **Ctrl+C** in its own terminal.

## Warehouse and Model Notes

SQLite tables are `dim_machine`, `dim_time`, `fact_sensor_readings`, and `fact_failure_predictions`. `src/warehouse.py` exposes reports for daily machine temperature, highest vibration, machine risk, hourly statistics, and historical risk trends. Parquet is the durable streamed analytical output; SQLite supports convenient local dashboard queries.

Features are the five sensor measurements plus temperature × vibration and vibration ÷ pressure. Fixed sensor setpoints are used when values are missing or outside declared bounds; no full-dataset statistics are learned before the train/test split. Risk bands are Low `< 0.35`, Medium `0.35–0.64`, and High `≥ 0.65`. Thresholds are illustrative and require validation against real labeled data before use.

False positives can cause unnecessary inspections. False negatives can delay maintenance. Neither the model nor its feature importances establish causation. Do not use this demo for safety-critical maintenance decisions.

## Troubleshooting

- **`py`/`python` not found:** Install Python 3.11, reopen VS Code, and confirm the selected interpreter.
- **PowerShell blocks activation:** Run the process-scoped `Set-ExecutionPolicy` command above; it does not change the machine-wide policy.
- **`ModuleNotFoundError`:** Activate `.venv` and run `python -m pip install -r requirements.txt` from the project root.
- **`JAVA_GATEWAY_EXITED` or Java not found:** Install a JDK (not only a JRE), set `JAVA_HOME`, confirm `java -version`, then restart VS Code.
- **No predictions:** Generate data and train the model before running the Spark process; inspect the Model evaluation page.
- **Spark says stopped:** Keep `run_streaming.py` open in a second terminal. Check `data/stream_status.json` for an error and ensure a new, uniquely named JSON event file appears after the query starts.
- **Dashboard is empty:** Use **Create synthetic demo** or run the generator, database initializer, and training scripts in order.
- **Port 8501 is busy:** Run `python -m streamlit run app.py --server.port 8502`.

## Manual End-to-End Checklist

- Generate files and verify the training CSV has a `failure_label` while stream JSON files do not.
- Initialize SQLite, train the model, and inspect `data/models/metrics.json` for all requested evaluation metrics and the synthetic-data warning.
- Start Streamlit before and after creating a demo; confirm the empty state, KPI values, filters, charts, CSV download, and risk disclaimer.
- Start Spark with Java available; add a new seed's JSON events and verify Parquet output, SQLite predictions, and a running/stopped status transition.
- Stop Spark with Ctrl+C and confirm the dashboard reports that the process is stopped.
- Run `python -m pytest -q` and record the actual local result in any project submission.

## Documentation

- [Architecture and data flow](docs/architecture.md)
- [Methodology and academic project notes](docs/methodology.md)

## Official References

- Apache Spark Structured Streaming: https://spark.apache.org/docs/3.5.3/structured-streaming-programming-guide.html
- PySpark installation: https://spark.apache.org/docs/3.5.3/api/python/getting_started/install.html
- Streamlit documentation: https://docs.streamlit.io/
- scikit-learn model evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html
- pandas documentation: https://pandas.pydata.org/docs/
- Plotly Python documentation: https://plotly.com/python/