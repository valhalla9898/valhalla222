# Advanced Q&A System Documentation
# 

## Overview

The Agentic-IAM project now includes an enterprise-grade Q&A system with:
- **3000+ Egyptian Arabic questions** with multiple categories
- **Advanced Security** with rate limiting, sessions, and blacklisting
- **Comprehensive Analytics** tracking user progress and performance
- **Intelligent Recommendations** using spaced repetition algorithm
- **Interactive Dashboard** with Streamlit for real-time engagement

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Main App │
│ (/api/v1/qa routes included) │
└────────────────┬────────────────────────────────────────────┘
 │
 ┌────────────┼────────────┬─────────────┬──────────────┐
 │ │ │ │ │
 ▼ ▼ ▼ ▼ ▼
┌─────────┐ ┌────────┐ ┌──────────┐ ┌───────┐ ┌─────────────┐
│Database │ │Security│ │Analytics │ │Recomm.│ │ Streamlit │
│(3000 Q) │ │Manager │ │Engine │ │Engine │ │ Dashboard │
└─────────┘ └────────┘ └──────────┘ └───────┘ └─────────────┘
```

## Quick Start

### 1. Basic Usage

```python
# Get a random question
curl -X GET "http://localhost:8000/api/v1/qa/random" \
 -H "X-User-ID: user123"

# Submit an answer
curl -X POST "http://localhost:8000/api/v1/qa/answer" \
 -H "X-User-ID: user123" \
 -H "Content-Type: application/json" \
 -d '{
 "user_id": "user123",
 "question_id": 1,
 "user_answer": "",
 "time_taken": 45
 }'

# Get personalized recommendations
curl -X GET "http://localhost:8000/api/v1/qa/recommendations/user123" \
 -H "X-User-ID: user123"
```

### 2. Streamlit Dashboard

```bash
streamlit run qa_dashboard.py
```

Access at: `http://localhost:8501`

## API Endpoints

### Core Endpoints

#### `/api/v1/qa/health` - System Health
```
GET /api/v1/qa/health
Response: {
 "status": "healthy",
 "total_questions": 3000,
 "categories": 6
}
```

#### `/api/v1/qa/categories` - Get Categories
```
GET /api/v1/qa/categories
Response: [
 {
 "category": "",
 "arabic_name": " ",
 "count": 500
 },
 ...
]
```

#### `/api/v1/qa/random` - Get Random Question
```
GET /api/v1/qa/random?category=
Response: {
 "id": 1,
 "question": " RSA",
 "category": "",
 "difficulty": 3
}
```

#### `/api/v1/qa/answer` - Submit Answer
```
POST /api/v1/qa/answer
{
 "user_id": "user123",
 "question_id": 1,
 "user_answer": " ",
 "time_taken": 45
}
Response: {
 "correct": true,
 "actual_answer": "...",
 "points_earned": 10,
 "message": " ! 🎉"
}
```

### Advanced Endpoints

#### `/api/v1/qa/recommendations/{user_id}` - Get Recommendations
```
GET /api/v1/qa/recommendations/user123?limit=10
Response: [
 {
 "question_id": 42,
 "question_text": "",
 "category": "",
 "difficulty_level": "",
 "reason": "Helps strengthen weak area",
 "confidence_score": 85
 },
 ...
]
```

#### `/api/v1/qa/reviews/{user_id}` - Spaced Repetition
```
GET /api/v1/qa/reviews/user123
Response: {
 "user_id": "user123",
 "due_for_review": 5,
 "questions": [...]
}
```

#### `/api/v1/qa/analytics/{user_id}` - User Analytics
```
GET /api/v1/qa/analytics/user123
Response: {
 "statistics": {
 "total_questions_attempted": 150,
 "total_correct_answers": 120,
 "overall_accuracy_percentage": 80.0,
 "quiz_sessions_count": 15,
 ...
 },
 "performance_insights": {...},
 "category_breakdown": {...}
}
```

