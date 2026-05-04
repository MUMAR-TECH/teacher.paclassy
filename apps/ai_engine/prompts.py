LESSON_PLAN_PROMPT = """Create a detailed lesson plan in JSON format for:
- Subject: {subject}
- Grade: {grade}
- Duration: {duration} minutes
- Learning Objectives: {objectives}
- Curriculum: {curriculum}

Return ONLY valid JSON with this structure:
{{
  "title": "Lesson title",
  "overview": "Brief overview",
  "objectives": ["obj1", "obj2"],
  "materials": ["mat1", "mat2"],
  "sections": [
    {{
      "name": "Introduction",
      "duration": 10,
      "activities": ["activity1"],
      "teacher_notes": "notes"
    }}
  ],
  "assessment": "How to assess learning",
  "homework": "Homework assignment",
  "differentiation": {{
    "support": "For struggling students",
    "extension": "For advanced students"
  }}
}}"""

ASSESSMENT_PROMPT = """Generate {num} {type} questions for:
- Subject: {subject}
- Grade: {grade}
- Topic: {topic}
- Difficulty: {difficulty}

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "id": 1,
      "type": "mcq",
      "question": "Question text",
      "options": {{"A": "opt1", "B": "opt2", "C": "opt3", "D": "opt4"}},
      "correct_answer": "A",
      "explanation": "Why A is correct",
      "marks": 1
    }}
  ],
  "total_marks": 10,
  "instructions": "General instructions"
}}"""

CONTENT_PROMPT = """Generate {type} content in {language} for:
- Subject: {subject}
- Grade: {grade}
- Topic: {topic}
- Difficulty: {difficulty}

Provide comprehensive, well-structured content appropriate for the grade level.
Include examples, key concepts, and important points."""

TUTOR_SYSTEM_PROMPT = """You are Paclassy AI Tutor, an expert educational assistant for {subject} at {grade} level.
Your role is to:
- Explain concepts clearly and patiently
- Provide step-by-step solutions
- Give hints rather than direct answers for homework
- Encourage critical thinking
- Use age-appropriate language
- Provide examples relevant to the student's context

Always be encouraging, patient, and supportive."""

ESSAY_GRADING_PROMPT = """Grade the following student essay response.

Question: {question}
Student Answer: {answer}
Grading Rubric: {rubric}

Return ONLY valid JSON:
{{
  "score": 7,
  "max_score": 10,
  "percentage": 70,
  "grade": "B",
  "feedback": "Detailed feedback",
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1"],
  "detailed_breakdown": {{
    "content": {{"score": 3, "max": 4, "comment": "..."}},
    "structure": {{"score": 2, "max": 3, "comment": "..."}},
    "language": {{"score": 2, "max": 3, "comment": "..."}}
  }}
}}"""

REPORT_SUMMARY_PROMPT = """Write a constructive, encouraging report card summary for:
Student: {student_name}
Academic Performance: {grades}

Write 2-3 paragraphs covering:
1. Overall performance and strengths
2. Areas for improvement
3. Recommendations and encouragement

Use professional, positive language suitable for parents and students."""
