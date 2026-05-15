"""
Streamlit Dashboard للـ Q&A System
واجهة أمامية رائعة بـ 3000+ سؤال بالعربية المصرية
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import random
from qa_database import QADatabase, CATEGORIES

# Page configuration
st.set_page_config(
    page_title="نظام الأسئلة والأجوبة 🎓",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'qa_db' not in st.session_state:
    st.session_state.qa_db = QADatabase()

if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{random.randint(1000, 9999)}"

if 'current_question' not in st.session_state:
    st.session_state.current_question = None

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 3em;
        margin-bottom: 20px;
        font-weight: bold;
    }
    
    .question-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
    }
    
    .answer-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .success-message {
        background-color: #4caf50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .error-message {
        background-color: #f44336;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<h1 class='main-title'>🎓 نظام الأسئلة والأجوبة 🎓</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.title("القائمة الرئيسية")
    page = st.radio(
        "اختار الصفحة:",
        ["🏠 الرئيسية", "❓ الأسئلة", "📊 الإحصائيات", "🏆 اللاعبين", "🔍 البحث"]
    )
    
    st.markdown("---")
    st.info(f"🆔 معرف المستخدم: {st.session_state.user_id}")
    
    # System info
    total_q = st.session_state.qa_db.get_total_questions()
    st.success(f"📚 عدد الأسئلة: {total_q}")


# ============= HOME PAGE =============
if page == "🏠 الرئيسية":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stats-card"><h3>عدد الأسئلة</h3><h1>3000+</h1></div>', unsafe_allow_html=True)
    
    with col2:
        stats = st.session_state.qa_db.get_user_stats(st.session_state.user_id)
        if stats:
            st.markdown(f'<div class="stats-card"><h3>نقاطك</h3><h1>{stats["points"]}</h1></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stats-card"><h3>نقاطك</h3><h1>0</h1></div>', unsafe_allow_html=True)
    
    with col3:
        categories = st.session_state.qa_db.get_categories()
        st.markdown(f'<div class="stats-card"><h3>الفئات</h3><h1>{len(categories)}</h1></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Categories overview
    st.subheader("📂 فئات الأسئلة")
    
    categories = st.session_state.qa_db.get_categories()
    
    if categories:
        cols = st.columns(len(categories))
        
        for idx, (col, cat) in enumerate(zip(cols, categories)):
            with col:
                st.metric(
                    label=cat['arabic_name'],
                    value=cat['count'],
                    delta="أسئلة"
                )
    
    st.markdown("---")
    
    # Features
    st.subheader("✨ المميزات")
    
    features = [
        "✅ 3000+ سؤال بالعربية المصرية",
        "✅ تصنيفات متعددة (أمان، AI، تكنولوجيا، إدارة، عام)",
        "✅ نظام تقييم وتصنيف الاعبين",
        "✅ إحصائيات وتقارير شاملة",
        "✅ بحث سريع وفعال",
        "✅ واجهة سهلة وجميلة",
        "✅ نظام مستويات وإنجازات",
        "✅ حماية وأمان عالي"
    ]
    
    for feature in features:
        st.write(feature)


# ============= QUESTIONS PAGE =============
elif page == "❓ الأسئلة":
    st.subheader("حل الأسئلة")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        selected_category = st.selectbox(
            "اختار الفئة:",
            ["عشوائي"] + list(CATEGORIES.keys()),
            format_func=lambda x: "عشوائي" if x == "عشوائي" else CATEGORIES[x]
        )
    
    with col1:
        if st.button("📝 سؤال جديد", use_container_width=True):
            category = None if selected_category == "عشوائي" else selected_category
            st.session_state.current_question = st.session_state.qa_db.get_random_question(category=category)
            st.session_state.start_time = time.time()
    
    st.markdown("---")
    
    if st.session_state.current_question:
        q = st.session_state.current_question
        
        # Display question
        st.markdown(f'<div class="question-box"><h2>❓ السؤال:</h2><h3>{q["question"]}</h3></div>', unsafe_allow_html=True)
        
        # Display category and difficulty
        col1, col2 = st.columns(2)
        with col1:
            st.badge(f"الفئة: {CATEGORIES.get(q['category'], q['category'])}")
        with col2:
            difficulty_text = "سهل 🟢" if q['difficulty'] == 1 else "متوسط 🟡" if q['difficulty'] == 2 else "صعب 🔴"
            st.badge(f"المستوى: {difficulty_text}")
        
        st.markdown("---")
        
        # Answer input
        st.subheader("إجابتك:")
        user_answer = st.text_area("اكتب إجابتك هنا:", height=100, placeholder="اكتب إجابتك بشكل واضح...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ تحقق من الإجابة", use_container_width=True):
                if not user_answer.strip():
                    st.error("الرجاء إدخال إجابة!")
                else:
                    time_taken = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
                    
                    # Check answer
                    from difflib import SequenceMatcher
                    correct_answer = q['answer'].lower().strip()
                    user_ans_normalized = user_answer.lower().strip()
                    
                    is_correct = (
                        user_ans_normalized == correct_answer or
                        SequenceMatcher(None, user_ans_normalized, correct_answer).ratio() >= 0.7
                    )
                    
                    points = 10 if is_correct else 2
                    
                    # Record answer
                    st.session_state.qa_db.record_answer(
                        user_id=st.session_state.user_id,
                        question_id=q['id'],
                        user_answer=user_answer,
                        is_correct=is_correct,
                        time_taken=time_taken
                    )
                    
                    # Display result
                    if is_correct:
                        st.success(f"✅ صحيح! كسبت {points} نقاط")
                    else:
                        st.error(f"❌ خاطئ. النقاط: {points}")
                    
                    st.markdown(f'<div class="answer-box"><h4>✓ الإجابة الصحيحة:</h4><p>{q["answer"]}</p></div>', unsafe_allow_html=True)
                    
                    if time_taken > 0:
                        st.info(f"⏱️ الوقت المستغرق: {time_taken} ثانية")
        
        with col2:
            if st.button("⏭️ السؤال التالي", use_container_width=True):
                category = None if selected_category == "عشوائي" else selected_category
                st.session_state.current_question = st.session_state.qa_db.get_random_question(category=category)
                st.session_state.start_time = time.time()
                st.rerun()
    
    else:
        st.info("اضغط على زر 'سؤال جديد' عشان تبدأ!")


# ============= STATISTICS PAGE =============
elif page == "📊 الإحصائيات":
    st.subheader("إحصائياتك الشخصية")
    
    stats = st.session_state.qa_db.get_user_stats(st.session_state.user_id)
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("المستوى", f"Level {stats['level']}", "🎯")
        
        with col2:
            st.metric("النقاط", stats['points'], "⭐")
        
        with col3:
            st.metric("عدد الأسئلة", stats['total_questions'], "❓")
        
        with col4:
            st.metric("الدقة", f"{stats['accuracy']:.1f}%", "🎯")
        
        st.markdown("---")
        
        # Progress chart
        st.subheader("📈 تقدمك")
        
        if stats['total_questions'] > 0:
            progress_data = {
                "الحالة": ["صحيح", "خاطئ"],
                "العدد": [stats['correct_answers'], stats['total_questions'] - stats['correct_answers']]
            }
            
            df = pd.DataFrame(progress_data)
            st.bar_chart(df.set_index('الحالة'))
        
        st.markdown("---")
        
        # Category performance
        st.subheader("📊 أداؤك في كل فئة")
        
        categories = st.session_state.qa_db.get_categories()
        
        for cat in categories:
            with st.expander(f"📌 {cat['arabic_name']} ({cat['count']} أسئلة)"):
                st.write(f"عدد الأسئلة: {cat['count']}")
    
    else:
        st.info("لم تحل أي أسئلة بعد! ابدأ الآن من صفحة الأسئلة 🚀")


# ============= LEADERBOARD PAGE =============
elif page == "🏆 اللاعبين":
    st.subheader("🏆 أفضل اللاعبين")
    
    leaderboard = st.session_state.qa_db.get_leaderboard(limit=50)
    
    if leaderboard:
        # Create DataFrame
        df = pd.DataFrame([
            {
                "الترتيب": entry['rank'],
                "المستخدم": entry['user_id'],
                "النقاط": entry['points'],
                "الدقة": f"{entry['accuracy']:.1f}%"
            }
            for entry in leaderboard
        ])
        
        st.dataframe(df, use_container_width=True)
        
        # Check user's position
        st.markdown("---")
        st.subheader("📍 موضعك في الترتيب")
        
        user_position = next(
            (idx + 1 for idx, entry in enumerate(leaderboard) if entry['user_id'] == st.session_state.user_id),
            None
        )
        
        if user_position:
            st.success(f"أنت في المركز #{user_position} 🎉")
        else:
            st.info("انضم إلى لعبة الأسئلة لتظهر في الترتيب!")
    
    else:
        st.info("لا يوجد بيانات للاعبين حتى الآن!")


# ============= SEARCH PAGE =============
elif page == "🔍 البحث":
    st.subheader("🔍 ابحث عن الأسئلة")
    
    search_keyword = st.text_input("اكتب كلمة للبحث:")
    
    search_category = st.selectbox(
        "اختار الفئة (اختياري):",
        ["الكل"] + list(CATEGORIES.keys()),
        format_func=lambda x: "الكل" if x == "الكل" else CATEGORIES[x]
    )
    
    if st.button("🔎 بحث", use_container_width=True):
        if search_keyword:
            category = None if search_category == "الكل" else search_category
            results = st.session_state.qa_db.search_questions(search_keyword, category=category)
            
            st.markdown(f"### النتائج: {len(results)} سؤال")
            st.markdown("---")
            
            if results:
                for idx, result in enumerate(results, 1):
                    with st.expander(f"❓ السؤال {idx}: {result['question'][:50]}..."):
                        st.write(f"**السؤال:** {result['question']}")
                        st.write(f"**الفئة:** {CATEGORIES.get(result['category'], result['category'])}")
                        st.write(f"**الإجابة:** {result['answer']}")
                        difficulty_text = "سهل 🟢" if result['difficulty'] == 1 else "متوسط 🟡" if result['difficulty'] == 2 else "صعب 🔴"
                        st.write(f"**المستوى:** {difficulty_text}")
            else:
                st.warning("لم نجد أسئلة مطابقة!")
        else:
            st.warning("الرجاء إدخال كلمة للبحث عنها!")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🧠 نظام الأسئلة والأجوبة v1.0 | 3000+ سؤال بالعربية المصرية</p>
    <p>👨‍💻 Made with ❤️ for Learning</p>
</div>
""", unsafe_allow_html=True)
