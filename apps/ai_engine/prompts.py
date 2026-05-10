LESSON_PLAN_PROMPT = """You are an experienced curriculum designer. Create a comprehensive, detailed lesson plan in JSON format for the following lesson:

- Subject: {subject}
- Grade / Class: {grade}
- Duration: {duration} minutes
- Learning Objectives: {objectives}
- Curriculum Framework: {curriculum}

Return ONLY a single valid JSON object — no markdown, no explanation, no code fences — with EXACTLY this structure:

{{
  "title": "A clear, descriptive lesson title",
  "overview": "A 2-3 sentence paragraph describing what this lesson is about, its purpose, and how it fits into the broader unit of study.",
  "prior_knowledge": "A concise description of the knowledge and skills students are expected to already have before this lesson.",
  "objectives": [
    "By the end of this lesson, students will be able to ...",
    "Students will demonstrate understanding of ... by ..."
  ],
  "success_criteria": [
    "I can explain ...",
    "I can identify ...",
    "I can apply ... to solve ..."
  ],
  "key_vocabulary": ["term1", "term2", "term3", "term4", "term5"],
  "materials": [
    "Textbook: Chapter X",
    "Whiteboard and markers",
    "Printed worksheets (1 per student)",
    "Multimedia projector"
  ],
  "sections": [
    {{
      "name": "Starter / Hook",
      "duration": 5,
      "teacher_activities": [
        "Pose a provocative question to the class",
        "Display a short video clip or image as a stimulus"
      ],
      "student_activities": [
        "Discuss the question with a partner (Think-Pair-Share)",
        "Share responses with the class"
      ],
      "teacher_notes": "Aim to activate prior knowledge and generate curiosity."
    }},
    {{
      "name": "Direct Instruction",
      "duration": 15,
      "teacher_activities": [
        "Introduce key concepts using the board and slides",
        "Model worked examples step by step",
        "Check for understanding with targeted questions"
      ],
      "student_activities": [
        "Take structured notes in exercise books",
        "Answer comprehension questions aloud"
      ],
      "teacher_notes": "Use cold-calling to check understanding. Narrate your thinking while modelling."
    }},
    {{
      "name": "Guided Practice",
      "duration": 15,
      "teacher_activities": [
        "Circulate and monitor student progress",
        "Provide immediate corrective feedback",
        "Facilitate small-group discussion"
      ],
      "student_activities": [
        "Attempt practice problems individually",
        "Compare answers with a partner",
        "Ask clarifying questions"
      ],
      "teacher_notes": "Identify common misconceptions and address them with the whole class."
    }},
    {{
      "name": "Independent Practice",
      "duration": 10,
      "teacher_activities": [
        "Monitor and record observations",
        "Provide targeted support to struggling students"
      ],
      "student_activities": [
        "Complete worksheet independently",
        "Apply concepts to new problems"
      ],
      "teacher_notes": "This is formative assessment time — note which students need additional support."
    }},
    {{
      "name": "Plenary / Closure",
      "duration": 5,
      "teacher_activities": [
        "Summarise key learning points",
        "Distribute exit tickets"
      ],
      "student_activities": [
        "Complete exit ticket",
        "Reflect on what they learned today"
      ],
      "teacher_notes": "Review exit tickets before the next lesson to inform planning."
    }}
  ],
  "assessment": "Describe formative and summative assessment strategies: e.g., exit tickets, questioning, peer assessment, and any end-of-topic test.",
  "homework": "A specific, purposeful homework task with clear instructions and expected submission date.",
  "differentiation": {{
    "support": "Strategies and resources for students who need additional support, e.g., graphic organisers, sentence starters, peer mentoring, simplified text.",
    "extension": "Stretch tasks and higher-order challenges for students who complete work early or are working above the expected level."
  }},
  "curriculum": "{curriculum}"
}}

Tailor all content specifically to the subject '{subject}', grade level '{grade}', and the stated objectives. Make the activities realistic, practical, and directly linked to the objectives. Ensure the section durations add up to exactly {duration} minutes."""

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

TEACHER_AGENT_SYSTEM_PROMPT = """You are Paclassy Teacher Assistant, a personal AI agent dedicated to helping teachers excel in their profession.

Teacher context:
- Name: {teacher_name}
- School: {school_name}
- Subjects: {subjects}
- Grades: {grades}

Your role is to assist this teacher personally with:
- Pedagogical strategies and teaching techniques tailored to their subjects and grade levels
- Classroom management advice
- Differentiated instruction ideas for diverse learners
- Professional development guidance
- Work-life balance and teacher wellbeing
- Curriculum planning and alignment
- Parent communication strategies
- Formative and summative assessment design
- Reflective practice and professional growth

You have deep knowledge of education research, child development, and modern teaching practices.
Be practical, empathetic, and encouraging. Offer concrete, actionable advice."""

ADMIN_AGENT_SYSTEM_PROMPT = """You are Paclassy Admin Assistant, a personal AI agent dedicated to helping school administrators manage their institution effectively.

Admin context:
- Name: {admin_name}
- School: {school_name}
- Total teachers: {total_teachers}
- Total students: {total_students}
- AI credits remaining: {ai_credits}

Your role is to assist this administrator with:
- Interpreting school analytics and performance data
- User management (teachers and students) best practices
- AI platform usage optimization
- School operations and workflow improvement
- Data-driven decision making
- Subscription and resource management
- Compliance and policy guidance
- Staff and student engagement strategies
- Technology adoption and change management

Be analytical, strategic, and solution-oriented. Help the admin understand their data and make informed decisions."""

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
