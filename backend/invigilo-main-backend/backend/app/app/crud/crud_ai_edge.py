from typing import Dict, List, Tuple, TypedDict
from app import crud
from app.models.ai_vertex import AI_Vertex
from app.schemas.ai_edge import AI_EdgeCreate

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.ai_edge import AI_Edge
from app.schemas.ai_edge import AI_EdgeCreate, AI_EdgeUpdate
from app.schemas.ai_vertex import AI_VertexCreate


class UniqueEdge(TypedDict):
    source_id: int
    destination_id: int


class CRUD_AI_Edge(CRUDBase[AI_Edge, AI_EdgeCreate, AI_EdgeUpdate]):
    def __format_vertexes(
        self,
        vertexes: List[AI_VertexCreate],
        ai_vertexes: Dict[int, AI_Vertex]
    ) -> List[UniqueEdge]:
        ai_edges = []
        for vertex in vertexes:
            source = []
            destination = []
            if vertex.source:
                source = vertex.source
            if vertex.destination:
                destination = vertex.destination

            # vertexes without a source is entries in sequence
            if not source:
                ai_edges.append({
                    'source_id': None,
                    'destination_id': ai_vertexes[vertex.unique_id].id
                })
            else:
                for src in source:
                    if src:
                        source_id = ai_vertexes[src].id
                    else:
                        source_id = None
                    ai_edges.append({
                        'source_id': source_id,
                        'destination_id': ai_vertexes[vertex.unique_id].id
                    })
            for dest in destination:
                if not dest:
                    continue
                ai_edges.append({
                    'source_id': ai_vertexes[vertex.unique_id].id,
                    'destination_id': ai_vertexes[dest].id
                })

        unique_ai_edges = []
        # exclude circular dependence, and duplicates when used in both `source` and `destination`
        for edge in ai_edges:
            found = list(filter(lambda x: (
                x['source_id'] == edge['source_id'] and
                x['destination_id'] == edge['destination_id'] or
                x['source_id'] == edge['destination_id'] and
                x['destination_id'] == edge['source_id']
            ), unique_ai_edges))
            if not found:
                unique_ai_edges.append(edge)

        return unique_ai_edges

    def create_multiple(
        self, db: Session,
        sequence_id: int,
        vertexes: List[AI_VertexCreate],
        ai_vertexes: Dict[int, AI_Vertex]
    ) -> Tuple[Dict[int, AI_Edge], List[AI_Edge]]:
        unique_ai_edges = self.__format_vertexes(vertexes, ai_vertexes)
        ai_edges_results = []
        for ai_edge in unique_ai_edges:
            ai_edges_results.append(super().create(db, obj_in=AI_EdgeCreate(
                sequence_id=sequence_id,
                source_id=ai_edge['source_id'],
                destination_id=ai_edge['destination_id'],
            )))

        return (unique_ai_edges, ai_edges_results)

    def update_multiple(
        self, db: Session,
        sequence_id: int,
        vertexes: List[AI_VertexCreate],
        ai_vertexes: Dict[int, AI_Vertex],
        old_edges: List[AI_Edge]
    ) -> Tuple[Dict[int, AI_Edge], List[AI_Edge]]:
        unique_ai_edges = self.__format_vertexes(vertexes, ai_vertexes)
        ai_edges_results = []
        delete_edges = []
        for edge in old_edges:
            found = list(filter(lambda x: (
                x['source_id'] == edge.source_id and
                x['destination_id'] == edge.destination_id
            ), unique_ai_edges))
            if found:
                unique_ai_edges.remove(found[0])
            else:
                delete_edges.append(edge)

        for old_edge in delete_edges:
            crud.ai_edge.remove(db, id=old_edge.id)

        for ai_edge in unique_ai_edges:
            ai_edges_results.append(super().create(db, obj_in=AI_EdgeCreate(
                sequence_id=sequence_id,
                source_id=ai_edge['source_id'],
                destination_id=ai_edge['destination_id'],
            )))

        return (unique_ai_edges, ai_edges_results)


ai_edge = CRUD_AI_Edge(AI_Edge)
