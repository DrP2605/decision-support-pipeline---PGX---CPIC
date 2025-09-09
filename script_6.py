# Create comprehensive CSV data export showing the complete pipeline components

# Create CPIC Guidelines Reference Data
cpic_data = []

# CYP2C19 - Clopidogrel guidelines
cpic_data.extend([
    {
        'Gene': 'CYP2C19',
        'Drug': 'clopidogrel',
        'Allele': '*1',
        'Function': 'Normal Function',
        'Activity_Score': 1.0,
        'Phenotype': 'Normal Metabolizer',
        'Recommendation': 'Standard dosing',
        'Strength': 'Strong',
        'Dose_Modification': '75 mg daily'
    },
    {
        'Gene': 'CYP2C19', 
        'Drug': 'clopidogrel',
        'Allele': '*2',
        'Function': 'No Function',
        'Activity_Score': 0.0,
        'Phenotype': 'Poor Metabolizer',
        'Recommendation': 'Consider alternative P2Y12 inhibitor (prasugrel, ticagrelor)',
        'Strength': 'Strong',
        'Dose_Modification': 'Avoid or alternative therapy'
    },
    {
        'Gene': 'CYP2C19',
        'Drug': 'clopidogrel', 
        'Allele': '*17',
        'Function': 'Increased Function',
        'Activity_Score': 1.5,
        'Phenotype': 'Rapid Metabolizer',
        'Recommendation': 'Standard dosing',
        'Strength': 'Strong', 
        'Dose_Modification': '75 mg daily'
    }
])

# DPYD - Fluorouracil guidelines  
cpic_data.extend([
    {
        'Gene': 'DPYD',
        'Drug': '5-fluorouracil',
        'Allele': '*1', 
        'Function': 'Normal Function',
        'Activity_Score': 1.0,
        'Phenotype': 'DPD Normal Activity',
        'Recommendation': 'Standard dosing',
        'Strength': 'Strong',
        'Dose_Modification': 'Standard dose'
    },
    {
        'Gene': 'DPYD',
        'Drug': '5-fluorouracil',
        'Allele': '*2A',
        'Function': 'No Function', 
        'Activity_Score': 0.0,
        'Phenotype': 'DPD Deficiency',
        'Recommendation': 'Avoid 5-fluorouracil and related drugs',
        'Strength': 'Strong',
        'Dose_Modification': 'Contraindicated'
    },
    {
        'Gene': 'DPYD',
        'Drug': '5-fluorouracil',
        'Allele': 'c.2846A>T',
        'Function': 'Decreased Function',
        'Activity_Score': 0.5, 
        'Phenotype': 'DPD Intermediate Activity',
        'Recommendation': 'Start with 50% dose reduction',
        'Strength': 'Strong',
        'Dose_Modification': '50% of standard dose, titrate based on tolerance'
    }
])

# Convert to DataFrame and save
import pandas as pd
cpic_df = pd.DataFrame(cpic_data)
cpic_df.to_csv('cpic_guidelines_reference.csv', index=False)

print("✓ CPIC Guidelines Reference exported to 'cpic_guidelines_reference.csv'")
print(f"✓ Total guidelines entries: {len(cpic_data)}")
print("✓ Genes covered: CYP2C19, DPYD") 
print("✓ Drugs covered: clopidogrel, 5-fluorouracil")
print()

# Create example patient test data
patient_examples = [
    {
        'Patient_ID': 'PAT001',
        'CYP2C19_Genotype': '*2/*2',
        'DPYD_Genotype': '*1/*1',
        'CYP2C19_Phenotype': 'Poor Metabolizer',
        'DPYD_Phenotype': 'DPD Normal Activity', 
        'Requested_Drugs': 'clopidogrel',
        'High_Priority_Alerts': 1,
        'Requires_Intervention': True
    },
    {
        'Patient_ID': 'PAT002',
        'CYP2C19_Genotype': '*1/*17',
        'DPYD_Genotype': '*2A/*1', 
        'CYP2C19_Phenotype': 'Rapid Metabolizer',
        'DPYD_Phenotype': 'DPD Intermediate Activity',
        'Requested_Drugs': '5-fluorouracil,clopidogrel',
        'High_Priority_Alerts': 1,
        'Requires_Intervention': True
    },
    {
        'Patient_ID': 'PAT003',
        'CYP2C19_Genotype': '*1/*1',
        'DPYD_Genotype': '*1/*1',
        'CYP2C19_Phenotype': 'Normal Metabolizer', 
        'DPYD_Phenotype': 'DPD Normal Activity',
        'Requested_Drugs': 'clopidogrel',
        'High_Priority_Alerts': 0,
        'Requires_Intervention': False
    }
]

patient_df = pd.DataFrame(patient_examples)
patient_df.to_csv('example_patients.csv', index=False)

print("✓ Example patient data exported to 'example_patients.csv'")
print(f"✓ Total patient examples: {len(patient_examples)}")
print("✓ Includes normal, actionable, and high-risk scenarios")