from urllib.parse import unquote  # Importing unquote function from urllib.parse module
import csv  # Importing csv module for working with CSV files
import os  # Importing os module for operating system functions
import re  # Importing re module for regular expressions
from bs4 import BeautifulSoup  # Importing BeautifulSoup class from bs4 module for HTML parsing
import requests  # Importing requests module for making HTTP requests
import numpy as np
import time
import urllib3


def init_csv_writer(csv_save_dir):  # Defining a function to initialize a CSV writer
    csvFile = os.path.join(csv_save_dir, 'CSV.csv')  # Constructing the path to the CSV file
    with open(csvFile, "w",newline='', encoding='utf-8') as csvfile:  # Opening the CSV file in write mode
        writer = csv.writer(csvfile)  # Creating a CSV writer object
        writer.writerow(['title', 'promulgation_date'])  # Writing column headers to the CSV file
        csvfile.close()  # Closing the CSV file
    return csvFile  # Returning the path to the CSV file


def append_data_to_csv(csvFile, title, promulgation_date):  # Defining a function to append data to a CSV file
    with open(csvFile, "a",newline='', encoding='utf-8') as csvfile:  # Opening the CSV file in append mode
        writer = csv.writer(csvfile)  # Creating a CSV writer object
        writer.writerow([title, promulgation_date])  # Writing data to the CSV file
    return csvfile  # Returning the CSV file object


def making_dirs(dir):  # Defining a function to create directories if they don't exist
    if not os.path.exists(dir):  # Checking if the directory doesn't exist
        os.makedirs(dir)  # Creating the directory
    return dir  # Returning the directory path


def download_pdf(url, filename, pdf_save_dir):  # Defining a function to download a PDF file
    try:
        response = requests.get(url, stream=True,verify=False)  # Making an HTTP request to get the PDF file
        response.raise_for_status()  # Raise an exception for unsuccessful status codes
        file = os.path.join(pdf_save_dir, filename)  # Constructing the path to save the PDF file
        with open(file, 'wb') as f:
            for chunk in response.iter_content(1024):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
                print('Downloaded',filename)
    except (requests.exceptions.RequestException, urllib3.exceptions.ProtocolError) as e:
        print(f"Download failed: {e}")

def get_rules(page_source,pdf_save_dir, csv_save_dir):  # Defining a function to get rules from a page source
    titles = []  # Initializing a list to store titles
    dates = []  # Initializing a list to store promulgation dates
    get_rules_pdf_dir = os.path.join(pdf_save_dir,'getRules')  # Constructing the path to the PDF directory
    get_rules_csv_dir = os.path.join(csv_save_dir,'getRules')  # Constructing the path to the CSV directory
    soup = BeautifulSoup(page_source,'html.parser')  # Creating a BeautifulSoup object from the page source
    div_with_class_artlist = soup.find_all('div', class_='artlist')  # Finding all div elements with class 'artlist'
    pdf_dir = making_dirs(get_rules_pdf_dir)  # Creating the PDF directory
    csv_dir = making_dirs(get_rules_csv_dir)  # Creating the CSV directory
    csv_file = init_csv_writer(csv_dir)  # Initializing the CSV writer
    i = 0
    for d in div_with_class_artlist:  # Looping through div elements with class 'artlist'
        pdf_links = d.find_all('a')  # Finding all 'a' elements within the div
        for link in pdf_links:  # Looping through 'a' elements
            pdf_soup = BeautifulSoup(link['href'],'html.parser')  # Creating a BeautifulSoup object from the link URL
            for urls in (pdf_soup):  # Looping through URLs in the BeautifulSoup object
                res = requests.get(urls,verify=False)  # Making an HTTP request to get the page content
                res_soup = BeautifulSoup(res.text,'html.parser')  # Creating a BeautifulSoup object from the page content
                div_elements = res_soup.find_all('div',class_='artlist')  # Finding all div elements with class 'artlist'
                details = res_soup.find_all('div', class_='artdets')  # Finding all div elements with class 'artdets'
                for element in details:
                    # print(element)
                    # element.find()
                    # sec_soup = BeautifulSoup(element, 'html.parser')
                    promulgation_tag = element.find(text=re.compile(r'Promulgation Date:'))
                    if promulgation_tag:
                        date = promulgation_tag.split("|")[-2].split(":")[-1].strip()
                        dates.append(date) # Appending the promulgation date to the list of dates
                    else:
                        dates.append('N/A')  # Appending 'N/A' to the list of dates if there's no tag with promulgation date
                    # if promulgation_tag:
                    #     promulgation_date = re.search(r'Promulgation Date: (\w+ \d+, \d+)', promulgation_tag)
                    #     if promulgation_date:
                    #         dates.append(promulgation_date.group(1))
                    #         print(promulgation_date.group(1))
                    #     else:
                    #         dates.append('N/A')
                    #         print('N/A')
                # for detail in details:  # Looping through div elements with class 'artdets'
                #     details = detail.get_text(strip=True)  # Getting the text content of the div element
                #     promulgation_date = detail.split('|')[1].strip().split(':')[-1].strip()  # Extracting the promulgation date
                #     dates.append(promulgation_date)  # Appending the promulgation date to the list
                #     print(promulgation_date)  # Printing the promulgation date
                for div_element in div_elements:
                    linkes = div_element.find_all('a')  # Finding all 'a' elements within the div element
                    for l in linkes:  # Looping through 'a' elements
                        pdf_down = BeautifulSoup(l['href'],'html.parser')  # Creating a BeautifulSoup object from the link URL
                        for u in pdf_down:  # Looping through URLs in the BeautifulSoup object
                            result = requests.get(u,verify=False)  # Making an HTTP request to get the page content
                            ele_soup = BeautifulSoup(result.text,'html.parser')  # Creating a BeautifulSoup object from the page content
                            ele = ele_soup.find('object')  # Finding the first 'object' element
                            if ele is not None:  # Checking if the 'object' element is None
                                ele = ele.find('embed')  # Finding the first 'embed' element within 'object'
                                title = ele['title']  # Extracting the title attribute
                                # i = i + 1
                                # print(i,title)
                                titles.append(title)  # Appending the title to the titles list
                                rules_pdf_url = ele['src']  # Extracting the PDF URL
                                filename = re.search(r'.*\/(.*?)\.pdf', rules_pdf_url).group(1) + ".pdf"  # Extracting the filename from the PDF URL
                                download_pdf(rules_pdf_url, filename,pdf_dir)  # Downloading the PDF file
                                r = np.random.randint(1,3)
                                time.sleep(r)
                            else:  # If the 'object' element is not None
                                continue
    with open(csv_file, 'a', newline='') as csvfile:  # Opening the CSV file in append mode
        writer = csv.writer(csvfile)  # Creating a CSV writer object
        for title, date in zip(titles, dates):  # Iterating through titles and dates simultaneously
            writer.writerow([title, date])  # Writing the title and promulgation date to the CSV file
    return 'Done'  # Returning a message indicating the function execution is complete


