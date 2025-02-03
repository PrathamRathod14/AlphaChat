from nicegui import ui, app
import random
import time
from datetime import datetime
import os
from fpdf import FPDF 
import asyncio
from src.responses import responses
import shutil
import uuid
import pyjokes
import pywhatkit
import requests
import csv
from bs4 import BeautifulSoup
import speech_recognition as sr
import pyttsx3
from tavily import TavilyClient
import io
from PIL import Image
from fastapi.staticfiles import StaticFiles
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from docx import Document
from io import BytesIO
import tempfile

# ----------------- CONSTANTS & DIRECTORY SETUP ----------------- #
IMAGE_DIR = "generated_images"
HF_API_KEY = 'YOUR_API_KEY'  # Replace with your Hugging Face API key
os.makedirs(IMAGE_DIR, exist_ok=True)


# ----------------- UTILITY FUNCTIONS ----------------- #
def notify_user(message, color="info"):
    """Display a notification in the UI."""
    ui.notify(message, color=color)


def cleanup_directory(directory):
    """Delete all files in the specified directory."""
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


# ----------------- AUDIO ASSISTANT ----------------- #
# Initialize speech recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Global variable to track state
current_mode = None 
reminder_details = ""

def talk(text):
    """Speak the assistant's response and display it in the chat window."""
    engine.say(text)
    engine.runAndWait()
    with chat_window:  
        with ui.row().classes("justify-start mb-2"):
            ui.card().classes("w-auto bg-blue-100 p-3 rounded-lg shadow-md") 
            ui.label(f"AlphaChat: {text}").classes("text-sm")

