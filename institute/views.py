from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.db.models import Max
from datetime import datetime
import re

from .models import (
    Exam,
    ExamMock,
    ExamNote,
    ExamQuestion,
    ExamSection,
    ExamMockAttempt,
    StudentAchievement,
    InstituteCertificate,
    InstituteCourse,
)


MOCK_COUNT = 3
QUESTIONS_PER_MOCK = 10

DIFFICULTY_CONFIG = {
    'easy': {
        'label': 'Easy',
        'question_count': 8,
        'timer_seconds': 20 * 60,
        'rotation_bias': 0,
    },
    'medium': {
        'label': 'Medium',
        'question_count': 10,
        'timer_seconds': 15 * 60,
        'rotation_bias': 1,
    },
    'hard': {
        'label': 'Hard',
        'question_count': 12,
        'timer_seconds': 10 * 60,
        'rotation_bias': 2,
    },
}

COURSE_SECTION_ORDER = [
    {
        'key': 'programming-languages',
        'title': 'Programming Languages',
        'description': 'Core coding tracks for software development foundations.',
    },
    {
        'key': 'frontend-development',
        'title': 'Frontend Development',
        'description': 'Client-side UI development with modern web technologies.',
    },
    {
        'key': 'full-stack-development',
        'title': 'Full Stack Development',
        'description': 'End-to-end application development across frontend, backend, and deployment.',
    },
    {
        'key': 'database-analytics',
        'title': 'SQL and Data Analytics',
        'description': 'Database querying, data modeling, and reporting skills.',
    },
    {
        'key': 'computer-science',
        'title': 'Computer Science Foundations',
        'description': 'Data structures and algorithmic thinking for problem solving.',
    },
    {
        'key': 'entrance-exams',
        'title': 'EAPCET and JEE Mains',
        'description': 'Focused preparation plans for engineering entrance exams.',
    },
    {
        'key': 'mpc-foundation',
        'title': 'Mathematics, Physics, Chemistry',
        'description': 'Academic core subjects for board and entrance depth.',
    },
    {
        'key': 'aptitude-reasoning',
        'title': 'Aptitude and Logical Reasoning',
        'description': 'Placement-focused quant, verbal, and reasoning preparation.',
    },
]


def _build_generic_quiz(title):
    return [
        {
            'question': f'What is the primary goal of learning {title}?',
            'options': [
                'To build practical skill with real scenarios',
                'To memorize only theory without practice',
                'To avoid using tools and projects',
                'To skip fundamentals and start advanced topics only',
            ],
            'answer': 0,
            'explanation': f'{title} is best learned by combining concept clarity with practical exercises and projects.',
        },
        {
            'question': f'Which approach is best while studying {title}?',
            'options': [
                'Randomly reading topics without sequence',
                'Learning fundamentals, practicing regularly, and revising',
                'Skipping exercises and only watching videos',
                'Learning only interview questions first',
            ],
            'answer': 1,
            'explanation': 'Structured learning with regular practice and revision gives long-term retention and confidence.',
        },
        {
            'question': 'Why are mini projects important during course preparation?',
            'options': [
                'They are not important for learning',
                'They help convert concepts into implementation skills',
                'They are only useful after course completion',
                'They replace all theory and fundamentals',
            ],
            'answer': 1,
            'explanation': 'Projects force you to apply ideas, debug problems, and build confidence with real implementation.',
        },
        {
            'question': 'What is the best way to improve speed and accuracy in tests?',
            'options': [
                'Attempting without reviewing mistakes',
                'Avoiding timed practice',
                'Practicing timed sets and analyzing wrong answers',
                'Reading only notes before exam day',
            ],
            'answer': 2,
            'explanation': 'Timed practice plus detailed error analysis directly improves exam performance over time.',
        },
        {
            'question': 'What should you do after getting a wrong answer?',
            'options': [
                'Skip and move on quickly',
                'Blame the question quality',
                'Reattempt the same mistake repeatedly',
                'Study explanation, revise concept, and retry similar question',
            ],
            'answer': 3,
            'explanation': 'Reviewing explanation and revising the concept is the fastest way to avoid repeating mistakes.',
        },
        {
            'question': f'Which habit improves long-term progress in {title}?',
            'options': [
                'Only studying one day before exam',
                'Regular daily practice with small goals',
                'Skipping revision completely',
                'Using random topics without order',
            ],
            'answer': 1,
            'explanation': 'Consistency with small goals builds better retention and confidence than last-minute study.',
        },
        {
            'question': 'Why is revision necessary during course preparation?',
            'options': [
                'To overwrite learned concepts',
                'To reduce understanding of fundamentals',
                'To strengthen memory and reduce mistakes',
                'To avoid problem solving',
            ],
            'answer': 2,
            'explanation': 'Revision reinforces concepts and helps reduce repeated mistakes in tests and assignments.',
        },
        {
            'question': f'What is a good strategy to master {title} concepts?',
            'options': [
                'Read theory and avoid implementation',
                'Implement concepts with examples and exercises',
                'Copy answers without understanding',
                'Ignore foundational topics',
            ],
            'answer': 1,
            'explanation': 'Implementation plus guided practice helps convert theory into usable problem-solving skill.',
        },
        {
            'question': 'How should you approach mock test analysis?',
            'options': [
                'Focus only on score and ignore mistakes',
                'Review wrong answers and note concept gaps',
                'Retake without understanding errors',
                'Skip the explanation section',
            ],
            'answer': 1,
            'explanation': 'Mock analysis is useful only when mistakes are traced back to concepts and corrected.',
        },
        {
            'question': 'What improves performance most in timed assessments?',
            'options': [
                'No time planning',
                'Guessing all difficult questions',
                'Balancing speed, accuracy, and review',
                'Skipping easy questions first',
            ],
            'answer': 2,
            'explanation': 'Balanced time strategy improves both accuracy and completion under exam conditions.',
        },
        {
            'question': f'When learning {title}, why are fundamentals critical?',
            'options': [
                'Advanced topics depend on basic understanding',
                'Fundamentals are not useful in projects',
                'They only help in theory exams',
                'They can be skipped after first class',
            ],
            'answer': 0,
            'explanation': 'Strong fundamentals make advanced concepts easier and reduce confusion during implementation.',
        },
        {
            'question': 'What is the best post-class practice approach?',
            'options': [
                'No practice until weekend',
                'Quick recap, 2-3 practice problems, and summary notes',
                'Only watch videos repeatedly',
                'Jump directly to unrelated topics',
            ],
            'answer': 1,
            'explanation': 'Immediate recap and a few problems after class helps cement learning effectively.',
        },
        {
            'question': 'Why should you maintain personal notes while preparing?',
            'options': [
                'To increase confusion',
                'To avoid using official material',
                'To create quick revision references',
                'To replace all practice exercises',
            ],
            'answer': 2,
            'explanation': 'Personal notes make last-minute revision faster and capture your weak areas clearly.',
        },
        {
            'question': 'How can you improve confidence before final tests?',
            'options': [
                'Avoid mock tests',
                'Practice with section-wise and full-length mocks',
                'Skip weak topics',
                'Attempt only theoretical questions',
            ],
            'answer': 1,
            'explanation': 'Section-wise and full mocks simulate exam pressure and improve confidence.',
        },
        {
            'question': f'What makes {title} learning job-ready?',
            'options': [
                'Memorizing definitions only',
                'Combining fundamentals, projects, and problem-solving',
                'Skipping coding/practical tasks',
                'Studying without feedback',
            ],
            'answer': 1,
            'explanation': 'Job readiness comes from practical application, not only theoretical knowledge.',
        },
    ]


