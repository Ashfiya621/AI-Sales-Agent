COURSES = [
    {'key': 'design', 'name': 'Product Design Workshop', 'description': 'A hands-on demo for creative design learners.'},
    {'key': 'python', 'name': 'Python Automation Class', 'description': 'A practical introduction to Python automation.'},
    {'key': 'web', 'name': 'Web Development Sprint', 'description': 'Build a modern landing page with JavaScript.'},
]


def format_course_list():
    return '\n'.join([f"{idx + 1}. {course['name']}" for idx, course in enumerate(COURSES)])


def find_course_by_digit(digit):
    try:
        index = int(digit) - 1
        if 0 <= index < len(COURSES):
            return COURSES[index]
    except (ValueError, TypeError):
        return None
    return None
