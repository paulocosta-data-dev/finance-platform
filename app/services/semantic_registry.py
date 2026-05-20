from app.seeds.semantic_types import SEMANTIC_TYPES


SEMANTIC_TYPE_MAP = {
    semantic_type.semantic_type_id: semantic_type
    for semantic_type in SEMANTIC_TYPES
}


def get_semantic_type(
    semantic_type_id: str,
):

    return SEMANTIC_TYPE_MAP[semantic_type_id]