#### `/api/v1/qa/analytics/system/health` - System Health
```
GET /api/v1/qa/analytics/system/health
Response: {
 "health_metrics": {
 "total_registered_users": 250,
 "total_quiz_sessions": 1500,
 "average_system_score": 72.5,
 ...
 },
 "trending_questions": [...]
}
```

#### `/api/v1/qa/quiz/start` - Start Adaptive Quiz
```
POST /api/v1/qa/quiz/start?category=&size=10
Response: {
 "session_id": "uuid-string",
 "questions_count": 10,
 "questions": [...]
}
```

#### `/api/v1/qa/session/create` - Create Session
```
POST /api/v1/qa/session/create
Response: {
 "session_token": "token-string",
 "expires_in_seconds": 86400
}
```

### Security Endpoints

#### `/api/v1/qa/security/{user_id}` - Security Report
```
GET /api/v1/qa/security/user123
Response: {
 "security_report": {
 "suspicious_activities": 0,
 "active_sessions": 2,
 "is_blacklisted": false
 }
}
```

## Database Schema

### qa_database.db (3000+ Questions)
```sql
-- Questions table with encryption
CREATE TABLE questions (
 id INTEGER PRIMARY KEY,
 question TEXT,
 answer TEXT (encrypted),
 category TEXT,
 difficulty INTEGER,
 tags TEXT,
 created_at TIMESTAMP
);
```

### qa_security.db
```sql
-- Rate limiting
CREATE TABLE rate_limit (
 user_id TEXT,
 endpoint TEXT,
 request_count INTEGER,
 reset_time TIMESTAMP
);

-- Session management
CREATE TABLE user_sessions (
 user_id TEXT,
 session_token TEXT UNIQUE,
 ip_address TEXT,
 expires_at TIMESTAMP,
 is_active BOOLEAN
);

-- Blacklist
CREATE TABLE blacklist (
 user_id TEXT,
 reason TEXT,
 expires_at TIMESTAMP
);

-- Activity log
CREATE TABLE suspicious_activity (
 user_id TEXT,
 activity_type TEXT,
 description TEXT,
 ip_address TEXT,
 severity INTEGER
);
```

### qa_analytics.db
```sql
-- User progress
CREATE TABLE user_progress (
 user_id TEXT,
 question_id INTEGER,
 is_correct BOOLEAN,
 time_spent INTEGER,
 attempts INTEGER,
 last_attempt TIMESTAMP,
 UNIQUE(user_id, question_id)
);

-- Quiz sessions
CREATE TABLE quiz_sessions (
 user_id TEXT,
 session_id TEXT UNIQUE,
 category TEXT,
 difficulty_level TEXT,
 questions_count INTEGER,
 correct_answers INTEGER,
 score_percentage REAL,
 time_spent INTEGER,
 completed_at TIMESTAMP
);

-- Learning paths
CREATE TABLE learning_paths (
 user_id TEXT,
 category TEXT,
 current_level TEXT,
 total_questions_seen INTEGER,
 total_correct INTEGER,
 UNIQUE(user_id, category)
);
```

### qa_recommendations.db
```sql
-- User profiles
CREATE TABLE user_profiles (
 user_id TEXT PRIMARY KEY,
 preferred_category TEXT,
 preferred_difficulty TEXT,
 learning_speed TEXT
);

-- Spaced repetition
CREATE TABLE spaced_repetition (
 user_id TEXT,
 question_id INTEGER,
 interval INTEGER,
 ease_factor REAL,
 next_review TIMESTAMP,
 review_count INTEGER,
 PRIMARY KEY(user_id, question_id)
);
```

## Security Features

### Rate Limiting
```python
# Automatic rate limiting
# Default: 100 requests/minute per endpoint per user
# Configurable per endpoint
```

### Session Management
```python
# Secure session tokens (32 bytes, URL-safe)
# 24-hour expiration by default
# IP and User-Agent tracking
# Validation on every request
```

### User Blacklisting
```python
# Permanent or temporary blacklist
# Reasons tracking
# Expiration support
# Checked automatically on /answer and /quiz endpoints
```

