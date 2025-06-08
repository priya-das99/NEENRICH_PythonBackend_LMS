import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1/books/"

# Sample book data for 10 books
BOOKS_DATA = [
    {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "isbn": "978-0345391803",
        "copies": 5,
        "available_copies": 5,
        "category": "Science Fiction",
        "book_description": "A comedic science fiction series."
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "isbn": "978-0141439518",
        "copies": 7,
        "available_copies": 7,
        "category": "Classic",
        "book_description": "A romantic novel of manners written by Jane Austen."
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "978-0345339683",
        "copies": 6,
        "available_copies": 6,
        "category": "Fantasy",
        "book_description": "A children's fantasy novel."
    },
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "978-0441013593",
        "copies": 4,
        "available_copies": 4,
        "category": "Science Fiction",
        "book_description": "A science fiction novel set in the distant future amidst a feudal interstellar empire."
    },
    {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "isbn": "978-0486415871",
        "copies": 3,
        "available_copies": 3,
        "category": "Classic",
        "book_description": "A novel by the Russian author Fyodor Dostoevsky."
    },
    {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "isbn": "978-0618053267",
        "copies": 8,
        "available_copies": 8,
        "category": "Fantasy",
        "book_description": "An epic high-fantasy adventure novel."
    },
    {
        "title": "Foundation",
        "author": "Isaac Asimov",
        "isbn": "978-0553803719",
        "copies": 5,
        "available_copies": 5,
        "category": "Science Fiction",
        "book_description": "A science fiction novel by American writer Isaac Asimov."
    },
    {
        "title": "War and Peace",
        "author": "Leo Tolstoy",
        "isbn": "978-1400079988",
        "copies": 2,
        "available_copies": 2,
        "category": "Classic",
        "book_description": "A novel by the Russian author Leo Tolstoy."
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "978-0316769174",
        "copies": 4,
        "available_copies": 4,
        "category": "Fiction",
        "book_description": "A novel by J. D. Salinger."
    },
    {
        "title": "Dune Messiah",
        "author": "Frank Herbert",
        "isbn": "978-0441172696",
        "copies": 3,
        "available_copies": 3,
        "category": "Science Fiction",
        "book_description": "The second novel in the Dune series."
    }
]

async def add_books():
    print("Starting to add dummy books...")
    async with httpx.AsyncClient() as client:
        for i, book_data in enumerate(BOOKS_DATA):
            print(f"Adding book {i+1}/{len(BOOKS_DATA)}: {book_data['title']}")
            try:
                response = await client.post(BASE_URL, json=book_data)
                response.raise_for_status()  # Raise an HTTPStatusError for bad responses (4xx or 5xx)
                print(f"Successfully added book: {book_data['title']}")
            except httpx.HTTPStatusError as e:
                print(f"Error adding book {book_data['title']}: Client error '{e.response.status_code} {e.response.reason_phrase}' for url '{e.request.url}'")
                print(f"Response content: {e.response.text}")
            except httpx.RequestError as e:
                print(f"Error adding book {book_data['title']}: An error occurred while requesting {e.request.url!r}.")
            except Exception as e:
                print(f"An unexpected error occurred while adding book {book_data['title']}: {e}")
    print("Finished adding dummy books!")

if __name__ == "__main__":
    asyncio.run(add_books()) 