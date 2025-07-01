import numpy as np
from typing import List
from datetime import datetime
import json

class Book:
    def __init__(self, id:str, title:str, author:str, year:int, level_start:int, level_end:int, description:str,
                 stars=None, difficulties=None, comments=None, physical_books=None):
        # Info
        self.id = id # physical_id // 100 = id
        self.title = title
        self.author = author 
        self.year = year 
        self.level_start = level_start
        self.level_end = level_end
        self.description = description

        # Feedback
        self.stars = stars if stars is not None else [] # 1-5 stars
        self.difficulties = difficulties if difficulties is not None else [] # 1-3
        self.comments = comments if comments is not None else []

        # Library Status
        self.physical_books = physical_books if physical_books is not None else []
    

    # Add and remove stuff

    def add_feedback(self, stars, difficulty, comment):
        stars = min(stars, 5)
        stars = max(stars, 0)
        self.stars.append(stars)

        difficulty = min(difficulty, 3)
        difficulty = max(difficulty, 1)
        self.difficulties.append(difficulty)

        if not (comment is None or comment == ""):
            self.comments.append(comment)
            
    def remove_all_feedback(self):
        self.stars = []
        self.difficulties = []
        self.comments = []

    def add_copy(self):
        phys_id = 0
        print(f"id {self.id}")

        if not self.physical_books: # First copy
            print("H")
            phys_id = self.id * 100 + 1
        else: # Next copies
            biggest_id = 0
            print("A")
            for phys_b in self.physical_books:
                if phys_b.id > biggest_id:
                    biggest_id = phys_b.id
            phys_id = biggest_id + 1

        print(f"biggest_id {phys_id}")
        self.physical_books.append(PhysicalBook(id=phys_id))
        return phys_id

    def remove_copy(self, phys_id):
        index = -1
        for i, phys_book in enumerate(self.physical_books):
            if phys_book.id == phys_id:
                index = i
                break
        if index == -1:
            print(f"Removing copy failed: Physical ID does not exist")
        else:
            del self.physical_books[index]
            print(f"Removed copy {phys_id} from book")


    # Get stuff

    def get_num_availability(self):
        sum = 0
        for phys_b in self.physical_books:
            sum += 1 if phys_b.is_available else 0
        return sum

    def get_available_phys_ids_str(self):
        ids_str = ""
        for phys_b in self.physical_books:
            ids_str += f"{phys_b.id} " if phys_b.is_available else 0
        return ids_str

    def get_number_of_copies(self):
        return len(self.physical_books)

    def get_times_borrowed(self):
        return len(self.stars)

    def get_stars(self):
        return 0 if len(self.stars) == 0 else np.mean(self.stars)
    
    def get_stars_whole(self):
        return round(self.get_stars())
    
    def get_difficulty(self):
        return 0 if len(self.difficulties) == 0 else np.mean(self.difficulties)

    def get_difficulty_whole(self):
        return round(self.get_difficulty())
    
    def get_book_id_str(self):
        return str(self.id)
    


    def __str__(self):
        return f"""
ID: {self.id}, Title: {self.title}, Author: {self.author}, Year: {self.year}, Level: {self.level_start} - {self.level_end}
Stars: {self.stars}, difficulty: {self.difficulties}, 
Average Stars: {self.get_stars()}, Average Difficulty: {self.get_difficulty()}, Times Borrowed: {self.get_times_borrowed()}
Comments: {self.comments}, 
Physical copies: {[phys_b for phys_b in self.physical_books]}
"""
    

class PhysicalBook:
    def __init__(self, id:int, is_available:bool=True, give_back_until:str=None, owners=None):
        self.id = id # 100 * book_id + copy_n

        # Library status
        self.is_available = is_available
        self.give_back_until = give_back_until # Date Iso-Format
        self.owners: List[Owner] = owners if owners is not None else [] # List of Owner, owners[-1] currently has it

    def remove_history(self):
        self.is_available = True
        self.give_back_until = None 
        self.owners: List[Owner] = []

    def get_current_owner_name(self):
        return self.owners[-1].name if not self.is_available else "Ist verfügbar"
    
    def is_late(self):
        if self.is_available:
            return False
        else:
            return True if datetime.now() > datetime.fromisoformat(self.give_back_until) else False
                
    def __str__(self):
        return f"""
ID: {self.id}, Is available: {self.is_available}, Give back until: {self.give_back_until},
Owners: {[owner for owner in self.owners]}
"""
    

class Owner:
    def __init__(self, name:str, start_date:str, end_date:str=None):
        self.name = name
        self.start_date = start_date # Iso-Format
        self.end_date = end_date # Iso-Format

    def set_end_date(self, end_date:str):
        self.end_date = end_date

    def __str__(self):
        return f"Name: {self.name}, From: {self.start_date}, To: {self.end_date})"



# JSON Decoders

class BookDecoder(json.JSONDecoder):
    def decode(self, s):
        books_dict = json.loads(s)
        books = []

        for bd in books_dict:
            books.append(Book(id=bd['id'],
                              title=bd['title'],
                              author=bd['author'],
                              year=bd['year'],
                              level_start=bd['level_start'],
                              level_end=bd['level_end'],
                              description=bd['description'],

                              stars=bd['stars'],
                              comments=bd['comments'],
                              difficulties=bd['difficulties'],
                              physical_books=PhysicalBookDecoder().decode(json.dumps(bd['physical_books']))))
        return books

class PhysicalBookDecoder(json.JSONDecoder):
    def decode(self, s):
        phys_books_dict = json.loads(s)
        phys_books = []

        for pbd in phys_books_dict:
            phys_books.append(PhysicalBook(id=pbd['id'], 
                                           is_available=pbd['is_available'], 
                                           give_back_until=pbd['give_back_until'], 
                                           owners=OwnerDecoder().decode(json.dumps(pbd['owners']))))
        return phys_books
    
class OwnerDecoder(json.JSONDecoder):
    def decode(self, s):
        owners_dict = json.loads(s)
        owners = []

        for od in owners_dict:
            owners.append(Owner(name=od['name'], 
                                start_date=od['start_date'],
                                end_date=od['end_date']))
        return owners


