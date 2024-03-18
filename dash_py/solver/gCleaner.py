#import os
#os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
from graphviz import Source

class gCleaner():
    def __init__(self, graph_dot_path: str = "automaton.dot") -> None:
        self.cleaned_dot_graph = self.remove_failures_from_graph(graph_dot_path)

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

