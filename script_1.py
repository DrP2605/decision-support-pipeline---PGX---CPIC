# Core Decision Support Pipeline Implementation

class PharmacogenomicsDecisionSupport:
    """Main class for CPIC-based pharmacogenomics decision support"""
    
    def __init__(self):
        self.kb = CPICKnowledgeBase()
        self.supported_genes = list(self.kb.allele_definitions.keys())
        self.supported_drugs = list(self.kb.drug_guidelines.keys())
    
    def parse_genotype_input(self, genotype_data: Dict) -> List[Genotype]:
        """Parse various genotype input formats and create Genotype objects"""
        genotypes = []
        
        for gene, diplotype_str in genotype_data.items():
            if gene not in self.supported_genes:
                continue
                
            # Parse diplotype (e.g., "*1/*2", "*2A/*13")
            allele_names = diplotype_str.split("/")
            if len(allele_names) != 2:
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
        
        return recommendations
    
    def process_patient(self, patient_id: str, genotype_data: Dict, 
                       requested_drugs: List[str]) -> Dict:
        """Complete pipeline: genotype input to clinical recommendations"""
        
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
        
        return report
    
    def _generate_summary(self, phenotypes: List[Phenotype], 
                         recommendations: List[DrugRecommendation]) -> Dict:
        """Generate a summary of key findings"""
        actionable_genes = [p.gene for p in phenotypes if p.phenotype != "Normal Metabolizer" and p.phenotype != "DPD Normal Activity"]
        high_priority_recs = [r for r in recommendations if r.strength == RecommendationStrength.STRONG]
        
        return {
            "total_genes_tested": len(phenotypes),
            "actionable_genes": actionable_genes,
            "high_priority_recommendations": len(high_priority_recs),
            "requires_intervention": len(actionable_genes) > 0
        }

# Initialize the decision support system
pgx_system = PharmacogenomicsDecisionSupport()
print("✓ Pharmacogenomics Decision Support System initialized")
print(f"✓ Supported genes: {pgx_system.supported_genes}")
print(f"✓ Supported drugs: {pgx_system.supported_drugs}")