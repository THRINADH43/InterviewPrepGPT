import streamlit as st
from pypdf import PdfReader
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ChatMessageHistory


memory = ChatMessageHistory()


openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

if openai_api_key:
    llm = ChatOpenAI(model="gpt-3.5-turbo",temperature = 0, api_key=openai_api_key)

def get_resume_summary(resume_data):
    
    data = llm([
        SystemMessage(content="you need to summarize the text"),
        HumanMessage(content=resume_data)
    ])
    st.session_state.sessionMessages.append(SystemMessage(content=data.content))
    return data.content


def get_description_summary(description_data):
    
    data = llm([
        SystemMessage(content="you need to summarize the text"),
        HumanMessage(content=description_data)
    ])
    st.session_state.sessionMessages.append(SystemMessage(content=data.content))
    return data.content


def generate_question(resume_data, description_data):
    
    data = llm([
        SystemMessage(content="You need to Generate 5 Question each time on reading the resume and job description summaries from Human" ),
        HumanMessage(content=resume_data),
        HumanMessage(content=description_data)
    ])
    st.session_state.sessionMessages.append(SystemMessage(content=data.content))
    data_questions['questions'].append(data.content)
    return data.content

st.title('InterviewPrep GPT')


if "sessionMessages" not in st.session_state:
    st.session_state.sessionMessages = []
    st.session_state.sessionMessages.append(SystemMessage(content="You will be Given Resume and Job Description to Analyze and Generate Questions and after user answers then you need to give him feedback"))



data_questions = {
    'questions' : [],
    'answers' : []
}


def answers_from_users():
    input_answer = st.text_input("Enter answer: ")
    if input_answer:
        data_questions['answers'].append(input_answer)
        return input_answer

upload_resume = st.file_uploader("Upload your resume", type="pdf")
resume_data = ''
if upload_resume:
    reader = PdfReader(upload_resume)
    for i in range(len(reader.pages)):
        resume_data += reader.pages[i].extract_text()

upload_description = st.file_uploader("Upload job description", type="pdf")
description_data = ''
if upload_description:
    reader = PdfReader(upload_description)
    for i in range(len(reader.pages)):
        
        description_data += reader.pages[i].extract_text()
    

def generate_feeback():
    answers = ''
    for i in data_questions['answers']:
        answers += i
    
    questions = ''
    for i in data_questions['questions']:
        questions += i

    data = llm([
        SystemMessage(content="Analyze all the Questions & Answers and then provide feedback." + questions),
        HumanMessage(content=(answers + questions)),
        #HumanMessage(content=questions)
    ])
    return data.content


resume_button = st.button("Get Resume Summary")
if resume_button: 
    if len(resume_data) != None:
        st.subheader('Resume Summary')
        st.write(get_resume_summary(resume_data))
    else:
        st.write("Please upload resume")

description_button = st.button("Get Description Summary")

if description_button: 
    if  len(description_data) != None:
        st.subheader('Description Summary')
        st.write(get_description_summary(description_data))
    else:
        st.write("Please upload description")
        

if resume_data is not None and description_data is not None:
    question_button = st.button("Generate Questions", key="generate_questions")

    if question_button:
        questions = generate_question(resume_data, description_data)
        memory.add_ai_message(AIMessage(content=questions))
        st.subheader('Questions')
        st.write(questions)
        data_questions['questions'].append(questions)

    answer = st.text_input("Your Answer : ")

if st.button("submit"):
    memory.add_user_message(HumanMessage(content=answer))
    data_questions['answers'].append(answer)
    feedback = generate_feeback()
    st.subheader('Feedback')
    st.write(feedback)
    st.write("Thank you for using InterviewPrep GPT")
