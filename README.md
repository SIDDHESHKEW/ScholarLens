# ScholarMatch

> **ScholarMatch: Scholarship Finder and Eligibility Predictor**

ScholarMatch is a deterministic scholarship discovery system that evaluates student profiles against verified eligibility rules and free-text evidence, compares multi-dimensional academic preferences, calculates explainable 100-point compatibility scores, and delivers ranked scholarship recommendations.

ScholarMatch enforces a strict engineering principle: **eligibility evaluation always precedes recommendation ranking**. Disqualified opportunities are filtered out rather than promoted with misleading approval guarantees.

---

## Table of Contents

- [Product Overview](#product-overview)
- [Core Architecture & Pipeline](#core-architecture--pipeline)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Deterministic Eligibility Semantics](#deterministic-eligibility-semantics)
- [Soft Preference Matching](#soft-preference-matching)
- [Explainable 100-Point Scoring Policy](#explainable-100-point-scoring-policy)
- [Verification & Provenance](#verification--provenance)
- [Data Sources & Reproducibility](#data-sources--reproducibility)
- [Quick Start for Fresh Clone](#quick-start-for-fresh-clone)
- [Application URLs](#application-urls)
- [API Reference](#api-reference)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Trust, Integrity & Safety](#trust-integrity--safety)
- [Contributing](#contributing)
- [Project Status](#project-status)

---

## Product Overview

Finding compatible scholarships is traditionally difficult and opaque:
- Students spend hours manually searching scattered portals and deciphering complex qualification criteria.
- Generic platforms often score opportunities using black-box algorithms or make unsupportable approval guarantees.
- Opportunities that violate hard education levels, nationality restrictions, or academic prerequisites frequently slip through as false recommendations.

**ScholarMatch solves this through mathematical precision and deterministic evaluation:**
1. **Canonical Student Profiles**: Normalizes student background into structured attributes without guessing ambiguous inputs.
2. **Hard Eligibility Gate**: Evaluates strict mandatory rules (age, nationality, GPA, income) before any matching occurs.
3. **Contradiction Evidence Detection**: Scans free-text criteria to catch unindexed postgraduate or doctoral restrictions (`UNKNOWN ≠ PASS`).
4. **Discipline Quality Gate**: Prevents irrelevant academic disciplines from floating to the top.
5. **Explainable Scoring**: Provides transparent point contributions across 7 dimensions (summing to 100).
6. **Data Provenance & Freshness**: Surfaces verification status, source URLs, and warnings so users know exactly where each record originates.

---

## Core Architecture & Pipeline

```text
SCHOLARSHIP DATA PIPELINE
Sources (Tracked CSV: data/clean_scholarships.csv)
   ↓
Cleaning (HTML, Whitespace, Sentinels)
   ↓
Deduplication (Fingerprint Hashing)
   ↓
Normalization (Country, Level, Currency, Dates)
   ↓
Evidence Extraction (Target Level, Contradictions)
   ↓
Verification & Freshness Auditing
   ↓
Scholarship Database (Local SQLite generated via scripts/init_database.py)

RECOMMENDATION PIPELINE
Raw Student Form Input
   ↓
Profile Normalization Service
   ↓
Hard Eligibility Engine (Hard Rules + Contradiction Signals)
   ↓ [Disqualified -> NOT_ELIGIBLE (Excluded)]
Recommendation Quality Gate (Taxonomy: BROAD vs SPECIFIC)
   ↓ [Discipline Mismatches -> Blocked]
Soft Matching Engine (7 Preference Dimensions)
   ↓
Explainable Scoring Policy (Weighted Sum out of 100)
   ↓
Relevance Tier Ranking (Strong Match > Partial > Broad > Score Descending)
   ↓
Top-K Recommendation Response & UI Dashboard
```

---

## Key Features

- **Eligibility-First Pipeline**: Disqualified scholarships are blocked before scoring; incompatible opportunities never reach the recommendation list.
- **Evidence-Based Contradiction Handling**: Discovers hidden degree level restrictions from free-text descriptions (e.g. flagging undergraduate candidates applying for PhD grants).
- **Recommendation Quality Gate**: Categorizes fields into `BROAD`, `SPECIFIC`, and `UNKNOWN` taxonomies to prevent irrelevant opportunities from outranking direct major matches.
- **Explainable 100-Point Scoring**: Weighted dimension scoring with explicit `MATCH` (1.0), `PARTIAL_MATCH` (0.5), `MISMATCH` (0.0), and `UNKNOWN` (excluded from denominator) contributions.
- **Transparent Provenance & Data Notes**: Flags unverified records, stale listings, and source URLs directly on result cards.
- **Modern Responsive Frontend**: Built with React 19, TypeScript, and Tailwind CSS v4, featuring dark mode persistence and accessible layouts.
- **Random Profile Generator**: In-memory test generator for rapid end-to-end evaluation with direct review flow.
- **Deterministic API**: RESTful FastAPI backend with strict Pydantic v2 schemas and OpenAPI/Swagger documentation.

---

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (Asynchronous REST API)
- **Data Validation & Settings**: Pydantic v2 & Pydantic Settings
- **ORM & Database**: SQLAlchemy 2.x with SQLite
- **HTTP Client**: HTTPX (Timeout-safe verifier fetcher)

### Frontend
- **Framework**: React 19 (SPA Architecture)
- **Language**: TypeScript
- **Tooling & Bundler**: Vite 8
- **Styling**: Tailwind CSS v4 (Glassmorphism, CSS variables, Dark mode)
- **Icons**: Lucide React

### Testing & QA
- **Backend Testing**: pytest (Unit & integration test suites)
- **Frontend Testing**: Vitest & React Testing Library
- **Static Analysis**: `compileall`, TypeScript (`tsc -b`), and Oxlint

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    React 19 Frontend UI                     │
│  Landing Page  •  5-Step Profile Form  •  Results Dashboard │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI REST API Layer                  │
│       /recommendations  •  /eligibility  •  /matching       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Application & Intelligence Layer               │
│  ├── Student Profile Normalization (Alias & Type Normalizer)│
│  ├── Hard Eligibility Engine (Operators & Range Checks)     │
│  ├── Eligibility Evidence Detector (High-Confidence Scans)  │
│  ├── Recommendation Quality Gate (Discipline Taxonomy)      │
│  ├── Soft Matching Engine (7 Multi-Dimensional Comparators) │
│  └── Explainable Scoring Policy (100pt Weighted Breakdown)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data & Persistence Layer                  │
│   SQLAlchemy 2.x Repository  •  Local SQLite Database       │
│   Provenance History  •  Evidence Claims  •  Raw Payloads   │
└─────────────────────────────────────────────────────────────┘
```

---

## Deterministic Eligibility Semantics

ScholarMatch classifies scholarship eligibility into three mutually exclusive states:

| Outcome | Meaning | Recommendation Behavior |
| --- | --- | --- |
| **`ELIGIBLE`** | All hard requirements and high-confidence evidence conditions evaluated to `PASS`. | Included in recommendations. |
| **`POSSIBLY_ELIGIBLE`** | No criteria failed, but one or more requirements could not be confirmed due to missing or unverified source data. | Included **only** when `include_possibly_eligible=true` is requested. Unresolved fields are highlighted. |
| **`NOT_ELIGIBLE`** | At least one mandatory hard rule or high-confidence contradiction evaluated to `FAIL`. | **Strictly excluded** from recommendations. |

> **Core Principle: `UNKNOWN ≠ PASS`**  
> Missing structured fields are never treated as an automatic pass when strong contradictory evidence exists in scholarship descriptions or eligibility text.

---

## Soft Preference Matching

Following hard eligibility, student preferences are compared against scholarship criteria across 7 distinct dimensions:

1. **Field of Study**: Direct major matching, taxonomy-based subfield alignment, or broad/unrestricted acceptance.
2. **Preferred Study Country**: Geographic destination compatibility.
3. **Education Level**: Target degree qualification alignment.
4. **Study Mode**: On-campus, online/remote, hybrid, or full-time/part-time matching.
5. **Funding Preference**: Full tuition, partial scholarship, stipend, or grant alignment.
6. **Institution Type**: Public, private, or specialized institutional preference.
7. **Language Preference**: Curricular language requirements.

Each dimension produces one of four standard match statuses: `MATCH`, `PARTIAL_MATCH`, `MISMATCH`, or `UNKNOWN`.

---

## Explainable 100-Point Scoring Policy

ScholarMatch uses a centralized, deterministic scoring policy where weights sum to **100**:

| Dimension | Weight | Contribution Calculation |
| :--- | :---: | :--- |
| **Field of Study** | **30** | `MATCH = 1.0` (30.0 pts) \| `PARTIAL_MATCH = 0.5` (15.0 pts) \| `MISMATCH = 0.0` (0 pts) |
| **Study Country** | **20** | `MATCH = 1.0` (20.0 pts) \| `PARTIAL_MATCH = 0.5` (10.0 pts) \| `MISMATCH = 0.0` (0 pts) |
| **Education Level** | **15** | `MATCH = 1.0` (15.0 pts) \| `PARTIAL_MATCH = 0.5` (7.5 pts) \| `MISMATCH = 0.0` (0 pts) |
| **Funding Preference**| **15** | `MATCH = 1.0` (15.0 pts) \| `PARTIAL_MATCH = 0.5` (7.5 pts) \| `MISMATCH = 0.0` (0 pts) |
| **Study Mode** | **10** | `MATCH = 1.0` (10.0 pts) \| `PARTIAL_MATCH = 0.5` (5.0 pts) \| `MISMATCH = 0.0` (0 pts) |
| **Institution Type** | **5** | `MATCH = 1.0` (5.0 pts) \| `PARTIAL_MATCH = 0.5` (2.5 pts) \| `MISMATCH = 0.0` (0 pts) |
| **Language** | **5** | `MATCH = 1.0` (5.0 pts) \| `PARTIAL_MATCH = 0.5` (2.5 pts) \| `MISMATCH = 0.0` (0 pts) |

### Dynamic Denominator Handling
$$\text{Score} = \text{round}\left( \frac{\sum (\text{weight} \times \text{status\_contribution})}{\sum (\text{weights of known dimensions})} \times 100, 2 \right)$$

- `UNKNOWN` dimensions are excluded from the denominator so students are not penalized for unrecorded criteria.
- If all evaluated dimensions are `UNKNOWN`, the score evaluates to `null` and is displayed as *"Score unavailable"*.
- **The compatibility score measures preference alignment; it is not an approval probability or guarantee of financial award.**

---

## Verification & Provenance

Every scholarship record maintains provenance and verification metadata:
- **Verification Statuses**: `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`, `NEEDS_REVIEW`, `SOURCE_UNAVAILABLE`, `STALE`, and `CONTRADICTED`.
- **Freshness Policy**: Categorized as `FRESH`, `STALE`, or `UNKNOWN` based on last verification timestamp.
- **Truthful URLs**: Official application links are surfaced only when genuine URLs exist in the database record. If missing, an official source record or transparent notice (*"Official application link not provided"*) is displayed.

---

## Data Sources & Reproducibility

### Database Reproducibility
> **Important Database Architecture Notice:**  
> The SQLite database is generated locally and is intentionally not committed to Git.  
> The repository tracks canonical source data in `data/clean_scholarships.csv` and provides an automated initialization script (`scripts/init_database.py`) to build the database from scratch on any fresh clone.

### Data Sources
- **Canonical Tracked Dataset**: `data/clean_scholarships.csv` containing 800+ audited scholarship opportunities.
- **Database Initialization**: `python scripts/init_database.py` creates SQLite tables and ingests all records through the cleaning and normalization pipeline.
- **No Synthetic Runtime Records**: The system operates entirely on real scholarship records.

### Honest Data Limitations
- **Legacy Records**: Some historical listings contain unindexed free-text requirements that require manual applicant verification.
- **Deadline Variations**: Application windows and award amounts are subject to change by awarding institutions.
- **External Portals**: ScholarMatch encourages every student to confirm final requirements directly on the official scholarship provider portal.

---

## Quick Start for Fresh Clone

### Prerequisites
- **Python**: Version 3.11 or higher
- **Node.js**: Version 18 or higher (with `npm`)
- **Git**

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd ScholarMatch
```

### Step 2: Backend Setup & Database Initialization
```bash
# 1. Create virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the local database from the tracked dataset
python scripts/init_database.py

# 4. Start the backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 3: Frontend Setup & Launch
```bash
# In a new terminal window:
cd frontend

# 1. Install frontend dependencies
npm install

# 2. Start Vite development server
npm run dev
```

Open your browser and navigate to `http://localhost:5173`.

---

## Application URLs

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend UI** | `http://localhost:5173` | React Single Page Application |
| **Backend API** | `http://127.0.0.1:8000` | FastAPI application server |
| **Interactive API Docs** | `http://127.0.0.1:8000/docs` | Swagger UI for interactive API exploration |
| **ReDoc Documentation** | `http://127.0.0.1:8000/redoc` | Clean OpenAPI specification documentation |
| **OpenAPI Schema** | `http://127.0.0.1:8000/openapi.json`| Raw JSON OpenAPI contract |

---

## API Reference

### Major Endpoints

#### 1. Generate Recommendations
`POST /api/v1/recommendations`

```json
{
  "student_profile": {
    "age": 21,
    "nationality": "India",
    "residence_country": "India",
    "education_level": "bachelors",
    "field_of_study": "Computer Science",
    "preferred_study_country": "USA",
    "study_mode": "on_campus",
    "funding_preference": "full_scholarship",
    "gpa": 3.8
  },
  "limit": 5,
  "include_possibly_eligible": true
}
```

#### 2. Student Profile Normalization
`POST /api/v1/students/normalize`  
Validates user form strings against standard taxonomies and returns canonical profile objects.

#### 3. Deterministic Eligibility Evaluation
`POST /api/v1/eligibility/evaluate`  
Evaluates student attributes against structured hard rule sets with explainable pass/fail outcomes.

#### 4. Preference Matching
`POST /api/v1/matching/evaluate`  
Compares student preferences with scholarship parameters across all 7 soft dimensions.

#### 5. Health & Diagnostic Check
`GET /api/v1/health`  
Returns operational health status and database connectivity status (`service: "scholarmatch-api"`).

---

## Testing & Quality Assurance

ScholarMatch maintains a comprehensive test suite across backend services and frontend components.

```bash
# 1. Run all backend tests
python -m pytest -q

# 2. Validate backend compilation
python -m compileall app scripts tests

# 3. Run frontend unit and integration tests
cd frontend
npm test

# 4. Validate frontend TypeScript & Vite production build
npm run build
```

**Verified Test Baseline:**
- **Backend Tests**: 100 passed (`100/100` unit and integration tests passing)
- **Frontend Tests**: 41 passed (`41/41` Vitest component and flow tests passing)
- **Python Compilation**: All modules compile with 0 syntax errors
- **TypeScript & Vite Build**: 0 errors (clean production build)

---

## Project Structure

```text
ScholarMatch/
├── app/                              # FastAPI Backend Application
│   ├── api/                          # REST API routes and versioned endpoints
│   ├── core/                         # Configuration, settings, and logging
│   ├── db/                           # SQLAlchemy base, models, and session
│   ├── eligibility/                  # Hard eligibility rule engine
│   ├── intelligence/                 # Evidence detector and taxonomy classifiers
│   ├── matching/                     # Multi-dimensional soft matching engine
│   ├── pipeline/                     # Cleaning, deduplication, and normalization
│   ├── recommendations/              # Quality gate and recommendation service
│   ├── repositories/                 # Database persistence and queries
│   ├── schemas/                      # Pydantic data contracts
│   ├── scoring/                      # Explainable 100pt scoring policy
│   ├── student/                      # Profile normalization and alias mappers
│   ├── verification/                 # Scholarship freshness and claim verifier
│   └── main.py                       # FastAPI application entrypoint
│
├── frontend/                         # React 19 + Tailwind CSS Frontend
│   ├── public/                       # Favicon and static assets
│   │   ├── favicon.svg               # Custom ScholarMatch brand favicon
│   │   └── icons.svg
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/               # Navbar, Footer, Modal, Badge, Loader
│   │   │   ├── landing/              # Hero, HowItWorks, WhyScholarMatch, Trust
│   │   │   ├── profile/              # Multi-step form & Review components
│   │   │   └── results/              # Dashboard metrics, Cards, Details modal
│   │   ├── hooks/                    # Theme state management hook
│   │   ├── pages/                    # LandingPage, PredictPage, ResultsPage
│   │   ├── services/                 # API client, Adapter, and Random generator
│   │   ├── types/                    # TypeScript interfaces and form state
│   │   └── test/                     # Vitest component and integration tests
│   ├── index.html                    # HTML entrypoint with brand title & favicon
│   ├── package.json
│   └── vite.config.ts
│
├── data/                             # Tracked datasets and local database
│   ├── clean_scholarships.csv        # Canonical historical scholarship dataset
│   └── .gitkeep                      # (Local *.db SQLite files are git-ignored)
│
├── docs/                             # Architecture and data mapping documentation
│   └── csv_column_mapping.md
│
├── scripts/                          # Initialization, ingestion, and verification scripts
│   ├── init_database.py              # Official database creation and dataset ingestion
│   ├── audit_database.py             # Database statistics and quality audit
│   ├── benchmark_performance.py      # Recommendation engine latency benchmark
│   ├── evaluate_profiles.py          # Batch student profile evaluator
│   ├── ingest_scholarships_csv.py    # Standalone CSV ingestion adapter
│   ├── inspect_scholarships_csv.py   # Dataset schema inspector
│   └── verify_scholarships.py        # Live source URL verification runner
│
├── tests/                            # Pytest test suite
│   ├── fixtures/                     # Test fixtures
│   ├── integration/                  # API integration tests
│   └── unit/                         # Engine unit tests
│
├── .env.example                      # Template environment variables
├── .gitignore                        # Git exclusion rules (.db, node_modules, dist)
├── pyproject.toml                    # Python project configuration
├── requirements.txt                  # Python runtime dependencies
└── README.md                         # Complete project documentation
```

---

## Development Workflow

1. **Start Services**: Launch FastAPI backend on port 8000 and Vite frontend on port 5173.
2. **Access Discovery**: Navigate to `http://localhost:5173` in any browser.
3. **Fill Profile**: Click *"Predict Your Scholarship"* and enter your academic background, or click *"Fill Random Profile"* to immediately populate a test profile and jump to review.
4. **Review Parameters**: Inspect profile attributes and adjust result limit (default: 5).
5. **Run Evaluation**: Click *"Predict My Scholarships"* to trigger the recommendation pipeline.
6. **Inspect Results**: Explore ranked recommendations, view factor match compatibility, inspect data verification notes, or click *"Visit Official Application Portal"* to view external opportunities.

---

## Trust, Integrity & Safety

ScholarMatch is intentionally designed to uphold academic and technical integrity:
- **No Hallucinated Data**: Opportunities are matched strictly against verified database records; scholarship records and URLs are never fabricated.
- **Preserved Uncertainty**: When scholarship data is missing, it is reported as `UNKNOWN` rather than guessed.
- **Separation of Concerns**: Verification status is kept distinct from match score; unverified listings are never given artificial score boosts.
- **Safe External Links**: Links to official application portals are only rendered when valid URLs exist in source data.

---

## Contributing

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-improvement
   ```
2. Implement your changes adhering to code style and architecture guidelines.
3. Run backend and frontend test suites to ensure zero regressions:
   ```bash
   python -m pytest -q
   cd frontend && npm test && npm run build
   ```
4. Commit your changes and submit a Pull Request with a clear description.

---

## Project Status

**Status**: Ready for GitHub / Ready for Phase 12 Deployment.  
**License**: MIT / Educational & Non-Commercial Use.