def take_command():
    """Capture user voice input and return the recognized text."""
    try:
        with sr.Microphone() as source:
            talk("I'm listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            return command.lower()
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Sorry, there was an issue with the speech recognition service."

def handle_command(input_text):
    """Process the user's input and generate a response."""
    global current_mode, reminder_details

    # Display the user's input in the chat window (right side)
    with chat_window:
        with ui.row().classes("justify-end mb-2"):
            ui.card().classes("w-auto bg-green-100 p-3 rounded-lg shadow-md") 
            ui.label(f"You: {input_text}").classes("text-sm")

    # Handle reminder mode separately
    if current_mode == "reminder":
        reminder_details = input_text
        talk(f"Got it! I'll remind you: {reminder_details}")
        current_mode = None 
        return

    # Determine the response and take appropriate actions
    if 'play' in input_text:
        song = input_text.replace('play', '').strip()
        response = f"Playing {song}."
        pywhatkit.playonyt(song)
    elif 'time' in input_text:
        time_now = datetime.datetime.now().strftime('%I:%M %p')
        response = f"The current time is {time_now}."
    elif 'location' in input_text:
        response = "Ostfalia University is located in Lower Saxony, Germany, with campuses in Wolfenbüttel, Salzgitter, and Suderburg."
    elif 'courses' in input_text:
        response = "Ostfalia University offers a wide range of programs, including computer science, engineering, business, and social sciences."
    elif 'facilities' in input_text:
        response = "Ostfalia University has modern laboratories, libraries, and other student support services on its campuses."
    elif 'weather' in input_text:
        talk("Please tell me the name of the city you'd like the weather for.")
        city = take_command()
        if city:
            # Confirm the city and fetch the weather
            talk(f"Fetching weather for {city}.")
            get_weather(city) 
        else:
            talk("I couldn't hear the city name. Please try again.")
        return  
    elif 'set a reminder' in input_text:
        set_reminder()
    elif 'bye' in input_text:
        response = "Goodbye! Have a great day!"
        talk(response)
        exit()
    elif 'joke' in input_text:
        response = pyjokes.get_joke()
    else:
        response = "Sorry, I didn't understand that. Can you try again?"

    # Make the assistant speak the response
    talk(response)

import requests

def get_weather(city):
    """Fetch the weather for the specified city."""
    api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        data = response.json()
        if data.get("cod") == 200:
            main = data["main"]
            weather_desc = data["weather"][0]["description"]
            temp = main["temp"]
            weather_info = f"The current temperature in {city.capitalize()} is {temp}°C with {weather_desc}."
            talk(weather_info) 
        else:
            # Handle cases where the city is not found
            talk(f"Sorry, I couldn't fetch the weather details for {city}. Please check the city name.")
    except Exception as e:
        # Handle network errors or API issues
        talk("Sorry, I couldn't fetch the weather at the moment. Please try again later.")


def open_audio_assistant_dialog():
    """Open the dialog for the audio assistant."""
    with ui.dialog() as audio_dialog:
        with audio_dialog:
            with ui.column().classes("w-full max-w-lg mx-auto p-6 bg-white rounded-lg shadow-md"):
                ui.label("AlphaChat - Your Virtual Assistant").classes("text-2xl font-bold mb-4 text-center")
                global chat_window
                # Chat window to display messages
                chat_window = ui.column().classes("w-full max-h-96 overflow-y-scroll mb-4 border rounded-lg p-4 bg-gray-100")

                # Speak button to initiate voice input
                ui.button("Speak", on_click=on_speak_click).classes(
                    "bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 shadow"
                )

    audio_dialog.open()

def set_reminder():
    talk("What would you like to be reminded about?")
    reminder = take_command()
    talk("When would you like the reminder?")
    reminder_time = take_command()

    if reminder and reminder_time:
        talk(f"Setting a reminder for {reminder} at {reminder_time}.")
        time.sleep(5) 
        talk(f"Reminder: {reminder} at {reminder_time}.")
    else:
        talk("I didn't understand the reminder details. Please try again.")
        
def on_speak_click():
    """Handle the Speak button click event."""
    user_input = take_command() 
    if user_input: 
        handle_command(user_input)

# ----------------- WEB SEARCH ----------------- #

# Initialize Tavily Client with your API key
client = TavilyClient(api_key="YOUR_API_KEY") # Replace with your Tavily API key

# Function to execute a Tavily search query
def execute_search(query):
    try:
        # Execute the search with advanced depth
        response = client.search(query, search_depth="advanced")
        return response
    except Exception as e:
        return {"error": str(e)}

# Function to format the results into HTML for better styling
def format_results(response):
    if "results" in response and response["results"]:
        formatted_result = (
            f"<h3>Search Query: {response['query']}</h3>"
            f"<div style='margin-top: 20px;'>"
        )
        for idx, result in enumerate(response["results"], 1):
            formatted_result += (
                f"<div style='padding: 10px; border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px;'>"
                f"<strong>{idx}. Title:</strong> <a href='{result['url']}' target='_blank'>{result['title']}</a><br>"
                f"<strong>URL:</strong> <a href='{result['url']}' target='_blank'>{result['url']}</a><br>"
                f"<strong>Snippet:</strong> {result['content'][:200]}...<br>"
                f"<strong>Score:</strong> {result.get('score', 'Not available')}"
                f"</div>"
            )
        formatted_result += "</div>"
        return formatted_result
    else:
        return "<p>No results found or an error occurred.</p>"

# Set up NiceGUI dialog interface
def create_dialog_interface():
    search_dialog = ui.dialog()  
    with search_dialog, ui.card().classes('p-4 w-full max-w-2xl'):
        ui.label("Search Information").classes(
            "text-center mb-4 text-2xl font-semibold text-gray-800"
        )

        query_input = ui.input(placeholder="Enter your search query...").classes(
            "w-full p-3 border rounded-lg mb-4 text-lg"
        )

        search_result_label = ui.html().classes("mt-4 text-left")

        loading_label = ui.label("Loading...").classes(
            "text-center text-blue-500"
        ).style("display: none;")

        # Function to execute a search and update the UI
        def search():
            query = query_input.value.strip()
            if query:
                search_result_label.content = "" 
                loading_label.style("display: block;") 

                # Execute search
                response = execute_search(query)
                formatted_result = format_results(response) 

                search_result_label.content = formatted_result 
                loading_label.style("display: none;") 

        # Search button
        ui.button("Search", on_click=search).classes(
            "bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
        )

        # Layout for the results and input
        with ui.column().classes("max-w-4xl mx-auto mt-8"):
            query_input
            search_result_label

    return search_dialog  # Make sure to return the dialog object

# ----------------- IMAGE GENERATOR ----------------- #
class ImageGenerator:
    # Hugging Face API Details
    HUGGING_FACE_API_KEY = "YOUR_API_KEY"  # Replace with your Hugging Face API key
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    HEADERS = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}

    IMAGE_DIR = "generated_images"
    os.makedirs(IMAGE_DIR, exist_ok=True)

    app.mount("/generated_images", StaticFiles(directory=IMAGE_DIR), name="generated_images")

    # Function to generate an image from the prompt text
    def generate_image(self, dialog, img, prompt_input):
        """Generate an image from the prompt text and update the UI dialog."""
        prompt_text = prompt_input.value.strip()
        if not prompt_text:
            ui.notify("Please enter a prompt!", color="red")
            return

        ui.notify("Generating image, please wait...", color="blue")

        payload = {"inputs": prompt_text}

        try:
            response = requests.post(self.API_URL, headers=self.HEADERS, json=payload)

            if response.status_code == 200 and response.content:
                # Save the image
                timestamp = int(time.time())
                image_filename = f"generated_image_{timestamp}.png"
                image_path = os.path.join(self.IMAGE_DIR, image_filename)

                image = Image.open(io.BytesIO(response.content))
                image.save(image_path)

                # Update the dialog with the generated image
                img.set_source(f"/generated_images/{image_filename}")

                ui.notify("Image generated successfully!", color="green")
                # print(f"Image displayed: {image_path}")
            else:
                error_message = response.json().get("error", "Unknown error")
                ui.notify(f"API Error: {error_message}", color="red")

        except requests.exceptions.RequestException as e:
            ui.notify(f"API Request failed: {str(e)}", color="red")

    # Function to open the image generation dialog
    def open_image_generation_dialog(self):
        """Open the dialog for image generation."""
        with ui.dialog() as dialog:
            dialog.classes("w-[90vw] h-[90vh]") 

            with ui.card().classes("w-full h-full overflow-auto"):
                ui.label("Image Generation").classes("text-2xl font-bold mb-6 text-center")

                prompt_input = ui.input(label="Enter Prompt", placeholder="Describe your image...").classes("w-full mb-6")

                img_placeholder = ui.image("https://via.placeholder.com/600").classes("w-full h-100 rounded-lg shadow-md object-cover")

                generate_button = ui.button(
                    "Generate Image",
                    on_click=lambda: self.generate_image(dialog, img_placeholder, prompt_input),  
                ).classes("bg-blue-500 text-white px-6 py-3 rounded-lg mb-6 w-full")

        return dialog

