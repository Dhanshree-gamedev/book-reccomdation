"""
Book Recommendation Platform - Main Application

A production-ready book recommendation system built with Streamlit.
Features secure authentication, content-based and collaborative
filtering recommendations, and a modern card-based user interface.

Run with: streamlit run app.py
"""

import streamlit as st
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from services.user_service import UserService
from services.book_service import BookService
from services.recommendation_service import RecommendationService
from utils.constants import GENRES, APP_NAME, APP_VERSION
from utils.book_enrichment import enrich_book, enrich_books

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database on startup
db.init_database()


# ============================================================================
# Page Configuration & Styling
# ============================================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS with soft green theme and card-based UI
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 50%, #81c784 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2e7d32;
        margin: 1.25rem 0 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-top: 0.5rem;
    }
    
    /* Book Card Grid - Responsive */
    .book-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 1.25rem;
        padding: 0.75rem 0 1rem 0;
        width: 100%;
        margin-bottom: 0;
    }
    
    /* Responsive breakpoints */
    @media (min-width: 768px) {
        .book-grid {
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2rem;
        }
    }
    
    @media (min-width: 1200px) {
        .book-grid {
            grid-template-columns: repeat(5, 1fr);
            gap: 1.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .book-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
    }
    
    /* Book Card */
    .book-card {
        background: #ffffff;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 4px 16px rgba(0, 0, 0, 0.04);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        text-decoration: none;
        display: block;
        border: 1px solid rgba(76, 175, 80, 0.1);
        position: relative;
    }
    
    .book-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.05) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.35s ease;
        pointer-events: none;
    }
    
    .book-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 16px 48px rgba(46, 125, 50, 0.18), 0 8px 24px rgba(0, 0, 0, 0.08);
        border-color: #81c784;
    }
    
    .book-card:hover::before {
        opacity: 1;
    }
    
    .book-card:active {
        transform: translateY(-4px) scale(1.01);
    }
    
    .book-card-link {
        text-decoration: none;
        color: inherit;
        display: block;
        height: 100%;
        width: 100%;
        cursor: pointer;
    }
    
    .book-card-link:hover {
        text-decoration: none;
    }
    
    .book-card-link:focus {
        outline: 2px solid #4caf50;
        outline-offset: 2px;
        border-radius: 16px;
    }
    
    /* Book Cover Image */
    .book-cover-container {
        width: 100%;
        height: 220px;
        overflow: hidden;
        background: linear-gradient(145deg, #f1f8e9 0%, #e8f5e9 50%, #c8e6c9 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .book-cover-container::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 40px;
        background: linear-gradient(to top, rgba(255,255,255,0.8), transparent);
        pointer-events: none;
    }
    
    .book-cover {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    
    .book-card:hover .book-cover {
        transform: scale(1.05);
    }
    
    .book-cover-placeholder {
        font-size: 4rem;
        color: #81c784;
    }
    
    /* Book Info */
    .book-info {
        padding: 0.9rem 0.85rem;
        background: #ffffff;
        position: relative;
        z-index: 1;
    }
    
    .book-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1b5e20;
        margin: 0 0 0.4rem 0;
        line-height: 1.35;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        transition: color 0.2s ease;
    }
    
    .book-card:hover .book-title {
        color: #2e7d32;
    }
    
    .book-author {
        font-size: 0.8rem;
        color: #757575;
        margin: 0 0 0.6rem 0;
        font-weight: 400;
    }
    
    .book-rating {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.8rem;
        color: #ffa000;
        font-weight: 500;
    }
    
    /* Genre Tags */
    .genre-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin-top: 0.6rem;
    }
    
    .genre-tag {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        color: #2e7d32;
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        border: 1px solid rgba(46, 125, 50, 0.15);
        transition: all 0.2s ease;
    }
    
    .book-card:hover .genre-tag {
        background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
        border-color: rgba(46, 125, 50, 0.25);
    }
    
    /* View PDF Badge */
    .pdf-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        opacity: 0;
        transform: translateY(-5px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4);
        z-index: 10;
    }
    
    .book-card:hover .pdf-badge {
        opacity: 1;
        transform: translateY(0);
    }
    
    /* Recommendation Card */
    .rec-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4caf50;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    }
    
    .rec-reason {
        background: #f1f8e9;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #33691e;
        margin-top: 0.5rem;
        display: inline-block;
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(46, 125, 50, 0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Interest Tags */
    .interest-tag {
        display: inline-block;
        background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: #f8fdf8;
    }
    
    /* Button Overrides */
    .stButton > button {
        background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
    }
    
    /* Form Styling */
    .stForm {
        background: #f8fdf8;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e8f5e9;
    }
    
    /* Search Box */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e8f5e9;
        padding: 0.8rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }
    
    /* Multiselect */
    .stMultiSelect > div {
        border-radius: 12px;
    }
    
    /* Welcome Card */
    .welcome-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(46, 125, 50, 0.15);
    }
    
    .welcome-text {
        font-size: 1.3rem;
        color: #1b5e20;
        margin: 0;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'


def get_current_user():
    """Get current authenticated user with session validation."""
    if st.session_state.session_token:
        user = UserService.get_current_user(st.session_state.session_token)
        if user:
            st.session_state.current_user = user
            return user
        else:
            st.session_state.session_token = None
            st.session_state.current_user = None
    return None


def is_authenticated():
    """Check if user is authenticated."""
    return get_current_user() is not None


# ============================================================================
# UI Components - Book Cards
# ============================================================================

def render_book_card_html(book: dict) -> str:
    """Generate HTML for a single book card."""
    # Enrich book with cover and links
    enriched = enrich_book(book)
    
    title = enriched.get('title', 'Unknown Title')
    author = enriched.get('author', 'Unknown Author')
    cover_url = enriched.get('cover_image', '')
    fallback_cover = enriched.get('fallback_cover', '')
    pdf_link = enriched.get('pdf_link', '#')
    genres = enriched.get('genres', [])[:2]
    avg_rating = enriched.get('avg_rating')
    
    # Rating stars
    rating_html = ""
    if avg_rating:
        stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))
        rating_html = f'<div class="book-rating">{stars} {avg_rating:.1f}</div>'
    
    # Genre tags
    genres_html = "".join([f'<span class="genre-tag">{g}</span>' for g in genres])
    
    return f'''
    <a href="{pdf_link}" target="_blank" class="book-card-link" rel="noopener noreferrer">
        <div class="book-card">
            <div class="book-cover-container">
                <img 
                    class="book-cover" 
                    src="{cover_url}" 
                    alt="Cover of {title}"
                    onerror="this.onerror=null; this.src='{fallback_cover}';"
                    loading="lazy"
                />
                <span class="pdf-badge">📖 Read</span>
            </div>
            <div class="book-info">
                <h3 class="book-title">{title}</h3>
                <p class="book-author">by {author}</p>
                {rating_html}
                <div class="genre-tags">{genres_html}</div>
            </div>
        </div>
    </a>
    '''


