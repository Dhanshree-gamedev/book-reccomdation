#!/usr/bin/env python3
"""
Database Seeding Script for Book Recommendation Platform

Populates the database with 60+ high-quality, real book records.
Safe to run multiple times (idempotent) - uses INSERT OR IGNORE.

Usage:
    python seed_books.py

Author: System
"""

import sqlite3
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.constants import DB_PATH


# ============================================================================
# Book Data - 65 Real Books with Diverse Genres
# ============================================================================

BOOKS = [
    # Fiction / Literary Fiction
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genres": ["Fiction", "Classic"],
        "description": "A powerful story of racial injustice and childhood innocence in the American South during the 1930s."
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "genres": ["Fiction", "Science Fiction", "Classic"],
        "description": "A dystopian masterpiece exploring totalitarianism, surveillance, and the manipulation of truth."
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genres": ["Fiction", "Classic"],
        "description": "A tragic tale of wealth, love, and the American Dream set in the Jazz Age."
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genres": ["Fiction", "Romance", "Classic"],
        "description": "A witty exploration of love, class, and society in Regency-era England."
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "genres": ["Fiction", "Classic"],
        "description": "A coming-of-age story following Holden Caulfield's experiences in New York City."
    },
    
    # Science Fiction
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "genres": ["Science Fiction", "Fantasy", "Adventure"],
        "description": "An epic tale of politics, religion, and ecology on the desert planet Arrakis."
    },
    {
        "title": "Foundation",
        "author": "Isaac Asimov",
        "genres": ["Science Fiction", "Classic"],
        "description": "The story of a group of scientists who seek to preserve knowledge as the Galactic Empire crumbles."
    },
    {
        "title": "Neuromancer",
        "author": "William Gibson",
        "genres": ["Science Fiction", "Technology"],
        "description": "A groundbreaking cyberpunk novel that defined the genre and predicted the internet age."
    },
    {
        "title": "The Martian",
        "author": "Andy Weir",
        "genres": ["Science Fiction", "Adventure"],
        "description": "An astronaut must use his ingenuity to survive alone on Mars after being left behind."
    },
    {
        "title": "Ender's Game",
        "author": "Orson Scott Card",
        "genres": ["Science Fiction", "Young Adult"],
        "description": "A young genius is trained in battle school to fight an alien invasion."
    },
    {
        "title": "The Left Hand of Darkness",
        "author": "Ursula K. Le Guin",
        "genres": ["Science Fiction", "Fantasy"],
        "description": "An envoy's mission to a planet where inhabitants can change their gender."
    },
    {
        "title": "Snow Crash",
        "author": "Neal Stephenson",
        "genres": ["Science Fiction", "Technology"],
        "description": "A pizza deliveryman and hacker uncovers a conspiracy in a near-future America."
    },
    {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "genres": ["Science Fiction", "Fiction"],
        "description": "A comedic space adventure following Arthur Dent after Earth's destruction."
    },
    
    # Fantasy
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genres": ["Fantasy", "Adventure", "Classic"],
        "description": "Bilbo Baggins embarks on an unexpected journey with dwarves to reclaim their homeland."
    },
    {
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
        "genres": ["Fantasy", "Adventure"],
        "description": "The first-person narrative of a legendary hero telling his own story."
    },
    {
        "title": "A Game of Thrones",
        "author": "George R.R. Martin",
        "genres": ["Fantasy", "Adventure"],
        "description": "Noble families fight for control of the Iron Throne in a land where seasons last years."
    },
    {
        "title": "The Way of Kings",
        "author": "Brandon Sanderson",
        "genres": ["Fantasy", "Adventure"],
        "description": "An epic fantasy set in a world of storms, magical armor, and ancient secrets."
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "genres": ["Fantasy", "Young Adult", "Adventure"],
        "description": "A young orphan discovers he's a wizard and begins his magical education at Hogwarts."
    },
    {
        "title": "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe",
        "author": "C.S. Lewis",
        "genres": ["Fantasy", "Children", "Classic"],
        "description": "Four children enter a magical land through a wardrobe and help defeat an evil witch."
    },
    
    # Mystery / Thriller
    {
        "title": "The Girl with the Dragon Tattoo",
        "author": "Stieg Larsson",
        "genres": ["Mystery", "Thriller"],
        "description": "A journalist and a hacker investigate a decades-old disappearance in Sweden."
    },
    {
        "title": "Gone Girl",
        "author": "Gillian Flynn",
        "genres": ["Mystery", "Thriller"],
        "description": "A marriage unravels when a wife disappears and all evidence points to her husband."
    },
    {
        "title": "The Da Vinci Code",
        "author": "Dan Brown",
        "genres": ["Mystery", "Thriller", "Adventure"],
        "description": "A symbologist uncovers a conspiracy hidden in Leonardo da Vinci's artwork."
    },
    {
        "title": "And Then There Were None",
        "author": "Agatha Christie",
        "genres": ["Mystery", "Classic"],
        "description": "Ten strangers are lured to an island where they are murdered one by one."
    },
    {
        "title": "The Silent Patient",
        "author": "Alex Michaelides",
        "genres": ["Mystery", "Thriller"],
        "description": "A therapist becomes obsessed with a woman who shot her husband and stopped speaking."
    },
    {
        "title": "In the Woods",
        "author": "Tana French",
        "genres": ["Mystery", "Thriller"],
        "description": "A detective investigates a murder that mirrors an unsolved case from his childhood."
    },
    
    # Romance
    {
        "title": "Outlander",
        "author": "Diana Gabaldon",
        "genres": ["Romance", "Fantasy", "Adventure"],
        "description": "A WWII nurse is transported back to 18th-century Scotland and falls for a Highland warrior."
    },
    {
        "title": "The Notebook",
        "author": "Nicholas Sparks",
        "genres": ["Romance", "Fiction"],
        "description": "An elderly man reads a love story to a woman with dementia in a nursing home."
    },
    {
        "title": "Me Before You",
        "author": "Jojo Moyes",
        "genres": ["Romance", "Fiction"],
        "description": "A young woman becomes a caregiver for a paralyzed man, and their lives are forever changed."
    },
    {
        "title": "The Time Traveler's Wife",
        "author": "Audrey Niffenegger",
        "genres": ["Romance", "Science Fiction", "Fiction"],
        "description": "A love story about a man with a genetic disorder that causes him to time travel."
    },
    
    # Non-Fiction / Self-Help
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "genres": ["Self-Help", "Non-Fiction", "Business"],
        "description": "A practical guide to building good habits and breaking bad ones using small changes."
    },
    {
        "title": "Thinking, Fast and Slow",
        "author": "Daniel Kahneman",
        "genres": ["Non-Fiction", "Science", "Philosophy"],
        "description": "A Nobel laureate explores the two systems that drive the way we think."
    },
    {
        "title": "The Power of Habit",
        "author": "Charles Duhigg",
        "genres": ["Self-Help", "Non-Fiction", "Science"],
        "description": "An exploration of the science of habit formation and how to change them."
    },
    {
        "title": "How to Win Friends and Influence People",
        "author": "Dale Carnegie",
        "genres": ["Self-Help", "Business", "Classic"],
        "description": "Timeless principles for building relationships and influencing others positively."
    },
    {
        "title": "The 7 Habits of Highly Effective People",
        "author": "Stephen R. Covey",
        "genres": ["Self-Help", "Business"],
        "description": "A principle-centered approach for solving personal and professional problems."
    },
    {
        "title": "Deep Work",
        "author": "Cal Newport",
        "genres": ["Self-Help", "Business", "Technology"],
        "description": "Rules for focused success in a distracted world."
    },
    
    # Business
    {
        "title": "Zero to One",
        "author": "Peter Thiel",
        "genres": ["Business", "Non-Fiction", "Technology"],
        "description": "Notes on startups, and how to build companies that create new things."
    },
    {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "genres": ["Business", "Non-Fiction", "Technology"],
        "description": "How today's entrepreneurs use continuous innovation to create successful businesses."
    },
    {
        "title": "Good to Great",
        "author": "Jim Collins",
        "genres": ["Business", "Non-Fiction"],
        "description": "Why some companies make the leap to greatness and others don't."
    },
    {
        "title": "Thinking in Bets",
        "author": "Annie Duke",
        "genres": ["Business", "Non-Fiction", "Philosophy"],
        "description": "Making smarter decisions when you don't have all the facts."
    },
    {
        "title": "The Innovator's Dilemma",
        "author": "Clayton M. Christensen",
        "genres": ["Business", "Technology", "Non-Fiction"],
        "description": "Why great companies fail and how they can avoid disruption."
    },
    
    # Biography / History
    {
        "title": "Steve Jobs",
        "author": "Walter Isaacson",
        "genres": ["Biography", "Business", "Technology"],
        "description": "The definitive biography of Apple's legendary co-founder."
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "genres": ["History", "Science", "Non-Fiction"],
        "description": "A sweeping narrative of human history from the Stone Age to the present."
    },
    {
        "title": "Educated",
        "author": "Tara Westover",
        "genres": ["Biography", "Non-Fiction"],
        "description": "A memoir of a woman who grew up in a survivalist family and went on to earn a PhD."
    },
    {
        "title": "The Diary of a Young Girl",
        "author": "Anne Frank",
        "genres": ["Biography", "History", "Classic"],
        "description": "The diary of a Jewish girl hiding from the Nazis during World War II."
    },
    {
        "title": "Becoming",
        "author": "Michelle Obama",
        "genres": ["Biography", "Non-Fiction"],
        "description": "The former First Lady's deeply personal memoir of her life and career."
    },
    {
        "title": "The Wright Brothers",
        "author": "David McCullough",
        "genres": ["Biography", "History"],
        "description": "The story of two brothers who taught the world how to fly."
    },
    
    # Technology / Science
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "genres": ["Technology", "Non-Fiction"],
        "description": "A handbook of agile software craftsmanship for better programming practices."
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "David Thomas and Andrew Hunt",
        "genres": ["Technology", "Non-Fiction"],
        "description": "Your journey to mastery as a software developer."
    },
    {
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "genres": ["Science", "Non-Fiction", "Classic"],
        "description": "An exploration of the universe, black holes, and the nature of time."
    },
    {
        "title": "The Gene: An Intimate History",
        "author": "Siddhartha Mukherjee",
        "genres": ["Science", "Non-Fiction", "History"],
        "description": "The story of the gene and how it shapes our bodies, minds, and future."
    },
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "genres": ["Technology", "Non-Fiction"],
        "description": "The big ideas behind reliable, scalable, and maintainable systems."
    },
    
    # Philosophy
    {
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "genres": ["Philosophy", "Classic", "Self-Help"],
        "description": "Personal writings by the Roman Emperor on Stoic philosophy."
    },
    {
        "title": "Man's Search for Meaning",
        "author": "Viktor E. Frankl",
        "genres": ["Philosophy", "Biography", "Non-Fiction"],
        "description": "A psychiatrist's experience in Nazi concentration camps and his theory of logotherapy."
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "genres": ["Fiction", "Philosophy", "Adventure"],
        "description": "A shepherd boy's journey to find treasure teaches him about following one's dreams."
    },
    {
        "title": "Siddhartha",
        "author": "Hermann Hesse",
        "genres": ["Fiction", "Philosophy", "Classic"],
        "description": "A young man's spiritual journey in ancient India to find meaning."
    },
    
    # Young Adult
    {
        "title": "The Hunger Games",
        "author": "Suzanne Collins",
        "genres": ["Young Adult", "Science Fiction", "Adventure"],
        "description": "In a dystopian future, teenagers fight to the death in a televised competition."
    },
    {
        "title": "Divergent",
        "author": "Veronica Roth",
        "genres": ["Young Adult", "Science Fiction", "Adventure"],
        "description": "A society divided into factions based on virtues tests one girl's identity."
    },
    {
        "title": "The Maze Runner",
        "author": "James Dashner",
        "genres": ["Young Adult", "Science Fiction", "Thriller"],
        "description": "A boy wakes up in a maze with no memory and must find a way out."
    },
    {
        "title": "The Fault in Our Stars",
        "author": "John Green",
        "genres": ["Young Adult", "Romance", "Fiction"],
        "description": "Two teenagers with cancer fall in love and search for meaning."
    },
    {
        "title": "Percy Jackson and the Lightning Thief",
        "author": "Rick Riordan",
        "genres": ["Young Adult", "Fantasy", "Adventure"],
        "description": "A teenager discovers he's the son of Poseidon and must prevent a war among the gods."
    },
    
    # Horror
    {
        "title": "The Shining",
        "author": "Stephen King",
        "genres": ["Horror", "Thriller", "Fiction"],
        "description": "A family's winter stay at an isolated hotel becomes a nightmare."
    },
    {
        "title": "It",
        "author": "Stephen King",
        "genres": ["Horror", "Thriller"],
        "description": "A group of children face an ancient evil that takes the form of a clown."
    },
    {
        "title": "Dracula",
        "author": "Bram Stoker",
        "genres": ["Horror", "Classic", "Fiction"],
        "description": "The classic tale of the Transylvanian vampire Count Dracula."
    },
    {
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "genres": ["Horror", "Science Fiction", "Classic"],
        "description": "A scientist creates life and must face the consequences of playing God."
    },
]


