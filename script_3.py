# Patient 2: DPYD deficiency requiring 5-fluorouracil

patient2_genotypes = {
    "DPYD": "*2A/*1",  # Intermediate activity (heterozygous for no-function allele)
    "CYP2C19": "*1/*17"  # Normal/rapid metabolizer
}

patient2_drugs = ["5-fluorouracil", "clopidogrel"]

print("=== PATIENT 2 EXAMPLE ===")
print(f"Genotype: {patient2_genotypes}")
print(f"Requested drugs: {patient2_drugs}")
print()

patient2_report = pgx_system.process_patient("PAT002", patient2_genotypes, patient2_drugs)

print("ANALYSIS RESULTS:")
print(f"Patient ID: {patient2_report['patient_id']}")
print()

print("GENOTYPES:")
for gt in patient2_report['genotypes']:
    print(f"  {gt['gene']}: {gt['diplotype']} (Activity Score: {gt['allele1']['activity_score'] + gt['allele2']['activity_score']})")
print()

print("PREDICTED PHENOTYPES:")
for pt in patient2_report['phenotypes']:
    print(f"  {pt['gene']}: {pt['phenotype']} (Activity Score: {pt['activity_score']})")
print()

print("CLINICAL RECOMMENDATIONS:")
for i, rec in enumerate(patient2_report['recommendations'], 1):
    print(f"  {i}. Drug: {rec['drug']}")
    print(f"     Gene: {rec['gene']}")
    print(f"     Patient Phenotype: {rec['patient_phenotype']}")
    print(f"     Recommendation: {rec['recommendation']}")
    print(f"     Strength: {rec['strength']}")
    print(f"     Rationale: {rec['rationale']}")
    if rec['alternative_drugs']:
        print(f"     Alternative Drugs: {', '.join(rec['alternative_drugs'])}")
    if rec['dose_modification']:
        print(f"     Dose Modification: {rec['dose_modification']}")
    if rec['monitoring']:
        print(f"     Monitoring: {rec['monitoring']}")
    print()

print("SUMMARY:")
summary = patient2_report['summary']
print(f"  Genes tested: {summary['total_genes_tested']}")
print(f"  Actionable genes: {summary['actionable_genes']}")
print(f"  High priority recommendations: {summary['high_priority_recommendations']}")
print(f"  Requires intervention: {summary['requires_intervention']}")
print("\n" + "="*50 + "\n")