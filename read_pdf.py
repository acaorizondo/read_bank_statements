# import libraries
import PyPDF2
import re
import os
import csv

os.system('cls') # clear console

# functions declaration
def extract_statement_headers(first_index, first_pattern, line_text):
    statement_header = line_text[:first_index:] # locating the header
    statement_header = statement_header[:statement_header.find("Page"):] # removing Page label from header
    
    # extract the header of the transactions
    length = len(first_pattern)
    transactions_header = line_text[first_index:first_index+length+5:]
   
    return (statement_header, transactions_header)

def split_transaction(transaction):
    # getting Activity Date
    search_pattern_activity_date = r'([A-Z][a-z]{2}\s[0-9]{2})'
    activity_date_obj = re.search(search_pattern_activity_date, transaction)
    activity_date = transaction[activity_date_obj.start():activity_date_obj.end():]

    # getting Post Date
    transaction = transaction[activity_date_obj.end()::]
    search_pattern_post_date = r'([A-Z][a-z]{2}\s[0-9]{2})'
    post_date_obj = re.search(search_pattern_post_date, transaction)
    post_date = transaction[post_date_obj.start():post_date_obj.end():]

    # getting Reference Number
    transaction = transaction[post_date_obj.end()::]
    search_pattern_post_date = r'([0-9]+\s)'
    reference_number_obj = re.search(search_pattern_post_date, transaction)
    reference_number = transaction[reference_number_obj.start():reference_number_obj.end()-1:]

    # getting Amount
    transaction = transaction[reference_number_obj.end()::]
    search_pattern_amount = r'(\d+.\d+\s*\w*$)'
    amount_obj = re.search(search_pattern_amount, transaction, re.ASCII)
    amount = transaction[amount_obj.start():amount_obj.end():]
    # split Amount value and CR
    search_pattern_amount = r'(\d+.\d{2})'
    obj = re.search(search_pattern_amount, amount)
    amount_value = amount[obj.start():obj.end():]
    amount_cr = amount[obj.end()+1::]

    # getting Transaction Description
    description = transaction[:amount_obj.start()-1:]           

    item=[activity_date, post_date, reference_number, description, amount_value, amount_cr]
    return item

def locate_transactions(first_pattern, first_index, last_index, line_text):
    transactions = line_text[first_index:last_index:]
    transactions_detail = transactions[len(first_pattern)+6::]
    search_pattern = r'([A-Z][a-z]{2}\s[0-9]{2}\s[A-Z][a-z]{2}\s[0-9]{2})'
    transactions_index = re.finditer(search_pattern, transactions_detail)
        
    # create a position list for each trasnsaction
    position_list = []
    for match_obj in transactions_index:
        position_list.append(match_obj.start())
    
    return position_list, transactions_detail 

def read_transactions(position_list, transactions_detail, transactions_list):
    count_of_positions = len(position_list)
    if (count_of_positions > 0):
        index = 0
        for pos in position_list:
            # setting positions
            begin_position = pos
            if (index == count_of_positions-1):
                end_position = len(transactions_detail)
            else:
                index += 1
                end_position = position_list[index]
                
            transaction = transactions_detail[begin_position:end_position-1:]

            #split transaction
            item = split_transaction(transaction)
            
            # save each transaction in a list
            transactions_list.append(item)
    
    return transactions_list

def create_csv_file(file_dir, file_name, file_header, file_data):
    csv_file = file_dir + file_name
    try:
        with open(csv_file, 'w', newline='') as f:
            # create the csv writer
            writer = csv.writer(f)
            # write a row to the csv file
            writer.writerow(file_header)
            writer.writerows(file_data)
            return True
    except Exception as e:
        print(e)
        return False

def convert_statementPDF_to_statementeCSV(pdf_dir, pdf_name):
    with open(pdf_dir + pdf_name, mode='rb') as pdf_file:
        # create a pdf reader
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)

        # setting parameters
        num_pages = pdf_reader.numPages # total pages of the document
        first_page = 2  # page where transactions record begin
        page_number = first_page

        first_pattern = "Transactions Activity Date Post Date Reference Number Description Amount Card Number Ending in:"
        last_pattern_fees = "Fees Activity Date Post Date Reference Number Description Amount"
        last_pattern_no_fees = "Fees TOTAL FEES FOR THIS PERIOD"
    
        processed_pages = 0
        next_page = True
        transactions_list = []
    
        # process each page
        while next_page:
            page = pdf_reader.getPage(page_number)
            page_text = page.extract_text()
            # convert de page in a single string
            line_text = " ".join(line.strip() for line in page_text.splitlines())

            # delimitate the block where statements are
            first_index = line_text.find(first_pattern)
            last_index = int(line_text.find(last_pattern_fees)) * int(line_text.find(last_pattern_no_fees)) * -1
        
            # extract the headers of the statement once
            if (processed_pages == 0):
                statement_header, transactions_header = extract_statement_headers(first_index, first_pattern, line_text) 
                print(statement_header)
                print(transactions_header)

            # locate transactions in the file
            position_list, transactions_detail = locate_transactions(first_pattern, first_index, last_index, line_text)
        
            # read transactions
            transactions_list = read_transactions(position_list, transactions_detail, transactions_list)    

            # increment page number if current page is not the last one that contain transactions
            processed_pages += 1
            if (processed_pages == num_pages-2 or last_index != -1):
                next_page = False
            else:
                page_number += 1    
    
            # create csv file
            file_dir = pdf_dir
            file_name = pdf_name[:len(pdf_name)-3:]+'csv'  # remove .pdf from name of file and add csv extension
            file_header = ['Activity Date', 'Post Date', 'Reference Number', 'Description', 'Amount', 'CR']
            file_data = transactions_list
            created = create_csv_file(file_dir, file_name, file_header, file_data)
            if (created):
                print('File created!')
                print(file_dir + file_name)
                return file_dir + file_name
            else:
                print('Conversion has failed')


# setting global parameters
pdf_name = "file_name.pdf"
pdf_dir = "path"
csv_file = convert_statementPDF_to_statementeCSV(pdf_dir, pdf_name)
    


    
    

