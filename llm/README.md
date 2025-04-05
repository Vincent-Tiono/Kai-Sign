# ERC7730 Specification Evaluator API

A FastAPI application that evaluates ERC7730 JSON specifications using Google's Gemini AI.

## Installation

1. Install the required dependencies:

```bash
pip install fastapi uvicorn google-genai pydantic
```

2. Run the API server:

```bash
# From the project root directory
uvicorn llm.api:app --reload
```

The server will start on http://localhost:8000

## Usage

### Evaluate a Specification

Send a POST request to `/evaluate` with your JSON specification:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"spec": YOUR_JSON_SPEC_HERE}'
```

Example with curl:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"spec": {
  "$schema": "../../specs/erc7730-v1.schema.json",
  "context": {
    "eip712": {
      "deployments": [{ "chainId": 1, "address": "0x1234567890123456789012345678901234567890" }],
      "domain": { "name": "Example", "chainId": 1, "verifyingContract": "0x1234567890123456789012345678901234567890" }
    }
  },
  "metadata": { "owner": "Example Owner" },
  "display": {
    "formats": {
      "ExampleType": {
        "intent": "Example Intent",
        "fields": [
          { "path": "field1", "label": "Field 1", "format": "raw" }
        ]
      }
    }
  }
}}'
```

### Response

The API will return a JSON object with the evaluation result:

```json
{
  "Good": "80%",
  "Bad": "20%"
}
```

### Health Check

You can check if the API is running with:

```bash
curl http://localhost:8000/health
```

## API Documentation

FastAPI automatically generates interactive documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 