import networkx as nx

class DependencyManager():
    """
    Clase para gestionar dependencias entre eventos en un grafo.
    
    Esta clase permite establecer dependencias y validar secuencias de eventos.
    """
    
    def is_multidigraph_dag(multidigraph):
        """
        Comprueba si un MultiDiGraph es un DAG (Grafo Acíclico Dirigido).
        
        Args:
            multidigraph (nx.MultiDiGraph): Grafo dirigido con múltiples aristas.
        
        Returns:
            bool: True si es un DAG, False si contiene ciclos.
        """
        # Convertimos el MultiDiGraph a un DiGraph simple (ignorando múltiples aristas)
        simple_digraph = nx.DiGraph(multidigraph)
        
        # Verificamos si el grafo simple es acíclico
        return nx.is_directed_acyclic_graph(simple_digraph)
    
    