# ----------------- WEB SCRAPER ----------------- #

# Function to scrape headings from a website
def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        headings = []
        for heading_tag in ['h1', 'h2', 'h3']:
            headings.extend([(heading_tag, h.get_text(strip=True)) for h in soup.find_all(heading_tag)])

        return headings
    except requests.exceptions.RequestException as e:
        return f"Error fetching the website: {e}"

# Function to save the scraped data to a CSV file
def save_to_csv(data, filename='scraped_data.csv'):
    formatted_data = []
    for index, (_, text) in enumerate(data, start=1):
        formatted_data.append([str(index), text])

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['No', 'Names'])
        writer.writerows(formatted_data)

    return filename, formatted_data

# Function to save the scraped data to a PDF file
def save_to_pdf(data, filename='scraped_data.pdf'):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Scraped Data", ln=True, align='C')
    pdf.ln(10)

    for count, (_, text) in enumerate(data, start=1):
        # Replace unsupported characters with safe ones or remove them
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, txt=f"{count}. {safe_text}", ln=True)

    pdf.output(filename)
    return filename

# Function to create a dialog interface for web scraping
def create_scraping_dialog():
    def on_scrape():
        url = url_input.value.strip()
        if not url:
            ui.notify('Please enter a valid URL.', type='negative')
            return

        result = scrape_website(url)
        if isinstance(result, str):
            ui.notify(result, type='negative')
        else:
            if result:
                table_data = [{"No": str(index + 1), "Names": text} for index, (_, text) in enumerate(result)]

                result_area.clear()

                with result_area:
                    ui.label('Scraped Data:').classes('text-lg font-bold mb-2')
                    ui.table(
                        columns=[{"name": "No", "label": "No", "field": "No", "align": "center"},
                                 {"name": "Names", "label": "Names", "field": "Names"}],
                        rows=table_data
                    ).props('dense wrap-cells').classes('w-full')

                with ui.row().classes('justify-center gap-4 mt-4'):
                    ui.button('Download CSV', on_click=lambda: save_to_csv_and_notify(result)).classes('bg-blue-500 text-white')
                    ui.button('Download PDF', on_click=lambda: save_to_pdf_and_notify(result)).classes('bg-blue-500 text-white')

    def save_to_csv_and_notify(data):
        filename, _ = save_to_csv(data)
        ui.notify(f'CSV file saved as {filename}', type='positive')

    def save_to_pdf_and_notify(data):
        filename = save_to_pdf(data)
        ui.notify(f'PDF file saved as {filename}', type='positive')

    def refresh_and_close():
        ui.run_javascript('location.reload()') 
        dialog.close()

    with ui.dialog() as dialog:
        with ui.card().classes('p-4 w-full max-w-2xl'):
            ui.label('Web Scraping Tool').classes('text-xl font-bold mb-4')
            url_input = ui.input('Enter the URL').props('outlined full-width').classes("w-full")
            result_area = ui.column().classes('mt-4 overflow-auto').style('max-height: 300px;')
            with ui.row().classes('mt-4 justify-end'):
                ui.button('Scrape Data', on_click=on_scrape).props('primary')
                ui.button('Close', on_click=refresh_and_close).props('secondary')

    return dialog

