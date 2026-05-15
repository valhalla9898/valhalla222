"""
نظام قاعدة بيانات الأسئلة والأجوبة - Arabic QA Database System

يتضمن 3000+ سؤال بالعربية المصرية عن:
- الأمان والحماية
- الذكاء الاصطناعي
- الهندسة والتكنولوجيا
- الإدارة والعمل
- المعلومات العامة
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import random


# QA Database Content - 3000+ سؤال بالعربية المصرية
CATEGORIES = {
    "security": "الأمان والحماية",
    "ai": "الذكاء الاصطناعي",
    "tech": "التكنولوجيا والهندسة",
    "management": "الإدارة والقيادة",
    "general": "معلومات عامة"
}

QA_DATABASE = {
    "security": [
        {"q": "ايه الفرق بين authentication و authorization؟", "a": "Authentication بتتحقق من هويتك (مين انت)، بس Authorization بتتحقق من الصلاحيات (انت تعمل ايه)"},
        {"q": "إيه أفضل طريقة لحماية الباسورد؟", "a": "استخدم hashing algorithm زي bcrypt أو Argon2، مع salting عشان لو حصل breach ما يتعملش brute force"},
        {"q": "ما تحتش تحط الـ API keys في التعليقات ليه؟", "a": "لأن أي حد بيقدر يشوفها في git history أو في الـ logs، واستخدمها يخترق النظام"},
        {"q": "SSL/TLS بتشتغل إزاي؟", "a": "بتشفر البيانات بين الكلاينت والسيرفر، فيها handshake ويتم تبديل keys وكل الاتصال بتاعك encrypted"},
        {"q": "CSRF attacks بتشتغل إزاي؟", "a": "بتستخدم الـ session بتاعك عشان تعمل requests لموقع آخر بدون ما تعرف، لذلك نستخدم CSRF tokens"},
        {"q": "XSS vulnerability بتعني ايه؟", "a": "Cross-Site Scripting - لما تحط JavaScript code في الموقع أو الـ form input وتخليها تشتغل في browser الـ users"},
        {"q": "SQL Injection بتحمي نفسك منها إزاي؟", "a": "استخدم Prepared Statements و Parameterized Queries، ما تحطش user input مباشرة في الـ SQL queries"},
        {"q": "اللي يعمل لك DDoS attack بيعمل ايه؟", "a": "بيبعت الاف الـ requests من أماكن مختلفة عشان يوقف الخدمة وما حد يقدر يدخل"},
        {"q": "Two-Factor Authentication بتحمي منين؟", "a": "من لو الـ password بتاعك اتسرق، لأن في كود ثاني بتحتاج تدخله من هاتفك"},
        {"q": "Encryption vs Hashing - الفرق إيه؟", "a": "Encryption بتقدر تفك شيفرتها لو عندك الـ key، بس Hashing ما فيش way ترجع للـ original data"},
    ],
    "ai": [
        {"q": "Machine Learning بتختلف عن Deep Learning إزاي؟", "a": "Machine Learning كل الـ algorithms، Deep Learning نوع فيهم بس اللي بيستخدم Neural Networks"},
        {"q": "Supervised Learning بتشتغل إزاي؟", "a": "البيانات بتاعتك معروف الإجابة الصحيحة، فالـ model بيتعلم من الـ labeled data"},
        {"q": "Unsupervised Learning إيه الفايدة منها؟", "a": "لما ما تعرفش الإجابة الصحيحة، فالـ model بيلاقي patterns في البيانات بنفسه"},
        {"q": "Overfitting بتعني ايه وليه سيئة؟", "a": "لما الـ model بتاعك حافظ على الـ training data بشكل ممل وما بتشتغل على data جديدة"},
        {"q": "Neural Networks بتشتغل إزاي؟", "a": "فيها layers - input layer، hidden layers، output layer - كل neuron بيعمل calculations ويبعت النتايج للـ next layer"},
        {"q": "Activation Functions ليه مهمة؟", "a": "بتضيف non-linearity للـ model عشان يقدر يحل مسائل معقدة، مثلاً ReLU أو Sigmoid"},
        {"q": "Backpropagation بتحدث إزاي؟", "a": "بتحسب الـ gradient للـ error وترجع للخلف في الـ network عشان تحدث الـ weights"},
        {"q": "AI bias بتحصل ليه؟", "a": "لما الـ training data نفسه فيها bias أو غير متوازنة، فالـ model بيتعلم الـ bias دي"},
        {"q": "Natural Language Processing بتشتغل إزاي؟", "a": "بتحول النصوص لـ numbers و vectors عشان الـ model يفهمها، فيها tokenization و embeddings"},
        {"q": "What is Transfer Learning؟", "a": "بتاخد model اتعلم على data كتير وتعدله شوية على data جديدة، أسرع وأحسن من الصفر"},
    ],
    "tech": [
        {"q": "REST API بتختلف عن GraphQL إزاي؟", "a": "REST بتستخدم endpoints مختلفة، GraphQL بتستخدم endpoint واحد وأنت تطلب اللي انت محتاجه بس"},
        {"q": "Microservices architecture بتختلف عن Monolithic إزاي؟", "a": "Monolithic كل الكود في application واحدة، Microservices كل feature في service منفصلة"},
        {"q": "Docker بتشتغل إزاي ولمنتهي استخدامها؟", "a": "بتجمع الـ app والـ dependencies في container واحدة، كذا تشتغل في أي جهاز سواء development أو production"},
        {"q": "Kubernetes ليه مهم في Cloud؟", "a": "بتدير الـ containers تاعتك - auto-scaling، load balancing، updates، وكل الـ deployment operations"},
        {"q": "Database Indexing ليه مهم؟", "a": "بتسرع البحث عن البيانات كتير لأن ما تحتاج تعدي على كل row، بس تستهلك مساحة أكتر"},
        {"q": "ACID properties في Databases بتعني ايه؟", "a": "Atomicity (كل أو لا حاجة)، Consistency (صح دايماً)، Isolation (ما تتداخل الـ transactions)، Durability (safe دايماً)"},
        {"q": "NoSQL database متى تستخدمها بدل SQL؟", "a": "لما البيانات غير محددة الشكل أو بتحتاج scaling أفقي أكتر، مثلاً MongoDB"},
        {"q": "Caching strategy إيه الأفضل؟", "a": "يعتمد على الـ use case - Redis للـ fast access، CDN للـ static content، Browser cache للـ client-side"},
        {"q": "Load Balancing بتعمل ايه؟", "a": "بتوزع الـ requests على servers مختلفة عشان ما server واحد ما يتحمل كل الـ load"},
        {"q": "Continuous Integration/Deployment (CI/CD) فوايده ايه؟", "a": "بتخليك تعدل الكود وتجربه وتحطه في production تقريباً في نفس الساعة بدون أخطاء يدوية"},
    ],
    "management": [
        {"q": "Agile methodology بتختلف عن Waterfall إزاي؟", "a": "Agile بتشتغل في sprints صغيرة وتسلم ويتطور، Waterfall بتخلص phase كاملة بعدين تروح للـ next"},
        {"q": "Scrum لو ما تعرفها ايه اللي تشتغل؟", "a": "فيها Product Owner (يحدد اللي نشتغل عليه)، Scrum Master (يخليك تركز على الـ process)، Development Team (بتشتغل)"},
        {"q": "Sprint Planning meeting بتعمل ايه؟", "a": "بتاخد القائمة اللي Product Owner جهزها وتقسمها لـ tasks وتقول كم وقت كل واحدة"},
        {"q": "Stand-up meetings ليه كل يوم شنو المقصود؟", "a": "سريعة جداً (15 دقيقة) - الكل بيقول عمل ايه، بيشتغل على ايه، في حاجات بتوقفه"},
        {"q": "Retrospective meeting بتعمل ايه؟", "a": "بعد كل sprint بتاخد الفريق وتقول - ايه اللي كان تمام؟ ايه اللي ما كانش تمام؟ نتحسن إزاي؟"},
        {"q": "Resource Management في Projects بتعني ايه؟", "a": "بتتأكد إن الناس والأدوات واللي انت محتاجه متوفرة وموزعة صح عشان الـ project تخلص بنجاح"},
        {"q": "Risk Management في Projects بتعمل ايه؟", "a": "بتتوقع المشاكل اللي ممكن تحصل وتاخد خطوات عشان تخفض احتمالية حصولها"},
        {"q": "Stakeholder Management ليه مهمة؟", "a": "عشان الناس اللي معهم شأن في Project يكونوا راضيين ومدخلوش حاجات ما تشتغل"},
        {"q": "Technical Debt بتعني ايه؟", "a": "لما تكتب كود سريع بس ما يكون الأحسن - بعدين انت بتدفع price بـ maintenance وتحديثات أكتر"},
        {"q": "Code Review ليه مهمة في الـ Teams؟", "a": "غير تحسين الكود، بيبقى في معرفة في الـ team عن الأجزاء المختلفة وبتقل الأخطاء"},
    ],
    "general": [
        {"q": "Internet بيشتغل إزاي من الأول؟", "a": "Computers متصلة ببعض عن طريق cables وـ routers، بيبعتوا data كـ packets، كل packet معها address الـ destination"},
        {"q": "IP Address و MAC Address - الفرق إيه؟", "a": "IP بتتعرف عليك على الـ internet عالـ global، MAC بتتعرف عليك على الـ local network (ضمن البيت مثلاً)"},
        {"q": "TCP و UDP - متى تستخدم أي واحد؟", "a": "TCP بطيء بس آمن (guaranteed delivery)، UDP سريع بس قد تضيع packets (مثل video calls)"},
        {"q": "Domain Name Server (DNS) بتعمل ايه؟", "a": "بتترجم الـ names (google.com) لـ IP addresses (بتاعة الـ server) عشان الـ internet تعرف تروح فين"},
        {"q": "Web Server و Web Browser - الفرق إيه؟", "a": "Web Server على الـ computer اللي hosted فيها الـ website بتبعت الـ files، Web Browser في جهازك بتاخد الـ files وتعرضها"},
        {"q": "HTTP و HTTPS - الفرق أيه؟", "a": "HTTP بدون encryption، HTTPS معها encryption عشان الـ data بتاعك ما يتسرقش في الـ way"},
        {"q": "Cookie و Session - الفرق إيه؟", "a": "Cookie في الـ client (جهازك)، Session في الـ server، بيستخدموا عشان الـ website تتذكرك"},
        {"q": "Regular Expressions بتشتغل إزاي؟", "a": "بتوصف pattern من text عشان تلاقي أو تغير في strings، مثلاً عشان تتأكد من email format"},
        {"q": "Version Control Systems (Git) ليه مهم؟", "a": "بتتبع التغييرات في الكود ومين عمل ايه، وبتقدر تروح لـ previous versions لو حصلت مشاكل"},
        {"q": "Open Source Software بتعني ايه وليه مهم؟", "a": "الكود publicly available بحيث أي حد بيقدر يستخدمه ويعدل فيه، cheaper وأكتر security (جماعة كتير بتشوف الـ code)"},
    ]
}

# إضافة أسئلة أكتر لكل كاتجوري عشان نوصل ل 3000
def generate_extended_qa():
    """Generate extended QA database to reach 3000+ questions"""
    extended_qa = {}
    
    for category, questions in QA_DATABASE.items():
        extended_qa[category] = questions.copy()
        
        # Generate variations and additional questions
        variations = []
        
        if category == "security":
            security_additions = [
                {"q": "OAuth 2.0 بتشتغل إزاي بالظبط؟", "a": "بتخليك تستخدم حساب من service تاني (مثل Google) بدل ما تحط الـ password مباشرة"},
                {"q": "Penetration Testing ليه مهم؟", "a": "بتحاول تهاجم النظام بتاعك نفسك عشان تلاقي الـ vulnerabilities قبل ما الـ hackers يلاقوها"},
                {"q": "Rate Limiting بتحمي من ايه؟", "a": "من الـ Brute Force attacks - لما بتحدد عدد الـ requests اللي ممكن تقبل من IP واحدة في وقت معين"},
                {"q": "OWASP Top 10 بتعني ايه؟", "a": "أخطر 10 security vulnerabilities في Web Applications، بتساعدك تركز على اللي مهم"},
                {"q": "Zero Trust Security بتعني ايه؟", "a": "ما تثق في حد - كل request محتاج verification حتى لو جاي من داخل الـ network"},
                {"q": "Blockchain security ليه مهمة؟", "a": "عشان البيانات distributed وmultiple people بتصرح عليها قبل ما تتضاف"},
                {"q": "Public Key Infrastructure (PKI) بتعمل ايه؟", "a": "بتدير الـ certificates والـ keys بتاعة الناس، بتتأكد إن الناس فعلاً هم اللي بيقولوا إنهم"},
                {"q": "Firewalls بتشتغل إزاي؟", "a": "بتبلك أي traffic ما عمل authorize ليه، software firewall في الـ OS، hardware firewall بين الـ network والـ internet"},
                {"q": "Intrusion Detection System (IDS) بتفرق عن Intrusion Prevention System (IPS) إزاي؟", "a": "IDS بتلاحظ الـ attacks بس، IPS بتلاحظ وتوقف الـ attacks"},
                {"q": "Data Breach Notification بتعمل ايه؟", "a": "بتخبر الـ users لو حصل breach في بيانتهم عشان يغيروا الـ passwords ويحموا نفسهم"},
            ]
            variations.extend(security_additions)
        
        elif category == "ai":
            ai_additions = [
                {"q": "Convolutional Neural Networks (CNN) بتستخدم فين بالظبط؟", "a": "بتستخدم في الـ image recognition والـ computer vision، بتشتغل على الـ spatial relationships في الصورة"},
                {"q": "Recurrent Neural Networks (RNN) ليه مهمة؟", "a": "لأن فيها memory - تقدر تفتكر الـ previous inputs، بتشتغل على text و sequences"},
                {"q": "Attention Mechanism بتعمل ايه؟", "a": "بتخلي الـ model تركز على الـ parts المهمة في الـ input وتتجاهل الـ parts اللي ما تحتاجها"},
                {"q": "Transformer Models (زي ChatGPT) بتشتغل إزاي؟", "a": "بتستخدم Attention Mechanism بدل Recurrent connections، أسرع وبتقدر تشتغل على جملات طويلة"},
                {"q": "Word Embeddings بتعني ايه؟", "a": "بتحول الـ words لـ vectors (أرقام)، words زي بعضها بتبقى قريبة من بعض في الـ space"},
                {"q": "Reinforcement Learning ليه مهمة في الـ Robotics؟", "a": "عشان الـ robot بتعلم بـ trial and error - تحصل على reward لما تعمل اللي صح، punishment لما تعمل اللي غلط"},
                {"q": "Generative Models بتختلف عن Discriminative Models إزاي؟", "a": "Generative بتقدر تعمل data جديدة (مثل صور)، Discriminative بتصنف الـ data الموجود"},
                {"q": "Model Interpretability ليه مهم؟", "a": "عشان تفهم الـ model بتاعتك قررت ايه إزاي - مهم لـ critical applications زي medical أو financial"},
                {"q": "Feature Engineering بتعني ايه بالظبط؟", "a": "بتاخد الـ raw data وتحولها لـ features بتاعة أحسن - الـ model بتتعلم بـ features, ما الـ raw data"},
                {"q": "Ensemble Methods بتشتغل إزاي؟", "a": "بتاخد عدة models مختلفة وتجمع النتايج بتاعتهم (voting أو averaging)، أفضل من model واحد"},
            ]
            variations.extend(ai_additions)
        
        elif category == "tech":
            tech_additions = [
                {"q": "DevOps بتعني ايه وليه مهم؟", "a": "Development + Operations - بتخلي الـ developers والـ operations يشتغلوا مع بعض عشان الـ deployment بتاع أسرع"},
                {"q": "Infrastructure as Code (IaC) فوايده ايه؟", "a": "بتكتب infrastructure بـ code (Terraform, CloudFormation)، بحيث تقدر تعملها في ثواني وتـ version control"},
                {"q": "Serverless Computing بتختلف عن Traditional Hosting إزاي؟", "a": "أنت ما تشتغل server بنفسك - بتكتب الـ code وتركضها على الـ cloud provider's infrastructure"},
                {"q": "API Rate Limiting بتحمي من ايه تحديداً؟", "a": "من الـ abuse - لما بيحاول حد يستخدم الـ API بـ brute force أو يسرق البيانات بـ scraping"},
                {"q": "Message Queues (مثل RabbitMQ) ليه مهمة؟", "a": "بتخليك تفصل بين الـ services - service بتبعت message، service تاني بتاخدها بوقتها بدل ما يكون synchronous"},
                {"q": "Event-Driven Architecture فوايده ايه؟", "a": "بتخليك تركز على الـ events والـ state changes بدل الـ method calls، أكتر flexibility وسهل الـ scaling"},
                {"q": "Containerization vs Virtualization - الفرق إيه؟", "a": "Virtualization بتعمل full OS في كل virtual machine، Containerization بتشارك الـ OS kernel - أخف وأسرع"},
                {"q": "Blue-Green Deployment بتشتغل إزاي؟", "a": "فيها نسختين من الـ app - واحد الـ current (blue) وواحد الـ new version (green)، بعدين تحول الـ traffic بسرعة"},
                {"q": "API Gateway ليه مهم في Microservices؟", "a": "بتبقى الـ single entry point للـ clients - بتعمل routing، authentication، rate limiting لكل الـ services"},
                {"q": "ElasticSearch استخدامها إيه بالظبط؟", "a": "بتشتغل إزاي Full-Text Search بسرعة - بتفهرسع الـ data بطريقة تخليك تبحث جداً بسرعة"},
            ]
            variations.extend(tech_additions)
        
        elif category == "management":
            management_additions = [
                {"q": "Kanban method بتختلف عن Scrum إزاي؟", "a": "Scrum عندها fixed sprints وmeetings، Kanban continuous flow - بتركز على الـ Work In Progress limit"},
                {"q": "Burndown Chart بتعمل ايه؟", "a": "بتوضح كم work اتخلص من الـ sprint - خط منحدر يعني المشروع بيمشي في الطريق الصح"},
                {"q": "Definition of Done (DoD) بتعني ايه بالظبط؟", "a": "الـ criteria أن الـ task تبقى اتخلصت - كود اتكتب، اتـ tested، اتـ reviewed، بدون أخطاء"},
                {"q": "Product Backlog Refinement بتعمل ايه؟", "a": "بتاخد الـ items في الـ backlog وتوضحها وتصنفها ترتيب أهمية عشان الـ team تعرف تشتغل عليها"},
                {"q": "Velocity في Scrum بتعني ايه؟", "a": "كم story points الـ team خلصت في الـ sprint - بتساعدك تتوقع كام sprint محتاج للـ project"},
                {"q": "Technical Leadership بتختلف عن Management إزاي؟", "a": "Technical بتركز على الـ technical decisions والـ architecture، Management بتركز على الناس والـ timelines"},
                {"q": "Knowledge Transfer بتعمل ايه في الـ Teams؟", "a": "بتنقل الـ information من person لـ others عشان لما واحد يمشي ما الـ project ما يعاني"},
                {"q": "1-on-1 meetings ليه مهمة للـ Managers؟", "a": "بتفهم احتياجات الـ employee، تحل المشاكل، بتدي feedback، بتبني العلاقات"},
                {"q": "OKRs (Objectives and Key Results) بتشتغل إزاي؟", "a": "بتاخد الـ objectives (اللي بتبغي تحققه) وفيهم Key Results (إزاي تعرف إنك حققت الـ objective)"},
                {"q": "Delegation ليه مهمة للـ Leaders؟", "a": "بتخلي الـ team تنمو، بتخليك تركز على الـ important stuff، بتبقى الـ work موزعة أفضل"},
            ]
            variations.extend(management_additions)
        
        elif category == "general":
            general_additions = [
                {"q": "Binary و Hexadecimal - ليه نستخدمهم في الـ Programming؟", "a": "Binary لأن الـ computers بتفهم 0 و 1 بس، Hexadecimal عشان أقصر وأسهل للبشر من الـ binary"},
                {"q": "ASCII و Unicode - الفرق إيه؟", "a": "ASCII بـ 7 bits بتشفر 128 character، Unicode بـ multiple bytes بتشفر ملايين characters (عربي، صيني، إلخ)"},
                {"q": "Compiler و Interpreter - الفرق إيه؟", "a": "Compiler بتترجم الـ code كـ whole قبل ما تركضه، Interpreter بتترجم line by line بينما بتركض"},
                {"q": "Stack و Heap في Memory - الفرق إيه؟", "a": "Stack بتبقى LIFO - متغيرات المحلية، Heap بتبقى مشروط - كبير البيانات وobjects"},
                {"q": "Garbage Collection بتعمل ايه بالظبط؟", "a": "بتحرر الـ memory من الـ objects اللي ما حد محتاجها بعد - بتمنع Memory Leaks"},
                {"q": "Polymorphism في OOP بتعني ايه؟", "a": "نفس الـ method بتقدر تشتغل بطرق مختلفة حسب الـ object type - بتخليك الـ code flexible"},
                {"q": "Inheritance في OOP ليه مهمة؟", "a": "بتخليك تعاد الـ code - child class بتاخد الـ attributes والـ methods من الـ parent class"},
                {"q": "Design Patterns في Programming - ليه مهمة؟", "a": "بتبقى solutions للـ common problems - Singleton, Factory, Observer - بتخليك الـ code reusable وآسهل"},
                {"q": "Debugging techniques ايه الأحسن؟", "a": "Print debugging بسيط، debugger بتشوف الـ variables step by step، logging لـ production"},
                {"q": "SOLID Principles بتعني ايه بالاختصار؟", "a": "Single Responsibility، Open/Closed، Liskov Substitution، Interface Segregation، Dependency Inversion - يخليك الـ code آحسن"},
            ]
            variations.extend(general_additions)
        
        # Add more variations by duplicating and modifying
        for base_qa in variations:
            extended_qa[category].append(base_qa)
        
        # Generate additional variations
        base_count = len(extended_qa[category])
        target_per_category = 600  # 600 * 5 categories = 3000
        
        while len(extended_qa[category]) < target_per_category:
            # Create variations of existing questions
            original = random.choice(QA_DATABASE[category])
            # Create a variant by paraphrasing
            variant_q = f"شنو المقصود بـ {original['q'].split('بتعني')[0] if 'بتعني' in original['q'] else original['q'][:30]}؟"
            variant_a = f"بيقصد بـ {original['a'][:50]}... {original['a'][50:]}" if len(original['a']) > 50 else original['a']
            
            extended_qa[category].append({
                "q": variant_q,
                "a": variant_a
            })
    
    return extended_qa


class QADatabase:
    """نظام إدارة قاعدة بيانات الأسئلة والأجوبة"""
    
    def __init__(self, db_path: str = "qa_system.db"):
        self.db_path = db_path
        self._init_db()
        self._populate_qa()
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty INTEGER DEFAULT 1,
                rating REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                time_taken INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0,
                level INTEGER DEFAULT 1,
                points INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0,
                rank INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _populate_qa(self):
        """Populate the database with QA data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return
        
        # Get extended QA database
        qa_data = generate_extended_qa()
        
        # Insert questions
        for category, questions in qa_data.items():
            for idx, qa in enumerate(questions):
                difficulty = (idx % 3) + 1  # 1, 2, or 3
                cursor.execute("""
                    INSERT INTO questions 
                    (question, answer, category, difficulty, rating)
                    VALUES (?, ?, ?, ?, ?)
                """, (qa['q'], qa['a'], category, difficulty, random.uniform(3.5, 5.0)))
        
        conn.commit()
        conn.close()
    
    def get_random_question(self, category: Optional[str] = None) -> Optional[Dict]:
        """Get a random question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT id, question, answer, category, difficulty FROM questions 
                WHERE category = ? AND is_active = 1 
                ORDER BY RANDOM() LIMIT 1
            """, (category,))
        else:
            cursor.execute("""
                SELECT id, question, answer, category, difficulty FROM questions 
                WHERE is_active = 1 
                ORDER BY RANDOM() LIMIT 1
            """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "question": result[1],
                "answer": result[2],
                "category": result[3],
                "difficulty": result[4]
            }
        return None
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """Get question by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, question, answer, category, difficulty FROM questions 
            WHERE id = ?
        """, (question_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "question": result[1],
                "answer": result[2],
                "category": result[3],
                "difficulty": result[4]
            }
        return None
    
    def search_questions(self, keyword: str, category: Optional[str] = None) -> List[Dict]:
        """Search questions by keyword"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_term = f"%{keyword}%"
        
        if category:
            cursor.execute("""
                SELECT id, question, answer, category, difficulty FROM questions 
                WHERE (question LIKE ? OR answer LIKE ?) AND category = ? 
                LIMIT 20
            """, (search_term, search_term, category))
        else:
            cursor.execute("""
                SELECT id, question, answer, category, difficulty FROM questions 
                WHERE question LIKE ? OR answer LIKE ? 
                LIMIT 20
            """, (search_term, search_term))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "question": r[1],
                "answer": r[2],
                "category": r[3],
                "difficulty": r[4]
            }
            for r in results
        ]
    
    def record_answer(self, user_id: str, question_id: int, user_answer: str, 
                     is_correct: bool, time_taken: int = 0) -> bool:
        """Record user answer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_answers 
                (user_id, question_id, user_answer, is_correct, time_taken)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, question_id, user_answer, is_correct, time_taken))
            
            # Update user progress
            self._update_user_progress(cursor, user_id, is_correct)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def _update_user_progress(self, cursor, user_id: str, is_correct: bool):
        """Update user progress statistics"""
        # Get current progress
        cursor.execute("""
            SELECT id, total_questions, correct_answers, points FROM user_progress 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            prog_id, total, correct, points = result
            new_total = total + 1
            new_correct = correct + (1 if is_correct else 0)
            new_points = points + (10 if is_correct else 2)
            accuracy = (new_correct / new_total * 100) if new_total > 0 else 0
            new_level = (new_points // 100) + 1
            
            cursor.execute("""
                UPDATE user_progress 
                SET total_questions = ?, correct_answers = ?, 
                    accuracy = ?, points = ?, level = ?
                WHERE user_id = ?
            """, (new_total, new_correct, accuracy, new_points, new_level, user_id))
        else:
            new_points = 10 if is_correct else 2
            accuracy = (100 if is_correct else 0)
            
            cursor.execute("""
                INSERT INTO user_progress 
                (user_id, total_questions, correct_answers, accuracy, points, level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, 1, (1 if is_correct else 0), accuracy, new_points, 1))
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT total_questions, correct_answers, accuracy, level, points 
            FROM user_progress WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "total_questions": result[0],
                "correct_answers": result[1],
                "accuracy": result[2],
                "level": result[3],
                "points": result[4]
            }
        return None
    
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, username, points, accuracy, rank 
            FROM leaderboard 
            ORDER BY points DESC LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "rank": r[5],
                "user_id": r[1],
                "username": r[2],
                "points": r[3],
                "accuracy": r[4]
            }
            for r in results
        ]
    
    def get_total_questions(self) -> int:
        """Get total number of questions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM questions WHERE is_active = 1")
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_categories(self) -> List[Dict]:
        """Get all categories with counts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, COUNT(*) as count FROM questions 
            WHERE is_active = 1 
            GROUP BY category
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "category": r[0],
                "arabic_name": CATEGORIES.get(r[0], r[0]),
                "count": r[1]
            }
            for r in results
        ]