def get_laws(page_source,pdf_save_dir, csv_save_dir):  # Defining a function to get laws from a page source
    titles = []  # Initializing a list to store titles
    dates = []  # Initializing a list to store promulgation dates
    en_get_laws_pdf_dir = os.path.join(pdf_save_dir,'getLaws')  # Constructing the path to the PDF directory for laws
    en_get_laws_csv_dir = os.path.join(csv_save_dir,'getLaws')  # Constructing the path to the CSV directory for laws
    pdf_dir = making_dirs(en_get_laws_pdf_dir)  # Creating the PDF directory for laws
    csv_dir = making_dirs(en_get_laws_csv_dir)  # Creating the CSV directory for laws
    csv_file = init_csv_writer(csv_dir)  # Initializing the CSV writer for laws
    
    soup = BeautifulSoup(page_source,'html.parser')  # Creating a BeautifulSoup object from the page source
    div_with_class_alphabetical = soup.find_all('div', class_='row alphabets_wrap')  # Finding all div elements with class 'artlist'
    for url in div_with_class_alphabetical:
        alpha = url.find_all('a')
        for u in alpha:    
            alpha_request = requests.get(u['href'],verify=False)
            alpha_soup = BeautifulSoup(alpha_request.text,'html.parser')
            details = alpha_soup.find_all('div', class_='artdets')  # Finding all div elements with class 'artdets' for promulgation dates
            div_with_class_artlist = alpha_soup.find_all('div', class_='artlist')  # Finding all div elements with class 'artlist'
            for detail in details:  # Looping through div elements with class 'artdets'
                detail = detail.get_text(strip=True)  # Getting the text content of the div element
                promulgation_date = detail.split('|')[1].strip().split(':')[-1].strip()  # Extracting the promulgation date
                dates.append(promulgation_date)  # Appending the promulgation date to the list
            for d in div_with_class_artlist:  # Looping through div elements with class 'artlist'
                pdf_links = d.find_all('a')  # Finding all 'a' elements within the div for PDF links
                for link in pdf_links:  # Looping through 'a' elements
                    pdf_soup = BeautifulSoup(link['href'],'html.parser')  # Creating a BeautifulSoup object from the link URL
                    for urls in (pdf_soup):  # Looping through URLs in the BeautifulSoup object
                        res = requests.get(urls,verify=False)  # Making an HTTP request to get the page content
                        res_soup = BeautifulSoup(res.text,'html.parser')  # Creating a BeautifulSoup object from the page content
                        div_elements = res_soup.find('div',class_='artlist')  # Finding the first div element with class 'artlist'
                        if div_elements is None:  # Checking if div_elements is None
                            continue  # Skipping to the next iteration if div_elements is None
                        else:  
                            div_elements = div_elements.find('object')  # Finding the first 'object' element within div_elements
                            if div_elements is not None:  # Checking if div_elements is not None
                                div_elements = div_elements.find('embed')  # Finding the first 'embed' element within div_elements
                                titles.append(div_elements['title'])  # Appending the title to the titles list
                                pdf_url = div_elements['src']  # Extracting the PDF URL
                                filename = re.search(r'.*\/(.*?)\.pdf', pdf_url).group(1) + ".pdf"  # Extracting the filename from the PDF URL
                                download_pdf(pdf_url, filename,pdf_dir)  # Downloading the PDF file
                                r = np.random.randint(1,3)
                                time.sleep(r)
                            else:  # If div_elements is None
                                continue  # Skipping to the next iteration if div_elements is None
    with open(csv_file, 'a', newline='') as csvfile:  # Opening the CSV file in append mode
        writer = csv.writer(csvfile)  # Creating a CSV writer object
        for title, date in zip(titles, dates):  # Iterating through titles and dates simultaneously
            writer.writerow([title, date])  # Writing the title and promulgation date to the CSV file
    return "Done"  # Returning a message indicating the function execution is complete