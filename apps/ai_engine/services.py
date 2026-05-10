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
    DEFAULT_MODEL = 'gpt-4.1-mini'

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.model = getattr(settings, 'OPENAI_MODEL', self.DEFAULT_MODEL)
        self._client = None

    @property
    def client(self):
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning('openai package not available')
        return self._client

    def _get_cache_key(self, prompt: str) -> str:
        return f"ai_response_{hashlib.sha256(prompt.encode()).hexdigest()}"

    def generate(self, prompt: str, use_cache: bool = True) -> str:
        if not self.api_key or not self.client:
            return json.dumps({"raw": "AI service not configured. Please set OPENAI_API_KEY."})

        if use_cache:
            cache_key = self._get_cache_key(prompt)
            cached = cache.get(cache_key)
            if cached:
                return cached

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                store=True,
            )
            result = response.output_text

            if use_cache:
                cache.set(cache_key, result, timeout=3600)
            return result
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return json.dumps({"error": str(e), "raw": "AI generation failed."})

    def _chat(self, messages: list, use_cache: bool = False) -> str:
        """Send a multi-turn conversation to the Responses API."""
        if not self.api_key or not self.client:
            return json.dumps({"raw": "AI service not configured. Please set OPENAI_API_KEY."})

        try:
            response = self.client.responses.create(
                model=self.model,
                input=messages,
                store=True,
            )
            return response.output_text
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm having trouble responding right now. Please try again later."

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
            return f"[Mock {content_type} content for {topic} in {subject} for Grade {grade}]\n\nThis is sample content. Configure OPENAI_API_KEY for real AI-generated content."

        from .prompts import CONTENT_PROMPT
        prompt = CONTENT_PROMPT.format(
            type=content_type, subject=subject, grade=grade,
            topic=topic, difficulty=difficulty, language=language
        )
        return self.generate(prompt)

    def chat_with_tutor(self, messages, subject, grade):
        if not self.api_key:
            return "AI Tutor is not configured. Please set OPENAI_API_KEY to enable this feature."

        from .prompts import TUTOR_SYSTEM_PROMPT
        system_prompt = TUTOR_SYSTEM_PROMPT.format(subject=subject, grade=grade)

        try:
            input_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                role = msg.get("role")
                if role not in ("user", "assistant"):
                    logger.warning(
                        "Skipping message with unsupported role '%s'. Supported roles: 'user', 'assistant'.",
                        role,
                    )
                    continue
                input_messages.append({"role": role, "content": msg["content"]})
            return self._chat(input_messages)
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

    def _chat_with_agent(self, messages, system_prompt):
        """Shared chat logic for both teacher and admin agents."""
        if not self.api_key:
            return "AI Assistant is not configured. Please set OPENAI_API_KEY to enable this feature."

        try:
            input_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                role = msg.get("role")
                if role not in ("user", "assistant"):
                    logger.warning(
                        "Skipping message with unsupported role '%s'.", role
                    )
                    continue
                input_messages.append({"role": role, "content": msg["content"]})
            return self._chat(input_messages)
        except Exception as e:
            logger.error(f"Agent chat error: {e}")
            return "I'm having trouble responding right now. Please try again later."

    def chat_with_teacher_agent(self, messages, teacher_name, school_name, subjects, grades):
        if not self.api_key:
            return "Teacher Assistant is not configured. Please set OPENAI_API_KEY to enable this feature."

        from .prompts import TEACHER_AGENT_SYSTEM_PROMPT
        system_prompt = TEACHER_AGENT_SYSTEM_PROMPT.format(
            teacher_name=teacher_name,
            school_name=school_name or 'your school',
            subjects=', '.join(subjects) if subjects else 'General',
            grades=', '.join(grades) if grades else 'General',
        )
        return self._chat_with_agent(messages, system_prompt)

    def chat_with_admin_agent(self, messages, admin_name, school_name, total_teachers, total_students, ai_credits):
        if not self.api_key:
            return "Admin Assistant is not configured. Please set OPENAI_API_KEY to enable this feature."

        from .prompts import ADMIN_AGENT_SYSTEM_PROMPT
        system_prompt = ADMIN_AGENT_SYSTEM_PROMPT.format(
            admin_name=admin_name,
            school_name=school_name or 'your school',
            total_teachers=total_teachers,
            total_students=total_students,
            ai_credits=ai_credits,
        )
        return self._chat_with_agent(messages, system_prompt)

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
