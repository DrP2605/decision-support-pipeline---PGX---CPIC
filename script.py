# CPIC-based Pharmacogenomics Decision Support Pipeline
# A comprehensive implementation for genotype to clinical recommendation mapping

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
from datetime import datetime

# Define core data structures for the pipeline
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

# CPIC Guideline Knowledge Base
class CPICKnowledgeBase:
    def __init__(self):
        self.allele_definitions = self._load_allele_definitions()
        self.phenotype_mappings = self._load_phenotype_mappings()
        self.drug_guidelines = self._load_drug_guidelines()
    
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
                        rationale="Complete DPD deficiency; high risk of severe, potentially fatal toxicity",
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
            }
        }

print("✓ CPIC Knowledge Base structure defined")
print("✓ Core data structures created")