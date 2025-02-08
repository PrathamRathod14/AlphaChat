import csv
import json
import os
import re
from nicegui import ui

# Global state to track the active tab
active_tab = 'dashboard'

# Function to switch content dynamically
def switch_tab(tab_name):
    global active_tab
    active_tab = tab_name
    render_main_section()

# File to save Q&A responses_admin
responses_admin_FILE = "responses.py"

# Function to save Q&A to a file
def save_question_and_answer(question, answer):
    """Append a new question and answer to the responses_admin list."""
    if not os.path.exists(responses_admin_FILE):
        # Create the file and initialize it
        with open(responses_admin_FILE, "w") as f:
            f.write("# Auto-generated Q&A responses_admin\nresponses_admin = []\n")
    # Read existing data
    responses_admin = read_questions_and_answers()
    
    # Check if the question already exists
    for entry in responses_admin:
        if entry['question'] == question:
            ui.notify('This question already exists. Please edit it instead.', color='red')
            return

    # Append the new Q&A
    with open(responses_admin_FILE, "a") as f:
        f.write(f'responses_admin.append({{"question": "{question}", "answer": "{answer}"}})\n')

    ui.notify('Question and Answer saved successfully!', color='green')

# Function to handle Q&A submission
def render_add_qna_tab():
    with main_section:
        ui.label('Add Q&A').classes('text-2xl font-bold text-gray-800 mb-4')
        with ui.card().style('padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); width: 100%;'):
            with ui.column().classes('gap-4').style('width: 100%;'):
                question_input = ui.input('Enter Question').classes('w-full')
                answer_input = ui.input('Enter Answer').classes('w-full')
                ui.button(
                    'Submit',
                    on_click=lambda: handle_qna_submission(question_input.value, answer_input.value)
                ).classes('text-white bg-blue-600 rounded-lg')

# Read questions and answers from the file
def read_questions_and_answers():
    responses_admin = []
    if os.path.exists(responses_admin_FILE):
        try:
            with open(responses_admin_FILE, "r") as f:
                file_content = f.read()
            local_vars = {}
            exec(file_content, {}, local_vars)  
            responses_admin = local_vars.get('responses_admin', [])
        except Exception as e:
            ui.notify(f"Error reading Q&A: {e}", color='red')
            print(f"Error reading Q&A: {e}")  # Debug log
    return responses_admin

# Confirm Delete Q&A
def confirm_delete(question):
    """Show a confirmation dialog for deleting a question."""
    with ui.dialog() as dialog, ui.card():
        with ui.column().classes('p-4'):
            ui.label(f"Are you sure you want to delete the question: '{question}'?").classes('text-lg font-bold')
            with ui.row().classes('justify-end gap-4'):
                ui.button('Cancel', on_click=dialog.close).classes('text-gray-600')
                ui.button('Delete', on_click=lambda: [delete_question(question), dialog.close()]).classes('text-white bg-red-600')
    dialog.open()

# To delete question
def delete_question(question_to_delete):
    try:
        with open(responses_admin_FILE, "r") as f:
            lines = f.readlines()

        updated_lines = []
        found = False

        for line in lines:
            match = re.match(r'responses_admin\.append\((.*?)\)', line.strip())
            if match:
                qna = eval(match.group(1))
                if qna['question'] == question_to_delete:
                    found = True
                    continue
            updated_lines.append(line)

        if not found:
            ui.notify(f'Question "{question_to_delete}" not found!', color='red')
            return

        with open(responses_admin_FILE, "w") as f:
            f.writelines(updated_lines)

        ui.notify(f'Question "{question_to_delete}" deleted successfully!', color='green')

    except Exception as e:
        ui.notify(f"An error occurred: {e}", color='red')

# Render the Q&A list dynamically
def render_qna_list():
    """Function to render the Q&A list dynamically."""
    ui.clear()  # Clear existing UI elements if re-rendering
    responses_admin = load_responses_admin()  # Load the latest data
    for qna in responses_admin:
        with ui.card():
            ui.label(f"Q: {qna['question']}").classes('text-lg font-bold')
            ui.label(f"A: {qna['answer']}").classes('text-gray-600')
            ui.button('Delete', on_click=lambda q=qna: confirm_delete(q['question'])).classes('text-red-600')

