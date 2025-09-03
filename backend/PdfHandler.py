# LAST MODIFIED BY: Michael Tolentino
# LAST MODIFIED DATE: SEPT 3, 2025

import pdfplumber
import re
import csv

class PdfReader:
    """
    A class that reads PDF files and extracts text and images from them.
    Attributes:
        file_path (str): The path to the PDF file.
        extracted_text (list): A list to store extracted text sections with their page numbers and titles.

    Methods:
        extractText(): Extracts text from the PDF file.
        storeToCSV(output_path): Stores the extracted text to a CSV file.
        extractImages(): Extracts images from the PDF file.
    """
    def __init__(self, file_path:str):
        self.file_path = file_path
        self.extracted_text = [] # list of dictionary having page number, section title, section content
        self.section_title_pattern = re.compile(r'^\d+(\.\d+)*\s+.+', re.MULTILINE) # Regular expression for section titles (e.g., "1. Introduction", "2.1 Overview")
        
    def extractText(self):
        """
        Extracts text from the PDF file.
        Returns:
            str: The extracted text.
        """
        with pdfplumber.open(self.file_path) as pdf:
            for pagenum, page in enumerate(pdf.pages):
                # REMOVE ONCE DONE TESTING
                if pagenum == 25:
                    break
                text = page.extract_text()
                if text:
                    # Find all section titles and their positions
                    matches = list(self.section_title_pattern.finditer(text))
                    for idx, match in enumerate(matches):
                        section_title = match.group().strip().replace("\n", " ")
                        start = match.end()
                        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
                        section_content = text[start:end].strip().replace("\n", " ")
                        if section_content and not re.search(r"\.{5,}", section_title):
                            self.extracted_text.append({
                                "sectionNumber": pagenum + 1,
                                "sectionTitle": section_title,
                                "sectionContent": section_content
                            })

    def storeToCSV(self, output_path:str):
        """
        Stores the extracted text to a CSV file.
        Args:
            output_path (str): The path to the output CSV file.
        """
        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["page_number", "section_title", "section_content"])
            writer.writeheader()
            for row in self.extracted_text:
                writer.writerow(row)

    def extractImages(self):
        """
        Extracts images from the PDF file.
        Returns:
            list: A list of extracted images.
        """
        pass
