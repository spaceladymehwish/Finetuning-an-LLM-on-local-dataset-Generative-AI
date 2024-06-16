import csv
import json
import re 
import google.generativeai as genai #for text generation
import ast
from langchain.document_loaders import PDFMinerLoader #for pdf text extraction
from langchain.text_splitter import RecursiveCharacterTextSplitter # for text splitting
import os
import time #for waiting
import string #for punctuation

# Punctuation marks to be removed from the text before splitting 
punctuation = string.punctuation + "*[](){}\n"

# Load your API key 
GOOGLE_API_KEY= ""
genai.configure(api_key=GOOGLE_API_KEY) #

# it split the text into chunks of 3000 characters with 500 characters overlap between chunks for better results
splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n\n\n\n", "\n\n\n" , "\n\n\n\n\n"], chunk_size=3000, chunk_overlap=500)

# Gemini model for text generation 
model = genai.GenerativeModel('gemini-pro')

#track files in the folder and save it in trackFiles1.txt
fileName = "" #path of english-pdfs folder 
trackFiles = 'trackFiles1.txt' #path of trackFiles1.txt
for file in os.listdir('english-pdfs'): # loop through all files in the folder
    if not file:  # check if the file is empty or not
        continue  # if the file is empty, skip it
    file_path  = 'english-pdfs' + '\\' + file  # get the full path of the file in the folder
    loader = PDFMinerLoader(file_path).load()  # load the PDF file using PDFMinerLoader from langchain library
    text = splitter.split_text(loader[0].page_content)  # split the text into chunks using RecursiveCharacterTextSplitter
    print(file) # print the name of the file
    for t in text: # loop through the chunks
        if t in punctuation: # check if the chunk contains any punctuation marks
            text.remove(t) # remove the chunk if it contains punctuation marks
        result = model.generate_content(f"""
                                        Just find those questions that has detailed answers in this paragraph in python dictionary form. 
                                        Give me 50 detailed questions that has detailed answers from the given paragraph in the form that i can easily extract question and answers from it using python.
                                        Also give me question reference that this answer is of this question. Also give me code to convert it into python list at the end of the response.
                                        #####
                                        Paragraph: {t}
                                        """) # generate the response using the model and the given paragraph
        pattern = re.compile(r'\{[^{}]+\}') # compile the pattern to find the dictionary in the response
        if result.candidates: # check if the response has any candidates
            # Access the first candidate's content if available
            if result.candidates[0].content.parts: # check if the content of the candidate has any parts 
                generated_response = result.candidates[0].content.parts[0].text # get the text from the first part of the content
            else:
                generated_response = "None" # if the content has no parts, set the generated_response to None
        else:
            generated_response = "None" # if the response has no candidates, set the generated_response to None
        matches = pattern.findall(generated_response) # find all the matches in the generated_response using the pattern
        parsed_data = [] # initialize an empty list to store the parsed data
        
        for literal in matches: # loop through the matches in the generated_response using the pattern 
            try: # try to convert the literal to a dictionary 
                data = ast.literal_eval(literal) # convert the literal to a dictionary  
                parsed_data.append(data) # append the dictionary to the list of parsed data 
            except SyntaxError as e: # if the literal cannot be converted to a dictionary due to syntax error 
                print("Syntax error during parsing:", e) # print the error
            except ValueError as e: # if the literal cannot be converted to a dictionary due to value error 
                print("Value error, could not convert data:", e) # print the error
            
        for item in parsed_data: # loop through the parsed data  
            item = dict(item) # convert the parsed data to a dictionary
            question = item.get('question') # get the question from the dictionary
            answer = item.get('answer') # get the answer from the dictionary
            with open('output.csv', 'a', newline='', encoding='utf-8') as csvfile: # write the question and answer to the output.csv file
                fieldnames = ['question', 'answer'] # set the fieldnames to 'question' and 'answer'
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames) # create a DictWriter object with the fieldnames 
                answer_text = ', '.join(answer) if isinstance(answer, list) else answer # join the answer if it is a list, otherwise just set it to the answer
                writer.writerow({'question': question, 'answer': answer_text}) # write the question and answer to the output.csv file
    with open(trackFiles, 'a', newline='', encoding='utf-8') as trackfiles_f: # write the name of the file to the trackFiles1.txt file
        trackfiles_f.write(file + "\n") # write the name of the file to the trackFiles1.txt file
        trackfiles_f.close() # close the trackFiles1.txt file