# Delete a specific question from the list
def delete_question_from_list(question):
    """Delete a specific question from the list."""
    responses_admin = read_questions_and_answers()
    updated_responses_admin = [qna for qna in responses_admin if qna['question'] != question]

    # Rewrite the updated responses_admin to the file
    with open(responses_admin_FILE, "w") as f:
        f.write("# Auto-generated Q&A responses_admin\nresponses_admin = []\n")
        for qna in updated_responses_admin:
            f.write(f'responses_admin.append({{"question": "{qna["question"]}", "answer": "{qna["answer"]}"}})\n')

    ui.notify(f'Question "{question}" deleted successfully!', color='green')
    render_list_qna_tab()  # Refresh the list after deletion

# Load and save responses_admin data from responses.py (JSON file)
def load_responses_admin():
    """Function to load the responses_admin data from responses.py (JSON file)"""
    try:
        with open('src/responses.py', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("responses.py file not found.")
        return []

# Save the updated responses_admin data back to responses.py
def save_responses_admin(responses_admin):
    """Function to save the updated responses_admin data back to responses.py"""
    with open('src/responses.py', 'w') as file:
        json.dump(responses_admin, file, indent=4)  
    
# Update the Q&A in the responses.py file
def update_question_answer(old_question, new_question, new_answer, variants):
    try:
        responses_admin = read_questions_and_answers()
        updated_responses = []
        found = False

        # Prepare new_answer as a list of answers (primary + variants)
        answers_list = [new_answer] + variants  # Add primary answer and variants

        # Update the correct entry
        for qna in responses_admin:
            if qna['question'] == old_question:
                qna['question'] = new_question
                qna['answer'] = {'answer': answers_list, 'variants': variants}  # Nested dictionary
                found = True
            updated_responses.append(qna)

        if not found:
            ui.notify(f'Question "{old_question}" not found!', color='red')
            return

        # Open the file to preserve the content, and update only the responses_admin part
        with open(responses_admin_FILE, "r") as f:
            file_content = f.readlines()

        # Find where the responses_admin section starts
        start_idx = None
        for idx, line in enumerate(file_content):
            if line.strip().startswith("responses_admin ="):
                start_idx = idx
                break

        if start_idx is not None:
            file_content = file_content[:start_idx + 1] 

            for qna in updated_responses:
                file_content.append(f'responses_admin.append({{"question": "{qna["question"]}", "answer": {qna["answer"]}}})\n')

            # Add the rest of the content (after responses_admin) to the file
            with open(responses_admin_FILE, "w") as f:
                f.writelines(file_content)

        ui.notify(f'Updated successfully!', color='green')

    except Exception as e:
        ui.notify(f"An unexpected error occurred: {e}", color='red')

# Render the List Q&A tab
def render_list_qna_tab():
    """Render the List Q&A tab with row-style cards and action buttons."""
    with main_section:
        ui.label('List Q&A').classes('text-2xl font-bold text-gray-800 mb-4')

        def search_responses(query):
            results = []
            for item in responses_admin_FILE:
                if query.lower() in item['question'].lower():
                    results.append(item)
            return results
        
        # Add a search bar
        search_input = ui.input(label='Search Questions...', placeholder='Search Questions...',on_change=lambda e: display_qna_list(e.value)).classes('w-full mb-4')
        qna_list_container = ui.column().classes('gap-4 w-full')  # Ensure the container takes full width

        def display_qna_list(search_query=""):
            # Fetch Q&A list
            qna_list = read_questions_and_answers()

            # Apply search filter if needed
            if search_query:
                qna_list = [
                    qna for qna in qna_list if search_query.lower() in qna['question'].lower()
                ]

            # Clear the container before re-rendering
            qna_list_container.clear()

            if not qna_list:
                ui.label("No Q&A found.").classes('text-gray-600').add(qna_list_container)
            else:
                for qna in qna_list:
                    with qna_list_container:
                        with ui.card().classes('flex-row items-center justify-between p-4 w-full'):
                            with ui.column().classes('flex-grow'):
                                ui.label(f"Q: {qna['question']}").classes('text-lg font-bold mb-2')
                                ui.label(f"A: {', '.join(qna['answer']['answer'])}" if isinstance(qna['answer'], dict) else f"A: {', '.join(qna['answer'])}" if isinstance(qna['answer'], list) else f"A: {qna['answer']}").classes('text-gray-600')
                            with ui.row().classes('gap-2'):
                                ui.button('Edit', on_click=lambda qna=qna: show_edit_dialog(qna)).classes('text-blue-600')
                                ui.button('Delete', on_click=lambda qna=qna: confirm_delete(qna['question'])).classes('text-red-600')

        # Attach search functionality
        def on_search_input_change():
            display_qna_list(search_input.value)

        search_input.on('input', on_search_input_change)

        # Display initial Q&A list
        display_qna_list()

# Show the Edit Q&A dialog
def show_edit_dialog(qna):
    print("Edit dialog called for:", qna)  # Debugging line

    # Open dialog
    with ui.dialog() as dialog, ui.card().classes('w-full'):
        question_input = ui.input('Edit Question', value=qna['question']).classes('w-full')
        
        if isinstance(qna['answer'], dict):
            primary_answer = qna['answer']['answer'][0]  
            
        else:
            primary_answer = qna['answer']  

        answer_input = ui.input('Edit Answer', value=primary_answer).classes('w-full')
        
        with ui.row().classes('items-center w-full gap-2'):  
            answer_input  
            ui.button('+ Add Variant', on_click=lambda: add_variant_input()).classes('text-blue-600 cursor-pointer')
        
        # Variant inputs to be stored in the dialog scope
        variant_inputs = [] 

        # If variants exist, create input fields for them
        if isinstance(qna['answer'], dict) and 'variants' in qna['answer']:
            for variant in qna['answer']['variants']:
                variant_inputs.append(ui.input('New Variant', value=variant).classes('w-full mb-2'))

        # Function to add new variant input dynamically
        def add_variant_input():
            print("Adding variant input...")  # Debugging line
            new_variant_input = ui.input('New Variant').classes('w-full mb-2')  
            variant_inputs.append(new_variant_input)

            # Print the current list of variant inputs for debugging
            print(f"Current variant inputs: {[input.value for input in variant_inputs]}")  # Debugging line

        # Action Buttons
        with ui.row().classes('justify-end gap-4 mt-4'):
            ui.button('Cancel', on_click=dialog.close).classes('text-gray-600')
            ui.button(
                'Save',
                on_click=lambda: [
                    save_edited_qna(
                        qna['question'],  # Original question
                        question_input.value,  # Updated question
                        answer_input.value,  # Updated answer
                        variant_inputs,  # All variant inputs
                        dialog  # Close dialog after saving
                    ),
                    dialog.close()  # Close the dialog after saving
                ]
            ).classes('bg-blue-600 text-white')

        dialog.open()  # Open the dialog


# Save the edited Q&A
def save_edited_qna(old_question, new_question, new_answer, variant_inputs, dialog):
    if not new_question.strip() or not new_answer.strip():
        ui.notify('Both Question and Answer are required!', color='red')
        return

    variants = [variant.value for variant in variant_inputs if variant.value.strip()]
    
    variant_val = variants

    update_question_answer(old_question, new_question.strip(), new_answer.strip(), variant_val)

    ui.notify('Q&A updated successfully!', color='green')
    dialog.close()

def handle_qna_submission(question, answer):
    if not question.strip() or not answer.strip():
        ui.notify('Both Question and Answer are required!', color='red')
        return
    save_question_and_answer(question.strip(), answer.strip())
    ui.notify('Q&A added successfully!', color='green')

# Handle Q&A Submission
# Function to read uploaded CSV files and store the data in responses.py
def handle_csv_upload(event):
    """Process the uploaded CSV file and store its contents in responses.py."""
    uploaded_file = event.files[0]  
    if uploaded_file:
        try:
            temp_file_path = f"temp_{uploaded_file.name}"
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(uploaded_file.content)
            process_csv_file(temp_file_path)
            os.remove(temp_file_path)
            ui.notify(f"Successfully uploaded and processed {uploaded_file.name}", color="green")
        except Exception as e:
            ui.notify(f"Error processing the uploaded file: {e}", color="red")

# Render the CSV upload tab
def render_upload_csv_tab():
    with main_section:
        ui.label('Upload CSV').classes('text-2xl font-bold text-gray-800 mb-4')
        with ui.card().style('padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); width: 100%;'):
            ui.upload(on_upload=handle_file_upload).classes('mb-4')
            ui.label('Upload a CSV file with columns: "Question", "Answer"')

# Handle the file upload and process the file
def handle_file_upload(event):
    uploaded_file = event.content
    file_name = event.name
    uploaded_file.seek(0)
    file_content = uploaded_file.read()
    temp_file_path = f"temp_{file_name}"
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)
    process_csv_file(temp_file_path)
    os.remove(temp_file_path)

