#!/usr/bin/env python3
"""
EduMentor Agent - Educational Mentor
Provides structured educational content and learning guidance using RAG API and Groq enhancement.
"""

import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.rag_client import rag_client
from utils.groq_client import groq_client
from reinforcement.rl_context import RLContext

logger = get_logger(__name__)

class EduMentorAgent:
    """Agent for providing educational mentoring and structured learning."""

    def __init__(self):
        self.name = "EduMentorAgent"
        self.description = "Educational mentor providing structured learning guidance"
        self.rl_context = RLContext()
        self.persona = "educational_mentor"

        # Educational keywords for context enhancement
        self.educational_keywords = [
            "learn", "teach", "explain", "understand", "study", "education",
            "concept", "theory", "practice", "example", "exercise", "assessment",
            "knowledge", "skill", "competency", "curriculum", "pedagogy"
        ]

        logger.info("✅ EduMentorAgent initialized with RAG API and Groq enhancement")

    def _get_knowledge_context(self, query: str) -> tuple[str, list]:
        """Get relevant educational knowledge from RAG API."""
        try:
            # Enhance query with educational context
            enhanced_query = f"Educational learning guidance: {query}"

            # Query RAG API
            response = rag_client.query(enhanced_query, top_k=5)

            if response.get("status") == 200 and response.get("response"):
                # Combine relevant results for context
                contexts = []
                sources = []
                for result in response["response"][:3]:  # Top 3 results
                    if isinstance(result, dict) and "content" in result:
                        contexts.append(result["content"])
                        sources.append({
                            "content": result["content"][:200] + "...",  # Preview
                            "source": result.get("source", "unknown"),
                            "score": result.get("score", 0.0),
                            "document_id": result.get("document_id", ""),
                            "folder": result.get("folder", "rag_api")
                        })

                context_text = " ".join(contexts) if contexts else ""
                return context_text, sources

            logger.warning("⚠️ No educational context retrieved from RAG API")
            return "", []

        except Exception as e:
            logger.error(f"❌ Error getting educational context: {str(e)}")
            return "", []

    def _enhance_with_groq(self, query: str, knowledge_context: str = "") -> tuple[str, bool]:
        """Enhance response using Groq with educational mentor persona."""
        try:
            # Build educational mentoring enhancement prompt
            prompt = f"""As an experienced educational mentor and guide, provide structured, clear, and effective learning support for: "{query}"

{f'Educational Context: {knowledge_context}' if knowledge_context else 'Draw from established educational principles and best practices.'}

Please respond as a patient and encouraging teacher who:
- Explains concepts clearly and systematically
- Uses appropriate educational scaffolding
- Provides practical examples and applications
- Encourages critical thinking and understanding
- Adapts explanations to different learning styles
- Promotes active learning and engagement

Your response should include:
- Clear explanations of key concepts
- Step-by-step guidance when appropriate
- Practical examples or analogies
- Encouragement for further exploration
- Assessment of understanding

Educational Guidance:"""

            response, success = groq_client.generate_response(prompt, max_tokens=1200, temperature=0.7)

            if success and response:
                return response, True
            else:
                logger.warning("⚠️ Groq enhancement failed, using fallback")
                return self._fallback_response(query, knowledge_context), False

        except Exception as e:
            logger.error(f"❌ Groq enhancement error: {str(e)}")
            return self._fallback_response(query, knowledge_context), False

    def _fallback_response(self, query: str, knowledge_context: str = "") -> str:
        """Provide fallback educational response when Groq is unavailable."""
        base_response = f"As your educational mentor, I'm here to help you understand '{query}'. "

        if knowledge_context:
            base_response += f"Based on educational principles: {knowledge_context[:500]}..."
        else:
            base_response += "Learning is a journey of discovery. Let's break this down step by step."

        base_response += "\n\nRemember, understanding comes from consistent practice and asking questions. Keep exploring!"
        return base_response

    def process_query(self, query: str, task_id: str = None) -> Dict[str, Any]:
        """Process an educational query."""
        task_id = task_id or str(uuid.uuid4())

        try:
            logger.info(f"📚 EduMentorAgent processing query: '{query[:100]}...'")

            # Step 1: Get educational context from RAG API
            knowledge_context, sources = self._get_knowledge_context(query)

            # Step 2: Enhance with Groq using educational mentor persona
            enhanced_response, groq_used = self._enhance_with_groq(query, knowledge_context)

            # Step 3: Log RL context
            self.rl_context.log_action(
                task_id=task_id,
                agent=self.name,
                model="groq" if groq_used else "fallback",
                action="educational_guidance",
                metadata={
                    "query": query,
                    "knowledge_retrieved": bool(knowledge_context),
                    "groq_enhanced": groq_used,
                    "persona": self.persona,
                    "sources_count": len(sources)
                }
            )

            # Step 4: Prepare response with detailed sources
            response_data = {
                "response": enhanced_response,
                "query_id": task_id,
                "query": query,
                "agent": self.name,
                "persona": self.persona,
                "knowledge_context_used": bool(knowledge_context),
                "groq_enhanced": groq_used,
                "sources": sources,  # Include detailed source information
                "rag_data": {
                    "total_sources": len(sources),
                    "method": "rag_api_enhanced",
                    "knowledge_context_length": len(knowledge_context),
                    "has_groq_answer": groq_used
                },
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "metadata": {
                    "educational_keywords": [kw for kw in self.educational_keywords if kw in query.lower()],
                    "guidance_type": "educational_mentoring",
                    "enhancement_method": "groq" if groq_used else "fallback"
                }
            }

            logger.info(f"✅ EduMentorAgent completed processing for task {task_id}")
            return response_data

        except Exception as e:
            logger.error(f"❌ EduMentorAgent error: {str(e)}")

            # Return error response
            return {
                "response": "I apologize, but I'm experiencing difficulties providing educational guidance at this moment. Please try again later.",
                "query_id": task_id,
                "query": query,
                "agent": self.name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run(self, input_path: str, live_feed: str = "", model: str = "edumentor_agent",
            input_type: str = "text", task_id: str = None) -> Dict[str, Any]:
        """Main entry point for agent execution - compatible with existing interface."""
        return self.process_query(input_path, task_id)

    def health_check(self) -> Dict[str, Any]:
        """Check agent health and dependencies."""
        health_status = {
            "agent": self.name,
            "status": "healthy",
            "rag_api_available": False,
            "groq_api_available": False,
            "timestamp": datetime.now().isoformat()
        }

        # Check RAG API
        try:
            rag_health = rag_client.health_check()
            health_status["rag_api_available"] = rag_health.get("available", False)
        except Exception as e:
            logger.warning(f"RAG API health check failed: {e}")

        # Check Groq API
        try:
            groq_health = groq_client.health_check()
            health_status["groq_api_available"] = groq_client.health_check().get("available", False)
        except Exception as e:
            logger.warning(f"Groq API health check failed: {e}")

        # Overall status
        if not health_status["rag_api_available"] and not health_status["groq_api_available"]:
            health_status["status"] = "degraded"
        elif not health_status["rag_api_available"] or not health_status["groq_api_available"]:
            health_status["status"] = "partial"

        return health_status