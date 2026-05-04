import json
import hashlib
import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

MOCK_LESSON_PLAN = {
    "title": "Sample Lesson Plan",
    "overview": "A comprehensive lesson covering the requested topic.",
    "objectives": ["Understand key concepts", "Apply knowledge practically"],
    "materials": ["Textbook", "Whiteboard", "Worksheets"],
    "sections": [
        {
            "name": "Introduction",
            "duration": 10,
            "activities": ["Warm-up discussion", "Review previous lesson"],
            "teacher_notes": "Engage students with questions"
        },
        {
            "name": "Main Activity",
            "duration": 30,
            "activities": ["Direct instruction", "Group work", "Practice exercises"],
            "teacher_notes": "Monitor student understanding"
        },
        {
            "name": "Conclusion",
            "duration": 10,
            "activities": ["Summary", "Q&A"],
            "teacher_notes": "Ensure key points are understood"
        }
    ],
    "assessment": "Exit ticket with 3 questions",
    "homework": "Complete exercises 1-5 from the textbook",
    "differentiation": {
        "support": "Provide scaffolded worksheets",
        "extension": "Research project on advanced topics"
    }
}

MOCK_ASSESSMENT = {
    "questions": [
        {
            "id": 1,
            "type": "mcq",
            "question": "Sample question 1?",
            "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            "correct_answer": "A",
            "explanation": "Option A is correct because...",
            "marks": 1
        }
    ],
    "total_marks": 1,
    "instructions": "Answer all questions carefully."
}


class AIService:
    DEFAULT_MODEL = 'gemini-1.5-flash'

    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.model = getattr(settings, 'GEMINI_MODEL', self.DEFAULT_MODEL)
        self._client = None
        self._genai = None

    def _configure_genai(self):
        if self._genai is None and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._genai = genai
            except ImportError:
                logger.warning('google-generativeai package not available')
        return self._genai

    @property
    def client(self):
        if not self._client and self.api_key:
            genai = self._configure_genai()
            if genai:
                self._client = genai.GenerativeModel(self.model)
        return self._client

    def _get_cache_key(self, prompt: str) -> str:
        return f"ai_response_{hashlib.sha256(prompt.encode()).hexdigest()}"

    def generate(self, prompt: str, use_cache: bool = True) -> str:
        if not self.api_key or not self.client:
            return json.dumps({"raw": "AI service not configured. Please set GEMINI_API_KEY."})

        if use_cache:
            cache_key = self._get_cache_key(prompt)
            cached = cache.get(cache_key)
            if cached:
                return cached

        try:
            response = self.client.generate_content(
                prompt,
                generation_config={"temperature": 0.7},
            )
            result = response.text

            if use_cache:
                cache.set(cache_key, result, timeout=3600)
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return json.dumps({"error": str(e), "raw": "AI generation failed."})

    def generate_lesson_plan(self, subject, grade, duration, objectives, curriculum=None):
        if not self.api_key:
            return MOCK_LESSON_PLAN

        from .prompts import LESSON_PLAN_PROMPT
        prompt = LESSON_PLAN_PROMPT.format(
            subject=subject, grade=grade, duration=duration,
            objectives=objectives, curriculum=curriculum or 'Standard'
        )
        content = self.generate(prompt)
        try:
            return json.loads(content)
        except Exception:
            return {"raw": content, "sections": self._parse_sections(content)}

    def generate_assessment(self, subject, grade, assessment_type, num_questions, difficulty, topic=None):
        if not self.api_key:
            return MOCK_ASSESSMENT

        from .prompts import ASSESSMENT_PROMPT
        prompt = ASSESSMENT_PROMPT.format(
            subject=subject, grade=grade, type=assessment_type,
            num=num_questions, difficulty=difficulty, topic=topic or subject
        )
        content = self.generate(prompt)
        try:
            return json.loads(content)
        except Exception:
            return {"raw": content}

    def generate_content(self, content_type, subject, grade, topic, difficulty, language):
        if not self.api_key:
            return f"[Mock {content_type} content for {topic} in {subject} for Grade {grade}]\n\nThis is sample content. Configure GEMINI_API_KEY for real AI-generated content."

        from .prompts import CONTENT_PROMPT
        prompt = CONTENT_PROMPT.format(
            type=content_type, subject=subject, grade=grade,
            topic=topic, difficulty=difficulty, language=language
        )
        return self.generate(prompt)

    def _build_chat_model(self, system_instruction: str):
        genai = self._configure_genai()
        if not genai:
            return None
        return genai.GenerativeModel(self.model, system_instruction=system_instruction)

    def chat_with_tutor(self, messages, subject, grade):
        if not self.api_key:
            return "AI Tutor is not configured. Please set GEMINI_API_KEY to enable this feature."

        from .prompts import TUTOR_SYSTEM_PROMPT
        system_prompt = TUTOR_SYSTEM_PROMPT.format(subject=subject, grade=grade)

        try:
            model = self._build_chat_model(system_prompt)
            if not model:
                return "AI Tutor is not available. Please check that google-generativeai is installed."

            role_map = {"assistant": "model", "user": "user"}
            history = []
            for msg in messages[:-1]:
                role = role_map.get(msg["role"])
                if role is None:
                    logger.warning(
                        "Skipping message with unsupported role '%s'. Supported roles: 'user', 'assistant'.",
                        msg["role"],
                    )
                    continue
                history.append({"role": role, "parts": [msg["content"]]})
            chat = model.start_chat(history=history)
            last_message = messages[-1]["content"] if messages else ""
            response = chat.send_message(
                last_message,
                generation_config={"temperature": 0.8},
            )
            return response.text
        except Exception as e:
            logger.error(f"Tutor chat error: {e}")
            return "I'm having trouble responding right now. Please try again later."

    def grade_essay(self, question, answer, rubric=None):
        if not self.api_key:
            return {"feedback": "AI grading not configured.", "score": None}

        from .prompts import ESSAY_GRADING_PROMPT
        prompt = ESSAY_GRADING_PROMPT.format(
            question=question, answer=answer, rubric=rubric or 'Standard rubric'
        )
        content = self.generate(prompt, use_cache=False)
        try:
            return json.loads(content)
        except Exception:
            return {"feedback": content, "score": None}

    def generate_report_summary(self, student_name, grades_data):
        if not self.api_key:
            return f"Report summary for {student_name}. AI summary not configured."

        from .prompts import REPORT_SUMMARY_PROMPT
        prompt = REPORT_SUMMARY_PROMPT.format(
            student_name=student_name, grades=json.dumps(grades_data)
        )
        return self.generate(prompt, use_cache=False)

    def _parse_sections(self, content):
        sections = []
        current = {"title": "Introduction", "content": ""}
        for line in content.split('\n'):
            if line.startswith('#'):
                if current["content"]:
                    sections.append(current)
                current = {"title": line.strip('# '), "content": ""}
            else:
                current["content"] += line + "\n"
        if current["content"]:
            sections.append(current)
        return sections


ai_service = AIService()
