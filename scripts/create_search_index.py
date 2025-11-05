#!/usr/bin/env python3
"""
Script para crear el índice de Azure Cognitive Search
Uso: python scripts/create_search_index.py
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def create_ariba_knowledge_index():
    """Crea el índice de conocimiento de Ariba"""
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "ariba-knowledge")
    
    if not endpoint or not api_key:
        print("❌ Error: AZURE_SEARCH_ENDPOINT y AZURE_SEARCH_API_KEY deben estar configurados en .env")
        sys.exit(1)
    
    print(f"🔍 Conectando a Azure Cognitive Search: {endpoint}")
    
    # Cliente de índices
    credential = AzureKeyCredential(api_key)
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    
    # Eliminar índice existente si existe
    try:
        index_client.delete_index(index_name)
        print(f"🗑️  Índice existente '{index_name}' eliminado")
    except Exception:
        pass  # El índice no existe, continuar
    
    # Definir campos del índice
    fields = [
        # Campos clave
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),
        
        # Campos de contenido
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
            searchable=True,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
            searchable=True,
        ),
        SearchableField(
            name="description",
            type=SearchFieldDataType.String,
            searchable=True,
        ),
        
        # Campos de categorización
        SimpleField(
            name="category",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="subcategory",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="tags",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
            facetable=True,
        ),
        
        # Campos de documento
        SimpleField(
            name="document_type",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="source_url",
            type=SearchFieldDataType.String,
            filterable=False,
        ),
        
        # Campos temporales
        SimpleField(
            name="created_date",
            type=SearchFieldDataType.DateTimeOffset,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="modified_date",
            type=SearchFieldDataType.DateTimeOffset,
            filterable=True,
            sortable=True,
        ),
        
        # Campos de relevancia
        SimpleField(
            name="priority",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="language",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        
        # Campos de Ariba específicos
        SimpleField(
            name="ariba_module",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="ariba_process",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="related_apis",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
        ),
    ]
    
    # Configuración de búsqueda semántica
    semantic_config = SemanticConfiguration(
        name="ariba-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[
                SemanticField(field_name="content"),
                SemanticField(field_name="description"),
            ],
            keywords_fields=[
                SemanticField(field_name="tags"),
                SemanticField(field_name="category"),
            ],
        ),
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    # Crear el índice
    index = SearchIndex(
        name=index_name,
        fields=fields,
        semantic_search=semantic_search,
    )
    
    try:
        print(f"📝 Creando índice '{index_name}'...")
        result = index_client.create_or_update_index(index)
        print(f"✅ Índice '{result.name}' creado exitosamente")
        print(f"   - Campos: {len(result.fields)}")
        print(f"   - Búsqueda semántica: Habilitada")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear el índice: {str(e)}")
        return False


def upload_sample_documents():
    """Sube documentos de ejemplo al índice"""
    from azure.search.documents import SearchClient
    from datetime import datetime, timezone
    
    # Helper para crear timestamp
    def now_iso():
        return datetime.now(timezone.utc).isoformat()
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "ariba-knowledge")
    
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    # Documentos de ejemplo
    sample_docs = [
        {
            "@search.action": "upload",
            "id": "1",
            "title": "Crear Requisición de Compra en SAP Ariba",
            "content": "Para crear una requisición de compra en SAP Ariba, navega al módulo de Procurement y selecciona 'Nueva Requisición'. Completa los campos obligatorios como descripción del artículo, cantidad, y centro de costos.",
            "description": "Guía paso a paso para crear requisiciones de compra",
            "category": "Procurement",
            "subcategory": "Requisiciones",
            "tags": ["requisicion", "compra", "procurement"],
            "document_type": "tutorial",
            "source_url": "https://help.sap.com/ariba/procurement/requisitions",
            "created_date": now_iso(),
            "modified_date": now_iso(),
            "priority": 1,
            "language": "es",
            "ariba_module": "Procurement",
            "ariba_process": "Requisition",
            "related_apis": ["Requisition API", "Procurement API"],
        },
        {
            "@search.action": "upload",
            "id": "2",
            "title": "Aprobar Órdenes de Compra",
            "content": "El proceso de aprobación de órdenes de compra requiere revisar los detalles de la orden, verificar el presupuesto disponible, y aprobar o rechazar según las políticas de la empresa.",
            "description": "Proceso de aprobación de purchase orders",
            "category": "Procurement",
            "subcategory": "Aprobaciones",
            "tags": ["aprobacion", "orden-compra", "workflow"],
            "document_type": "process",
            "source_url": "https://help.sap.com/ariba/procurement/approvals",
            "created_date": now_iso(),
            "modified_date": now_iso(),
            "priority": 1,
            "language": "es",
            "ariba_module": "Procurement",
            "ariba_process": "Approval",
            "related_apis": ["Approval API", "Purchase Order API"],
        },
        {
            "@search.action": "upload",
            "id": "3",
            "title": "Gestión de Proveedores",
            "content": "La gestión de proveedores en SAP Ariba incluye el registro de nuevos proveedores, evaluación de desempeño, y mantenimiento de la información de contacto y capacidades.",
            "description": "Administración del catálogo de proveedores",
            "category": "Supplier Management",
            "subcategory": "Registro",
            "tags": ["proveedor", "supplier", "registro"],
            "document_type": "guide",
            "source_url": "https://help.sap.com/ariba/supplier-management",
            "created_date": now_iso(),
            "modified_date": now_iso(),
            "priority": 2,
            "language": "es",
            "ariba_module": "Supplier Management",
            "ariba_process": "Registration",
            "related_apis": ["Supplier API", "Vendor API"],
        },
    ]
    
    try:
        print(f"\n📤 Subiendo {len(sample_docs)} documentos de ejemplo...")
        
        # Primero probar con un documento simple sin arrays
        print("\n🔍 Probando con documento simple (sin arrays)...")
        simple_doc = {
            "id": "test-1",
            "title": "Documento de prueba",
            "content": "Contenido de prueba",
            "description": "Descripción de prueba",
            "category": "Test",
            "subcategory": "Test",
            "document_type": "test",
            "source_url": "https://test.com",
            "created_date": now_iso(),
            "modified_date": now_iso(),
            "priority": 1,
            "language": "es",
            "ariba_module": "Test",
            "ariba_process": "Test",
        }
        
        try:
            result = search_client.upload_documents(documents=[simple_doc])
            if result[0].succeeded:
                print("   ✅ Documento simple subido correctamente")
                print("   ℹ️  El problema está en los campos de tipo Collection")
            else:
                print(f"   ❌ Error: {result[0].error_message}")
        except Exception as e:
            print(f"   ❌ Error al subir documento simple: {str(e)}")
        
        # Ahora subir documentos completos uno por uno
        print("\n📤 Subiendo documentos completos...")
        success_count = 0
        for i, doc in enumerate(sample_docs, 1):
            try:
                # Remover @search.action ya que upload_documents lo agrega automáticamente
                doc_copy = {k: v for k, v in doc.items() if k != "@search.action"}
                
                result = search_client.upload_documents(documents=[doc_copy])
                if result[0].succeeded:
                    print(f"   ✅ Documento {i}/{len(sample_docs)} subido: {doc_copy['title'][:50]}...")
                    success_count += 1
                else:
                    print(f"   ❌ Error en documento {i}: {result[0].error_message}")
            except Exception as doc_error:
                print(f"   ❌ Error en documento {i}: {str(doc_error)}")
        
        print(f"\n✅ {success_count}/{len(sample_docs)} documentos subidos exitosamente")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error al subir documentos: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 Configuración de Azure Cognitive Search")
    print("=" * 60)
    print()
    
    # Crear índice
    if not create_ariba_knowledge_index():
        sys.exit(1)
    
    # Preguntar si subir documentos de ejemplo
    print()
    response = input("¿Deseas subir documentos de ejemplo? (y/n): ")
    
    if response.lower() in ['y', 'yes', 's', 'si', 'sí']:
        if upload_sample_documents():
            print("\n✅ Configuración completada exitosamente")
        else:
            print("\n⚠️  Índice creado pero hubo errores al subir documentos")
    else:
        print("\n✅ Índice creado. Puedes subir documentos manualmente más tarde.")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
