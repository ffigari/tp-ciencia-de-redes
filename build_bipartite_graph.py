import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ==========================
# 1. Read CSV path and optional sample percentage from argv
# ==========================
if len(sys.argv) < 2:
    print("Usage: python build_bipartite_graph.py <path_to_csv> [sample_percentage]")
    sys.exit(1)

csv_path = sys.argv[1]

# Default sample percentage = 100%
sample_percentage = 100
if len(sys.argv) >= 3:
    try:
        sample_percentage = float(sys.argv[2])
        if not (0 <= sample_percentage <= 100):
            raise ValueError
    except ValueError:
        print("Error: sample_percentage must be a number between 0 and 100")
        sys.exit(1)

# ==========================
# 2. Read dataset
# ==========================
try:
    data = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: File '{csv_path}' not found.")
    sys.exit(1)

# ==========================
# 3. Sample students if needed
# ==========================
if sample_percentage < 100:
    data = data.sample(frac=sample_percentage / 100, random_state=42).reset_index(drop=True)

students = data["id"].astype(str).tolist()

# ==========================
# 4. Define Attribute classes
# ==========================
class Attribute:
    def getName(self):
        raise NotImplementedError

    def matchesStudent(self, student):
        raise NotImplementedError

# Función auxiliar para normalizar valores
def normalize_value(value):
    """Normaliza cualquier valor del dataset"""
    if value is None:
        return None
    return str(value).strip().lower().replace("'", "").replace('"', '')

# ===== Género =====

class IsFemale(Attribute):
    def getName(self):
        return "Gender_Female"

    def matchesStudent(self, student):
        gender = normalize_value(student["Gender"])
        return gender == "female"

class IsMale(Attribute):
    def getName(self):
        return "Gender_Male"

    def matchesStudent(self, student):
        gender = normalize_value(student["Gender"])
        return gender == "male"

# ===== Edad =====

class IsYoung(Attribute):
    def getName(self):
        return "Age_Young"
    
    def matchesStudent(self, student):
        try:
            age = float(student["Age"])
            return 17 < age < 25
        except (ValueError, TypeError):
            return False

class IsYoungAdult(Attribute):
    def getName(self):
        return "Age_Young_Adult"
    
    def matchesStudent(self, student):
        try:
            age = float(student["Age"])
            return 24 < age < 40
        except (ValueError, TypeError):
            return False
        
class IsAdult(Attribute):
    def getName(self):
        return "Age_Adult"
    
    def matchesStudent(self, student):
        try:
            age = float(student["Age"])
            return age >= 40
        except (ValueError, TypeError):
            return False
        
# ===== Presión Académica =====

class HasLowAcademicPressure(Attribute):
    def getName(self):
        return "Low_Academic_Pressure"
    
    def matchesStudent(self, student):
        try:
            academicPressure = float(student["Academic Pressure"])
            return academicPressure < 3.0
        except (ValueError, TypeError):
            return False

class HasMediumAcademicPressure(Attribute):
    def getName(self):
        return "Medium_Academic_Pressure"
    
    def matchesStudent(self, student):
        try:
            academicPressure = float(student["Academic Pressure"])
            return academicPressure == 3.0
        except (ValueError, TypeError):
            return False

class HasHighAcademicPressure(Attribute):
    def getName(self):
        return "High_Academic_Pressure"
    
    def matchesStudent(self, student):
        try:
            academicPressure = float(student["Academic Pressure"])
            return academicPressure > 3.0
        except (ValueError, TypeError):
            return False

# ===== CGPA =====


# ===== Satisfacción académica =====

class HasLowStudySatisfaction(Attribute):
    def getName(self):
        return "Low_Study_Satisfaction"
    
    def matchesStudent(self, student):
        try:
            studySatisfaction = float(student["Study Satisfaction"])
            return studySatisfaction < 3.0
        except (ValueError, TypeError):
            return False

class HasMediumStudySatisfaction(Attribute):
    def getName(self):
        return "Medium_Study_Satisfaction"
    
    def matchesStudent(self, student):
        try:
            studySatisfaction = float(student["Study Satisfaction"])
            return studySatisfaction == 3.0
        except (ValueError, TypeError):
            return False

class HasHighStudySatisfaction(Attribute):
    def getName(self):
        return "High_Study_Satisfaction"
    
    def matchesStudent(self, student):
        try:
            studySatisfaction = float(student["Study Satisfaction"])
            return studySatisfaction > 3.0
        except (ValueError, TypeError):
            return False

# ===== Sueño =====

class HasGoodSleep(Attribute):
    def getName(self):
        return "HasGoodSleep"

    def matchesStudent(self, student):
        sleep = str(student["Sleep Duration"]).strip().replace("'", "")
        return sleep in ["7-8 hours", "More than 8 hours"]


class HasBadSleep(Attribute):
    def getName(self):
        return "HasBadSleep"

    def matchesStudent(self, student):
        sleep = str(student["Sleep Duration"]).strip().replace("'", "")
        return sleep in ["Less than 5 hours", "5-6 hours"]


# ==========================
# 5. Instantiate attribute objects
# ==========================
attributes = [HasGoodSleep(), HasBadSleep(), IsFemale(), IsMale(), IsYoung(), IsYoungAdult(), IsAdult(), HasLowAcademicPressure(), HasMediumAcademicPressure(), HasHighAcademicPressure(), HasLowStudySatisfaction(), HasMediumStudySatisfaction(), HasHighStudySatisfaction()]
attribute_nodes = [attr.getName() for attr in attributes]

# ==========================
# 6. Build the bipartite graph
# ==========================
B = nx.Graph()
B.add_nodes_from(students, bipartite=0)
B.add_nodes_from(attribute_nodes, bipartite=1)

edges = []
for _, student in data.iterrows():
    student_id = str(student["id"])
    for attr in attributes:
        if attr.matchesStudent(student):
            edges.append((student_id, attr.getName()))

B.add_edges_from(edges)

# ==========================
# 7. Print summary
# ==========================
print("\n--- Bipartite Graph Summary ---")
print(f"Total nodes: {B.number_of_nodes()}")
print(f"Total edges: {B.number_of_edges()}")
print(f"Sample students: {students[:5]}")
print(f"Attributes: {attribute_nodes}")
print(f"Is bipartite: {nx.is_bipartite(B)}")

# ==========================
# 8. Visualize the graph
# ==========================

plt.figure(figsize=(10, 6))

# Usar layout bipartito para separar los dos conjuntos
pos = nx.bipartite_layout(B, students)

# Separar nodos por su atributo bipartito
top_nodes = students
bottom_nodes = attribute_nodes

# Dibujar nodos de cada conjunto con diferentes colores
nx.draw_networkx_nodes(
    B,
    pos,
    nodelist=top_nodes,
    node_color="lightblue",
    node_size=800,
    label="Students",
)
nx.draw_networkx_nodes(
    B,
    pos,
    nodelist=bottom_nodes,
    node_color="lightgreen",
    node_size=800,
    label="Attributes",
)

# Dibujar aristas y etiquetas
nx.draw_networkx_edges(B, pos, edge_color="gray", width=1.5)
nx.draw_networkx_labels(B, pos, font_size=8, font_weight="bold")

plt.title("Bipartite Graph: Students and Attributes", fontsize=14, fontweight="bold")
plt.legend(scatterpoints=1, loc="upper right")
plt.axis("off")
plt.tight_layout()
plt.savefig("bipartite_graph.png", dpi=300)
print("Graph saved to 'bipartite_graph.png'")