# ----------------- PDF SUMMARIZATION ----------------- #

CHATGROQ_API_KEY = "YOUR_API_KEY"  # Replace with your ChatGroq API key
model = ChatGroq(api_key=CHATGROQ_API_KEY, model_name="llama-3.3-70b-versatile")

# Function to summarize text using ChatGroq API
async def summarize_text(text):
    """Summarizes the given text using ChatGroq API."""
    try:
        prompt = f"Write a concise summary of the following (Max 1 sentences):\n\n{text}"
        response = await asyncio.to_thread(model.invoke, [HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "An error occurred while summarizing the text."

# Function to handle the uploaded PDF file
async def handle_upload(file):
    """Handles the uploaded PDF file and provides feedback to the user."""
    try:
        output_text.set_text("Processing your file... Please wait.")
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file.name)

        with open(file_path, "wb") as f:
            f.write(file.content.read())

        summary = await process_pdf(file_path)
        os.remove(file_path)
        output_text.set_text(summary)
        show_download_buttons(summary)
    except Exception as e:
        print(f"Error handling upload: {e}")
        output_text.set_text("Error occurred during file upload. Please try again.")

# Function to process the uploaded PDF file
async def process_pdf(file_path):
    """Loads, splits, and summarizes the PDF content asynchronously."""
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        if not pages:
            return "Error: No text found in the uploaded PDF."

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(pages)

        if not chunks:
            return "Error: PDF could not be split into chunks."

        summaries = await asyncio.gather(*(summarize_text(chunk.page_content) for chunk in chunks))
        unique_summaries = list(set(filter(None, summaries)))
        return "\n".join(unique_summaries)
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return "An error occurred while processing the PDF."

# Function to generate a Word document from the summary
def generate_word(summary):
    """Generate a Word document from the summary."""
    doc = Document()
    doc.add_paragraph(summary)
    byte_io = BytesIO()
    doc.save(byte_io)
    byte_io.seek(0)
    return byte_io

# Function to generate a PDF document from the summary
def generate_pdf(summary):
    """Generate a valid PDF document from the summary."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, summary)
    pdf_data = pdf.output(dest='S').encode('latin1')  # Use 'S' to output as string
    byte_io = BytesIO(pdf_data)
    byte_io.seek(0)
    return byte_io

# Function to display download buttons for Word and PDF files
def show_download_buttons(summary):
    """Creates buttons to download the summary in Word and PDF formats."""
    def download_word():
        word_file = generate_word(summary)
        ui.download(word_file.read(), "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    def download_pdf():
        pdf_file = generate_pdf(summary)
        ui.download(pdf_file.read(), "summary.pdf", "application/pdf")


    with ui.row().classes("justify-center mt-4"):
        ui.button("Download as Word", on_click=download_word).classes("mr-2 bg-blue-500 hover:bg-blue-700 text-white")
        ui.button("Download as PDF", on_click=download_pdf).classes("ml-2 bg-green-500 hover:bg-green-700 text-white")

# Function to create a dialog interface for PDF summarization
def pdf_dialog_interface():
    pdf_dialog = ui.dialog()  
    with pdf_dialog, ui.card().classes('rounded-2xl shadow-lg p-8 bg-gray-100'):
        ui.label("Upload a PDF to Summarize").classes(
            "font-size: 24px; font-weight: bold; color: #2D3748; text-align: center;"
        )

        with ui.column().classes("justify-center items-center"):
                ui.upload(on_upload=handle_upload, multiple=False).props('primary').classes("mt-4")
                
        global output_text
        with ui.card().classes("mt-6 w-full p-4 bg-white rounded-xl shadow"):
            output_text = ui.label("Summary will appear here.").style(
                    "font-size: 16px; color: #555; white-space: pre-wrap; overflow-y: auto; max-height: 300px;"
                )

    return pdf_dialog 

# Function to get the current timestamp as HH:MM:SS
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

# Header Section
def header():
    with ui.header().classes("bg-gradient-to-r from-blue-400 to-purple-600 text-white py-6 px-10 shadow-xl"):
        with ui.row().classes("items-center justify-between gap-8"):
            ui.icon("chat_bubble_outline").classes("text-5xl transform hover:scale-110 transition-all duration-300 ease-in-out")
            ui.label("AlphaChat").classes("text-4xl font-extrabold tracking-wide transform hover:translate-x-2 transition-all duration-300 ease-in-out")

        with ui.row().classes("ml-auto gap-10 items-center"):
            ui.link("Home", "/").classes("text-lg font-semibold cursor-pointer text-white no-underline hover:text-purple-200 transition-all duration-300 ease-in-out transform hover:scale-105")
            ui.link("Start Chat", "/chatbot").classes("text-lg font-semibold cursor-pointer text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 px-8 py-4 rounded-full shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105")

# Footer Section
def footer():
    with ui.footer().classes("bg-gradient-to-r from-blue-400 to-purple-500 text-white py-6 px-10 text-center mt-16 border-t-2 border-white"):
        ui.label("© 2025 AlphaChat. All rights reserved.").classes("text-sm font-light")
        ui.row().classes("justify-center gap-4 mt-4")
        ui.link("Privacy Policy", "/privacy").classes("text-sm text-white hover:text-purple-300 no-underline transition-all duration-300 ease-in-out")
        ui.link("Terms of Service", "/terms").classes("text-sm text-white hover:text-purple-300 no-underline transition-all duration-300 ease-in-out")

# Intro Section (Text on the left, GIF on the right)
def intro_section():
    with ui.row().classes("w-full mt-16 justify-center px-12 items-center"): 
        with ui.grid(columns=2).classes("space-x-12"): 
            with ui.column().classes("flex flex-col justify-center items-start space-y-8"):
                ui.label("Welcome to the Future of Digital Solutions!").classes("text-5xl font-extrabold text-gray-800 mb-4 animate__animated animate__fadeIn")
                
                ui.label("Simplicity. Efficiency. Innovation.").classes("text-2xl font-semibold text-gray-700 mb-4 animate__animated animate__fadeIn animate__delay-1s")

                ui.label("Our platform offers state-of-the-art features designed to help you manage your applications, analyze user behavior, and more. "
                         "We focus on simplicity and efficiency to enhance your productivity.").classes("text-lg text-gray-600 mb-8 max-w-xl animate__animated animate__fadeIn animate__delay-2s")
                
                ui.link("Get Started", "/chatbot").classes("text-lg font-medium cursor-pointer text-white bg-purple-500 hover:bg-purple-600 px-6 py-3 rounded-lg shadow-md transition-all ease-in-out duration-200 no-underline hover:shadow-xl hover:scale-105")

            with ui.column().classes("flex justify-center items-center space-y-6"): 
                ui.image("../assets/img/about.jpg").classes("max-w-full max-h-[450px] object-contain transform hover:scale-105 transition-all duration-300 ease-in-out")
                
# Initialize global variable to track last activity time
last_activity_time = time.time()

# Define the chatbot page
@ui.page("/chatbot")
def chatbot_page():
    """Displays the chatbot page."""
    chat_history_data = [] 

    # Main container for the chatbot page with improved spacing and background gradient
    with ui.column().classes("w-full max-w-4xl mx-auto mt-8 space-y-6 bg-gradient-to-b from-indigo-50 to-white rounded-xl shadow-lg p-6"):
        ui.label("🤖 Welcome to Your Chatbot!").classes(
            "text-5xl font-extrabold text-center text-indigo-700 drop-shadow-lg"
        )
        ui.label("Ask me anything, and I'll try to help!").classes(
            "text-lg text-center text-gray-600 font-medium drop-shadow-md"
        )

        # Chat history container with more subtle gradient and shadow effects
        chat_history = ui.column().classes(
            "w-full p-6 bg-gradient-to-t from-gray-100 to-white rounded-2xl h-96 overflow-y-auto space-y-0 shadow-xl border-2 border-gray-300"
        ).style("max-height: 384px; overflow-y: auto; background: linear-gradient(to top, #f3f4f6, #ffffff); border-radius: 1rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);")

        with ui.row().classes("w-full space-x-4 items-center"):
            question_input = ui.input("Type your question...").classes(
                "flex-grow py-4 px-6 text-lg border-2 rounded-lg border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-lg transition-all duration-300 hover:shadow-xl"
            ).style("min-height: 50px; background-color: #f9fafb; border-radius: 10px;")

            menu = ui.select(
                options=[
                    "Audio Assistance",
                    "Image Generation",
                    "Web Searching",
                    "PDF Summarization",
                    "Web Scraping",
                ],
                label="🌐 Select",
                on_change=lambda e: handle_menu_selection(e.value),
            ).classes(
                "bg-white text-gray-800 px-6 py-3 rounded-lg shadow-sm transition-all duration-300 hover:bg-indigo-50 focus:ring-2 focus:ring-indigo-500"
            ).style("min-width: 160px;")

            send_button = ui.button(
                "Send",
                on_click=lambda: handle_ask_question(
                    question_input.value, chat_history, chat_history_data, question_input, download_button
                )
            ).classes(
                "bg-indigo-600 text-white py-3 px-6 rounded-lg shadow-lg hover:bg-indigo-700 transition-all duration-300 hover:scale-105 hover:shadow-2xl"
            ).style("min-width: 120px;")

        download_button = ui.button(
            "Download PDF Chat Log",
            on_click=lambda: download_chat_log_as_pdf(chat_history_data)
        ).classes(
            "bg-green-600 text-white py-3 px-6 rounded-lg shadow-lg hover:bg-green-700 transition-all duration-300 hover:scale-105"
        ).style("min-width: 180px;")
        download_button.disable() 

        asyncio.create_task(check_inactivity(chat_history))


def handle_menu_selection(selection):
    """Handle menu selection and call the appropriate function."""
    if selection == "Audio Assistance":
        open_audio_assistant_dialog() 
    elif selection == "Image Generation":
        image_generator = ImageGenerator()
        image_generator.open_image_generation_dialog().open()
    elif selection == "Web Searching":
        web_search = create_dialog_interface() 
        web_search.open()
    elif selection == "PDF Summarization":
        pdf_summarization = pdf_dialog_interface()  
        pdf_summarization.open()
    elif selection == "Web Scraping":
        web_scraper = create_scraping_dialog()
        web_scraper.open()
    else:
        ui.notify("Invalid selection! Please choose a valid option.", type="error")

# Handle question submission
def handle_ask_question(question, chat_history, chat_history_data, question_input, download_button):
    """Handles user input and adds it to the chat history."""
    if question.strip():
        chat_history_data.append(f"You: {question}")
        with chat_history:
            with ui.card().classes("bg-blue-100 p-4 rounded-lg shadow-md w-full"):
                with ui.row().classes("items-center"):
                    ui.label("You:").classes("font-bold text-blue-700 text-sm")
                    ui.label(question).classes("text-gray-800 text-sm")

        question_input.set_value('')

        send_bot_response(question, chat_history, chat_history_data, download_button)
        global last_activity_time
        last_activity_time = time.time()
    else:
        ui.notify("Please enter a question!", color="red")

# Generate and display bot's response
def send_bot_response(question, chat_history, chat_history_data, download_button):
    """Generates and adds the bot's response to chat history."""
    response_options = responses.get(normalize_text(question))
    if response_options:
        response = random.choice(response_options)
    else:
        response = "I'm sorry, I don't know the answer to that."
    
    chat_history_data.append(f"Bot: {response}")
    with chat_history:
        with ui.card().classes("bg-indigo-100 py-4 rounded-lg shadow-md w-full"):
            with ui.row().classes("items-center space-x-0"):
                ui.label(f"Bot:").classes("font-bold text-indigo-700 text-sm")
                ui.label(response).classes("text-gray-800 text-sm")

    ui.run_javascript(f'document.querySelector("#{chat_history.id}").scrollTop = document.querySelector("#{chat_history.id}").scrollHeight;')

    if chat_history_data and not download_button.enabled:
        download_button.enable()

# Check inactivity
async def check_inactivity(chat_history):
    """Checks for user inactivity and prompts after 30 seconds."""
    global last_activity_time
    while True:
        if time.time() - last_activity_time > 30:
            with chat_history:
                ui.label("Hey, are you still there? 🤖").classes("text-red-600 font-bold")
            last_activity_time = time.time()
        await asyncio.sleep(1)

# Download chat log as PDF
def download_chat_log_as_pdf(chat_history_data):
    """Generates and downloads the chat log as a PDF."""
    if chat_history_data:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        filename = f"chat-log-{timestamp}.pdf"
        save_dir = os.path.join(os.getcwd(), "logs")
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        temp_path = os.path.join(save_dir, filename)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Chat Log [AlphaChat]", ln=True, align='C')
        pdf.ln(10)

        for line in chat_history_data:
            pdf.multi_cell(0, 10, txt=line)

        pdf.output(temp_path)
        ui.download(temp_path)
        ui.notify(f"Chat log PDF downloaded successfully as {filename}!", color="green")

# Initialize the web page
header()
intro_section()
footer()

ui.run()
