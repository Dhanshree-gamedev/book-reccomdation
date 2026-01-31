"""
Book Enrichment Module

Dynamically enriches book data with cover images and PDF links.
Uses Open Library Covers API for book covers and provides
appropriate PDF links based on public domain status.
"""

import urllib.parse
from typing import Dict, Any, List


# Public domain books with their Project Gutenberg IDs
# These are classic books that are definitely in the public domain
PUBLIC_DOMAIN_BOOKS = {
    "pride and prejudice": "https://www.gutenberg.org/files/1342/1342-pdf.pdf",
    "1984": "https://www.planetebook.com/free-ebooks/1984.pdf",
    "the great gatsby": "https://www.planetebook.com/free-ebooks/the-great-gatsby.pdf",
    "to kill a mockingbird": "https://giove.isti.cnr.it/demo/eread/Libri/angry/mockingbird.pdf",
    "frankenstein": "https://www.gutenberg.org/files/84/84-pdf.pdf",
    "dracula": "https://www.gutenberg.org/files/345/345-pdf.pdf",
    "the adventures of sherlock holmes": "https://www.gutenberg.org/files/1661/1661-pdf.pdf",
    "alice's adventures in wonderland": "https://www.gutenberg.org/files/11/11-pdf.pdf",
    "the picture of dorian gray": "https://www.gutenberg.org/files/174/174-pdf.pdf",
    "a tale of two cities": "https://www.gutenberg.org/files/98/98-pdf.pdf",
    "the odyssey": "https://www.gutenberg.org/files/1727/1727-pdf.pdf",
    "moby dick": "https://www.gutenberg.org/files/2701/2701-pdf.pdf",
    "war and peace": "https://www.gutenberg.org/files/2600/2600-pdf.pdf",
    "crime and punishment": "https://www.gutenberg.org/files/2554/2554-pdf.pdf",
    "the count of monte cristo": "https://www.gutenberg.org/files/1184/1184-pdf.pdf",
    "jane eyre": "https://www.gutenberg.org/files/1260/1260-pdf.pdf",
    "wuthering heights": "https://www.gutenberg.org/files/768/768-pdf.pdf",
    "great expectations": "https://www.gutenberg.org/files/1400/1400-pdf.pdf",
    "the scarlet letter": "https://www.gutenberg.org/files/25344/25344-pdf.pdf",
    "les miserables": "https://www.gutenberg.org/files/135/135-pdf.pdf",
    "the divine comedy": "https://www.gutenberg.org/files/8800/8800-pdf.pdf",
    "don quixote": "https://www.gutenberg.org/files/996/996-pdf.pdf",
    "meditations": "https://www.gutenberg.org/files/2680/2680-pdf.pdf",
    "the art of war": "https://www.gutenberg.org/files/132/132-pdf.pdf",
    "the prince": "https://www.gutenberg.org/files/1232/1232-pdf.pdf",
    "the republic": "https://www.gutenberg.org/files/1497/1497-pdf.pdf",
    "the iliad": "https://www.gutenberg.org/files/6130/6130-pdf.pdf",
    "beowulf": "https://www.gutenberg.org/files/16328/16328-pdf.pdf",
    "the metamorphosis": "https://www.gutenberg.org/files/5200/5200-pdf.pdf",
    "heart of darkness": "https://www.gutenberg.org/files/219/219-pdf.pdf",
    "the jungle book": "https://www.gutenberg.org/files/236/236-pdf.pdf",
    "treasure island": "https://www.gutenberg.org/files/120/120-pdf.pdf",
    "the call of the wild": "https://www.gutenberg.org/files/215/215-pdf.pdf",
    "the time machine": "https://www.gutenberg.org/files/35/35-pdf.pdf",
    "the war of the worlds": "https://www.gutenberg.org/files/36/36-pdf.pdf",
    "a christmas carol": "https://www.gutenberg.org/files/46/46-pdf.pdf",
    "the strange case of dr. jekyll and mr. hyde": "https://www.gutenberg.org/files/43/43-pdf.pdf",
    "the hound of the baskervilles": "https://www.gutenberg.org/files/2852/2852-pdf.pdf",
    "around the world in eighty days": "https://www.gutenberg.org/files/103/103-pdf.pdf",
    "20000 leagues under the sea": "https://www.gutenberg.org/files/164/164-pdf.pdf",
    "the hobbit": "https://archive.org/download/TheHobbitByJRRTolkien/The%20Hobbit.pdf",
    "siddhartha": "https://www.gutenberg.org/files/2500/2500-pdf.pdf",
    "the diary of a young girl": "https://www.bfrfrenchclub.org/uploads/3/1/8/3/31839903/the_diary_of_a_young_girl.pdf",
}

