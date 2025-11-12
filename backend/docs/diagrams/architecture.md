# System Architecture Diagram

This diagram shows the overall architecture of the Barton Toolbox Hub system.

## Hub-and-Spoke Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Frontend<br/>Port 5173]
        Mobile[Mobile Apps<br/>Future]
    end

    subgraph "Barton Toolbox Hub<br/>(FastAPI - Port 8000)"
        Main[Main Application<br/>routes & middleware]
        Router[API Router]

        subgraph "Tool Spokes"
            Parser[Parser Tool<br/>/api/parser/*]
            Validator[Validator Tool<br/>/api/validator/*]
            Logger[Logger Tool<br/>/api/logger/*]
            Future[... Future Tools]
        end
    end

    subgraph "Storage Layer"
        Neon[(Neon<br/>PostgreSQL)]
        Firebase[(Firebase<br/>Firestore)]
    end

    subgraph "External Systems"
        N8N[n8n<br/>Workflows]
        External[Other Systems<br/>via API]
    end

    UI -->|HTTP/JSON| Router
    Mobile -.->|Future| Router

    Router --> Parser
    Router --> Validator
    Router --> Logger
    Router -.-> Future

    Parser -->|Primary| Neon
    Parser -.->|Failover| Firebase
    Parser -->|Webhooks| N8N

    Validator --> Parser
    Validator --> Logger

    Logger -->|Primary| Neon
    Logger -.->|Failover| Firebase

    Parser --> External

    style Main fill:#6cf,stroke:#333,stroke-width:3px
    style Parser fill:#f96,stroke:#333,stroke-width:2px
    style Validator fill:#ff6,stroke:#333,stroke-width:2px
    style Logger fill:#9cf,stroke:#333,stroke-width:2px
    style Neon fill:#9f6,stroke:#333,stroke-width:2px
    style Firebase fill:#fc6,stroke:#333,stroke-width:2px
    style N8N fill:#c9f,stroke:#333,stroke-width:2px
```

## Component Details

### Frontend Layer
- **React Frontend:** User interface (Lovable.dev platform)
- **Mobile Apps:** Future mobile support
- **Communication:** HTTP/JSON REST API

### Hub Layer
- **Main Application:** Central coordinator
- **API Router:** Routes requests to appropriate tools
- **Tool Spokes:** Independent, self-contained tools

### Tool Spokes

#### Parser Tool
- **Purpose:** OCR and field extraction
- **Endpoints:** `/api/parser/*`
- **Dependencies:** Neon (primary), Firebase (failover), n8n

#### Validator Tool
- **Purpose:** Field validation
- **Endpoints:** `/api/validator/*`
- **Dependencies:** Parser (for field mappings), Logger

#### Logger Tool
- **Purpose:** Event logging and audit trail
- **Endpoints:** `/api/logger/*`
- **Dependencies:** Neon (primary), Firebase (failover)

### Storage Layer

#### Neon (PostgreSQL)
- **Role:** Primary database
- **Tables:**
  - `doc_parser_fillable` - Parsed documents
  - `doc_event_log` - Event audit trail
- **Features:** ACID compliance, SQL queries, indexes

#### Firebase (Firestore)
- **Role:** Failover storage
- **Collections:**
  - `doc_parser_fillable` - Document mirror
  - `doc_event_log` - Event mirror
- **Features:** Real-time sync, high availability

### External Systems

#### n8n
- **Role:** Workflow automation
- **Integration:** Webhook triggers
- **Use Cases:** Automated workflows, notifications, data sync

#### Other Systems
- **Integration:** REST API
- **Examples:** CRM, ERP, Data warehouses

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Input"
        PDF[PDF Document]
        Text[Text Input]
        API[API Data]
    end

    subgraph "Processing"
        Parse[Parser<br/>Extract Fields]
        Valid[Validator<br/>Check Rules]
        Promo[Promoter<br/>Save Data]
    end

    subgraph "Storage"
        DB[(Database<br/>Neon/Firebase)]
        Log[(Event Log<br/>Neon/Firebase)]
    end

    subgraph "Output"
        N8N[n8n<br/>Workflows]
        Export[Data Export]
        Dash[Dashboards]
    end

    PDF --> Parse
    Text --> Parse
    API --> Parse

    Parse -->|Fields| Valid
    Parse -->|Log Events| Log

    Valid -->|Validated| Promo
    Valid -->|Log Events| Log

    Promo -->|Save| DB
    Promo -->|Trigger| N8N
    Promo -->|Log Events| Log

    DB --> Export
    DB --> Dash
    Log --> Dash

    style Parse fill:#f96,stroke:#333
    style Valid fill:#ff6,stroke:#333
    style Promo fill:#9f6,stroke:#333
    style DB fill:#69f,stroke:#333
    style Log fill:#9cf,stroke:#333
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DevLocal[Local Development<br/>localhost:8000]
    end

    subgraph "Staging"
        StageAPI[Staging API<br/>staging.example.com]
        StageDB[(Staging DB<br/>Neon)]
    end

    subgraph "Production"
        ProdAPI[Production API<br/>api.example.com]
        ProdDB[(Production DB<br/>Neon)]
        ProdFB[(Backup DB<br/>Firebase)]
    end

    DevLocal -->|Deploy| StageAPI
    StageAPI -->|Test & Deploy| ProdAPI

    StageAPI --> StageDB
    ProdAPI --> ProdDB
    ProdAPI -.->|Failover| ProdFB

    style DevLocal fill:#fc6,stroke:#333
    style StageAPI fill:#ff6,stroke:#333
    style ProdAPI fill:#9f6,stroke:#333
```

## Security Architecture

```mermaid
graph TB
    Client[Client Application]

    subgraph "Security Layer"
        Auth[Authentication<br/>Future: JWT/OAuth]
        CORS[CORS<br/>Configured Origins]
        Valid[Input Validation<br/>Pydantic Models]
    end

    subgraph "Application Layer"
        API[FastAPI Application]
        Tools[Tools/Routes]
    end

    subgraph "Data Layer"
        Encrypt[Encryption at Rest]
        SSL[SSL/TLS]
        DB[(Database)]
    end

    Client -->|HTTPS| CORS
    CORS --> Auth
    Auth --> Valid
    Valid --> API
    API --> Tools
    Tools -->|Encrypted| SSL
    SSL --> Encrypt
    Encrypt --> DB

    style Auth fill:#f96,stroke:#333,stroke-width:2px
    style CORS fill:#ff6,stroke:#333
    style Valid fill:#9f6,stroke:#333
    style Encrypt fill:#69f,stroke:#333
```

## Scalability Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Stateless design enables easy scaling
- Database connection pooling

### Vertical Scaling
- Increase CPU/RAM for parsing operations
- Optimize database queries
- Cache frequently accessed data

### Tool Independence
- Each tool can scale independently
- Deploy parser on more powerful instances
- Validator and logger can use smaller instances

## Tool Template Structure

```
/backend/tools/{tool_name}/
├── core/               ← Business logic
│   ├── {module}.py
│   └── __init__.py
├── schemas/            ← Validation schemas (optional)
├── sql/                ← Database schemas (reference)
├── tests/              ← Unit tests
├── routes.py           ← FastAPI endpoints
├── __init__.py
├── .env.example        ← Environment template
├── requirements.txt    ← Dependencies
└── README.md           ← Documentation
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | Neon (PostgreSQL) |
| **Failover DB** | Firebase (Firestore) |
| **Workflows** | n8n |
| **Frontend** | React + TypeScript + Vite |
| **UI Library** | Radix UI + shadcn/ui |
| **Styling** | Tailwind CSS |
| **State** | TanStack Query |
| **Validation** | Pydantic + Zod |
| **Testing** | pytest + jest |
| **Deployment** | Docker (future) |

## Communication Patterns

### Synchronous
- REST API calls between frontend and backend
- Tool-to-tool communication (e.g., Validator → Parser)

### Asynchronous
- Event logging (fire-and-forget)
- Webhook triggers (n8n)
- Background processing (future: Celery/Redis)

### Data Persistence
- Primary: Neon (ACID)
- Failover: Firebase (eventual consistency)
- Caching: In-memory (future: Redis)

---

**Generated with Claude Code**
**Maintainer:** Barton Toolbox Team
