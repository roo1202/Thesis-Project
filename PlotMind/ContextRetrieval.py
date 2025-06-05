# from sentence_transformers import SentenceTransformer

# # Descargar 'all-mpnet-base-v2' (768-dim)
# model_mpnet = SentenceTransformer('all-mpnet-base-v2')

# # Descargar 'e5-large-v2' (1024-dim, de Microsoft)
# model_e5 = SentenceTransformer('intfloat/e5-large-v2')

# embeddings_mpnet = model_mpnet.encode("Ejemplo de evento narrativo")
# embeddings_e5 = model_e5.encode("query: Ejemplo de evento narrativo")  # 'e5' requiere prefijo "query:"

# print(f"all-mpnet-base-v2: {embeddings_mpnet.shape}")  # (768,)
# print(f"e5-large-v2: {embeddings_e5.shape}")           # (1024,)

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Union, Optional
import faiss
from functools import lru_cache
from sklearn.cluster import DBSCAN

from StorySpace.Event import Event

class ContextRetrieval:
    def __init__(self, 
                 model_name: str = 'intfloat/e5-large-v2',
                 faiss_index_size: int = 1024,
                 cache_size: int = 1000):
        """
        Inicializa el sistema de recuperación de contexto con embeddings.
        
        Args:
            model_name: Nombre del modelo de embeddings
            faiss_index_size: Dimensión de los embeddings
            cache_size: Tamaño máximo de la caché LRU
        """
        
        self.model = SentenceTransformer(model_name)
        self.model.max_seq_length = 512  
        
        # Configurar FAISS
        self.index = faiss.IndexFlatIP(faiss_index_size)  
        self.faiss_id_to_event = {}
        self.current_id = 0
        
        # Metadatos y caché
        # self.metadata: Dict[int, Dict] = {}
        self.cache = lru_cache(maxsize=cache_size)
        
        # Normalizar embeddings para cosine similarity
        self.do_normalize = True if "e5" in model_name else False
    
    def add_events(self, events: List[Event]) -> None:
        """
        Añade eventos con metadatos opcionales.
        
        Args:
            events: Lista de strings con los eventos
            metadata_list: Lista de diccionarios con metadatos
        """
        try:
            if not events:
                return
                
            processed_events = [f"passage: {event.description}" for event in events]
            
            # Generación de embeddings
            embeddings = self.model.encode(processed_events, 
                                        convert_to_tensor=False,
                                        normalize_embeddings=self.do_normalize)
            
            # Conversión y validación de embeddings
            embeddings = np.array(embeddings).astype('float32')
            if len(embeddings.shape) != 2:
                raise ValueError("Embeddings debe ser matriz 2D")
                
            # Añadir a FAISS
            start_id = self.current_id
            self.index.add(embeddings)
            
            # Almacenar metadatos
            for i in range(len(events)):
                self.faiss_id_to_event[start_id + i] = {
                    "text": events[i].description,
                    "embedding": embeddings[i],
                    "metadata": events[i].to_dict()
                }
                
            self.current_id += len(events)
            
        except Exception as e:
            print(f"Error añadiendo eventos: {str(e)}")
            raise
    
    def _query_processing(self, query: Union[str, List[str]]) -> np.ndarray:
        """Obtiene el embedding para una consulta (puede ser un evento o lista de eventos)"""
        if "e5" in self.model._get_name():
            if isinstance(query, list):
                processed = [f"query: {q}" for q in query]
            else:
                processed = [f"query: {query}"]

            return self.model.encode(processed, 
                              convert_to_tensor=False, 
                              normalize_embeddings=self.do_normalize)
        else :
            if isinstance(query, list):
                # Promediar los embeddings si es una lista de eventos
                embeddings = self.model.encode(query, convert_to_tensor=False)
                return np.mean(embeddings, axis=0)
            else:
                return self.model.encode(query, convert_to_tensor=False)
            
        
    @lru_cache(maxsize=1000)
    def retrieve_similar_events(self, 
                              query: Union[str, List[str]], 
                              k: int = 5,
                              filter_func: Optional[callable] = None) -> List[Dict]:
        """
        Encuentra los k eventos más similares a la consulta.
        
        Args:
            query: Consulta o lista de consultas
            k: Número de resultados a devolver
            filter_func: Función para filtrar por metadatos (e.g., lambda m: m['type'] == 'battle')
            
        Returns:
            Lista de resultados con texto, similitud y metadatos
        """
        # Generar embedding de consulta
        query_embedding = self._query_processing(query)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # Búsqueda en FAISS
        distances, indices = self.index.search(query_embedding, k)
        
        # Procesar resultados
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0:
                continue  # Índice inválido en FAISS
                
            event_data = self.faiss_id_to_event.get(idx)
            if event_data:
                # Aplicar filtro de metadatos
                if filter_func and not filter_func(event_data['metadata']):
                    continue
                    
                results.append({
                    "text": event_data['text'],
                    "similarity": float(distance),
                    "metadata": event_data['metadata']
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:k]
    
    def get_context(self, 
                  events: List[str], 
                  k: int = 5, 
                  m: int = 3,
                  filter_rules: Optional[Dict] = None) -> List[Dict]:
        """
        Obtiene el contexto relevante para una lista de eventos.
        
        Args:
            events: Lista de eventos para los que se necesita contexto
            k: Número de eventos contextuales a recuperar
            m: Límite para usar recuperación semántica
            filter_rules: Diccionario con reglas de filtrado (e.g., {'type': 'conflicto', 'location': 'forest'})
        """
        # Construir función de filtrado
        filter_func = None
        if filter_rules:
            filter_func = lambda meta: all(
                meta.get(key) == value for key, value in filter_rules.items()
            )
        
        if len(events) <= m:
            return [{"text": e} for e in events]
            
        return self.retrieve_similar_events(tuple(events), k=k, filter_func=filter_func)
    
    def save_index(self, filename: str):
        """Guarda el índice FAISS en disco"""
        faiss.write_index(self.index, filename)
    
    def load_index(self, filename: str):
        """Carga un índice FAISS desde disco"""
        self.index = faiss.read_index(filename)
    
    def __len__(self) -> int:
        return self.index.ntotal


    def get_clusters(self, min_samples: int) -> dict:
        """
        Agrupa eventos temáticamente similares usando DBSCAN.
        
        Args:
            min_samples: Mínimo número de eventos para formar un cluster.
        
        Returns:
            Dict con:
            - 'labels': Array de clusters asignados (-1 es ruido)
            - 'n_clusters': Número de clusters encontrados
            - 'avg_distance': Distancia promedio usada como eps
            - 'cluster_details': Dict con metadatos por cluster
        """
        try:
            # 1. Obtener embeddings como array numpy
            all_data = list(self.faiss_id_to_event.values())
            embeddings = np.array([data['embedding'] for data in all_data]).astype('float32')
            
            if len(embeddings) == 0:
                return {'labels': [], 'n_clusters': 0, 'avg_distance': 0.0, 'cluster_details': {}}
            
            # 2. Calcular eps como distancia promedio entre puntos cercanos (más robusto)
            from sklearn.neighbors import NearestNeighbors
            neigh = NearestNeighbors(n_neighbors=2)
            neigh.fit(embeddings)
            distances, _ = neigh.kneighbors(embeddings)
            avg_distance = np.mean(distances[:, 1])  # Distancia al vecino más cercano
            
            # 3. Aplicar DBSCAN
            clustering = DBSCAN(
                eps=avg_distance * 1.5,  # Ajuste heurístico
                min_samples=min_samples,
                metric='euclidean'
            ).fit(embeddings)
            
            # 4. Procesar resultados
            labels = clustering.labels_
            unique_labels = set(labels)
            n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
            
            # 5. Generar metadatos por cluster
            cluster_details = {}
            for label in unique_labels:
                if label == -1:
                    continue
                    
                cluster_indices = np.where(labels == label)[0]
                cluster_events = [all_data[i]['metadata'] for i in cluster_indices]
                
                cluster_details[label] = {
                    'size': len(cluster_events),
                    'sample_titles': [e['title'][:50] + "..." for e in cluster_events[:3]],
                    'avg_similarity': np.mean([
                        np.dot(embeddings[i], embeddings[j])
                        for i in cluster_indices
                        for j in cluster_indices if i != j
                    ])
                }
            
            return {
                'labels': labels,
                'n_clusters': n_clusters,
                'avg_distance': avg_distance,
                'cluster_details': cluster_details
            }
            
        except Exception as e:
            print(f"Error en clustering: {str(e)}")
            raise
        

    def _get_cluster_details(self, labels: np.ndarray) -> dict:
        """Genera metadatos descriptivos para cada cluster"""
        cluster_details = {}
        for label in set(labels):
            if label == -1:
                continue
                
            # Obtener eventos del cluster
            cluster_events = [
                self.faiss_id_to_event[i]['metadata']
                for i, l in enumerate(labels) if l == label
            ]
            
            # Estadísticas básicas
            cluster_details[label] = {
                'size': len(cluster_events),
                'sample_titles': [e['title'][:50] for e in cluster_events[:3]],
                'common_themes': self._extract_common_themes(cluster_events)
            }
        return cluster_details

    def _extract_common_themes(self, events: list) -> list:
        """Extrae temas comunes usando los embeddings (simplificado)"""
        if not events:
            return []
        
        # Usar el primer evento como referencia
        base_embedding = events[0]['embedding']
        similarities = [
            np.dot(base_embedding, e['embedding'])
            for e in events[1:]
        ]
        
        if np.mean(similarities) > 0.7:  # Umbral alto para temas muy similares
            return ["Tema principal: " + events[0]['title'][:30]]
        
        return ["Múltiples subtemas"]