def render_book_grid(books: list, columns: int = 5):
    """Render a grid of book cards using native Streamlit columns."""
    if not books:
        st.info("📚 No books found. Try a different search or add some books!")
        return
    
    # Process books in rows
    num_books = len(books)
    
    for row_start in range(0, num_books, columns):
        row_books = books[row_start:row_start + columns]
        cols = st.columns(columns, gap="small")
        
        for idx, book in enumerate(row_books):
            with cols[idx]:
                # Enrich book data
                enriched = enrich_book(book)
                title = enriched.get('title', 'Unknown')
                author = enriched.get('author', 'Unknown')
                cover_url = enriched.get('cover_image', '')
                pdf_link = enriched.get('pdf_link', '#')
                genres = enriched.get('genres', [])[:2]
                avg_rating = enriched.get('avg_rating')
                
                # Render clickable card as HTML
                rating_stars = ""
                if avg_rating:
                    rating_stars = f"⭐ {avg_rating:.1f}"
                
                genre_text = " · ".join(genres) if genres else ""
                
                st.markdown(f'''
                <a href="{pdf_link}" target="_blank" style="text-decoration:none;color:inherit;">
                    <div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);border:1px solid #e8f5e9;margin-bottom:0.5rem;transition:transform 0.2s,box-shadow 0.2s;">
                        <div style="height:180px;overflow:hidden;background:linear-gradient(145deg,#f1f8e9,#c8e6c9);display:flex;align-items:center;justify-content:center;">
                            <img src="{cover_url}" alt="{title}" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';" />
                            <div style="display:none;align-items:center;justify-content:center;width:100%;height:100%;color:#81c784;font-size:3rem;">📖</div>
                        </div>
                        <div style="padding:0.75rem;">
                            <div style="font-size:0.85rem;font-weight:600;color:#1b5e20;line-height:1.3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{title}</div>
                            <div style="font-size:0.75rem;color:#757575;margin-top:0.2rem;">{author}</div>
                            <div style="font-size:0.7rem;color:#ffa000;margin-top:0.3rem;">{rating_stars}</div>
                            <div style="font-size:0.65rem;color:#2e7d32;margin-top:0.2rem;">{genre_text}</div>
                        </div>
                    </div>
                </a>
                ''', unsafe_allow_html=True)