def _get_mock_number(raw_value):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return 1
    return max(1, min(MOCK_COUNT, value))


def _slugify_topic(value):
    cleaned = ''.join(ch.lower() if ch.isalnum() else '-' for ch in value)
    while '--' in cleaned:
        cleaned = cleaned.replace('--', '-')
    return cleaned.strip('-') or 'topic'


def _get_difficulty(raw_value):
    if raw_value in DIFFICULTY_CONFIG:
        return raw_value
    return 'medium'


def _get_topic_choices(course):
    choices = []
    seen = set()
    for topic_name in course.get('syllabus', [])[:5]:
        slug = _slugify_topic(topic_name)
        if slug in seen:
            continue
        seen.add(slug)
        choices.append({'slug': slug, 'name': topic_name})
    return choices


def _get_topic_slug(course, raw_value):
    if not raw_value:
        return ''
    valid_slugs = {choice['slug'] for choice in _get_topic_choices(course)}
    return raw_value if raw_value in valid_slugs else ''


def _filter_questions_by_topic(course, question_bank, topic_slug):
    if not topic_slug or not question_bank:
        return question_bank

    topic_choices = _get_topic_choices(course)
    if not topic_choices:
        return question_bank

    topic_index = None
    for idx, choice in enumerate(topic_choices):
        if choice['slug'] == topic_slug:
            topic_index = idx
            break

    if topic_index is None:
        return question_bank

    chunk_size = max(1, len(question_bank) // len(topic_choices))
    start = topic_index * chunk_size
    end = start + chunk_size
    topic_questions = question_bank[start:end]
    return topic_questions if topic_questions else question_bank


def _get_mock_questions(course, mock_number, difficulty, topic_slug):
    base_questions = _filter_questions_by_topic(course, course['quiz'], topic_slug)
    if not base_questions:
        return []

    difficulty_config = DIFFICULTY_CONFIG[difficulty]
    question_count = difficulty_config['question_count']

    # Rotate the question bank by mock number and difficulty to vary each attempt.
    shift = ((mock_number - 1) * 3 + difficulty_config['rotation_bias'] * 2) % len(base_questions)
    ordered = base_questions[shift:] + base_questions[:shift]

    questions = []
    idx = 0
    while len(questions) < question_count:
        questions.append(ordered[idx % len(ordered)])
        idx += 1

    return questions


COURSE_CATALOG = [
    {
        'slug': 'c-language',
        'category': 'programming-languages',
        'title': 'C Language',
        'icon_sprite': 'c-language',
        'icon': '⌨️',
        'summary': 'Foundation programming with problem-solving basics.',
        'overview': 'This course builds strong programming fundamentals including syntax, logic building, functions, arrays, and pointers with hands-on coding tasks.',
        'syllabus': [
            'C basics, variables, data types, operators',
            'Conditional statements and loops',
            'Functions and recursion',
            'Arrays, strings, and pointers',
            'Structures and file handling',
            'Mini programs and logic practice',
        ],
        'notes_pdf': 'C Language.pdf',
        'quiz': _build_generic_quiz('C Language'),
    },
    {
        'slug': 'python',
        'category': 'programming-languages',
        'title': 'Python',
        'icon_sprite': 'python-course',
        'icon': '💻',
        'summary': 'Core to advanced Python for real project building.',
        'overview': 'Python training covers syntax, data structures, functions, modules, OOP, and practical scripting with project-based assignments.',
        'syllabus': [
            'Python syntax and control flow',
            'Lists, tuples, sets, dictionaries',
            'Functions, modules, and exceptions',
            'Object-oriented programming',
            'File handling and automation scripts',
            'Project-oriented coding sessions',
        ],
        'notes_pdf': 'Python.pdf',
        'quiz': _build_generic_quiz('Python'),
    },
    {
        'slug': 'html-css-javascript',
        'category': 'frontend-development',
        'title': 'HTML, CSS, JavaScript',
        'icon_sprite': 'frontend-web',
        'icon': '🌐',
        'summary': 'Frontend development from basics to responsive UI.',
        'overview': 'This web development track teaches page structure, styling, responsiveness, and JavaScript DOM for interactive UI building.',
        'syllabus': [
            'HTML document structure and semantic tags',
            'CSS selectors, layout, box model, flex and grid',
            'JavaScript basics and DOM manipulation',
            'Events, forms, validation, and dynamic updates',
            'DOM traversal, nodes, collections, and NodeList',
            'Mini projects: Todo app, quiz app, image filters, form apps',
        ],
        'notes_pdf': 'DCA Notes.pdf',
        'quiz': [
            {
                'question': 'What does DOM stand for in JavaScript?',
                'options': ['Document Object Model', 'Data Object Mapping', 'Dynamic Object Model', 'Document Orientation Method'],
                'answer': 0,
                'explanation': 'DOM means Document Object Model and represents the page as a tree of nodes that JavaScript can manipulate.',
            },
            {
                'question': 'Which method returns the first element matching a CSS selector?',
                'options': ['getElementsByClassName()', 'querySelector()', 'querySelectorAll()', 'getElementsByTagName()'],
                'answer': 1,
                'explanation': 'querySelector() returns only the first matching element, while querySelectorAll() returns all matches.',
            },
            {
                'question': 'Which property is suitable to update only visible text content?',
                'options': ['innerText', 'outerHTML', 'childNodes', 'nodeType'],
                'answer': 0,
                'explanation': 'innerText updates visible text while respecting layout and visibility rules.',
            },
            {
                'question': 'Why do we use e.preventDefault() in form submission?',
                'options': ['To refresh the page', 'To disable JavaScript', 'To stop default form submit behavior', 'To hide the form'],
                'answer': 2,
                'explanation': 'preventDefault() is used to stop browser default behavior so validation/custom logic can run first.',
            },
            {
                'question': 'Which API is preferred for smooth browser animation loops?',
                'options': ['setTimeout only', 'setInterval only', 'requestAnimationFrame()', 'document.write()'],
                'answer': 2,
                'explanation': 'requestAnimationFrame() syncs with browser rendering and gives smoother, efficient animations.',
            },
            {
                'question': 'Which method returns all matching elements for a CSS selector?',
                'options': ['querySelectorAll()', 'getElementById()', 'innerText', 'setAttribute()'],
                'answer': 0,
                'explanation': 'querySelectorAll() returns a static NodeList of all matching elements.',
            },
            {
                'question': 'Which event is commonly used to react to user typing in an input?',
                'options': ['submit', 'input', 'blur', 'load'],
                'answer': 1,
                'explanation': 'The input event fires whenever the value of an input/textarea changes while typing.',
            },
            {
                'question': 'What is the purpose of classList.toggle()?',
                'options': ['Deletes an element', 'Adds or removes a class conditionally', 'Gets computed styles', 'Finds parent node'],
                'answer': 1,
                'explanation': 'classList.toggle() applies a class if missing and removes it if already present.',
            },
            {
                'question': 'Which property gives all child element nodes (not text nodes)?',
                'options': ['childNodes', 'children', 'firstChild', 'nextSibling'],
                'answer': 1,
                'explanation': 'children returns only element children, while childNodes includes text/comment nodes too.',
            },
            {
                'question': 'Which function is used to prevent form submission and handle it manually?',
                'options': ['stopPropagation()', 'e.preventDefault()', 'remove()', 'appendChild()'],
                'answer': 1,
                'explanation': 'e.preventDefault() cancels browser default behavior like form submission.',
            },
            {
                'question': 'How do you create a new element node in JavaScript?',
                'options': ['document.newElement()', 'document.createElement()', 'append()', 'querySelector()'],
                'answer': 1,
                'explanation': 'document.createElement(tagName) creates a new element node in memory.',
            },
            {
                'question': 'What does event.target represent?',
                'options': ['The first element in DOM', 'The element that triggered the event', 'Current CSS rule', 'Current browser URL'],
                'answer': 1,
                'explanation': 'event.target points to the specific element where the event occurred.',
            },
        ],
    },
    {
        'slug': 'java',
        'category': 'programming-languages',
        'title': 'Java',
        'icon_sprite': 'java-course',
        'icon': '☕',
        'summary': 'Object-oriented programming and application concepts.',
        'overview': 'Java course includes OOP fundamentals and an interview-focused Data Structures and Algorithms track with problem solving.',
        'syllabus': [
            'Java syntax, classes, objects, and OOP principles',
            'Arrays, linked lists, stacks, queues, hashing, trees, graphs',
            'Searching, sorting, recursion, backtracking, dynamic programming',
            'Time complexity and space complexity analysis',
            'LeetCode practice set: Two Sum, Maximum Subarray, Shuffle Array, etc.',
            'Hands-on coding drills and interview preparation',
        ],
        'notes_pdf': None,
        'quiz': [
            {
                'question': 'Which data structure follows Last-In-First-Out order?',
                'options': ['Queue', 'Stack', 'Linked List', 'Graph'],
                'answer': 1,
                'explanation': 'Stack uses LIFO behavior where the most recently inserted item is removed first.',
            },
            {
                'question': 'What is the average time complexity of HashMap get/put operations?',
                'options': ['O(n)', 'O(log n)', 'O(1)', 'O(n log n)'],
                'answer': 2,
                'explanation': 'HashMap provides average O(1) lookup and insertion due to hashing.',
            },
            {
                'question': 'Binary search works correctly on which type of array?',
                'options': ['Random unsorted array', 'Sorted array', 'Array with unique only', '2D array only'],
                'answer': 1,
                'explanation': 'Binary search relies on sorted order to discard half the search space each step.',
            },
            {
                'question': 'Merge sort has which time complexity in all cases?',
                'options': ['O(n^2)', 'O(log n)', 'O(n log n)', 'O(n)'],
                'answer': 2,
                'explanation': 'Merge sort divides and merges recursively with O(n log n) time complexity.',
            },
            {
                'question': 'Why is complexity analysis important in DSA?',
                'options': ['Only for theory exams', 'To estimate scalability and performance', 'To reduce syntax errors only', 'To avoid writing functions'],
                'answer': 1,
                'explanation': 'Complexity analysis helps compare algorithm efficiency and choose scalable solutions.',
            },
            {
                'question': 'Which data structure is best to represent hierarchical data?',
                'options': ['Queue', 'HashMap', 'Tree', 'Stack'],
                'answer': 2,
                'explanation': 'Tree structure is ideal for hierarchical relationships like file systems and org charts.',
            },
            {
                'question': 'What is the worst-case time complexity of linear search?',
                'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'],
                'answer': 2,
                'explanation': 'Linear search may need to check every element, giving O(n) worst case.',
            },
            {
                'question': 'Which algorithmic strategy solves problems by combining optimal subproblems?',
                'options': ['Greedy only', 'Dynamic Programming', 'Brute force only', 'Hashing'],
                'answer': 1,
                'explanation': 'Dynamic Programming stores subproblem results and combines them optimally.',
            },
            {
                'question': 'What is the average time complexity of binary search?',
                'options': ['O(log n)', 'O(n)', 'O(1)', 'O(n²)'],
                'answer': 0,
                'explanation': 'Binary search halves search space each step, leading to O(log n).',
            },
            {
                'question': 'Which traversal uses a queue in graphs/trees?',
                'options': ['DFS', 'BFS', 'Inorder', 'Postorder only'],
                'answer': 1,
                'explanation': 'Breadth First Search processes nodes level by level using a queue.',
            },
            {
                'question': 'Which sort is stable and guaranteed O(n log n)?',
                'options': ['Bubble Sort', 'Selection Sort', 'Merge Sort', 'Insertion Sort'],
                'answer': 2,
                'explanation': 'Merge Sort guarantees O(n log n) time and is stable with extra space usage.',
            },
            {
                'question': 'What is the purpose of recursion base case?',
                'options': ['To increase memory usage', 'To terminate recursive calls safely', 'To sort arrays automatically', 'To replace loops entirely'],
                'answer': 1,
                'explanation': 'Base case stops recursion and prevents infinite function calls.',
            },
        ],
    },
    {
        'slug': 'sql',
        'category': 'database-analytics',
        'title': 'SQL',
        'icon_sprite': 'sql-course',
        'icon': '🗄️',
        'summary': 'Database querying, design, and optimization skills.',
        'overview': 'SQL training covers relational databases, query writing, joins, aggregation, indexing, and optimization best practices.',
        'syllabus': [
            'RDBMS concepts and table design',
            'SELECT, WHERE, GROUP BY, HAVING, ORDER BY',
            'Joins, subqueries, and views',
            'Constraints, keys, normalization basics',
            'Indexes and query optimization',
            'Real-world query practice sessions',
        ],
        'notes_pdf': 'DCA Notes.pdf',
        'quiz': _build_generic_quiz('SQL'),
    },
    {
        'slug': 'data-structures',
        'category': 'computer-science',
        'title': 'Data Structures',
        'icon_sprite': 'data-structures',
        'icon': '📚',
        'summary': 'Efficient coding using linear and non-linear structures.',
        'overview': 'Data Structures course focuses on implementing and applying core structures to solve problems efficiently.',
        'syllabus': [
            'Arrays, linked lists, stacks, queues',
            'Trees, binary search trees, heaps',
            'Hashing and hash tables',
            'Graphs and traversals',
            'Use-case based implementation practice',
        ],
        'notes_pdf': None,
        'quiz': _build_generic_quiz('Data Structures'),
    },
    {
        'slug': 'algorithms',
        'category': 'computer-science',
        'title': 'Algorithms',
        'icon_sprite': 'algorithms',
        'icon': '⚙️',
        'summary': 'Logic building and time-complexity focused coding.',
        'overview': 'Algorithm training helps students solve problems with better logic, optimization strategy, and complexity awareness.',
        'syllabus': [
            'Searching and sorting algorithms',
            'Recursion and divide-conquer',
            'Greedy methods and dynamic programming',
            'Graph algorithms and shortest path basics',
            'Complexity analysis and optimization drills',
        ],
        'notes_pdf': None,
        'quiz': _build_generic_quiz('Algorithms'),
    },
    {
        'slug': 'power-bi',
        'category': 'database-analytics',
        'title': 'Power BI',
        'icon_sprite': 'power-bi',
        'icon': '📊',
        'summary': 'Business dashboards and data visualization workflows.',
        'overview': 'Power BI training includes data cleaning, modeling, DAX basics, and creating interactive dashboards for business reporting.',
        'syllabus': [
            'Power BI interface and data import',
            'Data transformation with Power Query',
            'Data model relationships',
            'DAX basics and calculated measures',
            'Dashboard design and storytelling',
        ],
        'notes_pdf': 'DCA Notes.pdf',
        'quiz': _build_generic_quiz('Power BI'),
    },
    {
        'slug': 'bootstrap',
        'category': 'frontend-development',
        'title': 'Bootstrap',
        'icon_sprite': 'bootstrap-course',
        'icon': '🧩',
        'summary': 'Fast UI design with component-based layout system.',
        'overview': 'Bootstrap course teaches responsive layout systems, utility classes, and reusable UI components for rapid frontend development.',
        'syllabus': [
            'Grid system and responsive breakpoints',
            'Typography, spacing, and utility classes',
            'Buttons, cards, navbars, forms',
            'Modals and interactive components',
            'Responsive page mini projects',
        ],
        'notes_pdf': 'DCA Notes.pdf',
        'quiz': _build_generic_quiz('Bootstrap'),
    },
    {
        'slug': 'full-stack-web-development',
        'category': 'full-stack-development',
        'title': 'Full Stack Web Development',
        'icon_sprite': 'full-stack',
        'icon': '🚀',
        'summary': 'End-to-end web development with deployment guidance.',
        'scope_tags': ['Frontend', 'Backend', 'Database', 'Deployment'],
        'overview': 'This full stack track covers frontend, backend, databases, APIs, and deployment workflow with project implementation.',
        'syllabus': [
            'Frontend fundamentals and responsive design',
            'Backend architecture and API basics',
            'Database modeling and CRUD operations',
            'Authentication and role management',
            'Deployment and production readiness',
        ],
        'notes_pdf': 'DCA Notes.pdf',
        'quiz': _build_generic_quiz('Full Stack Web Development'),
    },
    {
        'slug': 'eapcet-jee-mains',
        'category': 'entrance-exams',
        'title': 'EAPCET and JEE Mains',
        'icon_sprite': 'exam-prep',
        'icon': '🎯',
        'summary': 'Focused preparation strategy with regular practice.',
        'overview': 'Entrance exam coaching with concept clarity, timed tests, revision plans, and detailed performance analysis.',
        'syllabus': [
            'Exam pattern and smart preparation planning',
            'Concept revision and chapter-wise practice',
            'Previous year question strategy',
            'Timed mock tests and analysis',
            'Final revision and score improvement methods',
        ],
        'notes_pdf': None,
        'quiz': _build_generic_quiz('EAPCET and JEE Mains'),
    },
    {
        'slug': 'mathematics-physics-chemistry',
        'category': 'mpc-foundation',
        'title': 'Mathematics, Physics, Chemistry',
        'icon_sprite': 'mpc-foundation',
        'icon': '📐',
        'summary': 'Concept-driven academics for entrance exam success.',
        'overview': 'MPC foundation course for strong conceptual understanding and problem-solving depth for board and entrance exams.',
        'syllabus': [
            'Core mathematics concepts and speed drills',
            'Physics fundamentals and numerical approach',
            'Chemistry theory with reaction/problem practice',
            'Mixed subject tests and concept revision',
            'Exam strategy and error reduction methods',
        ],
        'notes_pdf': None,
        'quiz': _build_generic_quiz('Mathematics, Physics, Chemistry'),
    },
    {
        'slug': 'general-aptitude',
        'category': 'aptitude-reasoning',
        'title': 'General Aptitude',
        'icon_sprite': 'aptitude',
        'icon': '🧠',
        'summary': 'Quant and verbal aptitude for placements and exams.',
        'overview': 'General aptitude training for placements and exams with quant shortcuts, verbal logic, and timed practice modules.',
        'syllabus': [
            'Arithmetic and percentage-based problem solving',
            'Time-speed-distance and work-time concepts',
            'Verbal aptitude and reading comprehension',
            'Data interpretation basics',
            'Timed aptitude sets and analysis',
        ],
        'notes_pdf': None,
        'quiz': _build_generic_quiz('General Aptitude'),
    },
    {
        'slug': 'logical-reasoning',
        'category': 'aptitude-reasoning',
        'title': 'Logical Reasoning',
        'icon_sprite': 'logical-reasoning',
        'icon': '🔍',
        'summary': 'Analytical thinking and structured problem solving.',
        'overview': 'Logical reasoning course focuses on patterns, analytical puzzles, and decision-based question solving strategies.',
        'syllabus': [
            'Series, analogies, and classification',
            'Coding-decoding and blood relation',
            'Direction and arrangement problems',
            'Syllogisms and logical statements',
            'Timed reasoning practice and explanation review',
        ],
        'notes_pdf': None,
        'quiz': _build_generic_quiz('Logical Reasoning'),
    },
]


