from fpdf import FPDF
import streamlit as st
import openai
import math
import os


openai.api_key = os.getenv("OPENAI_API_KEY")


# Define topics and their relative weights
gku_percentages = {
    "Computing Foundations": 33,
    "Engineering Fundamentals": 17,
    "Professional Practice": 6,
    "Software Modeling and Analysis": 6,
    "Requirements Analysis and Specification": 6,
    "Software Design": 10,
    "Software Verification & Validation": 8,
    "Software Process": 7,
    "Software Quality": 4,
    "Security": 2
}

# Function to calculate the number of questions per topic
def calculate_questions(total_questions, percentages):
    raw_distribution = {topic: (percentage / 100) * total_questions for topic, percentage in percentages.items()}
    rounded_distribution = {topic: math.floor(count) for topic, count in raw_distribution.items()}
    difference = total_questions - sum(rounded_distribution.values())
    fractional_parts = {topic: raw_distribution[topic] - rounded_distribution[topic] for topic in raw_distribution}
    sorted_topics = sorted(fractional_parts, key=fractional_parts.get, reverse=True)
    for i in range(difference):
        rounded_distribution[sorted_topics[i]] += 1
    return rounded_distribution

# Function to generate questions for a given topic
def generate_questions(topic, num_questions, difficulty="Medium"):
    prompt = f"Generate {num_questions} {difficulty} difficulty questions about '{topic}'. Provide only the questions, numbered."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in generating educational questions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        questions = response['choices'][0]['message']['content'].strip()
        return questions.split("\n")
    except Exception as e:
        return [f"Error generating questions for {topic}: {e}"]

# Function to generate a PDF file
def create_pdf(exam_questions):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI-Powered Exam", ln=True, align="C")
    pdf.ln(10)
    for question in exam_questions:
        pdf.multi_cell(0, 10, question)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin1')

# Streamlit UI
st.title("AI-Powered Exam Generator Software Engineering")

# Input for total number of questions
total_questions = st.number_input("Enter the total number of questions for the exam:", min_value=10, max_value=200, value=60, step=10)

# Select difficulty level
difficulty = st.selectbox("Select Difficulty Level:", ["Easy", "Medium", "Hard"], index=1)

# Generate button
if st.button("Generate Exam"):
    # Calculate questions per topic based on GKUs
    questions_distribution = calculate_questions(total_questions, gku_percentages)
    st.write("Generating exam...")
    exam_questions = []

    # Generate questions for each topic
    for topic, count in questions_distribution.items():
        if count > 0:  # Skip topics with zero questions
            st.write(f"Generating {count} questions for {topic}...")
            topic_questions = generate_questions(topic, count, difficulty)
            exam_questions.append(f"Topic: {topic}")
            exam_questions.extend(topic_questions)
            exam_questions.append("")  # Add blank line between topics
    
    # Display the exam
    st.success("Exam Generated Successfully!")
    st.write("\n".join(exam_questions))

    # Provide a downloadable version of the exam as text
    exam_text = "\n".join(exam_questions)
    st.download_button(
        label="Download Exam as Text File",
        data=exam_text,
        file_name="exam.txt",
        mime="text/plain"
    )

    # Provide a downloadable version of the exam as PDF
    pdf_data = create_pdf(exam_questions)
    st.download_button(
        label="Download Exam as PDF",
        data=pdf_data,
        file_name="exam.pdf",
        mime="application/pdf"
    )
