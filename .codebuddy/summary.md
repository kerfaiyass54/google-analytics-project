# Project Summary

## Overview

This repository contains a multi-service Google Play analytics application. It brings together a web interface and backend services for managing Google Play app data, exploring trends, generating downloadable analyses, and producing app predictions.

The system is organized as several independently built components:

1. **Analytics data management** — a Java/Spring service for storing and managing app records and statistics.
2. **Exploratory data analysis (EDA)** — a Python API for analysis queries and exporting results.
3. **Prediction service** — a Python API for training and serving models that predict app-related values.
4. **Prediction event service** — a Python service for consuming prediction events and supporting evaluation/dashboard data.
5. **Web UI** — an Angular application that presents dashboards and operations, and integrates with the backend APIs.

The project’s purpose is inferred from the names and structure of the services and UI features; exact API contracts and runtime behavior require consulting the source and configuration files.

## Languages, frameworks, and main libraries

### Languages and configuration formats

- **Java** — analytics data-management backend.
- **Python** — EDA, prediction, and prediction-event services.
- **TypeScript, HTML, and CSS** — Angular frontend.
- **SQL** — database-related script.
- **YAML, JSON, and `.properties`** — service, build, and application configuration.
- **Dockerfile / Docker Compose YAML** — container build and orchestration definitions.

### Frameworks and libraries indicated by project files

- **Spring Boot / Maven** — Java analytics data-management service. Its `pom.xml` and standard Spring-style package layout indicate a Maven-built Spring application.
- **FastAPI** — Python APIs, supported by the installed environment and API-oriented source layout.
- **Pydantic** — Python request/response schema and settings support.
- **Elasticsearch Python client** — used by the EDA and prediction services’ Elasticsearch modules and repositories.
- **SQLAlchemy and PostgreSQL driver (`psycopg2`)** — database integration in the Python services.
- **Kafka Python client (`kafka-python`)** — event consumption/publishing support, especially relevant to the prediction-events service.
- **scikit-learn, pandas, NumPy, and SciPy** — machine-learning and data-processing stack for predictions.
- **ReportLab / FPDF-related tooling, openpyxl, and CSV utilities** — export formats indicated by the EDA export modules and dependencies.
- **Angular** — frontend framework, with Angular CLI configuration and component-based application structure.
- **Keycloak integration** — authentication and authorization support across backend services and the UI.
- **pytest** — Python test framework; the Java service also contains a Spring application test.
- **Docker Compose** — service-level container orchestration.

The `venv` directories contain installed packages and tools, not project source or dependency declarations. The project-level `requirements.txt` and Maven `pom.xml` are the relevant dependency manifests.

## Purpose and functional areas

### 1. Analytics data management

`/analytics-data-management` is a Java backend centered on Google Play app records. Its source layout separates REST controllers, DTOs, entities, repositories, services, configuration, and security. The service appears to support app management, importing/cleaning data, statistics, and dataset initialization. It includes an SQL script associated with adding a Google Play app email field.

### 2. Exploratory data analysis

`/google-analytics-eda` is a Python service for querying and presenting Google Play analytics. Its analysis modules cover topics such as free-versus-paid apps, install distribution, category ratings, and review counts. The API also has dedicated analysis export functionality, with CSV, Excel, and PDF exporters. Elasticsearch-backed repositories and index definitions provide the data-access layer.

### 3. Prediction service

`/google-analytics-prediction` is a Python machine-learning API. Its structure includes endpoints for predictions, model management, training, and evaluations; service modules for training and prediction workflows; and ML helpers for feature preparation, install buckets, rating validation, and pipeline construction. The presence of install- and rating-prediction models indicates the service predicts app install and rating-related outcomes.

### 4. Prediction events and evaluation

`/google-analytics-prediction-events` is a separate Python service with a Kafka consumer, prediction/evaluation repositories, and a dashboard service. Its role appears to include processing prediction-related events and making evaluation or dashboard information available to other parts of the system.

### 5. Web application

`/google-analytics-ui` is an Angular frontend. It includes dashboards for app categories and statistics, an EDA page, application-list and operations screens, and prediction pages for users and administrators. Shared components include charts, tables, dialogs, navigation, and user details. Authentication flows and route guards are integrated with Keycloak.

## Build, configuration, and project files

The following are the project-level build, dependency, runtime configuration, container, and project/documentation files visible in the supplied file listing. Generated `target` artifacts and environment-installed package files are not treated as source configuration.

### Analytics data management

