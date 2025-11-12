# Complete Document Processing Pipeline

This diagram shows the complete end-to-end flow for document processing in the Barton Toolbox Hub.

```mermaid
graph TD
    Start[Document Upload] -->|POST /api/parser/extract| Parser[Parser Tool]

    Parser -->|Log Event| L1[Logger: parsing_started]
    Parser -->|Extract Fields| Extract[Field Extraction]
    Extract -->|5 Patterns| Patterns[Colon, Equals, Dollar, Table, Date]
    Patterns -->|150+ Mappings| Mapped[Mapped Fields]
    Mapped -->|Confidence Scoring| Scored[Fields with Confidence]

    Scored --> ParseCheck{Parsing Success?}
    ParseCheck -->|Yes| L2[Logger: parsing_completed]
    ParseCheck -->|No| L3[Logger: parsing_failed]

    L2 -->|POST /api/validator/validate| Validator[Validator Tool]
    L3 --> End1[End: Parse Failed]

    Validator -->|Log Event| L4[Logger: validation_started]
    Validator -->|Apply Rules| Rules[8 Rule Types]
    Rules -->|Check| Checks[Required, Type, Range, Regex, Length, Enum, Date, Custom]

    Checks --> ValidCheck{Validation Pass?}
    ValidCheck -->|Yes| L5[Logger: validation_completed]
    ValidCheck -->|No| L6[Logger: validation_failed]

    L5 -->|POST /api/parser/promote| Promote[Data Promotion]
    L6 --> End2[End: Validation Failed]

    Promote -->|Log Event| L7[Logger: promotion_started]
    Promote -->|Save to Neon| Neon[(Neon Database)]
    Promote -->|Trigger Webhook| N8N[n8n Workflow]
    Promote -->|Optional Backup| Firebase[(Firebase)]

    Neon --> PromoCheck{Promotion Success?}
    N8N --> PromoCheck
    Firebase --> PromoCheck

    PromoCheck -->|Yes| L8[Logger: promotion_completed]
    PromoCheck -->|No| L9[Logger: promotion_failed]

    L8 --> Success[✓ End: Success]
    L9 --> End3[End: Promotion Failed]

    style Parser fill:#f96,stroke:#333,stroke-width:3px
    style Validator fill:#ff6,stroke:#333,stroke-width:3px
    style Promote fill:#9f6,stroke:#333,stroke-width:3px
    style L1 fill:#69f,stroke:#333,stroke-width:2px
    style L2 fill:#69f,stroke:#333,stroke-width:2px
    style L4 fill:#69f,stroke:#333,stroke-width:2px
    style L5 fill:#69f,stroke:#333,stroke-width:2px
    style L7 fill:#69f,stroke:#333,stroke-width:2px
    style L8 fill:#69f,stroke:#333,stroke-width:2px
    style Success fill:#0f0,stroke:#333,stroke-width:3px
    style L3 fill:#f66,stroke:#333,stroke-width:2px
    style L6 fill:#f66,stroke:#333,stroke-width:2px
    style L9 fill:#f66,stroke:#333,stroke-width:2px
```

## Legend

- **Red Tools:** Parser (field extraction)
- **Yellow Tools:** Validator (validation)
- **Green Tools:** Promoter (data promotion)
- **Blue Logs:** Info/Success events
- **Red Logs:** Error/Failed events
- **Green Success:** Final success state

## Flow Steps

1. **Document Upload** → Start processing
2. **Parser Tool** → Extract fields from text
3. **Logger** → Track parsing events
4. **Validator Tool** → Validate extracted fields
5. **Logger** → Track validation events
6. **Data Promotion** → Save to external systems
7. **Logger** → Track promotion events
8. **Success/Failure** → Final state

## Key Decision Points

- **Parsing Success?** → Continue to validation or end
- **Validation Pass?** → Continue to promotion or end
- **Promotion Success?** → Success or end with error