def _course_by_slug(slug):
    for course in COURSE_CATALOG:
        if course['slug'] == slug:
            return course
    return None


def _admin_course_by_slug(slug):
    course = InstituteCourse.objects.filter(slug=slug, is_active=True).first()
    if not course:
        return None

    syllabus_items = [item.strip() for item in (course.syllabus or '').splitlines() if item.strip()]
    return {
        'slug': course.slug,
        'category': course.section_key,
        'title': course.title,
        'icon_sprite': course.icon_sprite,
        'summary': course.summary,
        'overview': course.overview or course.summary,
        'syllabus': syllabus_items or ['Syllabus will be updated soon.'],
        'notes_pdf': None,
        'notes_url': course.notes_url,
        'quiz': _build_generic_quiz(course.title),
    }


def _course_payload_by_slug(slug):
    course = _course_by_slug(slug)
    if course:
        return course
    return _admin_course_by_slug(slug)


def _related_exam_mocks_for_course(course):
    base_qs = (
        ExamMock.objects.filter(
            is_active=True,
            section__is_active=True,
            section__exam__is_active=True,
        )
        .select_related('section', 'section__exam')
        .order_by('section__exam__display_order', 'section__display_order', 'display_order', 'title')
    )

    slug = (course.get('slug') or '').lower()
    exact_map = {
        'c-language': ['c language'],
        'python': ['python'],
        'html-css-javascript': ['html', 'css', 'javascript'],
        'java': ['java'],
        'sql': ['sql'],
        'data-structures': ['data structures'],
        'algorithms': ['algorithm'],
        'power-bi': ['power bi'],
        'bootstrap': ['bootstrap'],
        'full-stack-web-development': [],
        'eapcet-jee-mains': ['eapcet', 'jee mains', 'jee'],
        'mathematics-physics-chemistry': ['mathematics', 'physics', 'chemistry'],
        'general-aptitude': ['aptitude'],
        'logical-reasoning': ['reasoning', 'logical reasoning'],
    }

    mapped = exact_map.get(slug, [])
    if not mapped:
        return []

    filtered = []
    for mock in base_qs:
        haystack = f"{mock.title} {mock.section.title} {mock.section.exam.title}".lower()
        if any(re.search(rf'(?<!\w){re.escape(token.lower())}(?!\w)', haystack) for token in mapped):
            filtered.append(mock)

    return filtered[:8]


