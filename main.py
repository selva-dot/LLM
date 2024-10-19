from pdfminer.high_level import extract_text
from PIL import Image
import pdfplumber
import os
import re
import subprocess 
from typing import List, Dict
import pandas as pd
from typing import Optional
import regex
from ast import literal_eval



# Function to extract content using pdftotext
def extract_content_pdftotext(file_path):
    print(f"Extracting content from PDF file with pdftotext: {file_path}")
    output_file = './result/pdftotext_output.txt'

    try:
        # Call the pdftotext command with -layout flag for better formatting
        subprocess.run(['pdftotext', '-layout', file_path, output_file], check=True)
        
        # Read the content from the output file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # print(f"Content extracted successfully using pdftotext. Size: {len(content)} characters.")
        os.remove(output_file)
        return content
    except Exception as e:
        print(f"Failed to extract content using pdftotext: {e}")
        return ""

bullet_patterns = re.compile(r"""
    ^\s*
    (   \d{1,3}(\.\d{1,3}){0,3}    # 1., 1.1., 1.1.1., etc.
    |   [A-Z]\.                    # A., B., C., etc.
    |   [a-z]\.                    # a., b., c., etc.
    |   [IVXLCDM]+                 # I, II, III, etc. (without dot)
    |   [ivxlcdm]+                 # i, ii, iii, etc. (without dot)
    |   \d+\)                      # 1), 2), 3), etc.
    |   \(\d+\)                    # (1), (2), (3), etc.
    )
    \s*  # Optional space after the bullet
""", re.VERBOSE)

clause_title_pattern = re.compile(r"""
    ^\s*                           # Start of the line with optional leading spaces
    (Clause\s+Title:)?             # Optional "Clause Title:" prefix (if it exists)
    \s*([A-Z][A-Z\s]*)             # Capture uppercase letters and spaces (e.g., ARTICLE I)
    \s*[:]*\s*$                    # Optional colon at the end
""", re.VERBOSE)



def extract_clauses_with_bullets(pdftotext_output: str) -> List[Dict[str, str]]:
    """
    Extract clauses from the text based on heuristics for clause numbering patterns.
    Handles cases where clause titles and content may be split across multiple lines.
    
    Args:
        pdftotext_output (str): The text extracted from the PDF.

    Returns:
        List[Dict[str, str]]: A list of dictionaries where each dict represents a clause with 'title', 'content',
                              and 'confidence' score (0-1), and the 'line_number' where the title starts.
    """
    # Initialize variables
    clauses = []
    current_clause = None
    is_title_continuation = False  # Flag to detect title continuation

    # Split the text into lines for processing
    lines = pdftotext_output.splitlines()

    # Initialize a counter to skip the first five lines
    line_counter = 0

    # Step 1: Extract the clause titles with their line numbers
    for i, line in enumerate(lines):
        line = line.strip()  # Clean up leading/trailing whitespace

        # Increment the line counter
        line_counter += 1

        # Skip the first five lines (e.g., header, metadata)
        if line_counter <= 5:
            continue

        # Check for clause title
        match = clause_title_pattern.match(line)

        if match:
            # If we find a new title, finalize the previous clause (if any)
            if current_clause and not is_title_continuation:
                clauses.append(current_clause)

            if is_title_continuation:
                current_clause["title"] += f", {match.group(2)}"
            else:
            # Start a new clause and record its title and line number
                new_title = match.group(2)
                current_clause = {
                    "title": new_title,
                    "content": "",  # Content will be filled later
                    "confidence": 1.0,
                    "line_number": i + 1  # Store the 1-based line number of the title
                }

            # Set flag to indicate title continuation
            is_title_continuation = True
            continue

        # Reset title continuation flag, as we're now processing content
        is_title_continuation = False

    # Add the last clause (if any)
    if current_clause:
        clauses.append(current_clause)

    # Step 2: Extract content between titles using line numbers
    for idx, clause in enumerate(clauses):
        start_line = clause['line_number']  # Get starting line of current clause title
        end_line = clauses[idx + 1]['line_number'] if idx + 1 < len(clauses) else len(lines)  # Next title line

        # Extract content between the current title line and the next title's line
        content_lines = lines[start_line:end_line-1]  # Slice the lines between titles
        clause['content'] = "\n".join(content_lines).strip()  # Join lines as content for the clause

    return clauses

