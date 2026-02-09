Questionnaire

1. Why should processing be decoupled from upload?

Decoupling upload from processing is a fundamental backend design principle for scalability, reliability, and user experience.

Reasons

1. Responsiveness & UX
   Uploading a file should be fast. Heavy processing (OCR, parsing, ML inference) can take seconds or minutes. If coupled, the client would block or time out.

2. Failure Isolation
   Upload may succeed while processing fails. Decoupling allows retrying processing without re-uploading the file.

3. Scalability
   Upload is I/O-bound, processing is CPU/GPU-bound. They scale differently and should be handled by different worker pools.

4. Asynchronous Execution
   Processing can be triggered via background tasks, message queues, or workers without impacting API availability.

5. Extensibility
   Future pipelines (OCR → NLP → ML → LangGraph) can evolve independently of the upload API.

In this project

* POST /documents → handles **only upload + metadata persistence**
* POST /documents/{id}/process → triggers **processing lifecycle**

This separation mirrors production systems used in document ingestion platforms.



2. How would you make `POST /documents/{id}/process` idempotent?

Idempotency ensures multiple identical requests do not cause duplicate processing.

Problem

Without idempotency:

* Multiple clicks or retries could start processing multiple times
* Results may overwrite each other or corrupt state

Solution (Recommended Approach)

1. Database State Guard**

   * Add a `status` field (`UPLOADED`, `PROCESSING`, `COMPLETED`, `FAILED`)
   * Before processing:

     * If status is `PROCESSING` or `COMPLETED` → return early

2. Atomic State Transition**

   * Use a transaction:

     * Check status
     * Update to `PROCESSING`
     * Commit

3. Optional Idempotency Key**

   * Accept an `Idempotency-Key` header
   * Store key + document_id
   * Reject duplicate keys

Result

* Safe retries
* No duplicate background jobs
* Deterministic behavior

This is critical for distributed systems and retry-heavy clients.


3. How would you scale this to 1,000 concurrent uploads?

Scaling to high concurrency requires addressing API, storage, processing, and infrastructure layers.

API Layer

* Run multiple Uvicorn workers (Gunicorn + Uvicorn workers)
* Place behind a reverse proxy (NGINX / Load Balancer)

Upload Handling

* Stream uploads (avoid loading full file into memory)
* Enforce file size limits
* Use chunked uploads for very large files

Storage Layer

* Replace local filesystem with:
   * AWS S3 / GCS / Azure Blob
   
* Store only object references in DB

Processing Layer

* Move processing to async workers:

  * Celery / RQ / Dramatiq
  * Queue-based execution
  * Horizontal worker scaling

Database

* Use connection pooling
* Migrate from SQLite → PostgreSQL

Result

* Upload throughput scales independently
* Processing scales horizontally
* System remains stable under load

This is a production-grade, cloud-ready architecture.


4. Where would the LangGraph / ML pipeline fit later?

LangGraph / ML pipelines belong in the processing stage, not the API layer.

Placement

POST /documents/{id}/process
        ↓
Processing Orchestrator
        ↓
LangGraph / ML Pipeline
        ↓
Persist Results

Responsibilities

* API: request validation, auth, orchestration trigger
* Service Layer: job coordination, state updates
* ML / LangGraph Layer:

  * OCR
  * Embeddings
  * Classification
  * Graph-based reasoning

Why this works

* ML pipelines are compute-heavy and evolving
* Keeps API stateless and lightweight
* Allows independent experimentation and scaling

Future Extension

* Swap synchronous processor with distributed ML workers
* Add model versioning and A/B testing

Summary

This design:

* Follows separation of concerns
* Is resilient to failures
* Scales horizontally
* Is ML-ready without architectural rewrites

It reflects real-world backend system design rather than toy implementations.


Project Overview

This project is a FastAPI-based backend for a Document Lifecycle Management System, designed to demonstrate clean API design, security, and system thinking rather than OCR or ML implementation.

The system allows authenticated users to:

* Upload documents (PDF/DOCX)

* Track document status through its lifecycle

* Trigger asynchronous document processing (simulated)

* Retrieve processing results once completed

Key design goals:

* Separation of concerns between API, business logic, storage, and processing

* JWT-based authentication with access & refresh tokens

* Structured logging for request and document lifecycle observability

* Production-style project layout suitable for scaling

* CI-ready with linting, tests, and Docker build support

The project intentionally simulates processing logic (no OCR/LLM) to focus on backend architecture, correctness, and extensibility.


Setup Instructions

1. Prerequisites

Make sure you have the following installed:

* Python 3.11+

* Git

* Docker (optional, but recommended)

2️. Clone the Repository
git clone https://github.com/<your-username>/document-api.git
cd document-api

3️. Create Virtual Environment (Local Run)
python -m venv venv
venv\Scripts\activate    Windows
# source venv/bin/activate  # Linux/Mac

4️. Install Dependencies
pip install -r requirements.txt

5️. Run the Application Locally
uvicorn app.main:app --reload


* The API will be available at:

http://127.0.0.1:8000


* Swagger UI:

http://127.0.0.1:8000/docs

6️. Authentication Flow

1. Login

* POST /auth/login


  Returns access + refresh tokens.

2. Use the access token as:

Authorization: Bearer <token>


3. Refresh expired access tokens via:

POST /auth/refresh

7️. Running with Docker (Optional)

* Build the image:

docker build -t document-api .


* Run the container:

docker run -p 8000:8000 document-api

8️. Running Tests
* pytest

9️. CI Pipeline (GitHub Actions)

On every push to main, the CI pipeline automatically:

1. Checks out the code

2. Installs dependencies

3. Runs linting (ruff)

4. Runs tests

5. Builds the Docker image

CI configuration lives in:

.github/workflows/ci.yml