def _group_courses_for_home():
    admin_courses = list(InstituteCourse.objects.filter(is_active=True).order_by('display_order', 'id'))
    if admin_courses:
        grouped = []
        grouped_map = {}
        section_lookup = {section['key']: section for section in COURSE_SECTION_ORDER}

        for course in admin_courses:
            section = section_lookup.get(course.section_key, {})
            section_key = course.section_key

            if section_key not in grouped_map:
                group = {
                    'key': section_key,
                    'title': section.get('title') or course.section_title or course.section_key.replace('-', ' ').title(),
                    'description': section.get('description') or course.section_description,
                    'courses': [],
                }
                grouped_map[section_key] = group
                grouped.append(group)

            grouped_map[section_key]['courses'].append(
                {
                    'slug': course.slug,
                    'title': course.title,
                    'icon_sprite': course.icon_sprite,
                    'summary': course.summary,
                    'scope_tags': [],
                    'detail_available': _course_payload_by_slug(course.slug) is not None,
                }
            )

        return grouped

    grouped = []
    for section in COURSE_SECTION_ORDER:
        courses = [course for course in COURSE_CATALOG if course.get('category') == section['key']]
        if not courses:
            continue
        grouped.append(
            {
                'key': section['key'],
                'title': section['title'],
                'description': section['description'],
                'courses': courses,
            }
        )
    return grouped


