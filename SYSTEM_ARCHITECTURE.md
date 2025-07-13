# System Architecture Diagrams

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web Interface<br/>HTML5, CSS3, Bootstrap]
        JS[JavaScript<br/>ES6+, AJAX]
    end
    
    subgraph "Backend Layer"
        Flask[Flask Web Server<br/>Python 3.10+]
        Routes[API Routes<br/>Search, Enhance, Trends]
    end
    
    subgraph "Core Services"
        PubMed[PubMed Fetcher<br/>E-utilities API]
        Parser[XML Parser<br/>BeautifulSoup4]
        Filter[Industry Filter<br/>Affiliation Analysis]
        LLM[LLM Service<br/>Groq API Integration]
    end
    
    subgraph "External APIs"
        NCBI[NCBI PubMed<br/>E-utilities]
        Groq[Groq LLM API<br/>Llama3-8B-8192]
    end
    
    subgraph "Data Processing"
        Cache[In-Memory Cache<br/>Search Results]
        Export[CSV Exporter<br/>Pandas DataFrame]
    end
    
    UI --> JS
    JS --> Flask
    Flask --> Routes
    Routes --> PubMed
    Routes --> LLM
    PubMed --> Parser
    Parser --> Filter
    Filter --> Cache
    LLM --> Cache
    Cache --> Export
    PubMed --> NCBI
    LLM --> Groq
    
    style UI fill:#e1f5fe
    style Flask fill:#f3e5f5
    style LLM fill:#fff3e0
    style NCBI fill:#e8f5e8
    style Groq fill:#fff8e1
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Flask
    participant PubMed
    participant LLM
    participant Database
    
    User->>Frontend: Enter search query
    Frontend->>Flask: POST /search
    Flask->>PubMed: Search papers
    PubMed-->>Flask: Return paper IDs
    Flask->>PubMed: Fetch paper details
    PubMed-->>Flask: Return XML data
    Flask->>Flask: Parse & filter papers
    Flask->>LLM: Generate insights (top 10)
    LLM-->>Flask: Return AI analysis
    Flask->>Database: Cache results
    Flask-->>Frontend: Return processed data
    Frontend-->>User: Display results
    
    User->>Frontend: Request trend analysis
    Frontend->>Flask: GET /analyze-trends
    Flask->>LLM: Analyze research trends
    LLM-->>Flask: Return trend insights
    Flask-->>Frontend: Return analysis
    Frontend-->>User: Display trends
```

## Component Interaction Model

```mermaid
graph LR
    subgraph "Input Processing"
        Query[User Query]
        Enhance[AI Enhancement]
        Search[PubMed Search]
    end
    
    subgraph "Data Retrieval"
        Fetch[Fetch Papers]
        Parse[Parse XML]
        Extract[Extract Metadata]
    end
    
    subgraph "Analysis Engine"
        Industry[Industry Detection]
        AI[AI Insights]
        Trends[Trend Analysis]
    end
    
    subgraph "Output Generation"
        Format[Format Results]
        Paginate[Pagination]
        Export[CSV Export]
    end
    
    Query --> Enhance
    Enhance --> Search
    Search --> Fetch
    Fetch --> Parse
    Parse --> Extract
    Extract --> Industry
    Industry --> AI
    AI --> Trends
    Trends --> Format
    Format --> Paginate
    Paginate --> Export
```

## Technology Stack Overview

```mermaid
graph TD
    subgraph "Frontend Technologies"
        HTML[HTML5<br/>Semantic Structure]
        CSS[CSS3 + Bootstrap 5<br/>Responsive Design]
        JS[JavaScript ES6+<br/>Interactive Features]
        FA[Font Awesome<br/>Icons & UI]
    end
    
    subgraph "Backend Technologies"
        Python[Python 3.10+<br/>Core Language]
        Flask[Flask Framework<br/>Web Server]
        Pandas[Pandas<br/>Data Processing]
        Requests[Requests<br/>HTTP Client]
    end
    
    subgraph "AI/ML Stack"
        Groq[Groq API<br/>LLM Inference]
        Llama[Llama3-8B-8192<br/>Language Model]
        NLP[Natural Language Processing<br/>Text Analysis]
    end
    
    subgraph "External Services"
        PubMedAPI[PubMed E-utilities<br/>Research Database]
        NCBI[NCBI Services<br/>Biomedical Data]
    end
    
    HTML --> CSS
    CSS --> JS
    JS --> Flask
    Flask --> Python
    Python --> Pandas
    Python --> Groq
    Groq --> Llama
    Flask --> PubMedAPI
    PubMedAPI --> NCBI
```

## Security and Performance Architecture

```mermaid
graph TB
    subgraph "Security Layer"
        CORS[CORS Protection<br/>Cross-Origin Requests]
        Input[Input Validation<br/>Query Sanitization]
        API[API Key Management<br/>Environment Variables]
    end
    
    subgraph "Performance Layer"
        Cache[In-Memory Caching<br/>Search Results]
        Batch[Batch Processing<br/>API Requests]
        Async[Asynchronous Operations<br/>Background Tasks]
    end
    
    subgraph "Monitoring Layer"
        Logs[Application Logging<br/>Error Tracking]
        Metrics[Performance Metrics<br/>Response Times]
        Health[Health Checks<br/>System Status]
    end
    
    CORS --> Cache
    Input --> Batch
    API --> Async
    Cache --> Logs
    Batch --> Metrics
    Async --> Health
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Local Development<br/>Flask Debug Mode]
        Test[Unit Testing<br/>pytest Framework]
    end
    
    subgraph "Production Environment"
        Web[Web Server<br/>Gunicorn/uWSGI]
        Proxy[Reverse Proxy<br/>Nginx]
        SSL[SSL/TLS<br/>HTTPS Security]
    end
    
    subgraph "Cloud Services"
        Host[Cloud Hosting<br/>AWS/GCP/Azure]
        CDN[Content Delivery<br/>Static Assets]
        Monitor[Monitoring<br/>Application Performance]
    end
    
    Dev --> Test
    Test --> Web
    Web --> Proxy
    Proxy --> SSL
    SSL --> Host
    Host --> CDN
    CDN --> Monitor
```

## Error Handling Flow

```mermaid
graph TD
    Start[User Request] --> Validate[Input Validation]
    Validate -->|Valid| Process[Process Request]
    Validate -->|Invalid| Error1[Return Validation Error]
    
    Process --> API[External API Call]
    API -->|Success| Parse[Parse Response]
    API -->|Failure| Error2[Handle API Error]
    
    Parse -->|Success| AI[AI Processing]
    Parse -->|Failure| Error3[Handle Parse Error]
    
    AI -->|Success| Return[Return Results]
    AI -->|Failure| Error4[Handle AI Error]
    
    Error1 --> Log[Log Error]
    Error2 --> Log
    Error3 --> Log
    Error4 --> Log
    
    Log --> User[Return User-Friendly Error]
    Return --> Success[Success Response]
```

This architecture ensures:
- **Scalability**: Modular design allows independent scaling
- **Reliability**: Comprehensive error handling and fallbacks
- **Performance**: Caching and batch processing optimization
- **Security**: Input validation and secure API management
- **Maintainability**: Clear separation of concerns and documentation
