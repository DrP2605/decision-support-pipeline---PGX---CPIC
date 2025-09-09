# Demonstration of different input formats and API responses

print("=== DEMONSTRATION: DIFFERENT INPUT FORMATS ===")
print()

# Example 1: VCF-like data input
print("1. VCF SUMMARY INPUT:")
vcf_input = {
    "CYP2C19": {
        "variants": ["rs4244285", "rs4986893"],
        "genotypes": ["GA", "GT"]  # Heterozygous for *2, wild type for *17 position
    }
}
print(f"VCF Input: {vcf_input}")

parsed_vcf = parser.parse_vcf_summary(vcf_input)
print(f"Parsed Genotypes: {parsed_vcf}")
print()

# Example 2: Lab report format
print("2. LAB REPORT INPUT:")
lab_report = {
    "patient_id": "LAB123456",
    "lab": "Genomics Laboratory",
    "tests": [
        {"gene": "CYP2C19", "result": "*1/*2", "phenotype": "Intermediate Metabolizer"},
        {"gene": "DPYD", "result": "*1/*1", "phenotype": "Normal Activity"}
    ]
}
print(f"Lab Report: {lab_report}")

parsed_lab = parser.parse_lab_report(lab_report)
print(f"Parsed Genotypes: {parsed_lab}")
print()

print("=== DEMONSTRATION: API REQUESTS ===")
print()

# API Request Example 1: Full report
api_request1 = {
    "patient_id": "API_PAT001", 
    "genotypes": {"CYP2C19": "*2/*2"},
    "drugs": ["clopidogrel"],
    "format": "full"
}

print("1. FULL REPORT REQUEST:")
print(f"Request: {json.dumps(api_request1, indent=2)}")
response1 = api.process_request(api_request1)
print(f"Response Status: {response1['status']}")
if response1['status'] == 'success':
    print(f"Recommendations Count: {len(response1['data']['recommendations'])}")
    print(f"Requires Intervention: {response1['data']['summary']['requires_intervention']}")
print()

# API Request Example 2: Alerts only
api_request2 = {
    "patient_id": "API_PAT002",
    "genotypes": {"DPYD": "*2A/*1"}, 
    "drugs": ["5-fluorouracil"],
    "format": "alerts_only"
}

print("2. ALERTS ONLY REQUEST:")
print(f"Request: {json.dumps(api_request2, indent=2)}")
response2 = api.process_request(api_request2)
print(f"Response Status: {response2['status']}")
if response2['status'] == 'success':
    print(f"Alerts Generated: {len(response2['data']['alerts'])}")
    for alert in response2['data']['alerts']:
        print(f"  - Alert Level: {alert['alert_level']}")
        print(f"  - Title: {alert['title']}")
        print(f"  - Message: {alert['message']}")
print()

print("=== DEMONSTRATION: CLINICAL ALERTS ===")
print()

# Generate EHR alert for strong recommendation
sample_recommendation = DrugRecommendation(
    drug="clopidogrel",
    gene="CYP2C19", 
    patient_phenotype="Poor Metabolizer",
    recommendation="Consider alternative P2Y12 inhibitor (prasugrel, ticagrelor)",
    strength=RecommendationStrength.STRONG,
    rationale="Significantly reduced platelet inhibition; increased risk for adverse cardiovascular events",
    alternative_drugs=["prasugrel", "ticagrelor"],
    dose_modification=None,
    monitoring="Enhanced monitoring for cardiovascular events"
)

ehr_alert = alert_gen.generate_ehr_alert(sample_recommendation)
print("EHR ALERT FORMAT:")
print(json.dumps(ehr_alert, indent=2))
print()

# Generate patient safety card
sample_report = {
    "patient_id": "CARD_PAT001",
    "timestamp": "2025-09-09T12:03:00",
    "recommendations": [asdict(sample_recommendation)]
}

patient_card = alert_gen.generate_patient_card(sample_report)
print("PATIENT SAFETY CARD:")
print(json.dumps(patient_card, indent=2))