def institute_home(request):
    course_sections = _group_courses_for_home()
    all_courses = [course for section in course_sections for course in section['courses']]
    student_reviews = list(
        StudentAchievement.objects.filter(is_active=True, show_on_home=True)
        .order_by('display_order', 'id')[:20]
    )
    return render(
        request,
        'institute/home.html',
        {
            'course_sections': course_sections,
            'preview_courses': all_courses[:6],
            'all_courses': all_courses,
            'student_reviews': student_reviews,
        },
    )


def institute_courses(request):
    course_sections = _group_courses_for_home()
    all_courses = [course for section in course_sections for course in section['courses']]
    return render(
        request,
        'institute/courses.html',
        {
            'course_sections': course_sections,
            'all_courses': all_courses,
        },
    )


def institute_certificates(request):
    certificate_records = list(
        InstituteCertificate.objects.filter(is_active=True)
        .order_by('certificate_id')
        .values('certificate_id', 'student_name', 'course_name', 'completed_on', 'certificate_image_url')
    )

    for item in certificate_records:
        item['completed_on'] = item['completed_on'].isoformat() if item['completed_on'] else ''

    return render(
        request,
        'institute/certificates.html',
        {
            'certificate_records': certificate_records,
            'default_certificate_image_url': 'https://www.prathibhainstitutions.com/images/0.%20CERTIFICATE.jpg',
        },
    )


