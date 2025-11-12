# Document Processing Sequence Diagram

This diagram shows the detailed interaction sequence between all components.

```mermaid
sequenceDiagram
    actor User
    participant Parser
    participant Validator
    participant Logger
    participant Neon
    participant Firebase
    participant n8n

    Note over User,n8n: Document Processing Workflow

    %% Parsing Phase
    User->>Parser: POST /api/parser/extract<br/>{text, doc_id}
    activate Parser

    Parser->>Logger: POST /api/logger/event<br/>event_type: parsing_started
    activate Logger
    Logger->>Neon: INSERT INTO doc_event_log
    alt Neon Success
        Neon-->>Logger: event_id: 1001
        Logger-->>Parser: {success: true, storage: neon}
    else Neon Fails
        Logger->>Firebase: Failover: Store event
        Firebase-->>Logger: event_id: fb_abc
        Logger-->>Parser: {success: true, storage: firebase}
    end
    deactivate Logger

    Parser->>Parser: Extract fields<br/>(5 patterns, 150+ mappings)
    Parser->>Parser: Calculate confidence scores

    alt Parsing Success
        Parser->>Logger: POST /api/logger/event<br/>event_type: parsing_completed
        Logger->>Neon: INSERT INTO doc_event_log
        Neon-->>Logger: event_id: 1002
        Logger-->>Parser: {success: true}
        Parser-->>User: {fields: {...}, confidence: 0.92}
    else Parsing Fails
        Parser->>Logger: POST /api/logger/event<br/>event_type: parsing_failed
        Logger->>Neon: INSERT INTO doc_event_log
        Neon-->>Logger: event_id: 1003
        Logger-->>Parser: {success: true}
        Parser-->>User: {success: false, error: "..."}
        deactivate Parser
        Note over User,n8n: End: Parsing Failed
    end

    %% Validation Phase
    User->>Validator: POST /api/validator/validate<br/>{doc_id, fields, schema_id}
    activate Validator

    Validator->>Logger: POST /api/logger/event<br/>event_type: validation_started
    Logger->>Neon: INSERT INTO doc_event_log
    Neon-->>Logger: event_id: 1004
    Logger-->>Validator: {success: true}

    Validator->>Validator: Load schema<br/>(document_basic)
    Validator->>Validator: Apply validation rules<br/>(required, type, range, regex...)

    alt Validation Pass
        Validator->>Logger: POST /api/logger/event<br/>event_type: validation_completed
        Logger->>Neon: INSERT INTO doc_event_log
        Neon-->>Logger: event_id: 1005
        Logger-->>Validator: {success: true}
        Validator-->>User: {valid: true, errors: []}
        deactivate Validator
    else Validation Fails
        Validator->>Logger: POST /api/logger/event<br/>event_type: validation_failed
        Logger->>Neon: INSERT INTO doc_event_log
        Neon-->>Logger: event_id: 1006
        Logger-->>Validator: {success: true}
        Validator-->>User: {valid: false, errors: [{...}]}
        deactivate Validator
        Note over User,n8n: End: Validation Failed
    end

    %% Promotion Phase
    User->>Parser: POST /api/parser/promote<br/>{doc_id, fields, destinations}
    activate Parser

    Parser->>Logger: POST /api/logger/event<br/>event_type: promotion_started
    Logger->>Neon: INSERT INTO doc_event_log
    Neon-->>Logger: event_id: 1007
    Logger-->>Parser: {success: true}

    par Parallel Promotion
        Parser->>Neon: INSERT INTO doc_parser_fillable<br/>{doc_id, fields, metadata}
        Neon-->>Parser: {row_id: 12345}
    and
        Parser->>n8n: POST webhook<br/>{doc_id, fields, metadata}
        n8n-->>Parser: {workflow_id: wf_789, status: running}
    and (Optional)
        Parser->>Firebase: Add to collection<br/>doc_parser_fillable
        Firebase-->>Parser: {doc_id: fb_xyz}
    end

    alt All Promotions Success
        Parser->>Logger: POST /api/logger/event<br/>event_type: promotion_completed<br/>metadata: {neon: success, n8n: success}
        Logger->>Neon: INSERT INTO doc_event_log
        Neon-->>Logger: event_id: 1008
        Logger-->>Parser: {success: true}
        Parser-->>User: {success: true, results: {...}}
        deactivate Parser
        Note over User,n8n: End: Success ✓
    else Any Promotion Fails
        Parser->>Logger: POST /api/logger/event<br/>event_type: promotion_failed<br/>metadata: {errors: [...]}
        Logger->>Neon: INSERT INTO doc_event_log
        Neon-->>Logger: event_id: 1009
        Logger-->>Parser: {success: true}
        Parser-->>User: {success: false, errors: {...}}
        deactivate Parser
        Note over User,n8n: End: Promotion Failed
    end

    %% Retrieve Events
    Note over User,Logger: Later: Retrieve Event History
    User->>Logger: GET /api/logger/events/doc_001
    activate Logger
    Logger->>Neon: SELECT * FROM doc_event_log<br/>WHERE doc_id = 'doc_001'
    Neon-->>Logger: [event1, event2, event3, ...]
    Logger-->>User: {events: [...], total_count: 8}
    deactivate Logger
```

## Interaction Summary

### Parsing Phase
1. User uploads document to Parser
2. Parser logs `parsing_started`
3. Parser extracts fields with confidence scores
4. Parser logs `parsing_completed` or `parsing_failed`
5. Parser returns results to user

### Validation Phase
6. User sends fields to Validator
7. Validator logs `validation_started`
8. Validator applies schema rules
9. Validator logs `validation_completed` or `validation_failed`
10. Validator returns validation results

### Promotion Phase
11. User triggers promotion
12. Parser logs `promotion_started`
13. Parser saves to Neon, triggers n8n, optionally saves to Firebase (parallel)
14. Parser logs `promotion_completed` or `promotion_failed`
15. Parser returns promotion results

### Logging Throughout
- **Logger** handles all events
- **Neon** is primary storage
- **Firebase** is automatic failover
- Events can be retrieved later for audit trail

## Error Handling

- If Neon fails during logging → Automatic failover to Firebase
- If parsing fails → Log error and end workflow
- If validation fails → Log errors and return to user
- If promotion fails → Log failure with details
