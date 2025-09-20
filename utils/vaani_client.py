#!/usr/bin/env python3
"""
Vaani Sentinel X Client
Handles authentication and API communication with Vaani Sentinel X service.
"""

import os
import uuid
import requests
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class VaaniClient:
    """Comprehensive client for Vaani Sentinel X service"""

    def __init__(self, config=None):
        self.config = config
        self.base_url = "https://vaani-sentinel-gs6x.onrender.com"
        self.username = "admin"  # Fixed credentials as per user specification
        self.password = "secret"  # Fixed credentials as per user specification
        self.token = None
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Vaani and get JWT token"""
        try:
            auth_url = f"{self.base_url}/api/v1/auth/login"
            payload = {
                "username": self.username,
                "password": self.password
            }

            response = self.session.post(auth_url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                logger.info("✅ Vaani authentication successful")
            else:
                logger.error(f"❌ Vaani authentication failed: {response.status_code}")
                self.token = None

        except Exception as e:
            logger.error(f"❌ Vaani authentication error: {str(e)}")
            self.token = None

    def _ensure_authenticated(self):
        """Ensure we have a valid token"""
        if not self.token:
            self._authenticate()

    def _create_content_first(self, text: str, content_type: str = "tweet",
                            language: str = "en") -> Optional[str]:
        """Create content first as required by Vaani API"""
        try:
            create_url = f"{self.base_url}/api/v1/content/create"
            payload = {
                "text": text,
                "content_type": content_type,
                "language": language,
                "metadata": {"source": "bhiv_agent"}
            }

            response = self.session.post(create_url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                content_id = data.get("content_id")
                logger.info(f"✅ Content created with ID: {content_id}")
                return content_id
            else:
                logger.error(f"❌ Content creation failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Content creation error: {str(e)}")
            return None

    def generate_content(self, text: str, platforms: List[str] = None,
                        tone: str = "neutral", language: str = "en") -> Dict[str, Any]:
        """Generate platform-specific content using Vaani"""
        self._ensure_authenticated()

        try:
            # First create content
            content_id = self._create_content_first(text, "tweet", language)
            if not content_id:
                return {"error": "Failed to create content"}

            # Generate platform content
            generate_url = f"{self.base_url}/api/v1/agents/generate-content"
            generate_payload = {
                "content_id": content_id,
                "platforms": platforms or ["twitter", "instagram", "linkedin"],
                "tone": tone,
                "language": language
            }

            generate_response = self.session.post(generate_url, json=generate_payload, timeout=60)

            if generate_response.status_code == 200:
                result = generate_response.json()
                logger.info("✅ Vaani content generation successful")
                return result
            else:
                logger.error(f"❌ Vaani content generation failed: {generate_response.status_code}")
                return {"error": "Content generation failed"}

        except Exception as e:
            logger.error(f"❌ Vaani content generation error: {str(e)}")
            return {"error": str(e)}

    def translate_content(self, text: str, target_languages: List[str],
                        tone: str = "neutral") -> Dict[str, Any]:
        """Translate content using Vaani"""
        self._ensure_authenticated()

        try:
            # Create content first
            content_id = self._create_content_first(text, "tweet", "en")
            if not content_id:
                return {"error": "Failed to create content"}

            # Translate content
            translate_url = f"{self.base_url}/api/v1/multilingual/translate"
            translate_payload = {
                "content_id": content_id,
                "target_languages": target_languages,
                "tone": tone
            }

            translate_response = self.session.post(translate_url, json=translate_payload, timeout=60)

            if translate_response.status_code == 200:
                result = translate_response.json()
                logger.info("✅ Vaani translation successful")
                return result
            else:
                logger.error(f"❌ Vaani translation failed: {translate_response.status_code}")
                return {"error": "Translation failed"}

        except Exception as e:
            logger.error(f"❌ Vaani translation error: {str(e)}")
            return {"error": str(e)}

    def generate_voice(self, text: str, language: str = "hi",
                      tone: str = "devotional", voice_tag: str = "hi_in_female_devotional") -> Dict[str, Any]:
        """Generate voice content using Vaani"""
        self._ensure_authenticated()

        try:
            # Create content first
            content_id = self._create_content_first(text, "voice_script", language)
            if not content_id:
                return {"error": "Failed to create content"}

            # Generate voice
            voice_url = f"{self.base_url}/api/v1/agents/generate-voice"
            voice_payload = {
                "content_id": content_id,
                "language": language,
                "tone": tone,
                "voice_tag": voice_tag
            }

            voice_response = self.session.post(voice_url, json=voice_payload, timeout=60)

            if voice_response.status_code == 200:
                result = voice_response.json()
                logger.info("✅ Vaani voice generation successful")
                return result
            else:
                logger.error(f"❌ Vaani voice generation failed: {voice_response.status_code}")
                return {"error": "Voice generation failed"}

        except Exception as e:
            logger.error(f"❌ Vaani voice generation error: {str(e)}")
            return {"error": str(e)}

    def analyze_content_security(self, text: str) -> Dict[str, Any]:
        """Analyze content security using Vaani"""
        self._ensure_authenticated()

        try:
            # Create content first
            content_id = self._create_content_first(text, "tweet", "en")
            if not content_id:
                return {"error": "Failed to create content"}

            # Analyze security
            security_url = f"{self.base_url}/api/v1/security/analyze-content"
            security_payload = {"content_id": content_id}

            security_response = self.session.post(security_url, json=security_payload, timeout=30)

            if security_response.status_code == 200:
                result = security_response.json()
                logger.info("✅ Vaani security analysis successful")
                return result
            else:
                logger.error(f"❌ Vaani security analysis failed: {security_response.status_code}")
                return {"error": "Security analysis failed"}

        except Exception as e:
            logger.error(f"❌ Vaani security analysis error: {str(e)}")
            return {"error": str(e)}

    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language using Vaani"""
        self._ensure_authenticated()

        try:
            detect_url = f"{self.base_url}/api/v1/multilingual/detect-language"
            payload = {"content": text}

            response = self.session.post(detect_url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Vaani language detection successful")
                return result
            else:
                logger.error(f"❌ Vaani language detection failed: {response.status_code}")
                return {"error": "Language detection failed"}

        except Exception as e:
            logger.error(f"❌ Vaani language detection error: {str(e)}")
            return {"error": str(e)}

    async def generate_audio(self, text: str, language: str = "hi",
                            voice: str = "female") -> Optional[str]:
        """Generate audio using Vaani TTS (legacy method for compatibility)"""
        try:
            # Use the new voice generation method
            voice_result = self.generate_voice(text, language, "devotional", f"{language}_in_female_devotional")

            if "error" not in voice_result:
                # Return a mock URL for now (Vaani might provide actual audio URL)
                audio_id = str(uuid.uuid4())
                return f"/audio/{audio_id}.wav"
            else:
                logger.warning("⚠️ Vaani voice generation failed, using fallback")
                return None

        except Exception as e:
            logger.error(f"❌ Error generating audio: {str(e)}")
            return None

    def get_supported_platforms(self) -> List[str]:
        """Get supported platforms from Vaani"""
        self._ensure_authenticated()

        try:
            platforms_url = f"{self.base_url}/api/v1/agents/platforms"
            response = self.session.get(platforms_url, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                # Return default platforms
                return ["twitter", "instagram", "linkedin", "spotify"]

        except Exception as e:
            logger.error(f"❌ Error getting platforms: {str(e)}")
            return ["twitter", "instagram", "linkedin", "spotify"]

    def get_supported_languages(self) -> List[str]:
        """Get supported languages from Vaani"""
        self._ensure_authenticated()

        try:
            languages_url = f"{self.base_url}/api/v1/agents/languages"
            response = self.session.get(languages_url, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                # Return default languages
                return ["en", "hi", "sa", "mr", "gu", "ta", "te", "kn", "ml", "bn"]

        except Exception as e:
            logger.error(f"❌ Error getting languages: {str(e)}")
            return ["en", "hi", "sa", "mr", "gu", "ta", "te", "kn", "ml", "bn"]