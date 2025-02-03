# -*- coding: utf-8 -*-

import csv
import time
import argparse
import random
import re 
import os
import logging
from src.responses import *

# Utility Functions

# Function to get the current time in HH:MM:SS format
def get_timestamp():
    """Returns the current time as HH:MM:SS."""
    return time.strftime("%H:%M:%S")

# Function to print a message with a timestamp and sender label
def print_message(sender, message):
    """Prints a formatted message with a timestamp and sender label."""
    print(f"[{get_timestamp()}] {sender}: {message}")

# Function to normalize text (lowercase and strip punctuation)
def normalize_text(text):
    """Normalize input text by converting to lowercase and removing punctuation."""
    return text.lower().strip("?.! ")


# CSV Management Functions

# Function to import questions and answers from a CSV file
def import_csv(filepath):
    """Import data from a CSV file into responses, answers, and keywords dictionaries."""
    global responses, keywords, answers
    responses.clear()
    keywords.clear()
    answers.clear()

    try:
        if not filepath.endswith('.csv'):
            raise ValueError("Unsupported file type. Please provide a CSV file.")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at {filepath}.")

        with open(filepath, mode="r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            # Validate required columns
            required_columns = {"Question", "Keywords", "Answer1"}
            if not required_columns.issubset(set(csv_reader.fieldnames)):
                raise ValueError("Missing required columns: 'Question', 'Keywords', 'Answer1'.")

            for row in csv_reader:
                question = normalize_text(row["Question"])
                keywords_list = [normalize_text(kw) for kw in row["Keywords"].split(";")]
                
                # Initialize answer_variants list and validate non-empty answers
                answer_variants = []
                for i in range(1, 5):
                    answer = row.get(f"Answer{i}")
                    if answer and answer.strip():  # Ensure the answer is not None or empty
                        answer_variants.append(answer.strip())

                # Populate answers dictionary
                if answer_variants:
                    answers[question] = answer_variants[0]

                # Populate responses dictionary
                responses[question] = answer_variants

                # Populate keywords dictionary
                for keyword in keywords_list:
                    keywords.setdefault(keyword, []).append(question)

        print_message("System", f"Knowledge base successfully imported from {filepath}")
        #provide the answer to the user here
        return True
    
    except FileNotFoundError as e:
        print_message("System", f"Error: {str(e)}")
    except ValueError as e:
        print_message("System", f"Error: {str(e)}")
    except csv.Error as e:
        print_message("System", f"Error: Malformed or corrupted CSV file. {str(e)}")
    except Exception as e:
        print_message("System", f"Unexpected error: {str(e)}")
    return False


# Core Chatbot Functions

# Function to get the response for a given question
def get_answer(question):
    """Fetch answer for a question or provide default response."""
    if question in answers:
        return answers[question]
    if question in responses:
        return random.choice(responses[question])
    return random.choice(responses["default"])

# Function to get the canonical question
def get_canonical_question(user_input):
    """Finds the best match for a user's input in the question_variants and retrieves an appropriate answer."""
    normalized_input = normalize_text(user_input)

    for key, variants in responses.items():
        if normalized_input in variants:
            matched_question = key  # Canonical question that matches the variant
            return answers.get(matched_question, "Sorry, I don't have an answer for that.")

    return "Sorry, I don't have an answer for that."  # Default response if no match is found

# Function to handle single question and respond
def handle_single_question(question):
    """Respond to a single question."""
    response = get_answer(normalize_text(question))
    print_message("Chatbot", response)

# Function to handle multiple questions
def handle_compound_question(input_text):
    """Split input into individual questions and respond in Q&A format if there are multiple questions."""
    questions = re.split(r"\s(and|or)\s|[?]", input_text.lower())
    questions = [q.strip("?.!").strip() for q in questions if q and q not in ["and", "or"]]

    if len(questions) > 1:
        formatted_responses = [
            f"Q: {q.capitalize()}\n\tA: {get_answer(q)}" for q in questions
        ]
        print_message("Chatbot", "\n\t" + "\n\t".join(formatted_responses))
    else:
        handle_single_question(questions[0])

# Function to handle responses based on user input
def handle_responses(user_input):
    """Check if input has one or multiple questions, then call the appropriate handler."""
    if "and" in user_input or "or" in user_input or "?" in user_input:
        handle_compound_question(user_input)
    else:
        handle_single_question(user_input)


# Related Questions and Suggestions

# Function to provide related questions for a given keyword
def provide_related_questions(keyword):
    """Suggest related questions for a keyword or notify if none exist."""
    related = keywords.get(normalize_text(keyword), [])
    if related:
        print_message("Chatbot", f"Here are some related questions for '{keyword}':")
        for i, q in enumerate(related, 1):
            print(f"\t{i}. {q}")
        get_user_selection(related)
    else:
        print_message("Chatbot", "No related questions found for that keyword.")

# Function to ask the user to select a question and provide the corresponding answer
def get_user_selection(questions):
    """Allow user to select a related question and display its answer."""
    while True:
        try:
            choice = int(input(f"Please select a question number (1-{len(questions)}): "))
            if 1 <= choice <= len(questions):
                print_message("Chatbot", get_answer(questions[choice - 1]))
                break
            else:
                print_message("Chatbot", "Invalid selection. Please choose a valid number.")
        except ValueError:
            print_message("Chatbot", "Please enter a valid number.")

# Function to list all available questions in the knowledge base
def list_all_questions():
    """Prints all internal questions from the knowledge base (answers dictionary)."""
    print_message("Chatbot", "Listing all available questions in the knowledge base: ")
    all_questions = list(answers.keys()) + list(responses.keys())
    for i, question in enumerate(all_questions, 1):
        print(f"\t{i}. {question.capitalize()}")


# Add/Remove Questions and Answers

# Adds a new question with an optional answer to the knowledge base.
def add_question(question, answer, responses_file="responses.py"):
    """Add a new question or append an answer to an existing question in the knowledge base."""
    normalized_question = normalize_text(question)

    # Check if the question already exists
    if normalized_question in responses:
        # Append the answer if it doesn't already exist
        if answer not in responses[normalized_question]:
            responses[normalized_question].append(answer)

            # Update responses.py file
            try:
                with open(responses_file, mode="a", encoding="utf-8") as file:
                    file.write(f"responses['{normalized_question}'].append('{answer}')\n")
                print_message("System", f"Answer '{answer}' appended successfully to '{responses_file}'.")
            except Exception as e:
                print_message("System", f"Error: Failed to update responses file. {str(e)}")
                return False
        else:
            print_message("System", f"The answer '{answer}' already exists for question '{question}'.")
        return True
    else:
        # Add the new question and answer
        responses[normalized_question] = [answer]

        # Responses file
        try:
            with open(responses_file, mode="a", encoding="utf-8") as file:
                file.write(f"responses['{normalized_question}'] = ['{answer}']\n")
            print_message("System", f"Question '{question}' added successfully to '{responses_file}'.")
        except Exception as e:
            print_message("System", f"Error: Failed to update responses file. {str(e)}")
            return False

    return True

# Removes an existing question from the knowledge base.
def remove_question(question, responses_file="responses.py"):
    """Remove a question from the knowledge base."""
    normalized_question = normalize_text(question)

    # Check if the question exists
    if normalized_question not in responses:
        print_message("System", f"The question '{question}' does not exist in the knowledge base.")
        return False

    # Remove from internal dictionaries
    del responses[normalized_question]
    if normalized_question in answers:
        del answers[normalized_question]

    # Update the responses.py file
    try:
        with open(responses_file, mode="r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(responses_file, mode="w", encoding="utf-8") as file:
            for line in lines:
                if not line.strip().startswith(f"responses['{normalized_question}']"):
                    file.write(line)
        print_message("System", f"Question '{question}' removed successfully from '{responses_file}'.")
    except Exception as e:
        print_message("System", f"Error: Failed to update responses file. {str(e)}")
        return False

    return True

# Adds a new answer to an existing question in the knowledge base.
def add_answer(question, answer, responses_file="responses.py"):
    """Add a new answer to an existing question in the knowledge base."""
    normalized_question = normalize_text(question)

    if normalized_question not in responses:
        print_message("System", f"The question '{question}' does not exist in the knowledge base.")
        return False

    # Check if the answer already exists
    if answer in responses[normalized_question]:
        print_message("System", f"The answer '{answer}' already exists for question '{question}'.")
        return False

    # Add to internal dictionary
    responses[normalized_question].append(answer)

    # Update the responses.py file
    try:
        with open(responses_file, mode="a", encoding="utf-8") as file:
            file.write(f"responses['{normalized_question}'].append('{answer}')\n")
        print_message("System", f"Answer '{answer}' added successfully to '{responses_file}'.")
    except Exception as e:
        print_message("System", f"Error: Failed to update responses file. {str(e)}")
        return False

    return True

# Removes a specific answer from an existing question in the knowledge base.
def remove_answer(question, answer, responses_file="responses.py"):
    """Remove a specific answer from an existing question in the knowledge base."""
    normalized_question = normalize_text(question)

    if normalized_question not in responses:
        print_message("System", f"The question '{question}' does not exist in the knowledge base.")
        return False

    if answer not in responses[normalized_question]:
        print_message("System", f"The answer '{answer}' does not exist for question '{question}'.")
        return False

    # Remove from internal dictionary
    responses[normalized_question].remove(answer)

    # Update the responses.py file
    try:
        with open(responses_file, mode="r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(responses_file, mode="w", encoding="utf-8") as file:
            for line in lines:
                if f"'{answer}'" not in line or not line.strip().startswith(f"responses['{normalized_question}']"):
                    file.write(line)
        print_message("System", f"Answer '{answer}' removed successfully from '{responses_file}'.")
    except Exception as e:
        print_message("System", f"Error: Failed to update responses file. {str(e)}")
        return False

    return True


# SenseHat Functions

def startup_symbol():
    """Returns a smiley face symbol for the startup phase."""
    O = (0, 0, 0)    # Off
    Y = (255, 255, 0)  # Yellow (Face)
    B = (0, 0, 0)    # Black (Eyes/Mouth)
    W = (255, 255, 255)  # White (Background)

    return [
        W, W, W, W, W, W, W, W,
        W, Y, Y, Y, Y, Y, Y, W,
        Y, Y, B, Y, Y, B, Y, Y,
        Y, Y, Y, Y, Y, Y, Y, Y,
        Y, Y, B, Y, Y, B, Y, Y,
        Y, Y, Y, B, B, Y, Y, Y,
        W, Y, Y, Y, Y, Y, Y, W,
        W, W, W, W, W, W, W, W,
    ]

def display_feedback(icon_matrix):
        """Displays feedback on the SenseHat LED matrix."""
        sense.set_pixels(icon_matrix)
        time.sleep(1.5)  # Wait to display feedback
        sense.clear()  # Clear the matrix

def blink_feedback(icon_matrix, times=3, delay=0.3):
    """Blink the icon on the LED matrix."""
    for _ in range(times):
        sense.set_pixels(icon_matrix)
        time.sleep(delay)
        sense.clear()
        time.sleep(delay)

def green_tick():
    """Returns a green tick icon matrix."""
    G = (0, 255, 0)  # Green
    O = (0, 0, 0)    # Off
    return [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, G, O,
        O, O, O, O, O, G, O, O,
        O, O, O, O, G, O, O, O,
        O, G, O, G, O, O, O, O,
        O, O, G, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
    ]

def red_cross():
    """Returns a red cross icon matrix."""
    R = (255, 0, 0)  # Red
    O = (0, 0, 0)    # Off
    return [
            R, O, O, O, O, O, O, R,
            O, R, O, O, O, O, R, O,
            O, O, R, O, O, R, O, O,
            O, O, O, R, R, O, O, O,
            O, O, O, R, R, O, O, O,
            O, O, R, O, O, R, O, O,
            O, R, O, O, O, O, R, O,
            R, O, O, O, O, O, O, R,
        ]


# Trivia Game Functions

# Start the trivia game, handles questions, answers, feedback, and displays the final score on the SenseHat LED matrix.
def play_trivia():
    """Starts the built-in trivia game."""
    
    try:
        sense = SenseHat()
        sense.clear()
        sense_available = True
    except:
        sense_available = False  # If SenseHat is not connected

    def display_final_score(score, total):
        """Displays the final score on the SenseHat LED matrix."""
        message = f"Final Score: {score}/{total}"
        if sense_available:
            sense.show_message(message, text_colour=(255, 255, 255))
        else:
            print(message)

    logging.info("Starting trivia game.")  # Log when the game starts
    display_feedback(game_start_symbol()) if sense_available else None  # Show game-starting symbol if SenseHat is connected
    print("Chatbot: Trivia game activated! Answer the questions to test your knowledge. Type 'exit' anytime to stop the game.")

    questions = trivia_questions.copy()
    random.shuffle(questions)  # Shuffle questions for randomness

    total_questions = 5  # Only 5 questions in this version
    correct_answers = 0
    asked_questions = 0

    for i in range(total_questions):
        if not questions:
            break

        current_question = questions.pop()
        asked_questions += 1

        # Display progress and score
        print(f"Chatbot: Question {asked_questions} of {total_questions}; Score: {correct_answers}/{total_questions}")
        print(f"Chatbot: Question {asked_questions} of {total_questions}; Score: {correct_answers}/{total_questions}")

        print(f"Chatbot: {current_question['question']}")
        print(f"Chatbot: {current_question['question']}")
        for choice in current_question["choices"]:
            print(choice)

        while True:
            user_answer = input("Your answer (A/B/C/D) or type 'exit' to quit: ").strip().upper()
            if user_answer in ["A", "B", "C", "D", "EXIT"]:
                break
            print("Chatbot: Invalid input! Please choose from A, B, C, D or type 'exit'.")

        if user_answer == "EXIT":
            print_message("Chatbot", f"You exited the game. Final Score: {correct_answers}/{total_questions}")
            break

        if user_answer == current_question["answer"]:
            print_message("Chatbot", "Correct!")
            correct_answers += 1
        else:
            print_message("Chatbot", f"Wrong! The correct answer was: {current_question['answer']}.")

    # Log the end of the trivia game with the final score
    logging.info(f"Trivia game over! Final Score: {correct_answers}/{total_questions}")
    print(f"Chatbot: Trivia game over! Final Score: {correct_answers}/{total_questions}")
    display_final_score(correct_answers, total_questions)
    sense.clear() if sense_available else None

# Starts the trivia game if the input is 'trivia'.
def handle_trivia_command(user_input):
    normalized_input = normalize_text(user_input)
    if normalize_text(user_input) == "trivia":
        play_trivia()
        return True
    return False


# Weather Information Functions

# Function to get the current weather information for a given city
def fetch_weather(location_name):
    """Fetch the current weather for a given location using OpenWeatherMap API."""
    try:
        # API endpoint and parameters
        api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location_name,
            "appid": api_key,
            "units": "metric",  # Use metric units for temperature
        }
        
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the weather data
        data = response.json()
        weather = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        
        # Format the weather details
        return f"\nCurrent Weather: {weather}, Temperature: {temperature}°C"
    
    except requests.exceptions.RequestException as e:
        # Log the error
        logging.error(f"Error fetching weather data: {e}")
        return None
    except KeyError:
        # Handle unexpected API response structure
        logging.error("Unexpected weather data format.")
        return None


# Logging Setup

# Sets up the logging configuration
def setup_logging(enable_logging, log_level="WARNING"):
    """Setup logging configuration."""
    if not enable_logging:
        logging.disable(logging.CRITICAL)  # Disable all logging
        return

    log_level = log_level.upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        filename=os.path.join("../logs", "chatbot.log"),
        level=numeric_level,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )

# Main function to run the chatbot simulation
def main():
    """Runs the chatbot interaction loop."""
    try:
        try:
            from sense_hat import SenseHat
            sense = SenseHat()
            is_raspberry_pi = True
        except ImportError:
            print_message("System", "Running in a non-Raspberry Pi environment. Some features may be unavailable.")
            sense = None
            is_raspberry_pi = False

        parser = argparse.ArgumentParser(
            description="Chatbot interaction script. Use the arguments to manage knowledge base and chatbot behavior."
        )
        
        # Command-line arguments
        parser.add_argument("--add", action="store_true", help="Add a new question or answer")
        parser.add_argument("--remove", action="store_true", help="Remove an existing question or answer")
        parser.add_argument("--question", type=str, help="The question to add/remove")
        parser.add_argument("--answer", type=str, help="The answer to add/remove")
        parser.add_argument("--csv", type=str, default="chatbot_knowledge_base.csv", help="Path to the CSV file")
        parser.add_argument("--import-data", action="store_true", help="Import knowledge base from a file.")
        parser.add_argument("--filetype", type=str, help="File type for import (e.g., CSV).")
        parser.add_argument("--filepath", type=str, help="Path to the file for import.")
        parser.add_argument("--list-questions", action="store_true", help="List all available questions in the knowledge base.")
        parser.add_argument("--debug", action="store_true", help="Enable debugging mode.")
        parser.add_argument("--log", action="store_true", help="Enable logging to a file.")
        parser.add_argument("--log-level", type=str, choices=["INFO", "WARNING"], default="WARNING", help="Specify logging level. Default is WARNING.")
        parser.add_argument("--location", action="store_true", help="Get location weather details.")
        parser.add_argument("--compare-temps", nargs=2, metavar=("LOCATION1", "LOCATION2"), help="Compare current temperatures between two locations.")
        # parser.add_argument("--help", action="help", help="Show this message and exit.")

        # Parse arguments
        args = parser.parse_args()

        # Handle logging setup based on arguments
        setup_logging(args.log, args.log_level)

        logging.info("Chatbot application started.")

        if args.debug:
            print_message("System", "Debugging mode enabled.")
            logging.info("Debugging mode enabled.")

        # Handle adding a question or answer
        if args.add:
            if args.question and args.answer:
                add_question(args.question, args.answer)
            else:
                print("Error: Both --question and --answer are required for --add.")

        if args.remove:
            if args.question:
                if args.answer:
                    remove_answer(args.question, args.answer)
                else:
                    remove_question(args.question)
            else:
                print("Error: --question is required for --remove.")

        # Existing functionality
        if args.import_data:
            if args.filetype and args.filetype.lower() == "csv" and args.filepath:
                success = import_csv(args.filepath)
                if success:
                    logging.info(f"Data imported from {args.filepath}")
                else:
                    logging.warning(f"Failed to import data from {args.filepath}")
            else:
                print_message("System", "Invalid file type or missing filepath. Use --filetype CSV --filepath <path>.")
                logging.warning("Invalid import arguments.")
            return

        if args.list_questions:
            list_all_questions()
            logging.info("Listed all questions in the knowledge base.")
            return

        if args.question:
            handle_responses(args.question)
            logging.info(f"Handled question: {args.question}")
            return

        # # Handle location queries
        # if args.location:
        #     date = args.date if args.date else None
        #     response = handle_location_query(args.location, date)
        #     print_message("Chatbot", response)
        #     logging.info(f"Handled location query for: {args.location}")
        #     return 

        # Handle temperature comparison for two locations
        if args.compare_temps:
            location1, location2 = args.compare_temps
            result = compare_current_temperatures(location1, location2)
            print_message("Chatbot", result)
            return

        # Chat interaction loop
        if is_raspberry_pi:
            display_feedback(startup_symbol())  # Show startup symbol
        print_message("Chatbot", "Hello! You can ask me anything. Type 'bye' to exit.")
        logging.info("Chat interaction loop started.")
        
        while True:
            user_input = input(f"[{get_timestamp()}] You: ")

            # Normalize user input before checking for related questions
            normalized_input = normalize_text(user_input)

            if normalized_input == "bye":
                print_message("Chatbot", "Goodbye!")
                logging.info("User exited the chat.")
                break
            
            if handle_trivia_command(user_input):
                logging.info("Trivia game handled.")
                continue

            # Check for location-related queries
            elif any(location in normalized_input for location in location_dict.keys()):
                # Identify the location from the input
                for location in location_dict.keys():
                    if location in normalized_input:
                        # Fetch weather information for the identified location
                        weather_info = fetch_weather(location)
                        
                        # Construct the response
                        response = (
                            f"{location.capitalize()} is located at {location_dict[location]}"
                            f"{weather_info if weather_info else 'Weather details are currently unavailable.'}"
                        )
                        
                        # Respond to the user
                        print_message("Chatbot", response)
                        logging.info(f"Provided location and weather information for: {location}")
                        break

            elif normalized_input in keywords:
                provide_related_questions(normalized_input)
                logging.info(f"Provided related questions for keyword: {normalized_input}")
                
            elif get_canonical_question(normalized_input) != "Sorry, I don't have an answer for that.":
                answer = get_canonical_question(normalized_input)
                print_message("Chatbot", answer)
                logging.info(f"Answered user question: {user_input}")
            
            else:
                handle_responses(user_input)

    except Exception as e:
        print_message("System", f"An unexpected error occurred: {str(e)}")
        logging.critical(f"Critical error occurred: {str(e)}", exc_info=True)
        raise

# Run the main function if the script is executed
if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        pass  # Prevents a traceback when the user calls --help
    except Exception as e:
        print(f"Critical Error: {e}")

    