# Function to process the uploaded CSV file
def process_csv_file(file_path):
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    ui.notify("Skipping incomplete row.", color="red")
                    continue
                question, answer = row[:2]
                save_question_and_answer(question.strip(), answer.strip())
    except Exception as e:
        ui.notify(f"Error processing CSV file: {e}", color="red")
        print(f"Error processing CSV file: {e}")



# Simulated Data for the Dashboard
chatbot_stats = {
    'total_users': 500,
    'active_users': 370,
    'total_questions': 1200,
}

# Function to render the main section dynamically
def render_main_section():
    main_section.clear() 

    if active_tab == 'dashboard':
        with main_section: 
            ui.label('Admin Dashboard').classes('text-2xl font-bold text-gray-800 mb-4')

            with ui.row().classes('gap-6 justify-between mt-6'):
                create_stat_card('Total Users', str(chatbot_stats['total_users']), 'group')
                create_stat_card('Active Users', str(chatbot_stats['active_users']), 'person')
                create_stat_card('Total Questions', str(chatbot_stats['total_questions']), 'chat')
                create_chart()

    elif active_tab == 'manage_q&a_csv':
        render_upload_csv_tab()

    elif active_tab == 'manage_q&a_add':
        render_add_qna_tab()

    elif active_tab == 'manage_q&a_list':
        render_list_qna_tab()

