# 📚 Book Recommendation & Rating Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A modern, AI-powered book recommendation system with collaborative filtering, content-based recommendations, and an elegant user interface.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Tech Stack](#-tech-stack) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🎯 Smart Recommendations
- **Content-Based Filtering** — Recommends books based on genre preferences and reading history
- **Collaborative Filtering** — Finds similar users and suggests books they loved
- **Hybrid Approach** — Combines multiple algorithms for accurate recommendations

### 📖 Book Management
- **Dynamic Book Covers** — Auto-fetched from Open Library API
- **PDF Links** — Direct access to public domain books via Project Gutenberg
- **Genre Tagging** — Categorize and filter books by multiple genres
- **Rating System** — 5-star rating with aggregated scores

### 🎨 Modern UI/UX
- **Card-Based Layout** — Beautiful, responsive book grid
- **Click-to-Read** — Entire card links to book PDFs
- **Hover Effects** — Smooth animations and visual feedback
- **Mobile Responsive** — Works seamlessly on all devices

### 🔐 User Authentication
- **Secure Login/Register** — bcrypt password hashing
- **Session Management** — Persistent user sessions
- **User Profiles** — Track reading preferences and history

---

## 🚀 Demo

### Home Page with Book Grid
The platform displays books in an elegant card grid with cover images, ratings, and genre tags:

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│  📖 Book 1  │  📖 Book 2  │  📖 Book 3  │  📖 Book 4  │  📖 Book 5  │
│  ⭐⭐⭐⭐☆  │  ⭐⭐⭐⭐⭐  │  ⭐⭐⭐☆☆  │  ⭐⭐⭐⭐☆  │  ⭐⭐⭐⭐⭐  │
│  Fiction    │  Mystery    │  Sci-Fi     │  Romance    │  Thriller   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## 💻 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Dhanshree-gamedev/book-reccomdation.git
cd book-reccomdation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Access the App
Open your browser and navigate to: **http://localhost:8501**

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Frontend** | Streamlit, HTML5, CSS3 |
| **Backend** | Python 3.9+ |
| **Database** | SQLite with Foreign Keys |
| **Authentication** | bcrypt password hashing |
| **APIs** | Open Library Covers, Project Gutenberg |
| **ML/Algorithms** | Collaborative Filtering, Jaccard Similarity |

---

## 🏗 Architecture

```
book_recommender/
├── 📄 app.py                    # Main Streamlit application
├── 📄 database.py               # Database operations & SQLite
├── 📄 auth.py                   # Authentication & session management
├── 📄 models.py                 # Data models & constants
│
├── 📁 services/
│   ├── 📄 book_service.py       # Book CRUD operations
│   ├── 📄 user_service.py       # User management
│   └── 📄 recommendation_service.py  # Recommendation orchestration
│
├── 📁 recommender/
│   ├── 📄 content_based.py      # Content-based filtering
│   ├── 📄 collaborative.py      # Collaborative filtering
│   └── 📄 utils.py              # Recommendation utilities
│
├── 📁 utils/
│   ├── 📄 constants.py          # App constants & config
│   ├── 📄 validators.py         # Input validation
│   ├── 📄 hashing.py            # Password hashing
│   └── 📄 book_enrichment.py    # Cover & PDF link generation
│
└── 📄 requirements.txt          # Python dependencies
```

---

## 🧠 Recommendation Algorithms

### Content-Based Filtering
Uses **Jaccard Similarity** to match user interests with book genres:

```python
similarity = |user_interests ∩ book_genres| / |user_interests ∪ book_genres|
```

### Collaborative Filtering
Finds users with similar reading patterns and recommends their highly-rated books:

1. **Find Similar Users** — Based on genre overlap
2. **Get Their Top Ratings** — Books rated 4+ stars
3. **Filter Already Read** — Remove books user has rated
4. **Rank & Return** — Sort by score

---

## 📊 Database Schema

```sql
-- Users table with secure password storage
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    interests TEXT,  -- JSON array of genres
    created_at TIMESTAMP
);

-- Books with genre tagging
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genres TEXT,  -- JSON array
    description TEXT,
    added_by INTEGER REFERENCES users(id)
);

-- Rating system
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id),
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    UNIQUE(user_id, book_id)
);
```

---

## 🎨 UI Features

### Book Cards
- **Cover Images** — Auto-fetched from Open Library
- **Fallback Display** — Shows placeholder if image unavailable
- **Click-to-Read** — Links to PDF (Gutenberg or Google Books)
- **Hover Effects** — Smooth scale and shadow transitions

### Responsive Grid
- **Desktop** — 5 columns
- **Tablet** — 3-4 columns (auto-fill)
- **Mobile** — 2 columns

---

## 🔧 Key Skills Demonstrated

| Skill | Implementation |
|-------|----------------|
| **Full-Stack Python** | Streamlit frontend + Python backend |
| **Database Design** | Normalized SQLite schema with FKs |
| **Algorithm Development** | Custom recommendation algorithms |
| **API Integration** | Open Library, Project Gutenberg |
| **Security** | bcrypt hashing, session tokens |
| **Responsive Design** | CSS Grid, media queries |
| **Clean Architecture** | Service layer, separation of concerns |
| **Error Handling** | Graceful degradation, fallbacks |

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Dhanshree**  
🎮 Game Developer | 💻 Python Developer

[![GitHub](https://img.shields.io/badge/GitHub-Dhanshree--gamedev-181717?style=flat-square&logo=github)](https://github.com/Dhanshree-gamedev)

---

<div align="center">

### ⭐ If you found this project helpful, please give it a star!

Made with ❤️ and Python

</div>
