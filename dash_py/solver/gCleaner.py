#import os
#os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
from graphviz import Source
from utils.env import PATH_AUTOMATON, PATH_AUTOMATON_CLEANED
import pydot

class gCleaner():
    def __init__(self, graph_dot_path: str = PATH_AUTOMATON) -> None:
        self.cleaned_dot_graph = self.remove_failures_from_graph(graph_dot_path)
        self.cleaned_dot_graph = self.save_cleaned_dot_graph(PATH_AUTOMATON_CLEANED)

    def remove_failures_from_graph(self, path):
        dot_code = ""
        with open(path, 'r') as file:
            for line in file.readlines():
                if not ("label" in line and "/-1" in line):
                    dot_code+=line
        return dot_code
    
    def save_cleaned_dot_graph(self, dot_path):
        with open(dot_path, 'w') as file:
            file.write(self.cleaned_dot_graph)

    def save_cleaned_pdf_graph(self, pdf_path):
        graph = Source(self.cleaned_dot_graph, format='pdf')
        graph.render(pdf_path, cleanup=True)

    def remove_null_nodes_from_graph(self, graph_dot_path = PATH_AUTOMATON_CLEANED):        
        # Load the graph from a file
        graphs = pydot.graph_from_dot_file(graph_dot_path)
        graph = graphs[0]
        #print(graph)
        # Get all nodes
        nodes_graph = graph.get_nodes()
        # Get all edges
        edges = graph.get_edges()
        # Set to store nodes
        nodes = set()
        # Print edges
        for edge in edges:
            #print(f"edge in graph cleaned {edge}")
            # Get source and destination nodes
            source_node = edge.get_source()
            destination_node = edge.get_destination()
            # Add nodes to the set
            nodes.add(source_node)
            nodes.add(destination_node)
        #Iterate over all nodes
        for node in nodes_graph:            
            if node.get_name() not in nodes:
                # Remove the node
                graph.del_node(node.get_name())
                print(f"node {node} has no edges")
        graph.write(PATH_AUTOMATON_CLEANED)