# Function to create a stat card with consistent styling
def create_stat_card(title, value, icon):
    with ui.card().style('background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); height: 150px; flex: 1; display: flex; justify-content: center; align-items: center;'):
        with ui.column().classes('w-full h-full flex items-center justify-center text-center'):
            ui.icon(icon).classes('text-blue-600 text-4xl mb-2')
            ui.label(title).classes('text-sm text-gray-600 font-medium')
            ui.label(value).classes('text-xl font-bold text-blue-700')

# Function to create a chart (e.g., User Engagement Overview)
def create_chart():
    with ui.card().style('padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); width: 100%;'):
        ui.label('User Engagement Overview').classes('text-lg font-semibold text-gray-700 mb-4')
        ui.echart({
            'xAxis': {
                'type': 'category',
                'data': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            },
            'yAxis': {
                'type': 'value',
            },
            'series': [{
                'data': [120, 150, 180, 210, 240, 300],
                'type': 'line',
                'smooth': True,
                'lineStyle': {'color': '#007BFF'},
                'areaStyle': {'color': 'rgba(0,123,255,0.2)'},
            }],
        }).classes('w-full h-80') 

# Confirm logout
def confirm_logout():
    """Show a confirmation dialog for logging out."""
    with ui.dialog() as dialog, ui.card():
        with ui.column().classes('p-4'):
            ui.label(f"Are you sure you want to logout?").classes('text-lg font-bold')
            with ui.row().classes('justify-end gap-4'):
                ui.button('Cancel', on_click=dialog.close).classes('text-gray-600')
                ui.button(
                    'Logout',
                    on_click=lambda: [dialog.close(), perform_logout()]
                ).classes('text-white bg-red-600')
    dialog.open()

def perform_logout():
    """Perform the actual logout logic."""
    ui.notify("You have been logged out!", color="green")


# Main NiceGUI page
@ui.page('/')
def main():
    
    global main_section

    # Top Navigation Bar
    with ui.header().style('background-color: #ffffff; color: #333; padding: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);'):
        with ui.row().classes('justify-between items-center w-full'):
            ui.label('AlphaChat').classes('mb-8 text-xl font-bold text-gray-800')
            ui.button(
                'Logout',  
                on_click=confirm_logout  
            ).classes('css-classes')

    # Main Content
    with ui.row().classes('w-full min-h-screen').style('background-color: #f5f5f5; padding: 20px;'):
        # Sidebar
        with ui.column().classes('w-64').style('background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);'):
            ui.button('Dashboard', on_click=lambda: switch_tab('dashboard')).classes('mb-4 w-full')
            ui.button('Add Q&A', on_click=lambda: switch_tab('manage_q&a_add')).classes('mb-4 w-full')
            ui.button('View Q&A', on_click=lambda: switch_tab('manage_q&a_list')).classes('mb-4 w-full')
            ui.button('Upload CSV', on_click=lambda: switch_tab('manage_q&a_csv')).classes('mb-4 w-full')

        with ui.column().classes('flex-1 ml-4') as main_section:
            render_main_section()

# Start the app
ui.run()