def institute_gallery(request):
    return render(request, 'institute/gallery.html')


def course_detail(request, slug):
    course = _course_payload_by_slug(slug)
    if not course:
        raise Http404('Course not found')

    exam_mock_links = _related_exam_mocks_for_course(course)

    return render(
        request,
        'institute/course_detail.html',
        {
            'course': course,
            'mock_count': MOCK_COUNT,
            'difficulty_options': DIFFICULTY_CONFIG,
            'topic_choices': _get_topic_choices(course),
            'exam_mock_links': exam_mock_links,
        },
    )


@login_required
def exam_attempt_history(request):
    attempts = list(
        ExamMockAttempt.objects.filter(student=request.user)
        .select_related('mock', 'mock__section', 'mock__section__exam')
        .order_by('-submitted_at')
    )
    return render(
        request,
        'institute/exam_attempt_history.html',
        {
            'attempts': attempts,
        },
    )


def course_test(request, slug):
    course = _course_payload_by_slug(slug)
    if not course:
        raise Http404('Course not found')

    mock_number = _get_mock_number(request.GET.get('mock'))
    difficulty = _get_difficulty(request.GET.get('difficulty'))
    topic_slug = _get_topic_slug(course, request.GET.get('topic'))
    if request.method == 'POST':
        mock_number = _get_mock_number(request.POST.get('mock_number'))
        difficulty = _get_difficulty(request.POST.get('difficulty'))
        topic_slug = _get_topic_slug(course, request.POST.get('topic'))

    mock_questions = _get_mock_questions(course, mock_number, difficulty, topic_slug)
    topic_choices = _get_topic_choices(course)
    selected_topic_name = ''
    for choice in topic_choices:
        if choice['slug'] == topic_slug:
            selected_topic_name = choice['name']
            break
    timer_seconds = DIFFICULTY_CONFIG[difficulty]['timer_seconds']

    if request.method == 'POST':
        results = []
        score = 0

        for idx, question in enumerate(mock_questions):
            selected_raw = request.POST.get(f'q{idx}')
            selected_index = int(selected_raw) if selected_raw and selected_raw.isdigit() else None
            is_correct = selected_index == question['answer']
            if is_correct:
                score += 1

            results.append({
                'question': question['question'],
                'options': question['options'],
                'selected_index': selected_index,
                'correct_index': question['answer'],
                'selected_text': question['options'][selected_index] if selected_index is not None and selected_index < len(question['options']) else None,
                'correct_text': question['options'][question['answer']],
                'is_correct': is_correct,
                'explanation': question['explanation'],
            })

        total = len(mock_questions)
        percent = round((score / total) * 100, 2) if total else 0

        return render(
            request,
            'institute/course_result.html',
            {
                'course': course,
                'results': results,
                'score': score,
                'total': total,
                'percent': percent,
                'mock_number': mock_number,
                'mock_count': MOCK_COUNT,
                'difficulty': difficulty,
                'difficulty_label': DIFFICULTY_CONFIG[difficulty]['label'],
                'topic_slug': topic_slug,
                'topic_name': selected_topic_name,
            },
        )

    return render(
        request,
        'institute/course_test.html',
        {
            'course': course,
            'mock_questions': mock_questions,
            'mock_number': mock_number,
            'mock_count': MOCK_COUNT,
            'difficulty': difficulty,
            'difficulty_label': DIFFICULTY_CONFIG[difficulty]['label'],
            'topic_slug': topic_slug,
            'topic_choices': topic_choices,
            'timer_seconds': timer_seconds,
        },
    )
