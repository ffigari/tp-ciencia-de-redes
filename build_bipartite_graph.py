import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ==========================
# 1. Read CSV path from argv
# ==========================
if len(sys.argv) < 2:
    print("Usage: python build_bipartite_graph.py <path_to_csv>")
    sys.exit(1)

csv_path = sys.argv[1]

# ==========================
# 2. Read dataset
# ==========================
try:
    data = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: File '{csv_path}' not found.")
    sys.exit(1)

# ==========================
# 3. Create array of student nodes
# ==========================
students = data["id"].astype(str).tolist()

# ==========================
# 4. Define Attribute classes
# ==========================
class Attribute:
    def getName(self):
        """Return the name of the attribute"""
        raise NotImplementedError

    def matchesStudent(self, student):
        """Return True if this attribute applies to the student"""
        raise NotImplementedError


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
attributes = [HasGoodSleep(), HasBadSleep()]
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
