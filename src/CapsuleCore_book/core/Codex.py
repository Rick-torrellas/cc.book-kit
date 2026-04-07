from typing import List
from datetime import datetime
from dataclasses import replace
from typing import Any, Optional

from .Entry import Entry
from .Relation import Relation
from .CodexPolicy import CodexPolicy
from ..capsule import Lexicon


class Codex:
    def __init__(self, repository: Lexicon, policy: CodexPolicy = CodexPolicy()):
        self.repository = repository
        self.policy = policy

    def create_entry(
        self,
        title: str,
        content: str,
        tags: List[str] = None,
        category: str = None,
        **kwargs,
    ) -> Entry:

        clean_title = self._rules_title(title)
        clean_tags = self._rules_tags(tags or [])
        clean_category = self._rules_category(category)

        new_entry = Entry(
            title=clean_title,
            content=content,
            tags=clean_tags,
            category=clean_category,
            metadata=kwargs.get("metadata", {}),
        )

        self.repository.save(new_entry)

        return new_entry

    def create_relation(
        self, from_id: str, to_id: str, connection_type: str = "relation", **kwargs
    ) -> Relation:

        # 1 obtiene de la base a las entrys from y to, dos puntos relacionados
        # 2 si no encuentra una relacion entre las entradadas lanza un error
        # 3 crea la clase, la guarda en la base de datos y la retorna

        # 1
        origin = self.repository.get_by_id(from_id)
        target = self.repository.get_by_id(to_id)

        # 2
        if not origin or not target:
            missing = []
            if not origin:
                missing.append(f"Origen({from_id})")  # noqa: E701
            if not target:
                missing.append(f"Destino({to_id})")  # noqa: E701
            raise ValueError(
                f"No se puede crear la relación. Faltan: {', '.join(missing)}"
            )

        clean_type = connection_type.strip().lower() or "relation"

        # 3
        new_relation = Relation(
            from_id=origin.id,
            to_id=target.id,
            connection_type=clean_type,
            metadata=kwargs.get("metadata", {}),
        )

        if self.repository.check_relation(new_relation):
            raise ValueError(
                f"Ya existe una relación entre {from_id} y {to_id} con tipo '{clean_type}'"
            )

        self.repository.save_relation(new_relation)
        return new_relation

    def edit_entry(self, entry_id: str, **changes) -> Entry:
        existing = self.repository.get_by_id(entry_id)
        if not existing:
            raise ValueError(f"No se encontró la entrada con ID {entry_id}")

        # Definimos qué campos NO puede tocar el usuario bajo ninguna circunstancia
        IMMUTABLE_FIELDS = {"id", "created_at", "updated_at"}

        verified_changes = {}
        for field, new_val in changes.items():
            # Solo procesamos si el campo existe Y no es un campo protegido
            if hasattr(existing, field) and field not in IMMUTABLE_FIELDS:
                processed_value = self._process_field_change(field, new_val, existing)

                if processed_value is not None:
                    # Aseguramos ruptura de referencia para mutables (tu filosofía de recipiente vacío)
                    if isinstance(processed_value, (list, dict)):
                        processed_value = type(processed_value)(processed_value)

                    verified_changes[field] = processed_value

        # NORMA: Si no hay cambios reales en los datos, retornamos el original (no sube el updated_at)
        if not verified_changes:
            return existing

        # NORMA: El timestamp lo genera Codex, nadie más.
        verified_changes["updated_at"] = datetime.now()

        # Crear nueva instancia
        updated_entry = replace(existing, **verified_changes)
        self.repository.save(updated_entry)

        return updated_entry

    def delete_entry(self, entry_id: str) -> bool:
        # 1 verifica que el 1d exista
        # 2 busca en la base de datos si existe el entry, si no existe devuelve False, rettorna un bool como resultado de la operacion de la consulta de borrado.

        # 1
        if not entry_id or not isinstance(entry_id, str):
            raise ValueError(
                "Se requiere un ID de entrada válido (string) para eliminar."
            )

        # 2
        existing = self.repository.get_by_id(entry_id)
        if not existing:
            return False
        return self.repository.delete(entry_id)

    def disconnect_entries(
        self, from_id: str, to_id: str, connection_type: Optional[str] = None
    ) -> bool:
        # 1 intenta desconectar las entys devuelve un bool, manteniendo la consistencia con delete

        # 1
        success = self.repository.delete_relation(from_id, to_id, connection_type)
        return success

    def groupBy_backRelations(self, entry_id: str) -> List[Entry]:
        # 1 busca en la base de datos la relaciones internas a entry id
        # 2 si no encuentra relaciones devuelve una lista vacia
        # 3 lista los id de las entradas relacionadas a entry id
        # 4 busca en la base de datos una lista de entrys relacionadas a entry id, usando la lista id creada en 3 y lo retorna

        # 1
        relations = self.repository.get_in_relations(entry_id)

        # 2
        if not relations:
            return []

        # 3
        origin_ids = list({rel.from_id for rel in relations})
        return self.repository.get_by_ids(origin_ids)

    def groupBy_relations(self, entry_id: str) -> List[Entry]:
        """
        Recupera todas las entradas conectadas (entrantes o salientes)
        sin duplicados, tratando la relación como bidireccional.
        """
        # 1. Obtenemos IDs de ambos sentidos simultáneamente
        # Usamos un set comprehensions para mayor velocidad y limpieza
        out_ids = {rel.to_id for rel in self.repository.get_out_relations(entry_id)}
        in_ids = {rel.from_id for rel in self.repository.get_in_relations(entry_id)}

        # 2. Unión de conjuntos: Esto elimina duplicados automáticamente
        # Si un ID está en ambos (entrada y salida), solo quedará una vez.
        all_related_ids = out_ids.union(in_ids)

        # 3. Control de lista vacía
        if not all_related_ids:
            return []

        # 4. Retornamos los objetos Entry finales
        return self.repository.get_by_ids(list(all_related_ids))

    def groupBy_frontRelations(self, entry_id: str) -> List[Entry]:
        # 1 busca en la basce de datos las relaciones externas a entry id
        # 2 si no encuentra relaciones devuelve una lista vacia
        # 3 lista los id de las entradas relacionadas a entry id
        # 4 busca en la base de datos una lista de entrys relacionadas a entry id, usando la lista id creada en 3 y lo retorna

        # 1
        relations = self.repository.get_out_relations(entry_id)

        if not relations:
            return []

        # 2
        origin_ids = list({rel.to_id for rel in relations})

        # 3

        # 4
        return self.repository.get_by_ids(origin_ids)

    def groupBy_tags(self, tag: str) -> List[Entry]:
        # 1 si no le pasan el parametro tag te devuelve una lista vacia
        # 2 le limpia el parametro tag
        # 3 retorna una lista de entrys relacionadas a un tag

        # 1
        if not tag:
            return []

        # 2
        normalized_tag = self._rules_search_tag(tag)

        # 3
        return self.repository.get_by_tag(normalized_tag)

    def groupBy_categories(self, category: str) -> List[Entry]:
        # 1 si no le pasan el parametro category te devuelve una lista vacia
        # 2 le limpia el parametro category
        # 3 retorna una lista de entrys relacionadas a una categoria

        # 1
        if not category:
            return []

        # 2
        normalized_cat = self._rules_search_category(category)

        # 3
        return self.repository.get_by_category(normalized_cat)

    def _rules_tags(self, tags: Optional[List[str]]) -> List[str]:
        # 1. Manejo de nulos y política de vacío
        raw_tags = tags or []
        if not raw_tags and not self.policy.tags_allow_empty:
            raise ValueError("La política del Codex requiere al menos una etiqueta.")

        processed_tags = []
        for tag in raw_tags:
            t = tag
            # 2. Limpieza de espacios
            if self.policy.tags_strip:
                t = self._validate_string_whitespaces(t)

            # 3. Normalización a minúsculas
            if self.policy.tags_lowercase:
                t = self._validate_string_lowercase(t)

            # Solo agregamos si después de la limpieza el tag no quedó vacío
            if t:
                processed_tags.append(t)

        # 4. Unicidad (evitar ['python', 'python'])
        if self.policy.tags_unique:
            processed_tags = list(set(processed_tags))

        # 5. Ordenamiento (importante para comparar cambios en _process_field_change)
        if self.policy.tags_sort:
            processed_tags.sort()

        return processed_tags

    def _rules_category(self, category: Optional[str]) -> str:
        # 1. Aplicar valor por defecto si es None
        cat = category or self.policy.category_default

        # 2. Validar si es requerida (por si el default fuera None en otra política)
        if self.policy.category_required and not cat:
            raise ValueError("La categoría es obligatoria.")

        processed = cat

        # 3. Limpieza de espacios
        if self.policy.category_strip:
            processed = self._validate_string_whitespaces(processed)

        # 4. Formato (Capitalize: "proyectos" -> "Proyectos")
        if self.policy.category_capitalize:
            processed = processed.capitalize()

        # 5. Longitud (Las categorías suelen ser nombres cortos)
        if self.policy.category_max_length:
            processed = self._validate_string_length(
                processed, self.policy.category_max_length
            )

        return processed

    def _process_field_change(
        self, field_name: str, new_value: Any, existing_entry: Entry
    ) -> Any:
        current_value = getattr(existing_entry, field_name)

        # 1. Procesamiento de Título
        if field_name == "title":
            # Llamamos a _rules_title pasando el ID actual para evitar el error de unicidad consigo misma
            clean_title = self._rules_title(
                new_value, current_entry_id=existing_entry.id
            )

            if clean_title == current_value:
                return None
            return clean_title

        # 2. Procesamiento de Tags
        if field_name == "tags":
            # _rules_tags ya maneja la limpieza, unicidad y ordenamiento
            clean_tags = self._rules_tags(new_value or [])

            # Comparamos como listas/sets para ver si el contenido cambió
            if clean_tags == current_value:
                return None
            return clean_tags

        # 3. Procesamiento de Categoría
        if field_name == "category":
            # _rules_category valida que no sea None y limpia espacios
            clean_category = self._rules_category(new_value)

            if clean_category == current_value:
                return None
            return clean_category

        # 4. Otros campos (content, metadata, etc.)
        if new_value == current_value:
            return None

        return new_value

    def _rules_title(
        self, title: Optional[str], current_entry_id: Optional[str] = None
    ) -> str:
        """
        rules:
        1 verficica que no se none, si es None lanza un error
        2 le quita los espacios en blanco al principio y al final del string,
        3 valida que el título no esté vacío después de limpiar, si es así lanza un error
        4 valida que el título no exceda los 255 caracteres, si es así lanza un error
        5 valida que el título sea único, si no lo es lanza un error, hacemos na llamada a la base de datos y comparamos ids
        6 retorna el título limpio y validado
        """
        if self.policy.title_required and not title:
            raise ValueError("El título es requerido por la política del Codex.")

        processed = title or ""

        # 2. ¿Debo limpiar espacios? (Orquesta el helper)
        if self.policy.title_strip:
            processed = self._validate_string_whitespaces(processed)

        # 3. ¿Hay un límite de longitud? (Orquesta el helper)
        if self.policy.title_max_length:
            processed = self._validate_string_length(
                processed, self.policy.title_max_length
            )

        # 4. ¿Debe ser único?
        if self.policy.title_unique:
            self._validate_title_uniqueness(processed, current_entry_id)

        return processed

    def _rules_search_tag(self, tag: str) -> str:
        """
        Normaliza un tag individual basándose estrictamente en la política
        configurada para mantener consistencia entre guardado y búsqueda.
        """
        if not tag:
            return ""

        processed = tag

        # 1. Limpieza de espacios (Criterio de guardado)
        if self.policy.tags_strip:
            processed = self._validate_string_whitespaces(processed)

        # 2. Normalización a minúsculas (Criterio de guardado)
        if self.policy.tags_lowercase:
            processed = self._validate_string_lowercase(processed)

        return processed

    def _rules_search_category(self, category: Optional[str]) -> str:
        """
        Normaliza una categoría para búsqueda siguiendo la CodexPolicy.
        A diferencia de _rules_category, no aplica el valor por defecto ni
        lanza error si es vacío, permitiendo búsquedas opcionales.
        """
        if not category:
            return ""

        processed = category

        # 1. Limpieza de espacios
        if self.policy.category_strip:
            processed = self._validate_string_whitespaces(processed)

        # 2. Formato (Capitalize)
        if self.policy.category_capitalize:
            processed = self._validate_string_capitalize(processed)

        # 3. Recorte de longitud para coincidir con el almacenamiento
        if self.policy.category_max_length:
            processed = self._truncate_string(
                processed, self.policy.category_max_length
            )

        return processed

    def _validate_string_content(self, value: str) -> str:
        """Helper para validar que un string no sea vacío después de limpiar."""
        if not value:
            raise ValueError("cannot be empty or only whitespace.")
        return value

    def _validate_string_length(self, value: str, max_length: int = 255) -> str:
        """Helper para validar la longitud máxima de un string."""
        if len(value) > max_length:
            raise ValueError(f"Exceeds maximum length of {max_length} characters.")
        return value

    def _validate_title_uniqueness(
        self, title: str, current_entry_id: Optional[str] = None
    ) -> None:
        """Helper para validar que el título sea único en el repositorio."""
        existing = self.repository.get_by_title(title)
        if existing and (current_entry_id is None or existing.id != current_entry_id):
            raise ValueError(f"Ya existe una entrada con el título: '{title}'.")
        return None

    def _validate_string_whitespaces(self, value: str) -> str:
        """
        helper para validar que un string no tenga espacios al inicio o al final, si los tiene los elimina, si el resultado es un string vacío, lo retorna igual (la validación de 'no vacío' la hace otro helper)
        """
        return value.strip()

    def _validate_string_lowercase(self, value: str) -> str:
        """Helper para convertir un string a minúsculas."""
        return value.lower()

    def _validate_string_capitalize(self, value: str) -> str:
        """helper para capitalizar un string (primera letra mayúscula, el resto minúscula)."""
        return value.capitalize()

    def _truncate_string(self, text: str, max_length: Optional[int]) -> str:
        """Corta el texto según la longitud máxima permitida si el límite existe."""
        if max_length is not None and len(text) > max_length:
            return text[:max_length]
        return text
