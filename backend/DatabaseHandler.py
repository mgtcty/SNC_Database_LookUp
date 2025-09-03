# LAST MODIFIED BY: Michael Tolentino
# LAST MODIFIED DATE: SEPT 3, 2025

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import numpy as np
import os
import re


# TODOS: # 1. Add error handling for database operations.
#        # 2. Add validation checking for adding new data

base = declarative_base()

EMBEDDING_DIMENSION = 384  # Dimension for "all-MiniLM-L6-v2" model

class Manuals(base):
    __tablename__ = 'manuals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    version = Column(String)
    releaseDate = Column(String)
    sections = relationship("Sections", back_populates="manual")

class Sections(base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sectionNumber = Column(String) # page number of this section
    sectionTitle = Column(String)
    sectionContent = Column(String)
    manual_id = Column(Integer, ForeignKey('manuals.id'))
    manual = relationship("Manuals", back_populates="sections")

class DatabaseManager:
    """
    A class to manage database operations for storing and retrieving manuals and their sections.
    
    Attributes:
        engine: The SQLAlchemy engine for database connection.
        Session: The SQLAlchemy session for database operations.
    Methods:
        insertManual(title, version, releaseDate): Inserts a new manual into the database.
        bulk_insert_sections(sections_data, manual_id): Inserts multiple sections of a given manual into the database.
        giveSections(topRelatedSectionIds=None): Retrieves sections from the database.
        deleteAll(): Deletes all records from the manuals and sections tables.
    """
    def __init__(self, url:str):
        self.engine = create_engine(url, echo=True) # create an engine
        base.metadata.create_all(self.engine) # create the tables
        self.Session = sessionmaker(bind=self.engine) # create a configured "Session" class
        self.session = self.Session()

    def insertManual(self, title:str, version:str, releaseDate:str):
        """
        Inserts a new manual into the manuals table.

        Parameters:
            title (str): The title of the manual.
            version (str): The version of the manual.
            releaseDate (str): The release date of the manual.

        Returns:
            int: The ID of the inserted manual.
        """
        try:
            manual = Manuals(title=title, version=version, releaseDate=releaseDate)
            self.session.add(manual)
            self.session.commit()
            return manual.id  # Return the manual's ID for later use
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting manual: {e}")
            return None

    def bulk_insert_sections(self, sections_data, manual_id):
        """
        Inserts multiple sections into the sections table.

        Parameters:
            sections_data: list of dicts with keys: sectionNumber, sectionTitle, sectionContent
            manual_id: int, the manual this batch of sections belongs to
        """
        try:
            sections = [
                Sections(
                    sectionNumber=sec['sectionNumber'],
                    sectionTitle=sec['sectionTitle'],
                    sectionContent=f"{re.sub(r'^\s*\d+(\.\d+)*\s*', '', sec['sectionTitle'])}. {sec['sectionContent']}",
                    manual_id=manual_id
                )
                for sec in sections_data
            ]
            self.session.add_all(sections)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting sections: {e}")

    def getManualNameIdPairs(self):
        """
        Retrieves all manuals from the database.

        Returns:
            list of tuples: Each tuple contains (manual_id, manual_title).
        """
        manualsIdPairs = self.session.query(Manuals.id, Manuals.title).all()
        manuals, ids = zip(*manualsIdPairs)
        return manuals, ids

    def printSampleSection(self):
        """
        Prints a sample of sections from the database for verification.
        """
        sections = self.session.query(Sections).limit(20).all()
        for section in sections:
            print(f"title: {section.sectionTitle}, content: {section.sectionContent}, number: {section.sectionNumber}, \n\n\n")

    def printSampleManual(self):
        """
        Prints a sample of manuals from the database for verification.
        """
        manuals = self.session.query(Manuals).limit(100).all()
        print(f"Total manuals: {len(manuals)}")
        for manual in manuals:
            print(manual.title, manual.version, manual.releaseDate, "\n\n\n")

    def giveSections(self, topRelatedSectionIds=None):
        """
        Retrieves sections from the database. If topRelatedSectionIds is provided, retrieves only related sections.

        Parameters:
            - topRelatedSectionIds (list of int, optional): List of section IDs to retrieve
        """
        if topRelatedSectionIds:
            # query then unzip the resulting tuples
            topRelatedContents = self.session.query(Sections.sectionContent, Sections.id, Sections.sectionNumber).filter(Sections.id.in_(topRelatedSectionIds)).all()
            topRelatedContents, ids, sectionNumber = zip(*topRelatedContents)
            # convert to lists
            topRelatedContents = list(topRelatedContents)
            ids = list(ids)
            sectionNumber = list(sectionNumber)
            return topRelatedContents, ids, sectionNumber
        
        # if no ids provided, return all sections
        sections = self.session.query(Sections.sectionContent, Sections.id).all()
        # convert to lists
        contents, ids = zip(*sections)
        contents = list(contents)
        ids = list(ids)
        return contents, ids

    def deleteAll(self):
        """
        Deletes all records from the manuals and sections tables.

        Returns:
            int: The number of deleted records from each table (manual, section).
        """
        try:
            numSectionDeleted = self.session.query(Sections).delete()
            numManualDeleted = self.session.query(Manuals).delete()
            self.session.commit()
            print(f"Deleted {numSectionDeleted} sections and {numManualDeleted} manuals.")
            return numSectionDeleted, numManualDeleted
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting records: {e}")