- `/analytics-data-management/pom.xml` — Maven project and dependency/build configuration.
- `/analytics-data-management/mvnw` — Maven Wrapper launcher for Unix-like systems.
- `/analytics-data-management/mvnw.cmd` — Maven Wrapper launcher for Windows.
- `/analytics-data-management/src/main/resources/application.properties` — Spring application configuration.
- `/analytics-data-management/sql/add_google_play_app_email.sql` — database SQL script.
- `/analytics-data-management/HELP.md` — service help/documentation file.

### EDA service

- `/google-analytics-eda/requirements.txt` — Python dependencies.
- `/google-analytics-eda/api/application.yml` — YAML application configuration.
- `/google-analytics-eda/api/config.py` — Python service configuration module.
- `/google-analytics-eda/tests/test_pdf_export.py` — test for PDF export behavior.
- `/google-analytics-eda/tests/test_rating_sanitization.py` — test for rating sanitization.

### Prediction-events service

- `/google-analytics-prediction-events/Dockerfile` — container image build instructions.
- `/google-analytics-prediction-events/compose.yml` — Compose configuration for the service and its dependencies.
- `/google-analytics-prediction-events/requirements.txt` — Python dependencies.
- `/google-analytics-prediction-events/README.md` — project documentation.

### Prediction service

- `/google-analytics-prediction/Dockerfile` — container image build instructions.
- `/google-analytics-prediction/compose.yml` — Compose configuration.
- `/google-analytics-prediction/requirements.txt` — Python dependencies.
- `/google-analytics-prediction/README.md` — project documentation.
- `/google-analytics-prediction/tests/test_install_buckets.py` — test for install-bucket logic.

### Angular UI

- `/google-analytics-ui/angular.json` — Angular CLI workspace and build configuration.
- `/google-analytics-ui/package.json` — Node.js package manifest, scripts, and frontend dependencies.
- `/google-analytics-ui/src/tsconfig.app.json` — TypeScript configuration for the application.
- `/google-analytics-ui/src/tsconfig.json` — shared TypeScript compiler configuration.
- `/google-analytics-ui/src/tsconfig.spec.json` — TypeScript configuration for tests.
- `/google-analytics-ui/src/index.html` — HTML entry document.
- `/google-analytics-ui/src/main.ts` — application bootstrap entry point.
- `/google-analytics-ui/README.md` — frontend documentation.

### Repository-level orchestration

- `/docker-compose.yml` — root-level Docker Compose file, likely coordinating multiple services.
- `/commands-docker-compose.txt` — recorded Docker Compose commands or usage notes.

## Source code directories

- **Java backend source:**  
  `/analytics-data-management/src/main/java/com/googleanalytics/analyticsforgoogle/`  
  The package is split into `configurations`, `controllers`, `dtos`, `entities`, `enums`, `mapper`, `repositories`, `security`, and `services`.

- **Java backend tests:**  
  `/analytics-data-management/src/test/java/com/googleanalytics/analyticsforgoogle/`

- **EDA Python service:**  
  `/google-analytics-eda/analysis/` — analysis logic.  
  `/google-analytics-eda/api/` — API controllers and configuration.  
  `/google-analytics-eda/database/` — database connection support.  
  `/google-analytics-eda/elastic/` — Elasticsearch client, repositories, and index definitions.  
  `/google-analytics-eda/export/` — export entry point and CSV, Excel, and PDF exporters.  
  `/google-analytics-eda/schema/` — API and document schemas.  
  `/google-analytics-eda/security/` — Keycloak integration.  
  `/google-analytics-eda/services/` — analysis and export service logic.  
  `/google-analytics-eda/tests/` — service tests.

- **Prediction-events Python service:**  
  `/google-analytics-prediction-events/app/` — main application package.  
  Its subdirectories include `config`, `database`, `repositories`, and `services`; `consumer.py` and `main.py` are also under the `app` package.

- **Prediction Python service:**  
  `/google-analytics-prediction/app/` — main application package.  
  Its subdirectories include `api`, `config`, `database`, `elastic`, `ml`, `models`, `schemas`, `security`, and `services`.  
  `/google-analytics-prediction/tests/` — project tests.

- **Angular frontend:**  
  `/google-analytics-ui/src/app/` — application code, including `core`, `features`, and `shared`.  
  `/google-analytics-ui/src/app/core/` — authentication, guards, interceptors, and API services.  
  `/google-analytics-ui/src/app/features/` — dashboard, EDA, operations, app-list, and prediction screens.  
  `/google-analytics-ui/src/app/shared/` — reusable components, directives, models, and utilities.

## Documentation locations

- `/analytics-data-management/HELP.md`
- `/google-analytics-prediction/README.md`
- `/google-analytics-prediction-events/README.md`
- `/google-analytics-ui/README.md`

No top-level repository README is listed. The environment package documentation under the two `venv` directories belongs to third-party dependencies and is not project documentation.