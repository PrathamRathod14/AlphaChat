# 🤖 AlphaChat: A Chatbot Application


## 📝 Overview
AlphaChat is a chatbot with a GUI and console interface for real-time conversations, Q&A management, and AI-driven features like voice interaction, image generation, and PDF Summarization.

---

## 🌟 Features

### 🛠️ For Service Providers

[Admin Features Demo](https://github.com/user-attachments/assets/7b0d17a0-9efb-4e29-9f76-99d39c94f441)

- **Console App for Testing**: A straightforward console-based chatbot for feature testing.
- **Customizable Q&A Content**: Import questions and answers via CSV files. Edit and manage questions/answers using CLI arguments.
- **Basic Functionalities**: Handles compound and variant questions. Suggests questions based on keywords.
- **Logging and Debugging**: File-based logging with configurable levels (`INFO`, `WARNING`). Unit testing to isolate and debug potential issues.
- **Web Management Interface**: Centralized web page with actionable elements such as viewing, editing, deleting and searching Q&A lists. Accessing app logs and user activity.

### 🙋 For End Users

[User Features Demo 1](https://github.com/user-attachments/assets/a1246346-12fd-4e0c-a230-dc06838a6f61)

- **Interactive Chatbot**: Welcoming messages and opening questions. Handles CLI arguments to skip initial prompts.
- **Trivia Game**: Built-in trivia game with multiple-choice questions. Displays progress indicators and ✅/❌ symbols for answers.
- **Weather Integration**: Provides weather conditions for specific locations or events.
- **Error Handling**: Gracefully handles crashes with detailed logs and chat history.


[User Features Demo 2](https://github.com/user-attachments/assets/8fa10c3b-4171-4467-8035-0842b332aa88)

- **Audio Assistance**: Users can interact with the chatbot using voice commands. Processes spoken input and provides appropriate responses.
- **Image Generation**: Generates images based on user-provided text prompts. Leverages an AI-based image generation model.
- **Web Scraping**: Extracts data from online sources based on user queries. Collects structured data for analysis or display.
- **Web Search**: Enables users to search the web directly from the chatbot. Fetches results using an external search engine API.
- **PDF Summarization**: Processes and summarizes the content of PDF documents. Extracts key insights for quick understanding.

### 🖥️ Raspberry Pi Integration
- **LED Matrix Symbols**: Displays app status, trivia progress, and results.
- **Gesture & Sensor Support**: Potential support for Raspberry Pi motion and environmental sensors.

---
### Architecture 
![System Architecture](https://github.com/user-attachments/assets/87376cfc-711e-4bc1-a8db-eb39c6135e6f)
- System Administrator: Manages system settings and Q&A.
- User (Students): Interacts with the chatbot to play games, request weather updates and ask questions.
- Chatbot System: Processes user interactions, handles questions and manages system logs.
---

## 📌 Use Cases
- **Service Providers (Admin)**:
     Ideal for testing chatbot features and enhancing user experience.
     Easily manage and expand the chatbot's knowledge base.
- **End Users (Staff, Student)**:
     Engaging tool for Q&A, trivia, and real-time updates.
     Simple and efficient web-based interaction.
- **Educational Use**:
     Interactive learning and knowledge testing with trivia features.
     Saves time and effort.

---

## ⚙ Technology Highlights
-   Console-based chatbot app.
-   Supports CLI arguments for advanced functionality.
-   CSV import/export for managing Q&A content.
-   Raspberry Pi Sense HAT integration for enhanced UX.
-   Centralized web interface for comprehensive management.
-   Audio assistance for voice interaction.
-   AI-powered image generation.
-   Web scraping and integrated search functionality.
-   Web searching for real-time information retrieval.
-   PDF summarization for quick document insights.

---

## 🛠️ How to Use

1. **Unzip / Clone the File**:
   Extract the contents of the downloaded file.

2. **Set Up APIs**:  
   - **OpenWeatherAPI**:  (Weather Forecast)
     Sign up at [OpenWeatherAPI](https://openweathermap.org/) to get an API key.    

   - **Hugging Face**:  (Image Generation)
     Register at [Hugging Face](https://huggingface.co/) and obtain your API token.  
     
   - **ChatGroq**:  (PDF Summarization)
     Access the ChatGroq API at [ChatGroq](https://www.chatgroq.com/).  
     
   - **Tavily**:  (Web Search)
     Register at [Tavily](https://tavily.com/) to get access to their APIs. 

3. **Install Dependencies**:
   Run the command: 
   ***pip install -e .***
   (Do not forget the . at the end.)

4. **Run the Project (Console)**:
   Execute the command:
  ***myproject***

5. **Run the User Interface (Web)**:
   Navigate to the src directory and run the following command in the terminal:
   ***cd src***
   ***python index.py***

6. **Run the Admin Dashboard (Web)**:
   Navigate to the src directory and run the following command in the terminal:
   ***cd src***
   ***python dashboard.py***


---

## 🔧 Requirements
-  Python 3.x
-  Raspberry Pi with Sense HAT (for LED matrix features) (optional)
-  CSV files for importing questions and answers (optional)


---

## 📌 Roadmap
-  Expand weather API integration
-  Enhance web management UI
-  Integrate AI-based learning for adaptive interactions
-  Add web scraping and integrated search functionality
-  Enable AI-powered image generation
-  Improve voice interaction for real-time communication
-  Enhance gesture recognition for Raspberry Pi sensors

---

## 📜 License
MIT License. See LICENSE for details.

---

Developed with ❤️ by **PrathamRathod14**. Let's connect!

- 🔗 **GitHub**: [PrathamRathod14](https://github.com/PrathamRathod14)
