# Create comprehensive API specification
api_spec = '''# CPIC Pharmacogenomics Decision Support API Specification

## Overview
RESTful API for CPIC-based pharmacogenomics decision support pipeline providing genotype-to-recommendation services for clinical integration.

## Base URL
```
https://api.pgx-decision-support.healthcare.org/v1
```

## Authentication
- **Type**: API Key or OAuth 2.0
- **Headers**: `Authorization: Bearer <token>` or `X-API-Key: <api_key>`

## Core Endpoints

### 1. Process Patient Genotype
**Endpoint**: `POST /patients/process`

**Description**: Complete pipeline processing from genotype to clinical recommendations

**Request Body**:
```json
{
    "patient_id": "string (required)",
    "genotypes": {
        "CYP2C19": "*1/*2",
        "DPYD": "*1/*1"
    },
    "drugs": ["clopidogrel", "5-fluorouracil"],
    "format": "full|summary|alerts_only (optional, default: full)"
}
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "patient_id": "PAT001",
        "timestamp": "2025-09-09T12:03:00Z",
        "genotypes": [
            {
                "gene": "CYP2C19",
                "diplotype": "*1/*2",
                "allele1": {"symbol": "*1", "activity_score": 1.0},
                "allele2": {"symbol": "*2", "activity_score": 0.0}
            }
        ],
        "phenotypes": [
            {
                "gene": "CYP2C19",
                "phenotype": "Intermediate Metabolizer",
                "activity_score": 1.0
            }
        ],
        "recommendations": [
            {
                "drug": "clopidogrel",
                "gene": "CYP2C19",
                "patient_phenotype": "Intermediate Metabolizer",
                "recommendation": "Consider alternative P2Y12 inhibitor",
                "strength": "Moderate",
                "rationale": "Reduced platelet inhibition",
                "alternative_drugs": ["prasugrel", "ticagrelor"],
                "monitoring": "Consider platelet function testing"
            }
        ],
        "summary": {
            "total_genes_tested": 1,
            "actionable_genes": ["CYP2C19"],
            "high_priority_recommendations": 0,
            "requires_intervention": true
        }
    }
}
```

### 2. Get Supported Genes
**Endpoint**: `GET /genes`

**Description**: Retrieve list of supported pharmacogenes

**Response**:
```json
{
    "status": "success",
    "data": {
        "genes": [
            {
                "symbol": "CYP2C19",
                "name": "Cytochrome P450 2C19",
                "supported_alleles": ["*1", "*2", "*3", "*17"],
                "associated_drugs": ["clopidogrel", "omeprazole"]
            }
        ]
    }
}
```

### 3. Get Drug Guidelines
**Endpoint**: `GET /drugs/{drug_name}/guidelines`

**Description**: Retrieve CPIC guidelines for specific drug

**Parameters**:
- `drug_name`: Drug identifier (e.g., "clopidogrel")

**Response**:
```json
{
    "status": "success",
    "data": {
        "drug": "clopidogrel",
        "gene": "CYP2C19",
        "guidelines": {
            "Poor Metabolizer": {
                "recommendation": "Consider alternative P2Y12 inhibitor",
                "strength": "Strong",
                "alternatives": ["prasugrel", "ticagrelor"]
            }
        },
        "cpic_version": "2022.1",
        "last_updated": "2022-01-15"
    }
}
```

### 4. Generate Clinical Alerts
**Endpoint**: `POST /alerts/generate`

**Description**: Generate EHR-compatible clinical decision support alerts

**Request Body**:
```json
{
    "patient_id": "PAT001",
    "recommendations": [
        {
            "drug": "clopidogrel",
            "gene": "CYP2C19",
            "patient_phenotype": "Poor Metabolizer",
            "recommendation": "Consider alternative therapy",
            "strength": "Strong"
        }
    ],
    "alert_format": "ehr|fhir|cds_hooks"
}
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "alerts": [
            {
                "alert_id": "PGX_CYP2C19_clopidogrel",
                "alert_level": "HIGH",
                "title": "Pharmacogenomic Alert: clopidogrel",
                "message": "Consider alternative P2Y12 inhibitor",
                "actions": {
                    "alternatives": ["prasugrel", "ticagrelor"],
                    "monitoring": "Enhanced cardiovascular monitoring"
                }
            }
        ]
    }
}
```

### 5. Batch Processing
**Endpoint**: `POST /patients/batch`

**Description**: Process multiple patients simultaneously

**Request Body**:
```json
{
    "patients": [
        {
            "patient_id": "PAT001",
            "genotypes": {"CYP2C19": "*2/*2"},
            "drugs": ["clopidogrel"]
        },
        {
            "patient_id": "PAT002", 
            "genotypes": {"DPYD": "*2A/*1"},
            "drugs": ["5-fluorouracil"]
        }
    ],
    "format": "summary"
}
```

## Error Responses

### Standard Error Format
```json
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid genotype format",
        "details": {
            "field": "genotypes.CYP2C19",
            "value": "*1*2",
            "expected": "diplotype format like '*1/*2'"
        }
    }
}
```

### Error Codes
- `VALIDATION_ERROR`: Invalid input parameters
- `UNSUPPORTED_GENE`: Gene not in knowledge base
- `UNSUPPORTED_DRUG`: Drug not in guidelines
- `PROCESSING_ERROR`: Internal processing failure
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `AUTHENTICATION_FAILED`: Invalid credentials

## Rate Limiting
- **Standard**: 1000 requests/hour per API key
- **Batch**: 100 batch requests/hour per API key
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Data Models

### Genotype Input Formats

#### 1. Diplotype String
```json
{"CYP2C19": "*1/*2"}
```

#### 2. VCF Summary
```json
{
    "CYP2C19": {
        "variants": ["rs4244285"],
        "genotypes": ["GA"]
    }
}
```

#### 3. Lab Report
```json
{
    "tests": [
        {
            "gene": "CYP2C19",
            "result": "*1/*2",
            "phenotype": "Intermediate Metabolizer"
        }
    ]
}
```

## Integration Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function processPatient(patientData) {
    try {
        const response = await axios.post(
            'https://api.pgx-decision-support.healthcare.org/v1/patients/process',
            patientData,
            {
                headers: {
                    'Authorization': 'Bearer YOUR_TOKEN',
                    'Content-Type': 'application/json'
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error('PGx API Error:', error.response.data);
    }
}
```

### Python
```python
import requests

def process_patient(patient_data, api_key):
    url = "https://api.pgx-decision-support.healthcare.org/v1/patients/process"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=patient_data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
```

### cURL
```bash
curl -X POST "https://api.pgx-decision-support.healthcare.org/v1/patients/process" \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{
       "patient_id": "PAT001",
       "genotypes": {"CYP2C19": "*2/*2"},
       "drugs": ["clopidogrel"],
       "format": "full"
     }'
```

## FHIR Integration

### FHIR Observation Resource (Input)
```json
{
    "resourceType": "Observation",
    "status": "final",
    "code": {
        "coding": [{
            "system": "http://loinc.org",
            "code": "84413-4",
            "display": "CYP2C19 gene targeted mutation analysis"
        }]
    },
    "valueString": "*1/*2"
}
```

### FHIR MedicationRequest (Output)
```json
{
    "resourceType": "MedicationRequest",
    "status": "draft",
    "medicationCodeableConcept": {
        "coding": [{
            "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
            "code": "32968",
            "display": "clopidogrel"
        }]
    },
    "note": [{
        "text": "Consider alternative P2Y12 inhibitor based on CYP2C19 genotype"
    }]
}
```

## Webhook Support

### Callback URL Configuration
```json
{
    "webhook_url": "https://your-system.com/pgx/callbacks",
    "events": ["processing_complete", "high_priority_alert"],
    "secret": "webhook_secret_key"
}
```

### Webhook Payload
```json
{
    "event": "processing_complete",
    "timestamp": "2025-09-09T12:03:00Z",
    "patient_id": "PAT001",
    "requires_intervention": true,
    "high_priority_count": 1
}
```

## Testing Environment

### Sandbox URL
```
https://sandbox.pgx-decision-support.healthcare.org/v1
```

### Test Patient Data
```json
{
    "patient_id": "TEST_001",
    "genotypes": {"CYP2C19": "*2/*2"},
    "drugs": ["clopidogrel"]
}
```

## Support and Documentation
- **API Documentation**: https://docs.pgx-decision-support.healthcare.org
- **SDKs**: Available for Python, JavaScript, Java, C#
- **Support**: api-support@pgx-decision-support.healthcare.org
- **Status Page**: https://status.pgx-decision-support.healthcare.org
'''

with open('pgx_api_specification.md', 'w') as f:
    f.write(api_spec)

print("✓ Comprehensive API specification created: 'pgx_api_specification.md'")
print("✓ Includes all endpoints, data models, and integration examples")
print("✓ Ready for development team implementation")
print("✓ Supports FHIR, webhooks, and multiple programming languages")