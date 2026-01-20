"""
Celery tasks for AI operations
"""
import logging
from celery import shared_task
from django.utils import timezone
from ai.models import DraftGenerationTask
from repository.models import DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService
import google.generativeai as genai
from django.conf import settings
import numpy as np

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


@shared_task(bind=True, max_retries=3)
def generate_draft_async(self, task_id: str, tenant_id: str, contract_type: str, 
                        input_params: dict, template_id: str = None):
    """
    Async task to generate contract draft using RAG + Gemini
    
    Args:
        task_id: UUID of DraftGenerationTask
        tenant_id: Tenant UUID for isolation
        contract_type: Type of contract to generate
        input_params: Dictionary with generation parameters
        template_id: Optional template UUID
    """
    try:
        # Update task status
        task = DraftGenerationTask.objects.get(id=task_id, tenant_id=tenant_id)
        task.status = 'processing'
        task.started_at = timezone.now()
        task.save()
        
        logger.info(f"Starting draft generation for task {task_id}, type: {contract_type}")
        
        # Step 1: Retrieve template if specified
        template_text = ""
        if template_id:
            try:
                from contracts.models import ContractTemplate
                template = ContractTemplate.objects.get(id=template_id, tenant_id=tenant_id)
                template_text = template.template_text
                logger.info(f"Using template: {template.name}")
            except Exception as e:
                logger.warning(f"Template not found: {e}")
        
        # Step 2: Build RAG context from similar clauses
        context_clauses = []
        citations = []
        
        # Generate embedding for the contract type + parameters
        search_query = f"{contract_type} {' '.join(str(v) for v in input_params.values())}"
        embeddings_service = VoyageEmbeddingsService()
        
        try:
            query_embedding = embeddings_service.embed_query(search_query)
            
            if query_embedding:
                # Find similar document chunks from tenant's repository
                chunks = DocumentChunk.objects.filter(
                    document__tenant_id=tenant_id,
                    embedding__isnull=False
                )[:100]  # Limit to recent chunks
                
                # Calculate similarities
                query_vec = np.array(query_embedding, dtype=np.float32)
                query_norm = np.linalg.norm(query_vec)
                
                chunk_scores = []
                for chunk in chunks:
                    try:
                        chunk_vec = np.array(chunk.embedding, dtype=np.float32)
                        chunk_norm = np.linalg.norm(chunk_vec)
                        
                        if chunk_norm > 0 and query_norm > 0:
                            similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
                            
                            if similarity > 0.3:  # Threshold for relevance
                                chunk_scores.append({
                                    'chunk': chunk,
                                    'similarity': float(similarity)
                                })
                    except Exception as e:
                        logger.warning(f"Error calculating similarity: {e}")
                        continue
                
                # Sort and take top 5
                chunk_scores.sort(key=lambda x: x['similarity'], reverse=True)
                for item in chunk_scores[:5]:
                    chunk = item['chunk']
                    context_clauses.append(chunk.text)
                    citations.append({
                        'chunk_id': str(chunk.id),
                        'document_id': str(chunk.document_id),
                        'filename': chunk.document.filename,
                        'similarity': item['similarity']
                    })
                
                logger.info(f"Found {len(context_clauses)} relevant clauses for context")
        
        except Exception as e:
            logger.warning(f"RAG context building failed: {e}")
        
        # Step 3: Generate draft with Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Build prompt
        prompt_parts = [
            f"You are a legal AI assistant generating a {contract_type} contract draft.",
            f"\nContract Type: {contract_type}",
            f"\nParameters: {input_params}",
        ]
        
        if template_text:
            prompt_parts.append(f"\nTemplate to follow:\n{template_text}")
        
        if context_clauses:
            prompt_parts.append("\nRelevant clauses from similar contracts:")
            for i, clause in enumerate(context_clauses, 1):
                prompt_parts.append(f"\n{i}. {clause[:500]}...")  # Limit context length
        
        prompt_parts.append(
            "\nGenerate a comprehensive, professional contract draft. "
            "Include all standard sections: parties, definitions, obligations, "
            "termination, dispute resolution, and signatures."
        )
        
        prompt = "\n".join(prompt_parts)
        
        logger.info(f"Sending generation request to Gemini, prompt length: {len(prompt)}")
        
        response = model.generate_content(prompt)
        generated_text = response.text
        
        logger.info(f"Generated draft length: {len(generated_text)} characters")
        
        # Step 4: Update task with results
        task.status = 'completed'
        task.generated_text = generated_text
        task.citations = citations
        task.completed_at = timezone.now()
        task.save()
        
        logger.info(f"Task {task_id} completed successfully")
        return {
            'status': 'completed',
            'task_id': str(task_id),
            'generated_length': len(generated_text),
            'citations_count': len(citations)
        }
    
    except Exception as e:
        logger.error(f"Draft generation failed for task {task_id}: {str(e)}")
        
        try:
            task = DraftGenerationTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()
        except:
            pass
        
        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        return {
            'status': 'failed',
            'task_id': str(task_id),
            'error': str(e)
        }
