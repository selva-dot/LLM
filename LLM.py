import os
import re
import subprocess 
from typing import List, Dict, Tuple
import pandas as pd
from typing import Optional
import regex
from ast import literal_eval
import json
from unidecode import unidecode


clause_title_pattern = re.compile(r"""
    ^\s*                             
    (Clause\s+Title:)?               
    \s*                             
    \s*(\d+\.?)?\s*              
    \s*                              
    ([A-Z][A-Za-z\s]{1,30})         
    \s*                              
    (?:[.:])?                        
    \s*$                            
""", re.VERBOSE)


def extract_clauses_with_bullets(pdftotext_output: str) -> Tuple[List[Dict[str, str]], List[str]]:
   
    clauses = []
    line_numbers = [] 
    current_clause = None
    is_title_continuation = False  

    lines = pdftotext_output.splitlines()

    line_counter = 0

    for i, line in enumerate(lines):
        line = line.strip()

        
        line_counter += 1

        if line_counter <= 5:
            continue
        if line.isdigit():
            continue
        if line and line[0].isupper() and line.endswith('.'):
            continue

        match = clause_title_pattern.match(line)

        if match:
            title_line_number = i + 1  
            line_numbers.append(title_line_number)
       
            if current_clause and not is_title_continuation:
                clauses.append(current_clause)

            if is_title_continuation:
                current_clause["title"] += f", {match.group(0)}"
            else:
        
                new_title = match.group(0)
                current_clause = { 
                    "title": new_title,
                    "content": "",  
                    "line_number": title_line_number 
                }

          
            is_title_continuation = True
            continue


        is_title_continuation = False

    if current_clause:
        clauses.append(current_clause)


    total_titles = len(clauses)
    # print(f"Total number of titles: {total_titles}")
    # print(f"Title Line Numbers: {line_numbers}")
    for idx, clause in enumerate(clauses):
        start_line = clause['line_number'] + 1 
        end_line = clauses[idx + 1]['line_number'] if idx + 1 < len(clauses) else len(lines)  

        content_lines = lines[start_line:end_line-1] 
        clause['content'] = "\n".join(content_lines).strip()  

    return clauses, lines  

def sanitize_pdf_to_text(context, f_name=None):
    context = [item.strip() for item in context.split()]
    clean_context = " ".join(context)
    clean_context = unidecode(clean_context)

    if f_name:
        with open(f"./result/sanitized_pdftotext/{f_name}.txt", mode="w", encoding="utf8") as f:
            f.write(clean_context)

    output_data = {} 
    return clean_context, output_data
  

def get_filename_from_path(file_path):
    return os.path.basename(file_path)



def fuzzy_substring_search(major: str, minor: str, errs: int = 5) -> Optional[regex.Match]:

    if not minor.strip():  
        return None
    
    minor = regex.escape(minor)
    
    errs_ = 1
    s = regex.search(f"({minor}){{e<={errs_}}}", major)

    while s is None and errs_ <= errs:
        errs_ += 1
        s = regex.search(f"({minor}){{e<={errs_}}}", major)
    
    return s 


def process_row(row, data, rel_columns, output_data):

    if not isinstance(data, str):
        data = str(data)

    for column in rel_columns:
        # print("column:", column)
        if pd.notna(row[column]):  
            try:
                text = literal_eval(str(row[column]))
            except (ValueError, SyntaxError):
                text = str(row[column])

            if isinstance(text, str):
                text = [text]  
            
            for item in text:
                if isinstance(item, str):
                    # print(f"Type of data: {type(data)}")
                    # print(f"Type of item: {type(item)}")
                    
                    match = fuzzy_substring_search(major=data, minor=item, errs=5)
                    if match:
                        output_data["Answers"][column] = {
                            "start_index": match.start(),
                            "end_index": match.end(),
                            "text": match.group(),
                        }
                        # print(f"Match found for '{column}': {match.group()}")
                    else:
                        print(f"No match found for '{column}'.")
                else:
                    print(f"Item '{item}' is not a string, skipping.")



def extract_content_pdftotext(file_path, f_name=None):
 
    f_name=os.path.splitext(os.path.basename(f_name))[0]
    output_file = f'./result/pdftotext/{f_name}.txt'

    try:
        subprocess.run(['pdftotext', '-layout', file_path, output_file], check=True)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # print("content:",content)
        
        return content
    except Exception as e:
        print(f"Failed to extract content using pdftotext: {e}")
        return ""  
    
def process_pdf_and_fuzzy_matching(file_path, csv_file_path):
    """Process the PDF file and perform fuzzy matching with CSV content."""

    filename = get_filename_from_path(file_path)
    # print("filename:", filename)

    pdftotext_content = extract_content_pdftotext(file_path, f_name=filename)
    # print(" pdftotext_content:", pdftotext_content)
   
    sanitize_content=sanitize_pdf_to_text(context=pdftotext_content, f_name=filename)

    df = pd.read_csv(csv_file_path)

    output_data = {
        "Clauses": {},
        "Answers": {}  
    }

    rel_columns = [
        "Agreement Date",
        "Effective Date",
        "Expiration Date",
        "Renewal Term",
        "Notice Period To Terminate Renewal",
        "Governing Law",
    ]
    matching_row = df[df['Filename'] == filename]

    if not matching_row.empty:
        print(f"\nProcessing row for filename: {filename}")
        process_row(matching_row.iloc[0], sanitize_content, rel_columns, output_data) 

        clauses, lines = extract_clauses_with_bullets(pdftotext_content) 

        for index, clause in enumerate(clauses):
            start_index = clause.get("line_number", 0)  
       
            if index + 1 < len(clauses):
                end_index = clauses[index + 1].get("line_number", 0) - 1  
            else:
                end_index = len(lines) - 1  

            output_data["Clauses"][f"{index + 1}st Clause"] = {
                "start_index": start_index,
                "end_index": end_index,
                "title": clause.get("title", ""),
                "text": clause.get("content", ""),
            }

        for column in rel_columns:
            if column in output_data["Answers"]:
                output_data["Answers"][column] = {
                    "start_index": output_data["Answers"][column]["start_index"],
                    "end_index": output_data["Answers"][column]["end_index"],
                    "text": output_data["Answers"][column]["text"],
                }

        json_output_file = f'./result/Json/{get_filename_from_path(file_path).replace(".pdf", ".json")}'
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
    else:
        print(f"No matching row found for filename: {filename}")
        with open(no_match_file, 'a') as f:
            f.write(f"{filename}\n") 


folder_path = './static/'
csv_file_path = './csv/master_clauses.csv'
no_match_file = './result/not_found/no_match_files.txt' 


open(no_match_file, 'w').close() 
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    if os.path.isfile(file_path) and filename.endswith('.pdf'):

        
        process_pdf_and_fuzzy_matching(file_path, csv_file_path)