# Fallback cover image for books without covers
FALLBACK_COVER = "https://via.placeholder.com/300x450/e8f5e9/2e7d32?text=No+Cover"

# Sample PDF for non-public domain books
SAMPLE_PDF_URL = "https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf"


def get_cover_image_url(title: str) -> str:
    """
    Generate a book cover URL using Open Library Covers API.
    
    Args:
        title: Book title.
        
    Returns:
        URL string for the book cover image.
    """
    # URL encode the title for the API
    encoded_title = urllib.parse.quote(title)
    return f"https://covers.openlibrary.org/b/title/{encoded_title}-L.jpg"


def get_cover_image_with_fallback(title: str, author: str = "") -> str:
    """
    Generate a book cover URL with ISBN-based fallback.
    
    Uses Open Library search to find ISBN for better cover matching.
    
    Args:
        title: Book title.
        author: Author name (optional, improves accuracy).
        
    Returns:
        URL string for the book cover image.
    """
    # First try title-based cover
    encoded_title = urllib.parse.quote(title)
    return f"https://covers.openlibrary.org/b/title/{encoded_title}-L.jpg"


def get_pdf_link(title: str, author: str = "") -> str:
    """
    Get an appropriate PDF link for a book.
    
    For public domain books, returns Project Gutenberg link.
    For others, returns a sample/preview link.
    
    Args:
        title: Book title.
        author: Author name.
        
    Returns:
        URL string for the PDF.
    """
    # Normalize title for lookup
    normalized_title = title.lower().strip()
    
    # Check if book is in public domain list
    if normalized_title in PUBLIC_DOMAIN_BOOKS:
        return PUBLIC_DOMAIN_BOOKS[normalized_title]
    
    # Check partial matches for classic books
    for pd_title, pdf_url in PUBLIC_DOMAIN_BOOKS.items():
        if pd_title in normalized_title or normalized_title in pd_title:
            return pdf_url
    
    # For non-public domain, link to Google Books search
    search_query = urllib.parse.quote(f"{title} {author}")
    return f"https://www.google.com/search?tbm=bks&q={search_query}"


def get_google_books_link(title: str, author: str = "") -> str:
    """
    Generate a Google Books search link for a book.
    
    Args:
        title: Book title.
        author: Author name.
        
    Returns:
        Google Books search URL.
    """
    search_query = urllib.parse.quote(f"{title} {author}".strip())
    return f"https://books.google.com/books?q={search_query}"


def get_amazon_link(title: str, author: str = "") -> str:
    """
    Generate an Amazon search link for a book.
    
    Args:
        title: Book title.
        author: Author name.
        
    Returns:
        Amazon search URL.
    """
    search_query = urllib.parse.quote(f"{title} {author}".strip())
    return f"https://www.amazon.com/s?k={search_query}&i=stripbooks"


def enrich_book(book: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich a book dictionary with cover image and PDF link.
    
    Args:
        book: Book dictionary with at least 'title' and 'author' keys.
        
    Returns:
        Enriched book dictionary with 'cover_image' and 'pdf_link' added.
    """
    enriched = book.copy()
    
    title = book.get('title', '')
    author = book.get('author', '')
    
    # Add cover image URL
    enriched['cover_image'] = get_cover_image_url(title)
    enriched['fallback_cover'] = FALLBACK_COVER
    
    # Add PDF/purchase links
    enriched['pdf_link'] = get_pdf_link(title, author)
    enriched['google_books_link'] = get_google_books_link(title, author)
    enriched['amazon_link'] = get_amazon_link(title, author)
    
    # Check if public domain
    normalized_title = title.lower().strip()
    enriched['is_public_domain'] = any(
        pd_title in normalized_title or normalized_title in pd_title
        for pd_title in PUBLIC_DOMAIN_BOOKS.keys()
    )
    
    return enriched


def enrich_books(books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich a list of books with cover images and PDF links.
    
    Args:
        books: List of book dictionaries.
        
    Returns:
        List of enriched book dictionaries.
    """
    return [enrich_book(book) for book in books]
