from src.CapsuleCore_book.capsule.CodexService import CodexService
from src.CapsuleCore_book.capsule.SQLiteKnowledgeRepository import SQLiteKnowledgeRepository


# Asumiendo que tienes la estructura de carpetas:
# core/ (Entry, Relation)
# capsule/ (CodexService, KnowledgeRepository)
# infrastructure/ (SQLiteKnowledgeRepository)

# 1. Instanciamos el Adaptador (Infraestructura)
db_name = "mi_biblioteca_codex.db"
repo = SQLiteKnowledgeRepository(db_name)

# 2. Instanciamos el Servicio (Aplicación) inyectando el repositorio
service = CodexService(repo)

print("--- Iniciando Codex ---")

try:
    # CASO DE USO 1: Crear nuevas páginas de conocimiento
    print("\n[1] Creando entradas...")
    p1 = service.create_page(
        title="Arquitectura Hexagonal", 
        content="Diseño que aísla el core de la infraestructura mediante puertos y adaptadores.",
        tags=["Arquitectura", "Diseño", "Software"]
    )
    
    p2 = service.create_page(
        title="SQLite", 
        content="Base de datos relacional ligera contenida en un solo archivo.",
        tags=["Base de Datos", "SQL", "Ligero"]
    )

    # CASO DE USO 2: Editar una página existente
    # Nota: El servicio gestionará el contador de ediciones en metadata automáticamente
    print(f"\n[2] Editando entrada {p1.id}...")
    service.edit_page(p1.id, "Nueva definición: Arquitectura de Puertos y Adaptadores.")

    # CASO DE USO 3: Crear una relación entre conceptos
    print("\n[3] Conectando páginas...")
    # Validamos que el servicio pueda conectar P2 con P1
    service.connect_pages(from_id=p2.id, to_id=p1.id, connection_type="implementación")

    # CASO DE USO 4: Buscar por etiquetas
    print("\n[4] Buscando por tag 'Software'...")
    resultados = repo.find_by_tag("Software")
    for res in resultados:
        print(f" - Encontrado: {res.title} (Ediciones: {res.metadata.get('edit_count', 0)})")

    # CASO DE USO 5: Borrado
    # print("\n[5] Borrando entrada...")
    # service.repository.delete(p2.id)

except Exception as e:
    print(f"Error en la ejecución: {e}")

finally:
    print("\n--- Proceso finalizado. Los datos están seguros en", db_name, "---")