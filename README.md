# Banking Voice Assistant with Intent Classification

This project implements a voice-activated banking assistant using a fine-tuned Natural Language Processing (NLP) model. It captures user intent from speech, routes the request to the appropriate banking operation, and responds using Text-to-Speech.

---

## End-to-End Architecture

The system accepts voice input through a Twilio call, converts it to text, classifies the user's banking intent, executes the corresponding action via a banking API, and returns a spoken response.

---

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
