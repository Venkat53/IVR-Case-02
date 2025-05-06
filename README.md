### Mermaid Flowchart (Simplified for Maximum Compatibility)

```mermaid
graph TD
    A[Twilio] --> B(test_resp.py)
    B --> C(Vosk)
    C --> B
    B --> D(main.py)
    D --> E(nlp.py)
    E --> F(Fine-tuned Model)
    E --> G(ChromaDB)
    E --> H(router.py)
    H --> I(tools.py)
    I --> J(banking_api.py)
    J --> I
    I --> H
    H --> D
    D --> B
    B --> K(Twilio/Other TTS)
    D --> L(OpenAI)
    L --> B
```  

                                +------------------+     +------------------+     +--------------------------+
                                | Twilio (Call)    | --> | test_resp.py     | --> | Vosk (Speech-to-Text)    |
                                +------------------+     +------------------+     +--------------------------+
                                                                |                          |
                                                                | (Text)                   |
                                                                v                          |
                                                        +--------------------+            |
                                                        | test_resp.py       | <----------+
                                                        | (API Request)      |
                                                        +--------------------+
                                                                |
                                                                | (POST /predict_intent)
                                                                v
                                                        +--------------------+
                                                        | main.py (Flask)    |
                                                        | (Receive Query)    |
                                                        +--------------------+
                                                                |
                                                                | (Call process_user_query)
                                                                v
                                                        +--------------------+     +------------------+     +------------------+
                                                        | nlp.py             | --> | Fine-tuned Model |     | ChromaDB         |
                                                        | (Intent Classif.)  |     | (model.py)       |     | (Session Ctx)    |
                                                        +--------------------+     +------------------+     +------------------+
                                                                |
                                                                | (Intent, Confidence)
                                                                v
                                                        +--------------------+
                                                        | router.py          |
                                                        | (Route Request)    |
                                                        +--------------------+
                                                                |
                                                                | (Call Tool)
                                                                v
                                                        +--------------------+     +--------------------------+
                                                        | tools.py           | --> | banking_api.py           |
                                                        | (Tool Interface)   |     | (Banking Operations)     |
                                                        +--------------------+     +--------------------------+
                                                                |                          ^
                                                                | (API Call/Response)      |
                                                                v                          |
                                                        +--------------------+ <-----------+
                                                        | router.py          |
                                                        | (Process Result)   |
                                                        +--------------------+
                                                                |
                                                                | (Response)
                                                                v
                                                        +--------------------+     +------------------+     +--------------------------+
                                                        | main.py            | --> | test_resp.py     | --> | Twilio/Other TTS         |
                                                        | (Return Response)  |     | (Text-to-Speech) |     | (Play Back to Caller)    |
                                                        +--------------------+     +------------------+     +--------------------------+
                                                                ^
                                                                | (Low Confidence Fallback)
                                                                |
                                                        +------------------+
                                                        | OpenAI           |
                                                        | (Fallback Resp.) |
                                                        +------------------+
