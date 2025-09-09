# Additional utility functions for different input formats and integrations

class PGxDataParser:
    """Handles various input formats for pharmacogenomic data"""
    
    @staticmethod
    def parse_vcf_summary(vcf_data: Dict) -> Dict:
        """Parse summarized VCF data format"""
        # Example VCF summary format:
        # {"CYP2C19": {"variants": ["rs4244285", "rs4986893"], "genotypes": ["GT", "GA"]}}
        
        genotype_mapping = {
            "CYP2C19": {
                ("rs4244285", "GT"): "*1",  # Wild type
                ("rs4244285", "GA"): "*2",  # Heterozygous for *2
                ("rs4244285", "AA"): "*2",  # Homozygous for *2
                ("rs4986893", "GT"): "*1",  # Wild type
                ("rs4986893", "GA"): "*17", # Heterozygous for *17
                ("rs4986893", "AA"): "*17"  # Homozygous for *17
            }
        }
        
        parsed_genotypes = {}
        for gene, data in vcf_data.items():
            if gene in genotype_mapping:
                alleles = []
                for variant, genotype in zip(data["variants"], data["genotypes"]):
                    if (variant, genotype) in genotype_mapping[gene]:
                        alleles.append(genotype_mapping[gene][(variant, genotype)])
                
                if len(alleles) == 2:
                    parsed_genotypes[gene] = f"{alleles[0]}/{alleles[1]}"
        
        return parsed_genotypes
    
    @staticmethod 
    def parse_lab_report(lab_data: Dict) -> Dict:
        """Parse clinical laboratory report format"""
        # Example lab report format:
        # {"patient_id": "12345", "tests": [{"gene": "CYP2C19", "result": "*1/*2", "phenotype": "Intermediate Metabolizer"}]}
        
        genotypes = {}
        for test in lab_data.get("tests", []):
            gene = test.get("gene")
            result = test.get("result")
            if gene and result:
                genotypes[gene] = result
        
        return genotypes

class AlertGenerator:
    """Generates different types of clinical decision support alerts"""
    
    @staticmethod
    def generate_ehr_alert(recommendation: DrugRecommendation) -> Dict:
        """Generate EHR-compatible alert format"""
        
        # Map strength to alert level
        alert_level_map = {
            RecommendationStrength.STRONG: "HIGH",
            RecommendationStrength.MODERATE: "MEDIUM", 
            RecommendationStrength.OPTIONAL: "LOW",
            RecommendationStrength.NO_RECOMMENDATION: "INFO"
        }
        
        return {
            "alert_id": f"PGX_{recommendation.gene}_{recommendation.drug}",
            "alert_level": alert_level_map[recommendation.strength],
            "title": f"Pharmacogenomic Alert: {recommendation.drug}",
            "message": recommendation.recommendation,
            "rationale": recommendation.rationale,
            "actions": {
                "alternatives": recommendation.alternative_drugs,
                "dose_modification": recommendation.dose_modification,
                "monitoring": recommendation.monitoring
            },
            "dismiss_reasons": ["Clinician override", "Patient-specific factors", "Alternative assessment"]
        }
    
    @staticmethod
    def generate_patient_card(patient_report: Dict) -> Dict:
        """Generate patient wallet card format (like Safety Code cards)"""
        
        actionable_findings = []
        for rec in patient_report["recommendations"]:
            if rec["strength"] in ["Strong", "Moderate"]:
                actionable_findings.append({
                    "drug": rec["drug"],
                    "gene": rec["gene"],
                    "action": rec["recommendation"]
                })
        
        return {
            "patient_id": patient_report["patient_id"],
            "card_type": "Pharmacogenomic Safety Card",
            "issue_date": patient_report["timestamp"][:10],
            "actionable_findings": actionable_findings,
            "emergency_contact": "Contact prescribing physician",
            "qr_data": f"PGX_DATA_{patient_report['patient_id']}"
        }

class APIInterface:
    """REST API interface for the decision support system"""
    
    def __init__(self, pgx_system: PharmacogenomicsDecisionSupport):
        self.pgx_system = pgx_system
    
    def process_request(self, request_data: Dict) -> Dict:
        """Process API request and return formatted response"""
        
        try:
            # Extract request parameters
            patient_id = request_data.get("patient_id")
            genotype_data = request_data.get("genotypes", {})
            drugs = request_data.get("drugs", [])
            response_format = request_data.get("format", "full")  # full, summary, alerts_only
            
            # Process patient data
            report = self.pgx_system.process_patient(patient_id, genotype_data, drugs)
            
            # Format response based on requested format
            if response_format == "summary":
                response = {
                    "patient_id": report["patient_id"],
                    "timestamp": report["timestamp"],
                    "summary": report["summary"],
                    "high_priority_alerts": len([r for r in report["recommendations"] 
                                               if r["strength"] == "Strong"])
                }
            elif response_format == "alerts_only":
                alerts = [AlertGenerator.generate_ehr_alert(
                    DrugRecommendation(**rec)) for rec in report["recommendations"]]
                response = {
                    "patient_id": report["patient_id"],
                    "alerts": alerts
                }
            else:  # full format
                response = report
            
            return {
                "status": "success",
                "data": response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "code": "PROCESSING_ERROR"
            }

# Initialize additional components
parser = PGxDataParser()
alert_gen = AlertGenerator()
api = APIInterface(pgx_system)

print("✓ Additional utility classes initialized:")
print("  - PGxDataParser: Handles VCF and lab report formats")
print("  - AlertGenerator: Creates EHR alerts and patient cards") 
print("  - APIInterface: REST API for system integration")