DEFAULT_EXAM_CATEGORIES = [
    {
        'title': 'EAPCET 2026 Test Series',
        'description': 'A crucial entrance exam for engineering and medical streams.',
    },
    {
        'title': 'JEE Mains',
        'description': "One of India's most important engineering entrance exams.",
    },
    {
        'title': 'Programming Challenges',
        'description': 'Test your coding skills with competitive programming contests.',
    },
    {
        'title': 'Aptitude Tests',
        'description': 'Prepare for top recruitment exams with challenging aptitude tests.',
    },
]


def exam_home(request):
    exam_categories = list(Exam.objects.filter(is_active=True).order_by('display_order', 'title'))
    if not exam_categories:
        exam_categories = DEFAULT_EXAM_CATEGORIES

    return render(
        request,
        'institute/exam_home.html',
        {
            'exam_categories': exam_categories,
        }
    )


def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    sections = list(exam.sections.filter(is_active=True).order_by('display_order', 'title'))
    return render(
        request,
        'institute/exam_detail.html',
        {
            'exam': exam,
            'sections': sections,
        },
    )


def exam_section_detail(request, section_id):
    section = get_object_or_404(ExamSection.objects.select_related('exam'), id=section_id, is_active=True)
    notes = list(section.notes.filter(is_active=True).order_by('display_order', 'title'))
    mocks = list(section.mocks.filter(is_active=True).order_by('display_order', 'title'))

    for mock in mocks:
        local_question_count = mock.questions.filter(is_active=True).count()
        mock.local_question_count = local_question_count
        if not mock.question_count:
            mock.question_count = local_question_count

    return render(
        request,
        'institute/exam_section_detail.html',
        {
            'exam': section.exam,
            'section': section,
            'notes': notes,
            'mocks': mocks,
        },
    )


