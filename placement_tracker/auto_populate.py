import os
import django
import sys

# --- AUTOMATIC SETTINGS DETECTION ---
# This finds your settings file automatically so you don't get ModuleNotFoundError
sys.path.append(os.getcwd())
settings_file = None
for root, dirs, files in os.walk("."):
    if "settings.py" in files:
        settings_file = os.path.join(root, "settings.py").replace(os.sep, ".").replace(".settings.py", ".settings").strip(".\\")
        break

if not settings_file:
    print("Error: Could not find settings.py. Make sure you run this in the project root.")
    sys.exit()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)
django.setup()

# Import your models (Replace 'base' with your actual app name if it's different)
# If your app name is 'myapp', change 'base.models' to 'myapp.models'
try:
    from dashboard.models import MockTest, MockTestQuestion
except ImportError:
    print("Error: Could not find models. Change 'base.models' in the script to '[your_app_name].models'")
    sys.exit()

def populate_vault():
    test_data = [
        ("Python Masterclass", "Core Python, Decorators, Generators, and Memory Management."),
        ("DSA: Ultimate Graphs", "Traversals, Shortest Paths, and Connectivity algorithms."),
        ("Modern React Engine", "Hooks, Context API, Virtual DOM, and Reconciliation."),
        ("Database Architect", "Normalization, Indexing, and ACID Properties."),
        ("Operating Systems Pro", "Scheduling, Deadlocks, and Paging Mechanisms."),
        ("Java Enterprise", "JVM Architecture, Multithreading, and Spring basics."),
        ("Full Stack JS", "Node.js Event Loop, Express, and Middleware logic."),
        ("C++ Power User", "Pointers, STL, and Resource Management (RAII)."),
        ("Computer Networks", "TCP/IP, HTTP/S, OSI Layers, and Subnetting."),
        ("System Design Tier-1", "Load Balancing, Hashing, Caching, and Microservices."),
        ("Machine Learning", "Supervised Learning, Cost Functions, and Neural Nets."),
        ("SQL Injection & Sec", "Web security vulnerabilities and prevention techniques."),
        ("DevOps Lifecycle", "Docker, Kubernetes, and CI/CD Pipeline logic."),
        ("AWS Cloud Master", "EC2, S3, IAM, and Lambda serverless architecture."),
        ("Competitive Logic", "Bitmasking, DP, and Mathematical optimizations."),
        ("Linux Admin Shell", "Bash scripting, Grep, Sed, and Kernel basics."),
        ("Django Web Framework", "ORM, MVT, Middleware, and Security features."),
        ("Soft Skills Tech", "Logical reasoning, Aptitude, and Verbal for Tech rounds."),
        ("Big Data Concepts", "Hadoop, Spark, and Distributed Computing."),
        ("Cybersecurity Hub", "Encryption, JWT, and Auth protocols.")
    ]

    print("--- Starting Vault Population ---")
    for name, desc in test_data:
        test, created = MockTest.objects.get_or_create(name=name, defaults={'description': desc})
        if created:
            print(f"Created Test: {name}")
            questions = []
            for i in range(1, 36):
                questions.append(MockTestQuestion(
                    test=test,
                    question=f"Critical Question {i}: Analyze the core behavior of {name} in a high-concurrency environment.",
                    option1="Increases Latency",
                    option2="Decreases Throughput",
                    option3="Optimizes Resource Allocation",
                    option4="Fails under load",
                    answer="Option 3"
                ))
            # Batch create is much faster
            MockTestQuestion.objects.bulk_create(questions)
        else:
            print(f"Skipping {name} (Already exists)")

    print("--- Success: 20 Tests & 700 Questions Processed ---")

if __name__ == "__main__":
    populate_vault()