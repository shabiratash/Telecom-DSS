# Thesis Diagrams

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Date:** June 22, 2026
**Purpose:** System architecture and design diagrams for thesis documentation

---

## 1. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    PROVINCES ||--o{ CUSTOMERS : "contains"
    CUSTOMERS ||--o{ CUSTOMER_RISK_HISTORY : "tracks risk"

    PROVINCES {
        int province_id PK
        string province_name UK
        string security_level
    }

    CUSTOMERS {
        int customer_id PK
        int province_id FK
        int age
        string gender
        string area_type
        string network_quality
        string internet_type
        float call_drop_rate
        float recharge_amount
        int recharge_frequency
        string payment_method
        int tenure_months
        int inactive_days
        int complaint_count
        string tower_availability
        string competitor_offer_exposure
        string discount_usage
        tinyint churn
    }

    CUSTOMER_RISK_HISTORY {
        int id PK
        int customer_id FK
        float risk_score
        datetime recorded_at
    }
```

---

## 2. DFD Level 0 (Context Diagram)

```mermaid
flowchart TD
    User[Admin User] -->|Login| System[ATCPRS System]
    User -->|Manage Customers| System
    User -->|Predict Churn| System
    User -->|View Analytics| System
    User -->|Generate Reports| System
    User -->|Simulate Scenarios| System
    User -->|View Alerts| System
    User -->|View Financial Impact| System
    System -->|Results| User
    System -->|Dashboard| User
    System -->|Reports| User
```

---

## 3. DFD Level 1

```mermaid
flowchart TD
    User[Admin User] -->|Login Request| Auth[Authentication Module]
    Auth -->|Session| User
    
    User -->|Customer Data| CustMgmt[Customer Management]
    CustMgmt -->|CRUD Operations| DB[(MySQL Database)]
    DB -->|Customer Records| CustMgmt
    CustMgmt -->|Customer List| User
    
    User -->|Prediction Request| Pred[Prediction Module]
    Pred -->|Customer Features| MLModel[Trained ML Model]
    MLModel -->|Churn Probability| Pred
    Pred -->|Risk Score| CustMgmt
    Pred -->|Health Score| CustMgmt
    Pred -->|Recommendations| User
    
    User -->|Analytics Request| Analytics[Analytics Module]
    Analytics -->|Query Data| DB
    DB -->|Aggregated Data| Analytics
    Analytics -->|AI Insights| User
    Analytics -->|Charts| User
    
    User -->|Simulation Request| Simulator[What-If Simulator]
    Simulator -->|Modified Features| MLModel
    MLModel -->|New Prediction| Simulator
    Simulator -->|Impact Analysis| User
    
    User -->|Alert Request| EarlyWarning[Early Warning System]
    EarlyWarning -->|Risk History| DB
    DB -->|Risk Trends| EarlyWarning
    EarlyWarning -->|Alerts| User
    
    User -->|Financial Request| Financial[Financial Impact Module]
    Financial -->|Revenue Data| DB
    DB -->|Financial Metrics| Financial
    Financial -->|Risk Analysis| User
    
    User -->|Report Request| Reports[Report Generation]
    Reports -->|Export Data| DB
    DB -->|Report Data| Reports
    Reports -->|PDF/Excel/CSV| User
```

---

## 4. Use Case Diagram

```mermaid
flowchart TD
    Admin[Admin User] --> UC1[Login]
    Admin --> UC2[Manage Customers]
    Admin --> UC3[Predict Churn]
    Admin --> UC4[View Dashboard]
    Admin --> UC5[View Analytics]
    Admin --> UC6[Use What-If Simulator]
    Admin --> UC7[View Early Warnings]
    Admin --> UC8[View Financial Impact]
    Admin --> UC9[Generate Reports]
    Admin --> UC10[Manage ML Models]
    
    UC2 --> UC2a[Add Customer]
    UC2 --> UC2b[Edit Customer]
    UC2 --> UC2c[Delete Customer]
    UC2 --> UC2d[View Customer Profile]
    
    UC3 --> UC3a[Single Prediction]
    UC3 --> UC3b[Batch Prediction]
    UC3 --> UC3c[View AI Explainability]
    
    UC4 --> UC4a[View KPIs]
    UC4 --> UC4b[View Charts]
    UC4 --> UC4c[View Top Risk Customers]
    
    UC5 --> UC5a[View Feature Importance]
    UC5 --> UC5b[View Churn Heatmap]
    UC5 --> UC5c[View AI Insights]
    
    UC9 --> UC9a[Export PDF]
    UC9 --> UC9b[Export Excel]
    UC9 --> UC9c[Export CSV]
```

---

## 5. Sequence Diagram - Customer Churn Prediction

```mermaid
sequenceDiagram
    participant User as Admin User
    participant UI as Web Interface
    participant Auth as Auth Module
    participant Pred as Prediction Module
    participant ML as ML Model
    participant DB as Database
    participant CustMgmt as Customer Management
    
    User->>UI: Enter Login Credentials
    UI->>Auth: Validate Credentials
    Auth->>DB: Query User
    DB-->>Auth: User Data
    Auth-->>UI: Session Token
    UI-->>User: Dashboard
    
    User->>UI: Select Customer for Prediction
    UI->>CustMgmt: Get Customer Data
    CustMgmt->>DB: Query Customer
    DB-->>CustMgmt: Customer Features
    CustMgmt-->>UI: Customer Data
    UI-->>User: Display Prediction Form
    
    User->>UI: Submit Prediction Request
    UI->>Pred: Send Customer Features
    Pred->>ML: Predict Churn
    ML-->>Pred: Churn Probability & Risk Level
    Pred->>Pred: Calculate Health Score
    Pred->>Pred: Generate Recommendations
    Pred->>Pred: Generate Feature Contributions
    Pred-->>UI: Prediction Results
    UI-->>User: Display Prediction with AI Explainability
    
    User->>UI: View Customer Profile
    UI->>CustMgmt: Get Customer Details
    CustMgmt->>DB: Query Customer + Province
    DB-->>CustMgmt: Customer Data
    CustMgmt-->>UI: Customer Profile with Health Badge
    UI-->>User: Display Profile
```

---

## 6. Deployment Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Browser[Web Browser]
    end
    
    subgraph Server["Application Server"]
        Flask[Flask Application]
        Auth[Auth Module]
        Routes[Route Controllers]
        Services[Business Services]
        MLService[ML Prediction Service]
    end
    
    subgraph Database["Database Layer"]
        MySQL[(MySQL Database)]
    end
    
    subgraph Storage["File Storage"]
        Models[Trained Models]
        Static[Static Assets]
        Templates[Jinja2 Templates]
    end
    
    Browser -->|HTTPS| Flask
    Flask --> Auth
    Flask --> Routes
    Routes --> Services
    Services --> MLService
    Services --> MySQL
    MLService --> Models
    Flask --> Static
    Flask --> Templates
    
    Models -->|Load| MLService
    MySQL -->|Query| Services
    Static -->|Serve| Flask
    Templates -->|Render| Flask
```

---

## 7. System Architecture Overview

```mermaid
flowchart LR
    subgraph Presentation["Presentation Layer"]
        UI[Web UI<br/>Bootstrap 5 + Glassmorphism]
    end
    
    subgraph Application["Application Layer"]
        Controller[Flask Controllers<br/>Routes]
        Service[Business Services<br/>Logic Layer]
        ML[ML Module<br/>Prediction & Recommendations]
    end
    
    subgraph Data["Data Layer"]
        ORM[SQLAlchemy ORM]
        DB[(MySQL Database)]
    end
    
    subgraph Storage["Storage Layer"]
        ModelFiles[Trained Models<br/>.pkl files]
        StaticFiles[CSS/JS Assets]
    end
    
    UI --> Controller
    Controller --> Service
    Service --> ML
    Service --> ORM
    ORM --> DB
    ML --> ModelFiles
    UI --> StaticFiles
```

---

## 8. Module Interaction Diagram

```mermaid
flowchart TD
    Auth[Auth Module]
    Dashboard[Dashboard Module]
    Customer[Customer Module]
    Prediction[Prediction Module]
    Analytics[Analytics Module]
    Reports[Reports Module]
    ML_Center[ML Center Module]
    WhatIf[What-If Simulator]
    EarlyWarning[Early Warning System]
    Financial[Financial Impact]
    
    Auth --> Dashboard
    Dashboard --> Customer
    Dashboard --> Prediction
    Dashboard --> Analytics
    Dashboard --> EarlyWarning
    Dashboard --> Financial
    
    Customer --> Prediction
    Customer --> EarlyWarning
    
    Prediction --> ML_Center
    Analytics --> ML_Center
    
    WhatIf --> Prediction
    WhatIf --> ML_Center
    
    Reports --> Customer
    Reports --> Analytics
    Reports --> Financial
    
    EarlyWarning --> Customer
    Financial --> Customer
```

---

## Diagram Legend

### Symbols Used
- **||--o{**: One-to-Many relationship
- **-->**: Data flow / dependency
- **[( )**: Database entity
- **[ ]**: Process / module
- **{ }**: Data store

### Color Coding (if supported)
- **Blue**: User / External entities
- **Green**: Application modules
- **Orange**: Database / Storage
- **Purple**: ML / AI components

---

## Notes

1. **Production Focus**: All diagrams represent the deployed production system
2. **No Training Pipeline**: Data cleaning, feature engineering, and model training are excluded
3. **No Notebooks**: Jupyter notebooks and development tools are not shown
4. **Real-time Operations**: Diagrams show runtime operations, not development workflows
5. **Simplified View**: Complex internal logic is abstracted for clarity

---

## Usage in Thesis

These diagrams can be directly included in thesis documentation using:
- Mermaid-compatible markdown editors
- GitHub (native Mermaid support)
- VS Code with Mermaid extension
- Export to PNG/SVG for LaTeX inclusion