def get_book_count(cursor) -> int:
    """Get current number of books in database."""
    cursor.execute("SELECT COUNT(*) FROM books")
    return cursor.fetchone()[0]


def seed_books():
    """
    Seed the database with books.
    Uses INSERT OR IGNORE to be idempotent.
    """
    print("=" * 60)
    print("Book Recommendation Platform - Database Seeder")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Get initial count
    initial_count = get_book_count(cursor)
    print(f"\nBooks in database before seeding: {initial_count}")
    
    # Insert books
    inserted = 0
    skipped = 0
    
    for book in BOOKS:
        genres_json = json.dumps(book["genres"])
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO books (title, author, genres, description, added_by)
                VALUES (?, ?, ?, ?, ?)
            """, (
                book["title"],
                book["author"],
                genres_json,
                book["description"],
                None  # System-added books have no user
            ))
            
            if cursor.rowcount > 0:
                inserted += 1
                print(f"  [+] Added: {book['title']} by {book['author']}")
            else:
                skipped += 1
                
        except sqlite3.Error as e:
            print(f"  [!] Error adding '{book['title']}': {e}")
    
    # Commit changes
    conn.commit()
    
    # Get final count
    final_count = get_book_count(cursor)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60)
    print(f"  Books inserted:  {inserted}")
    print(f"  Books skipped:   {skipped} (already existed)")
    print(f"  Total books now: {final_count}")
    print("=" * 60)
    
    # Verify genre distribution
    print("\nGenre Distribution:")
    cursor.execute("""
        SELECT genres FROM books
    """)
    genre_counts = {}
    for row in cursor.fetchall():
        genres = json.loads(row[0])
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        print(f"  {genre}: {count} books")
    
    conn.close()
    
    return inserted, final_count


if __name__ == "__main__":
    seed_books()
