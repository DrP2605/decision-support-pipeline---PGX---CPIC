#!/usr/bin/env python3
"""
CPIC-Based Pharmacogenomics Decision Support Pipeline
Complete implementation for clinical decision support

Author: AI Research Assistant
Date: September 2025
Purpose: Transform patient genotypes into CPIC-based drug recommendations
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core data structures
class RecommendationStrength(Enum):
    STRONG = "Strong"
    MODERATE = "Moderate" 
    OPTIONAL = "Optional"
    NO_RECOMMENDATION = "No Recommendation"

class PhenotypeActivity(Enum):
    NORMAL = "Normal Function"
    DECREASED = "Decreased Function"
    NO_FUNCTION = "No Function"
    INCREASED = "Increased Function"
    UNCERTAIN = "Uncertain Function"

@dataclass
class Allele:
    """Represents a pharmacogenomic allele"""
    symbol: str
    function: PhenotypeActivity
    activity_score: float

@dataclass
class Genotype:
    """Represents patient genotype for a specific gene"""
    gene: str
    allele1: Allele
    allele2: Allele
    diplotype: str

    @property
    def activity_score(self) -> float:
        return self.allele1.activity_score + self.allele2.activity_score

@dataclass
class Phenotype:
    """Represents predicted phenotype based on genotype"""
    gene: str
    phenotype: str
    activity_score: float
    metabolizer_status: str

@dataclass
class DrugRecommendation:
    """Clinical recommendation for a drug based on pharmacogenetics"""
    drug: str
    gene: str
    patient_phenotype: str
    recommendation: str
    strength: RecommendationStrength
    rationale: str
    alternative_drugs: List[str]
    dose_modification: Optional[str]
    monitoring: Optional[str]

class CPICKnowledgeBase:
    """CPIC Guideline Knowledge Base Implementation"""

    def __init__(self):
        logger.info("Initializing CPIC Knowledge Base...")
        self.allele_definitions = self._load_allele_definitions()
        self.phenotype_mappings = self._load_phenotype_mappings()
        self.drug_guidelines = self._load_drug_guidelines()
        logger.info("CPIC Knowledge Base initialized successfully")

    def _load_allele_definitions(self) -> Dict:
        """Load CPIC allele definitions with function assignments"""
        return {
            "CYP2C19": {
                "*1": Allele("*1", PhenotypeActivity.NORMAL, 1.0),
                "*2": Allele("*2", PhenotypeActivity.NO_FUNCTION, 0.0),
                "*3": Allele("*3", PhenotypeActivity.NO_FUNCTION, 0.0),
                "*4": Allele("*4", PhenotypeActivity.NO_FUNCTION, 0.0),
                "*17": Allele("*17", PhenotypeActivity.INCREASED, 1.5)
            },
            "DPYD": {
                "*1": Allele("*1", PhenotypeActivity.NORMAL, 1.0),
                "*2A": Allele("*2A", PhenotypeActivity.NO_FUNCTION, 0.0),
                "*13": Allele("*13", PhenotypeActivity.NO_FUNCTION, 0.0),
                "c.2846A>T": Allele("c.2846A>T", PhenotypeActivity.DECREASED, 0.5),
                "c.1236G>A": Allele("c.1236G>A", PhenotypeActivity.DECREASED, 0.5)
            },
            "TPMT": {
                "*1": Allele("*1", PhenotypeActivity.NORMAL, 1.0),
                "*2": Allele("*2", PhenotypeActivity.DECREASED, 0.5),
                "*3A": Allele("*3A", PhenotypeActivity.NO_FUNCTION, 0.0),
                "*3C": Allele("*3C", PhenotypeActivity.NO_FUNCTION, 0.0)
            }
        }

    def _load_phenotype_mappings(self) -> Dict:
        """Load genotype to phenotype mappings following CPIC standards"""
        return {
            "CYP2C19": {
                "activity_ranges": [
                    (0.0, 0.5, "Poor Metabolizer"),
                    (0.5, 1.5, "Intermediate Metabolizer"),
                    (1.5, 2.0, "Normal Metabolizer"),
                    (2.0, 3.0, "Rapid Metabolizer"),
                    (3.0, float('inf'), "Ultrarapid Metabolizer")
                ]
            },
            "DPYD": {
                "activity_ranges": [
                    (0.0, 0.5, "DPD Deficiency"),
                    (0.5, 1.5, "DPD Intermediate Activity"),
                    (1.5, 2.0, "DPD Normal Activity")
                ]
            },
            "TPMT": {
                "activity_ranges": [
                    (0.0, 0.5, "Poor Metabolizer"),
                    (0.5, 1.5, "Intermediate Metabolizer"),  
                    (1.5, 2.0, "Normal Metabolizer")
                ]
            }
        }

    def _load_drug_guidelines(self) -> Dict:
        """Load CPIC drug-gene interaction guidelines"""
        return {
            "clopidogrel": {
                "gene": "CYP2C19",
                "recommendations": {
                    "Poor Metabolizer": DrugRecommendation(
                        drug="clopidogrel",
                        gene="CYP2C19",
                        patient_phenotype="Poor Metabolizer",
                        recommendation="Consider alternative P2Y12 inhibitor (prasugrel, ticagrelor)",
                        strength=RecommendationStrength.STRONG,
                        rationale="Significantly reduced platelet inhibition; increased risk for adverse cardiovascular events",
                        alternative_drugs=["prasugrel", "ticagrelor"],
                        dose_modification=None,
                        monitoring="Enhanced monitoring for cardiovascular events"
                    ),
                    "Intermediate Metabolizer": DrugRecommendation(
                        drug="clopidogrel",
                        gene="CYP2C19",
                        patient_phenotype="Intermediate Metabolizer",
                        recommendation="Consider alternative P2Y12 inhibitor or platelet function testing",
                        strength=RecommendationStrength.MODERATE,
                        rationale="Reduced platelet inhibition; potential increased risk for adverse cardiovascular events",
                        alternative_drugs=["prasugrel", "ticagrelor"],
                        dose_modification=None,
                        monitoring="Consider platelet function testing"
                    ),
                    "Normal Metabolizer": DrugRecommendation(
                        drug="clopidogrel",
                        gene="CYP2C19",
                        patient_phenotype="Normal Metabolizer",
                        recommendation="Standard dosing",
                        strength=RecommendationStrength.STRONG,
                        rationale="Normal platelet inhibition expected",
                        alternative_drugs=[],
                        dose_modification="75 mg daily",
                        monitoring="Standard monitoring"
                    ),
                    "Rapid Metabolizer": DrugRecommendation(
                        drug="clopidogrel",
                        gene="CYP2C19",
                        patient_phenotype="Rapid Metabolizer",
                        recommendation="Standard dosing",
                        strength=RecommendationStrength.STRONG,
                        rationale="Normal to enhanced platelet inhibition expected",
                        alternative_drugs=[],
                        dose_modification="75 mg daily",
                        monitoring="Standard monitoring"
                    )
                }
            },
            "5-fluorouracil": {
                "gene": "DPYD",
                "recommendations": {
                    "DPD Deficiency": DrugRecommendation(
                        drug="5-fluorouracil",
                        gene="DPYD",
                        patient_phenotype="DPD Deficiency",
                        recommendation="Avoid 5-fluorouracil and related drugs",
                        strength=RecommendationStrength.STRONG,
                        rationale="Complete or severe DPD deficiency; high risk of severe, potentially fatal toxicity",
                        alternative_drugs=["non-fluoropyrimidine regimens"],
                        dose_modification=None,
                        monitoring=None
                    ),
                    "DPD Intermediate Activity": DrugRecommendation(
                        drug="5-fluorouracil",
                        gene="DPYD",
                        patient_phenotype="DPD Intermediate Activity",
                        recommendation="Start with 50% dose reduction",
                        strength=RecommendationStrength.STRONG,
                        rationale="Reduced DPD activity; increased risk of severe toxicity with standard dosing",
                        alternative_drugs=["non-fluoropyrimidine regimens"],
                        dose_modification="Start with 50% of standard dose; titrate based on tolerance",
                        monitoring="Enhanced toxicity monitoring"
                    ),
                    "DPD Normal Activity": DrugRecommendation(
                        drug="5-fluorouracil",
                        gene="DPYD",
                        patient_phenotype="DPD Normal Activity",
                        recommendation="Standard dosing",
                        strength=RecommendationStrength.STRONG,
                        rationale="Normal DPD activity expected",
                        alternative_drugs=[],
                        dose_modification="Standard dose",
                        monitoring="Standard monitoring"
                    )
                }
            },
            "capecitabine": {
                "gene": "DPYD",
                "recommendations": {
                    "DPD Deficiency": DrugRecommendation(
                        drug="capecitabine",
                        gene="DPYD",
                        patient_phenotype="DPD Deficiency",
                        recommendation="Avoid capecitabine",
                        strength=RecommendationStrength.STRONG,
                        rationale="Complete or severe DPD deficiency; high risk of severe, potentially fatal toxicity",
                        alternative_drugs=["non-fluoropyrimidine regimens"],
                        dose_modification=None,
                        monitoring=None
                    ),
                    "DPD Intermediate Activity": DrugRecommendation(
                        drug="capecitabine",
                        gene="DPYD",
                        patient_phenotype="DPD Intermediate Activity",
                        recommendation="Start with 50% dose reduction",
                        strength=RecommendationStrength.STRONG,
                        rationale="Reduced DPD activity; increased risk of severe toxicity with standard dosing",
                        alternative_drugs=["non-fluoropyrimidine regimens"],
                        dose_modification="Start with 50% of standard dose; titrate based on tolerance",
                        monitoring="Enhanced toxicity monitoring"
                    ),
                    "DPD Normal Activity": DrugRecommendation(
                        drug="capecitabine",
                        gene="DPYD",
                        patient_phenotype="DPD Normal Activity",
                        recommendation="Standard dosing",
                        strength=RecommendationStrength.STRONG,
                        rationale="Normal DPD activity expected",
                        alternative_drugs=[],
                        dose_modification="Standard dose per protocol",
                        monitoring="Standard monitoring"
                    )
                }
            }
        }

class PharmacogenomicsDecisionSupport:
    """Main class for CPIC-based pharmacogenomics decision support"""

    def __init__(self):
        self.kb = CPICKnowledgeBase()
        self.supported_genes = list(self.kb.allele_definitions.keys())
        self.supported_drugs = list(self.kb.drug_guidelines.keys())
        logger.info(f"Decision Support System ready - Genes: {self.supported_genes}, Drugs: {self.supported_drugs}")

    def parse_genotype_input(self, genotype_data: Dict) -> List[Genotype]:
        """Parse various genotype input formats and create Genotype objects"""
        genotypes = []

        for gene, diplotype_str in genotype_data.items():
            if gene not in self.supported_genes:
                logger.warning(f"Unsupported gene: {gene}")
                continue

            # Parse diplotype (e.g., "*1/*2", "*2A/*13")
            allele_names = diplotype_str.split("/")
            if len(allele_names) != 2:
                logger.error(f"Invalid diplotype format: {diplotype_str}")
                continue

            allele1_name, allele2_name = allele_names

            # Get allele definitions
            if (allele1_name in self.kb.allele_definitions[gene] and 
                allele2_name in self.kb.allele_definitions[gene]):

                allele1 = self.kb.allele_definitions[gene][allele1_name]
                allele2 = self.kb.allele_definitions[gene][allele2_name]

                genotype = Genotype(
                    gene=gene,
                    allele1=allele1,
                    allele2=allele2,
                    diplotype=diplotype_str
                )
                genotypes.append(genotype)
                logger.info(f"Parsed genotype: {gene} {diplotype_str}")
            else:
                logger.warning(f"Unknown alleles for {gene}: {allele1_name}, {allele2_name}")

        return genotypes

    def predict_phenotype(self, genotype: Genotype) -> Phenotype:
        """Predict phenotype from genotype using CPIC mappings"""
        activity_score = genotype.activity_score
        gene = genotype.gene

        # Get activity ranges for this gene
        ranges = self.kb.phenotype_mappings[gene]["activity_ranges"]

        phenotype_name = "Unknown"
        for min_score, max_score, phenotype in ranges:
            if min_score <= activity_score < max_score:
                phenotype_name = phenotype
                break

        logger.info(f"Predicted phenotype: {gene} activity score {activity_score} -> {phenotype_name}")

        return Phenotype(
            gene=gene,
            phenotype=phenotype_name,
            activity_score=activity_score,
            metabolizer_status=phenotype_name
        )

    def get_drug_recommendations(self, phenotypes: List[Phenotype], 
                                drug_list: List[str]) -> List[DrugRecommendation]:
        """Generate clinical recommendations based on phenotypes and requested drugs"""
        recommendations = []

        for drug in drug_list:
            if drug not in self.supported_drugs:
                logger.warning(f"Unsupported drug: {drug}")
                continue

            drug_guideline = self.kb.drug_guidelines[drug]
            target_gene = drug_guideline["gene"]

            # Find relevant phenotype
            relevant_phenotype = None
            for phenotype in phenotypes:
                if phenotype.gene == target_gene:
                    relevant_phenotype = phenotype
                    break

            if relevant_phenotype and relevant_phenotype.phenotype in drug_guideline["recommendations"]:
                recommendation = drug_guideline["recommendations"][relevant_phenotype.phenotype]
                recommendations.append(recommendation)
                logger.info(f"Generated recommendation for {drug}: {recommendation.strength.value}")
            else:
                logger.warning(f"No recommendation available for {drug} with phenotype {relevant_phenotype.phenotype if relevant_phenotype else 'None'}")

        return recommendations

    def process_patient(self, patient_id: str, genotype_data: Dict, 
                       requested_drugs: List[str]) -> Dict:
        """Complete pipeline: genotype input to clinical recommendations"""

        logger.info(f"Processing patient {patient_id}")

        try:
            # Step 1: Parse genotype input
            genotypes = self.parse_genotype_input(genotype_data)

            # Step 2: Predict phenotypes
            phenotypes = [self.predict_phenotype(gt) for gt in genotypes]

            # Step 3: Generate recommendations
            recommendations = self.get_drug_recommendations(phenotypes, requested_drugs)

            # Step 4: Create comprehensive report
            report = {
                "patient_id": patient_id,
                "timestamp": datetime.now().isoformat(),
                "genotypes": [asdict(gt) for gt in genotypes],
                "phenotypes": [asdict(pt) for pt in phenotypes],
                "recommendations": [asdict(rec) for rec in recommendations],
                "summary": self._generate_summary(phenotypes, recommendations)
            }

            logger.info(f"Successfully processed patient {patient_id}")
            return report

        except Exception as e:
            logger.error(f"Error processing patient {patient_id}: {str(e)}")
            raise

    def _generate_summary(self, phenotypes: List[Phenotype], 
                         recommendations: List[DrugRecommendation]) -> Dict:
        """Generate a summary of key findings"""
        normal_phenotypes = ["Normal Metabolizer", "DPD Normal Activity"]
        actionable_genes = [p.gene for p in phenotypes if p.phenotype not in normal_phenotypes]
        high_priority_recs = [r for r in recommendations if r.strength == RecommendationStrength.STRONG]

        return {
            "total_genes_tested": len(phenotypes),
            "actionable_genes": actionable_genes,
            "high_priority_recommendations": len(high_priority_recs),
            "requires_intervention": len(actionable_genes) > 0,
            "genes_tested": [p.gene for p in phenotypes],
            "phenotype_summary": {p.gene: p.phenotype for p in phenotypes}
        }

# Example usage and testing
def main():
    """Example usage of the pharmacogenomics decision support pipeline"""

    print("=== CPIC-Based Pharmacogenomics Decision Support Pipeline ===\n")

    # Initialize the system
    pgx_system = PharmacogenomicsDecisionSupport()

    # Example patient scenarios
    test_cases = [
        {
            "patient_id": "DEMO_001",
            "genotypes": {"CYP2C19": "*2/*2"},
            "drugs": ["clopidogrel"],
            "description": "CYP2C19 Poor Metabolizer on Clopidogrel"
        },
        {
            "patient_id": "DEMO_002", 
            "genotypes": {"DPYD": "*2A/*1", "CYP2C19": "*1/*17"},
            "drugs": ["5-fluorouracil", "clopidogrel"],
            "description": "DPYD Intermediate + CYP2C19 Rapid Metabolizer"
        },
        {
            "patient_id": "DEMO_003",
            "genotypes": {"CYP2C19": "*1/*1", "DPYD": "*1/*1"},
            "drugs": ["clopidogrel", "capecitabine"],
            "description": "Normal Metabolizers (Control Case)"
        }
    ]

    # Process each test case
    for i, case in enumerate(test_cases, 1):
        print(f"=== TEST CASE {i}: {case['description']} ===")
        print(f"Patient ID: {case['patient_id']}")
        print(f"Genotypes: {case['genotypes']}")
        print(f"Requested Drugs: {case['drugs']}")
        print()

        try:
            report = pgx_system.process_patient(
                case['patient_id'], 
                case['genotypes'], 
                case['drugs']
            )

            print("RESULTS:")
            print(f"- Genes tested: {report['summary']['total_genes_tested']}")
            print(f"- Requires intervention: {report['summary']['requires_intervention']}")
            print(f"- High priority recommendations: {report['summary']['high_priority_recommendations']}")

            if report['recommendations']:
                print("\nCLINICAL RECOMMENDATIONS:")
                for j, rec in enumerate(report['recommendations'], 1):
                    print(f"  {j}. {rec['drug']} ({rec['gene']})")
                    print(f"     Phenotype: {rec['patient_phenotype']}")
                    print(f"     Recommendation: {rec['recommendation']}")
                    print(f"     Strength: {rec['strength']}")
                    if rec['dose_modification']:
                        print(f"     Dose: {rec['dose_modification']}")
            else:
                print("\nNo specific recommendations generated.")

        except Exception as e:
            print(f"ERROR: {str(e)}")

        print("\n" + "="*60 + "\n")

    print("Pipeline demonstration completed successfully!")

if __name__ == "__main__":
    main()
