# Example patient scenarios demonstrating the decision support pipeline

# Patient 1: CYP2C19 Poor Metabolizer requiring clopidogrel
patient1_genotypes = {
    "CYP2C19": "*2/*2",  # Poor metabolizer genotype
}

patient1_drugs = ["clopidogrel"]

print("=== PATIENT 1 EXAMPLE ===")
print(f"Genotype: {patient1_genotypes}")
print(f"Requested drugs: {patient1_drugs}")
print()

patient1_report = pgx_system.process_patient("PAT001", patient1_genotypes, patient1_drugs)

print("ANALYSIS RESULTS:")
print(f"Patient ID: {patient1_report['patient_id']}")
print()

print("GENOTYPES:")
for gt in patient1_report['genotypes']:
    print(f"  {gt['gene']}: {gt['diplotype']} (Activity Score: {gt['allele1']['activity_score'] + gt['allele2']['activity_score']})")
print()

print("PREDICTED PHENOTYPES:")
for pt in patient1_report['phenotypes']:
    print(f"  {pt['gene']}: {pt['phenotype']} (Activity Score: {pt['activity_score']})")
print()

print("CLINICAL RECOMMENDATIONS:")
for i, rec in enumerate(patient1_report['recommendations'], 1):
    print(f"  {i}. Drug: {rec['drug']}")
    print(f"     Gene: {rec['gene']}")
    print(f"     Patient Phenotype: {rec['patient_phenotype']}")
    print(f"     Recommendation: {rec['recommendation']}")
    print(f"     Strength: {rec['strength']}")
    print(f"     Rationale: {rec['rationale']}")
    if rec['alternative_drugs']:
        print(f"     Alternative Drugs: {', '.join(rec['alternative_drugs'])}")
    if rec['monitoring']:
        print(f"     Monitoring: {rec['monitoring']}")
    print()

print("SUMMARY:")
summary = patient1_report['summary']
print(f"  Genes tested: {summary['total_genes_tested']}")
print(f"  Actionable genes: {summary['actionable_genes']}")
print(f"  High priority recommendations: {summary['high_priority_recommendations']}")
print(f"  Requires intervention: {summary['requires_intervention']}")
print("\n" + "="*50 + "\n")