from util import Book, Owner, PhysicalBook, BookDecoder
import pickle
import json
from datetime import datetime, timedelta
from typing import List

class Library:
    def __init__(self):
        self.books: List[Book] = []

    def save_as_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.books, file, default=vars, ensure_ascii=False, sort_keys=True, indent=4)
            print(f"Saved library to {filename}")
        
    def load_from_json(self, filename):
        with open(filename, 'r') as file:
            self.books = json.load(file, cls=BookDecoder)
        print(f"Loaded library from {filename}")

    # Add and remove stuff
    def add_book(self, title, author, year, level_start, level_end, description): 
        book = Book(
            id=self.get_next_id(), 
            title=title, 
            author=author, 
            year=year, 
            level_start=level_start, 
            level_end=level_end, 
            description=description)
        book.add_copy()
        self.books.append(book)
        print(f"Added {book.id}: {book.title} to library")

    def remove_book(self, book_id):

        index = -1 # Get index from book_id
        for i, book in enumerate(self.books):
            if book.id == book_id:
                index = i
                break

        if index == -1:
            raise ValueError(f"Removing book failed: ID {book_id} does not exist")
        
        for phys_book in self.books[index].physical_books:
            self.remove_copy(phys_book.id) # Remove all copies first

        self.books.pop(index)
        print(f"Removed {book_id} from library")


    def add_copy(self, book_id):
        book = self.get_book_by_id(book_id)

        if book is None:
            print("No book with this ID")
            return

        phys_id = book.add_copy()
        print(f"Added copy of {book.title} with phys_id {phys_id} to library")

    def remove_copy(self, phys_id):
        book = self.get_book_by_id(self.get_book_id_from_physical_id(phys_id))
        
        if book is None:
            print("No book with this ID")
            return

        # Find index of physical book
        index = -1
        for i, phys_book in enumerate(book.physical_books):
            if phys_book.id == phys_id:
                index = i
                break
        
        if index == -1:
            raise ValueError(f"Removing copy failed: Physical ID {phys_id} does not exist")
        
        book.physical_books.pop(index) # Remove copy
        print(f"Removed {phys_id} from library")


    # Get stuff
    def get_my_books(self, username):
        my_books = []
        for book in self.books:
            for phys_book in book.physical_books:
                if not phys_book.is_available and phys_book.owners[-1].name == username:
                    my_books.append(phys_book)
        
        return my_books

    def get_next_id(self):
        # First book -> 1
        if not self.books:
            return 1

        # Additional books -> biggest id + 1
        biggest_id = 0
        for book in self.books:
            if book.id > biggest_id:
                biggest_id = book.id
        return biggest_id + 1

    def get_book_id_from_physical_id(self, phys_id):
        return phys_id // 100

    def get_book_by_id(self, book_id) -> Book:
        for book in self.books:
            if book.id == book_id:
                return book
            
        return None
    
    def get_physical_book_by_id(self, phys_id) -> PhysicalBook:
        book = self.get_book_by_id(self.get_book_id_from_physical_id(phys_id))

        if book is None:
            return None
        
        for phys_b in book.physical_books:
            if phys_b.id == phys_id:
                return phys_b

        return None
    

    # Borrowing logic and checks
    def check_too_late(self):
        now = datetime.now()

        for book in self.books:
            for phys_book in book.physical_books:
                if not phys_book.is_available:
                    if now > datetime.fromisoformat(phys_book.give_back_until):
                        print(f"{phys_book.owners[-1].name} is late with {book.title}. Diff: {now - datetime.fromisoformat(phys_book.give_back_until)}")

    def borrow(self, phys_id, username, n_days):
        phys_b = self.get_physical_book_by_id(phys_id)

        if phys_b is None:
            raise ValueError("No copy with this ID")
        
        if not phys_b.is_available:
            raise ValueError("Book is already borrowed")

        now = datetime.now()

        phys_b.is_available = False
        phys_b.owners.append(Owner(username, now.isoformat()))
        phys_b.give_back_until = (now + timedelta(days=n_days)).isoformat()

        print(f"Borrowed book: {phys_b.id}")
        
    def give_back(self, username, phys_id, stars, comment, difficulty):
        book = self.get_book_by_id(self.get_book_id_from_physical_id(phys_id))
        phys_book = self.get_physical_book_by_id(phys_id)

        if book is None:
            raise ValueError("No book with this ID")
        
        if phys_book is None:
            raise ValueError("No copy with this ID")

        if phys_book.is_available:
            raise ValueError("Book has not been borrowed")
        
        if username != 'admin' and phys_book.owners[-1].name != username:
            raise ValueError(f"Book has not been borrowed by {username}")
        
        now = datetime.now()

        if now > datetime.fromisoformat(phys_book.give_back_until):
            print(f"Gave book back too late. Diff: {now - datetime.fromisoformat(phys_book.give_back_until)}")

        phys_book.owners[-1].set_end_date(now.isoformat()) # Time given back
        phys_book.is_available = True
        phys_book.give_back_until = None
        
        book.add_feedback(stars=stars, difficulty=difficulty, comment=comment) # Set comment to None for no comment

        print(f"Returned book {book.id}: {book.title}")


    # Other
    def get_json(self):
        return json.dumps(self.books, default=vars, ensure_ascii=False, sort_keys=True, indent=4)

    def print_books(self):
        print("All books:")
        print("----------------------")
        for book in self.books:
            print(book)
            print("----------------------")