@login_required
@never_cache
def exam_mock_test(request, section_id, mock_id):
    section = get_object_or_404(ExamSection.objects.select_related('exam'), id=section_id, is_active=True)
    mock = get_object_or_404(ExamMock, id=mock_id, section=section, is_active=True)
    questions = list(mock.questions.filter(is_active=True).order_by('display_order', 'id'))
    session_key = f'exam_mock_start_{mock.id}'

    if not questions and mock.test_url:
        return render(
            request,
            'institute/exam_mock_result.html',
            {
                'exam': section.exam,
                'section': section,
                'mock': mock,
                'results': [],
                'score': 0,
                'total': 0,
                'percent': 0,
                'external_only': True,
            },
        )

    if request.method == 'GET':
        request.session[session_key] = timezone.now().isoformat()

    if request.method == 'POST':
        results = []
        score = 0
        warning_count = max(0, int((request.POST.get('warning_count') or '0').strip() or '0'))
        auto_submit_reason = (request.POST.get('auto_submit_reason') or '').strip()

        for idx, question in enumerate(questions):
            selected_option = (request.POST.get(f'q{question.id}') or '').strip().upper()
            is_correct = selected_option == question.correct_option
            if is_correct:
                score += 1

            options = {
                'A': question.option_a,
                'B': question.option_b,
                'C': question.option_c,
                'D': question.option_d,
            }

            results.append(
                {
                    'index': idx + 1,
                    'question_text': question.question_text,
                    'diagram_image': question.diagram_image,
                    'diagram_image_url': question.diagram_image_url,
                    'options': options,
                    'selected_option': selected_option,
                    'correct_option': question.correct_option,
                    'is_correct': is_correct,
                    'explanation': question.explanation,
                }
            )

        total = len(questions)
        percent = round((score / total) * 100, 2) if total else 0
        started_at = None
        started_at_raw = request.session.get(session_key)
        if started_at_raw:
            started_at = datetime.fromisoformat(started_at_raw)
            if timezone.is_naive(started_at):
                started_at = timezone.make_aware(started_at, timezone.get_current_timezone())

        attempt = ExamMockAttempt.objects.create(
            student=request.user,
            mock=mock,
            score=score,
            total_questions=total,
            percent=percent,
            warning_count=warning_count,
            auto_submitted=bool(auto_submit_reason),
            auto_submit_reason=auto_submit_reason,
            started_at=started_at,
        )
        request.session.pop(session_key, None)

        attempt_number = ExamMockAttempt.objects.filter(student=request.user, mock=mock).count()
        best_percent = (
            ExamMockAttempt.objects.filter(student=request.user, mock=mock).aggregate(best=Max('percent')).get('best')
            or 0
        )

        return render(
            request,
            'institute/exam_mock_result.html',
            {
                'exam': section.exam,
                'section': section,
                'mock': mock,
                'results': results,
                'score': score,
                'total': total,
                'percent': percent,
                'external_only': False,
                'attempt': attempt,
                'attempt_number': attempt_number,
                'best_percent': best_percent,
            },
        )

    return render(
        request,
        'institute/exam_mock_test.html',
        {
            'exam': section.exam,
            'section': section,
            'mock': mock,
            'questions': questions,
            'timer_seconds': max(1, mock.duration_minutes) * 60,
        },
    )


def institute_students(request):
    students = list(
        StudentAchievement.objects.filter(is_active=True).order_by('display_order', 'student_name', 'id')
    )

    grouped_students = {
        StudentAchievement.EXAM_EAPCET: [],
        StudentAchievement.EXAM_JEE_MAINS: [],
        StudentAchievement.EXAM_PLACEMENT: [],
    }

    for item in students:
        if item.exam_type in grouped_students:
            grouped_students[item.exam_type].append(item)

    def _rank_sort_key(student):
        raw_rank = (student.rank_label or '').strip().lower()
        match = re.search(r'\d[\d,]*', raw_rank)
        if not match:
            return (1, 10**9, student.display_order, student.student_name.lower(), student.id)

        rank_value = int(match.group(0).replace(',', ''))
        return (0, rank_value, student.display_order, student.student_name.lower(), student.id)

    for exam_type in grouped_students:
        grouped_students[exam_type].sort(key=_rank_sort_key)

    return render(
        request,
        'institute/students.html',
        {
            'grouped_students': grouped_students,
        },
    )


def institute_about(request):
    return render(request, 'institute/about.html')


def institute_contact(request):
    return render(request, 'institute/contact.html')