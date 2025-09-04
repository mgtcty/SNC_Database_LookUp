# LAST MODIFIED BY: Michael Tolentino
# LAST MODIFIED DATE: SEPT 3, 2025

from PdfHandler import PdfReader
from DatabaseHandler import DatabaseManager
from Retriever import Retriever
from Generator import Generator
import os
from dotenv import load_dotenv

def main():
    # === Load PDF ===
    x = PdfReader("sample.pdf")
    x.extractText()

    # === Load .env ===
    load_dotenv()
    creds = {k: os.getenv(k) for k in ["user", "password", "host", "port", "dbname"]}

    # === Database ===
    url = f"postgresql+psycopg2://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['dbname']}"
    db = DatabaseManager(url)
    db.deleteAll()
    print("Database cleared.")
    manual_id = db.insertManual("DETAILING MANUAL", "1st Edition Rev 0", "07/19/2022")
    db.bulk_insert_sections(x.extracted_text, manual_id) # Uncomment to insert data
    print("PDF data inserted into the database.")
    '''contents, ids = db.giveSections()

    # === RAG Components ===
    retriever = Retriever()
    retriever.add(contents, ids)

    generator = Generator()

    # === Query loop ===
    os.system("cls")
    print("Welcome to the SNC Engineering Manual Query System!")
    user_query = input("Enter your query: ")

    top_ids = retriever.search(user_query, top_k=3)
    top_contents, top_section_ids, section_numbers = db.giveSections(top_ids)

    ai_response = generator.generate(user_query, top_contents, section_numbers)

    os.system("cls")
    print(f"AI Response:\n{ai_response}")'''

if __name__ == "__main__":
    main()
