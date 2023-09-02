import numpy as np
import pandas as pd
from semopy import Model
import networkx as nx
import matplotlib.pyplot as plt

# Simulate data
np.random.seed(42)
num_patients = 500
doac_treatment = np.random.binomial(1, 0.5, num_patients)
warfarin_treatment = np.random.binomial(1, 0.5, num_patients)
no_coagulation_treatment = 1 - doac_treatment - warfarin_treatment

high_bmi = np.random.binomial(1, 0.5, num_patients)
high_sbp = np.random.binomial(1, 0.5, num_patients)

mca_infarcts = (
    1 - doac_treatment + np.random.normal(0, 0.5, num_patients)
)
hemorrhagic_processes = (
    (doac_treatment + warfarin_treatment) * (high_bmi + high_sbp) +
    np.random.normal(0, 0.5, num_patients)
)

df = pd.DataFrame({
    'DOAC_Treatment': doac_treatment,
    'Warfarin_Treatment': warfarin_treatment,
    'No_Coagulation_Treatment': no_coagulation_treatment,
    'MCA_Infarcts': mca_infarcts,
    'Hemorrhagic_Processes': hemorrhagic_processes,
    'High_BMI': high_bmi,
    'High_SBP': high_sbp
})

# Specify model
model_spec = """
MCA_Infarcts ~ DOAC_Treatment + Warfarin_Treatment + No_Coagulation_Treatment
Hemorrhagic_Processes ~ DOAC_Treatment + Warfarin_Treatment + High_BMI + High_SBP + MCA_Infarcts
"""

model = Model(model_spec)
model.fit(df)

# Results
results = model.inspect()
print(results)

# Intuitive Presentation of Results
print("Intuitive Presentation of Results:")
for _, row in results.iterrows():
    if row['op'] == '~':
        print(f"{row['lval']} is influenced by {row['rval']} with an estimate of {row['Estimate']:.2f} (p={row['p-value']:.4f})")

# Visualize the model paths
G = nx.DiGraph()

# Add nodes
variables = ["DOAC_Treatment", "Warfarin_Treatment", "No_Coagulation_Treatment",
             "MCA_Infarcts", "Hemorrhagic_Processes", "High_BMI", "High_SBP"]
node_labels = {
    "DOAC_Treatment": "DOACs",
    "Warfarin_Treatment": "Warfarin",
    "No_Coagulation_Treatment": "No Anti-Coag",
    "MCA_Infarcts": "MCA Infarcts",
    "Hemorrhagic_Processes": "Hemorrhage",
    "High_BMI": "High BMI",
    "High_SBP": "High SBP"
}
G.add_nodes_from(variables)

# Add edges based on paths
for _, row in results.iterrows():
    if row['op'] == '~':
        G.add_edge(row['rval'], row['lval'], weight=row['Estimate'], label=f"{row['Estimate']:.2f}")

# Layout for visualization
pos = {
    "DOAC_Treatment": np.array([0, 1]),
    "Warfarin_Treatment": np.array([-1, 0]),
    "No_Coagulation_Treatment": np.array([0, 0]),
    "MCA_Infarcts": np.array([-1, -1]),
    "Hemorrhagic_Processes": np.array([1, -1]),
    "High_BMI": np.array([2, 1]),
    "High_SBP": np.array([2, -1])
}

plt.figure(figsize=(12, 11))

# Draw nodes with custom labels
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="lightblue")
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12)

# Draw edges with arrows
edges = nx.draw_networkx_edges(G, pos, width=[d['weight']*2 for _, _, d in G.edges(data=True)], 
                               edge_color="gray", arrows=True, node_size=4000, 
                               arrowstyle='-|>', arrowsize=20)

# Draw edge labels with adjusted positions
edge_labels = nx.get_edge_attributes(G, 'label')
label_pos = {}
for k, v in pos.items():
    label_pos[k] = [v[0], v[1] - 0.2]
nx.draw_networkx_edge_labels(G, label_pos, edge_labels=edge_labels, font_size=10, font_color="red")

plt.title("Structural Equation Modeling Paths", size=18)
plt.axis("off")
plt.tight_layout()
plt.savefig('sem_AntiCoagulants_Remy_Cohan.png', format='png', dpi=300, bbox_inches='tight')
plt.show()