### Activity Logging
```python
# All suspicious activities logged
# IP address tracking
# Severity levels (1-10)
# Time-based filtering
```

## Analytics Features

### User Statistics
- Total questions attempted
- Correct answers count
- Overall accuracy percentage
- Average time per question
- Quiz session history
- Category-wise breakdown

### Performance Insights
- Weak areas identification
- Strong areas recognition
- Difficulty progression analysis
- Learning speed calculation
- Time to mastery estimation

### System Metrics
- Total registered users
- Active users (24h/7d/30d)
- Average system score
- Most popular categories
- Trending questions
- System health status

## Recommendation Engine

### Features
1. **Personalized Recommendations**
 - Based on user accuracy
 - Category preference learning
 - Difficulty-based selection
 - Weak area focus

2. **Spaced Repetition (SM-2)**
 - Optimal review intervals
 - Ease factor adjustment
 - Performance-based scheduling
 - Mastery tracking

3. **Adaptive Difficulty**
 - Auto-adjust based on accuracy
 - Progressive challenge increase
 - Optimal learning zone
 - Performance optimization

## Gamification

### Experience Points System
```python
Base points: 10
Difficulty multiplier: 1 + (difficulty - 1) * 0.5
Time bonus: 5 (< 30s), 3 (< 60s), 1 (< 120s)
Streak multiplier: 1 + (streak - 1) * 0.1
```

### Performance Levels
- (Excellent) - 90%+
- (Excellent) - 80%+
- (Very Good) - 70%+
- (Good) - 60%+
- (Fair) - 50%+
- (Poor) - 30%+
- (Very Poor) - <30%

## Configuration

### Environment Variables
```bash
# Database locations
QA_DB_PATH=qa_database.db
QA_SECURITY_DB=qa_security.db
QA_ANALYTICS_DB=qa_analytics.db
QA_RECOMMENDATIONS_DB=qa_recommendations.db

# Rate limiting
QA_RATE_LIMIT=100 # requests per minute
QA_TIME_WINDOW=3600 # seconds

# Session
QA_SESSION_EXPIRY=86400 # 24 hours
```

## Performance Tuning

### Database Optimization
```python
# Indexing on frequently queried columns
CREATE INDEX idx_user_questions ON user_progress(user_id);
CREATE INDEX idx_category_difficulty ON questions(category, difficulty);
CREATE INDEX idx_session_user ON quiz_sessions(user_id);
```

### Caching Strategy
- Cache category list (5 min TTL)
- Cache user stats (2 min TTL)
- Cache recommendations (1 hour TTL)
- Cache leaderboard (10 min TTL)

### Query Optimization
- Use prepared statements
- Batch inserts for analytics
- Indexed lookups
- Connection pooling

## Monitoring & Logging

### Key Metrics to Monitor
- Request rate per user
- Average response time
- Database query times
- Error rates
- Active sessions count
- Blacklist events

### Log Locations
```
logs/qa_system.log - General system logs
logs/qa_security.log - Security events
logs/qa_analytics.log - Analytics events
logs/qa_errors.log - Error logs
```

## Troubleshooting

### Common Issues

**Rate limit exceeded**
```
Error: "Rate limit exceeded. Retry after X seconds"
Solution: Implement exponential backoff in client
```

**Session invalid**
```
Error: "Invalid or expired session"
Solution: Create new session with /api/v1/qa/session/create
```

**User blacklisted**
```
Error: "User is blacklisted"
Solution: Contact administrator for whitelist
```

## Future Enhancements

- [ ] Advanced NLP for answer matching
- [ ] Machine learning for difficulty prediction
- [ ] Real-time collaboration features
- [ ] Mobile app integration
- [ ] Advanced reporting & export
- [ ] Multi-language support
- [ ] Video explanations for answers
- [ ] Live tutoring integration

## Support & Contact

For issues, questions, or feature requests:
- Create an issue in the repository
- Contact: agentic-iam@example.com

---

**Last Updated**: 2024
**Version**: 1.0.0 - Production Ready
**Status**: ✅ Enterprise Grade
