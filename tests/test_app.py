import unittest
import sys
import os

# Get the absolute path to the 'src' folder relative to the current working directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from app import (
    get_timestamp,
    normalize_text,
    import_csv,
    add_question,
    remove_question,
    add_answer,
    remove_answer,
    handle_responses,
    provide_related_questions,
    list_all_questions,
)

class TestApp(unittest.TestCase):
    # Test: Utility Functions
    def test_get_timestamp(self):
        result = get_timestamp()
        self.assertRegex(result, r"^\d{2}:\d{2}:\d{2}$")  # Matches HH:MM:SS format

    def test_normalize_text(self):
        self.assertEqual(normalize_text(" Hello! "), "hello")
        self.assertEqual(normalize_text("What's up?"), "what's up")
        self.assertEqual(normalize_text("...!!!"), "")

    # Test: Import CSV
    def test_import_csv_valid(self):
        # Assume 'sample.csv' is a valid CSV in the current directory
        with open("sample.csv", "w", encoding="utf-8") as f:
            f.write("Question,Keywords,Answer1\n")
            f.write("What is Python?,python,Python is a programming language.\n")
        result = import_csv("sample.csv")
        self.assertTrue(result)

    def test_import_csv_nonexistent(self):
        result = import_csv("nonexistent.csv")
        self.assertFalse(result)


    # Test: Add/Remove Question
    def test_add_question(self):
        result = add_question("What is Java?", "Java is a programming language.")
        self.assertTrue(result)

    def test_remove_question(self):
        add_question("What is Ruby?", "Ruby is a programming language.")
        result = remove_question("What is Ruby?")
        self.assertTrue(result)

    def test_remove_nonexistent_question(self):
        result = remove_question("This does not exist.")
        self.assertFalse(result)

    # Test: Add/Remove Answer
    def test_add_answer(self):
        add_question("What is Python?", "Python is a programming language.")
        result = add_answer("What is Python?", "Python is versatile.")
        self.assertTrue(result)

    def test_add_duplicate_answer(self):
        add_question("What is Python?", "Python is a programming language.")
        add_answer("What is Python?", "Python is versatile.")
        result = add_answer("What is Python?", "Python is versatile.")
        self.assertFalse(result)

    def test_remove_answer(self):
        add_question("What is Python?", "Python is a programming language.")
        add_answer("What is Python?", "Python is versatile.")
        result = remove_answer("What is Python?", "Python is versatile.")
        self.assertTrue(result)

    def test_remove_nonexistent_answer(self):
        add_question("What is Python?", "Python is a programming language.")
        result = remove_answer("What is Python?", "This does not exist.")
        self.assertFalse(result)

    # Test: Handle Responses
    def test_handle_responses_single(self):
        add_question("What is Python?", "Python is a programming language.")
        handle_responses("What is Python?")  # Ensure no exceptions occur

    def test_handle_responses_compound(self):
        add_question("What is Python?", "Python is a programming language.")
        add_question("What is AI?", "AI is artificial intelligence.")
        handle_responses("What is Python? and What is AI?")  # No exceptions expected

    # Test: Related Questions
    def test_provide_related_questions(self):
        add_question("What is Python?", "Python is a programming language.")
        provide_related_questions("Python")  # Should list related questions

    def test_provide_related_questions_none(self):
        provide_related_questions("NonexistentKeyword")  # Should handle gracefully

    # Test: List All Questions
    def test_list_all_questions(self):
        add_question("What is Python?", "Python is a programming language.")
        add_question("What is Java?", "Java is a programming language.")
        list_all_questions()  # Ensure no exceptions occur

if __name__ == "__main__":
    unittest.main()