def render_recommendation_card(rec: dict):
    """Render a recommendation with reason."""
    book = rec['book']
    enriched = enrich_book(book)
    
    title = enriched.get('title', '')
    author = enriched.get('author', '')
    cover_url = enriched.get('cover_image', '')
    fallback_cover = enriched.get('fallback_cover', '')
    pdf_link = enriched.get('pdf_link', '#')
    reason = rec.get('reason', 'Recommended for you')
    score = int(rec.get('score', 0) * 100)
    genres = enriched.get('genres', [])[:3]
    
    genres_html = "".join([f'<span class="genre-tag">{g}</span>' for g in genres])
    
    st.markdown(f'''
    <a href="{pdf_link}" target="_blank" class="book-card-link" rel="noopener noreferrer">
        <div class="rec-card" style="display: flex; gap: 1rem; align-items: center;">
            <img 
                src="{cover_url}" 
                alt="{title}"
                onerror="this.onerror=null; this.src='{fallback_cover}';"
                style="width: 80px; height: 120px; object-fit: cover; border-radius: 8px;"
            />
            <div style="flex: 1;">
                <h4 style="margin: 0 0 0.3rem 0; color: #1a1a1a;">{title}</h4>
                <p style="margin: 0 0 0.5rem 0; color: #666; font-size: 0.9rem;">by {author}</p>
                <div class="genre-tags">{genres_html}</div>
                <div class="rec-reason">💡 {reason} • {score}% match</div>
            </div>
        </div>
    </a>
    ''', unsafe_allow_html=True)


def render_stat_card(number, label, col):
    """Render a statistics card."""
    with col:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================================================
# Page: Home
# ============================================================================

