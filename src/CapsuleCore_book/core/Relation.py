from dataclasses import dataclass


@dataclass(frozen=True)
class Relation:
    from_id: str
    to_id: str
    connection_type: str  # Ejemplo: "referencia", "depende de", "contradicción"