def extract_content_pdfminer(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            extracted_text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    # Replace line breaks with spaces to form one continuous paragraph
                    extracted_text += page_text.replace('\n', ' ') + ' '
        
        # Strip extra spaces and return the single paragraph
        return extracted_text.strip()
    
    except Exception as e:
        print(f"Failed to extract content from PDF using pdfplumber: {e}")
        return ""

# Main function to process the PDF file using both pdfplumber and pdftotext
def process_file(file_path):
    # Extract content using pdfplumber
    pdfminer_content = extract_content_pdfminer(file_path)
    
    # Extract content using pdftotext
    pdftotext_content = extract_content_pdftotext(file_path)

    # Extract clauses from the content
    clauses = extract_clauses_with_bullets(pdftotext_content)
    
    # Write both results to separate text files
    pdfminer_content_output_file = './result/extracted_content_pdfminer.txt'
    pdftotext_output_file = './result/extracted_content_pdftotext.txt'
    output_file = './result/extracted_clauses.txt'

    with open(pdfminer_content_output_file, 'w', encoding='utf-8') as f:
        f.write(pdfminer_content)
    
    with open(pdftotext_output_file, 'w', encoding='utf-8') as f:
        f.write(pdftotext_content)
    
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for clause in clauses:
            f.write(f"Clause Title: {clause['title']}\n")
            f.write(f"Clause Content: {clause['content']}\n\n")

    print(f"Extracted clauses have been written to {output_file}")

    print(f"Extracted content using pdfplumber has been written to {pdfminer_content_output_file}")
    print(f"Extracted content using pdftotext has been written to {pdftotext_output_file}")

def get_filename_from_path(file_path):
    return os.path.basename(file_path)

# Function for fuzzy substring search
def fuzzy_substring_search(major: str, minor: str, errs: int = 5) -> Optional[regex.Match]:
    """Find the closest matching fuzzy substring.

    Args:
        major: the string to search in
        minor: the string to search with
        errs: the total number of errors (allowed errors in the match)

    Returns:
        Optional[regex.Match] object
    """
    errs_ = 0
    s = regex.search(f"({minor}){{e<={errs_}}}", major)
    while s is None and errs_ <= errs:
        errs_ += 1
        s = regex.search(f"({minor}){{e<={errs_}}}", major)
    return s

# Function to process each row
def process_row(row, data, rel_columns):
    """Process each row in the DataFrame and search for matches in the text data."""
    for column in rel_columns:
        print("column:", column)
        if pd.notna(row[column]):  # Check if the column value is not NaN
            try:
                # Use literal_eval to evaluate the string content as Python literals (optional)
                text = literal_eval(str(row[column]))
            except (ValueError, SyntaxError):
                # If literal_eval fails, just use the raw string
                text = str(row[column])
            
            # print(f"\nSearching for fuzzy match of column '{column}': '{text}'")
            
            for item in text:

            # Perform fuzzy substring search
                match = fuzzy_substring_search(major=data, minor=item, errs=5)
            
            # Print the match result (if any)
            if match:
                print(f"Match found for '{column}': {match.group()}")
            else:
                print(f"No match found for '{column}'.")

        
# Main processing function
def process_pdf_and_fuzzy_matching(file_path, csv_file_path):
    """Process the PDF file and perform fuzzy matching with CSV content."""
    # 1. Process the PDF (for example, using pdfplumber or pdftotext)
    pdfminer_content = extract_content_pdfminer(file_path)
    
    filename = get_filename_from_path(file_path)
    print("filename:", filename)
    # For demonstration purposes, let's assume we are searching within the pdftotext content
    data = pdfminer_content

    # 2. Load  the master clauses CSV
    df = pd.read_csv(csv_file_path)
    
    # 3. Define relevant columns
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
        # 5. Process the matching row
        print(f"\nProcessing row for filename: {filename}")
        process_row(matching_row.iloc[0], pdfminer_content, rel_columns)  # Assuming one matching row

    else:
        print(f"No matching row found for filename: {filename}")
    # # 4. Filter DataFrame to include only relevant columns
    # df = df[rel_columns]

    # # 5. Process each row in the DataFrame
    # for index, row in df.iterrows():
    #     print(f"\nProcessing row {index}:")
    #     process_row(row, data, rel_columns)
    #     # Remove this 'break' if you want to process more than one row
    #     break


# Example usage
file_path = './static/ZtoExpressCaymanInc_20160930_F-1_EX-10.10_9752871_EX-10.10_Transportation Agreement.pdf'
process_file(file_path)
csv_file_path = './static/master_clauses.csv'
process_pdf_and_fuzzy_matching(file_path, csv_file_path)