def page_home():
    """Render home page."""
    st.markdown('<h1 class="main-header">📚 Book Recommendation Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover your next favorite book with personalized recommendations</p>', unsafe_allow_html=True)
    
    user = get_current_user()
    
    if user:
        st.markdown(f'''
        <div class="welcome-card">
            <p class="welcome-text">👋 Welcome back, <strong>{user['username']}</strong>! Ready to find your next great read?</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Get personalized recommendations
        feed = RecommendationService.get_personalized_home_feed(user['id'], 5)
        
        if feed:
            st.markdown('<div class="section-header">🎯 Recommended for You</div>', unsafe_allow_html=True)
            for rec in feed:
                render_recommendation_card(rec)
    
    # Recent Books Section
    st.markdown('<div class="section-header">📖 Recently Added Books</div>', unsafe_allow_html=True)
    recent_books = BookService.get_recent_books(10)
    for book in recent_books:
        book['avg_rating'] = db.get_average_book_rating(book['id'])
    render_book_grid(recent_books)
    
    # Popular Books Section
    st.markdown('<div class="section-header">🔥 Popular Books</div>', unsafe_allow_html=True)
    popular_books = BookService.get_popular_books(10)
    render_book_grid(popular_books)


# ============================================================================
# Page: Browse Books
# ============================================================================

def page_browse():
    """Render book browsing page."""
    st.markdown('<h1 class="main-header">📖 Browse Books</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore our collection and find your next read</p>', unsafe_allow_html=True)
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search books", placeholder="Search by title or author...")
    with col2:
        genre_filter = st.selectbox("Filter by genre", ["All Genres"] + GENRES)
    
    # Get books
    if search_query:
        books = BookService.search_books(search_query)
    else:
        books = BookService.get_all_books()
    
    # Apply genre filter
    if genre_filter != "All Genres":
        books = [b for b in books if genre_filter in b.get('genres', [])]
    
    # Add ratings
    for book in books:
        book['avg_rating'] = db.get_average_book_rating(book['id'])
    
    st.markdown(f'<p style="color: #666; margin: 1rem 0;">Showing {len(books)} books</p>', unsafe_allow_html=True)
    
    # Render book grid
    render_book_grid(books)
    
    # Rating section for authenticated users
    user = get_current_user()
    if user and books:
        st.markdown("---")
        st.markdown("### ⭐ Rate a Book")
        
        book_options = {f"{b['title']} by {b['author']}": b['id'] for b in books}
        selected_book = st.selectbox("Select a book to rate", list(book_options.keys()))
        
        if selected_book:
            book_id = book_options[selected_book]
            existing_rating = BookService.get_user_book_rating(user['id'], book_id)
            
            rating = st.slider(
                "Your rating",
                min_value=1,
                max_value=5,
                value=existing_rating or 3
            )
            
            if st.button("Submit Rating"):
                success, msg = BookService.rate_book(user['id'], book_id, rating)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ============================================================================
# Page: Add Book
# ============================================================================

def page_add_book():
    """Render add book page."""
    st.markdown('<h1 class="main-header">📝 Add a Book</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Contribute to our library by adding a new book</p>', unsafe_allow_html=True)
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to add books.")
        return
    
    with st.form("add_book_form", clear_on_submit=True):
        title = st.text_input("Book Title *", placeholder="Enter the book title")
        author = st.text_input("Author *", placeholder="Enter the author's name")
        selected_genres = st.multiselect("Genres *", GENRES, help="Select at least one genre")
        description = st.text_area("Description", placeholder="Optional: Add a brief description")
        
        submitted = st.form_submit_button("Add Book", use_container_width=True)
        
        if submitted:
            if not title or not author or not selected_genres:
                st.error("Please fill in all required fields.")
            else:
                success, msg, book_id = BookService.add_book(
                    title=title,
                    author=author,
                    genres=selected_genres,
                    description=description,
                    added_by=user['id']
                )
                
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)


# ============================================================================
# Page: Recommendations
# ============================================================================

def page_recommendations():
    """Render recommendations page."""
    st.markdown('<h1 class="main-header">🎯 Your Recommendations</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Personalized book suggestions just for you</p>', unsafe_allow_html=True)
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to see personalized recommendations.")
        return
    
    # Stats
    stats = RecommendationService.get_recommendation_stats(user['id'])
    
    col1, col2, col3 = st.columns(3)
    render_stat_card(stats.get('interests_count', 0), "Interests Set", col1)
    render_stat_card(stats.get('books_rated', 0), "Books Rated", col2)
    render_stat_card(stats.get('similar_users_count', 0), "Similar Readers", col3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not stats.get('has_interests'):
        st.info("🔔 Set your reading interests in your Profile to get better recommendations!")
    
    # Get recommendations
    recs = RecommendationService.get_recommendations(user['id'], 10)
    
    # Content-based
    if recs['content_based']:
        st.markdown('<div class="section-header">🎨 Based on Your Interests</div>', unsafe_allow_html=True)
        for rec in recs['content_based'][:6]:
            render_recommendation_card(rec)
    
    # Collaborative
    if recs['collaborative']:
        st.markdown('<div class="section-header">👥 Loved by Similar Readers</div>', unsafe_allow_html=True)
        for rec in recs['collaborative'][:6]:
            render_recommendation_card(rec)
    
    # Fallback
    if recs['fallback']:
        st.markdown('<div class="section-header">🌟 Popular Picks</div>', unsafe_allow_html=True)
        for rec in recs['fallback'][:6]:
            render_recommendation_card(rec)


# ============================================================================
# Page: Profile
# ============================================================================

def page_profile():
    """Render user profile page."""
    st.markdown('<h1 class="main-header">👤 Your Profile</h1>', unsafe_allow_html=True)
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to view your profile.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### {user['username']}")
        st.markdown(f"📧 {user['email']}")
        st.markdown(f"📅 Member since: {user['created_at'][:10] if user.get('created_at') else 'N/A'}")
        
        st.markdown("### 📚 Your Reading Interests")
        if user.get('interests'):
            interests_html = "".join([f'<span class="interest-tag">{i}</span>' for i in user['interests']])
            st.markdown(interests_html, unsafe_allow_html=True)
        else:
            st.info("No interests set yet. Add some below!")
    
    with col2:
        user_stats = UserService.get_user_stats(user['id'])
        st.markdown("### 📊 Stats")
        st.metric("Books Rated", user_stats.get('total_ratings', 0))
        if user_stats.get('average_rating'):
            st.metric("Avg Rating Given", f"{user_stats['average_rating']:.1f} ★")
    
    st.markdown("---")
    
    # Update interests
    st.markdown("### ✏️ Update Your Interests")
    
    with st.form("update_interests_form"):
        new_interests = st.multiselect(
            "Select your favorite genres",
            GENRES,
            default=user.get('interests', [])
        )
        
        if st.form_submit_button("Save Interests", use_container_width=True):
            success, msg = UserService.update_user_interests(user['id'], new_interests)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    st.markdown("---")
    
    # Rated books
    st.markdown("### ⭐ Your Rated Books")
    rated_books = BookService.get_user_rated_books(user['id'])
    
    if rated_books:
        for rating in rated_books:
            stars = "★" * rating['rating'] + "☆" * (5 - rating['rating'])
            st.markdown(f"**{rating['title']}** by {rating['author']} - {stars}")
    else:
        st.info("You haven't rated any books yet.")


# ============================================================================
# Page: Login
# ============================================================================

def page_login():
    """Render login page."""
    st.markdown('<h1 class="main-header">🔐 Login</h1>', unsafe_allow_html=True)
    
    if is_authenticated():
        st.success("You are already logged in!")
        return
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if username and password:
                    success, msg, token = UserService.login(username, password)
                    if success:
                        st.session_state.session_token = token
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Please enter username and password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            interests = st.multiselect("Select your interests (optional)", GENRES)
            
            st.markdown("""
            **Password requirements:**
            - At least 8 characters
            - One uppercase letter
            - One lowercase letter
            - One digit
            """)
            
            if st.form_submit_button("Create Account", use_container_width=True):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif new_username and email and new_password:
                    success, msg, user_id = UserService.register(
                        new_username, email, new_password, interests
                    )
                    if success:
                        st.success(msg + " You can now log in.")
                    else:
                        st.error(msg)
                else:
                    st.error("Please fill in all required fields")


# ============================================================================
# Sidebar Navigation
# ============================================================================

def render_sidebar():
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown("## 📚 Navigation")
        
        user = get_current_user()
        
        if user:
            st.markdown(f"👋 **{user['username']}**")
            st.markdown("---")
            
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_page = 'home'
                st.rerun()
            
            if st.button("📖 Browse Books", use_container_width=True):
                st.session_state.current_page = 'browse'
                st.rerun()
            
            if st.button("📝 Add Book", use_container_width=True):
                st.session_state.current_page = 'add_book'
                st.rerun()
            
            if st.button("🎯 Recommendations", use_container_width=True):
                st.session_state.current_page = 'recommendations'
                st.rerun()
            
            if st.button("👤 Profile", use_container_width=True):
                st.session_state.current_page = 'profile'
                st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                UserService.logout(st.session_state.session_token)
                st.session_state.session_token = None
                st.session_state.current_user = None
                st.session_state.current_page = 'home'
                st.rerun()
        else:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_page = 'home'
                st.rerun()
            
            if st.button("📖 Browse Books", use_container_width=True):
                st.session_state.current_page = 'browse'
                st.rerun()
            
            if st.button("🔐 Login / Register", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"*v{APP_VERSION}*")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    page = st.session_state.current_page
    
    if page == 'home':
        page_home()
    elif page == 'browse':
        page_browse()
    elif page == 'add_book':
        page_add_book()
    elif page == 'recommendations':
        page_recommendations()
    elif page == 'profile':
        page_profile()
    elif page == 'login':
        page_login()
    else:
        page_home()


if __name__ == "__main__":
    main()
