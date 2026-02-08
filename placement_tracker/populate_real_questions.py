import os, django, sys, requests, random

# --- DJANGO SETUP ---
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_tracker.settings')
django.setup()

from dashboard.models import MockTest, MockTestQuestion

def sync_from_web():
    # Public API for Computer Science Questions (Category 18)
    api_url = "https://opentdb.com/api.php?amount=35&category=18&type=multiple"
    
    test_categories = [
        ("Python Masterclass", "Core logic and syntax"),
        ("Database Architect", "SQL and Normalization"),
        ("Web Foundations", "HTML/CSS and Networking")
    ]

    for name, desc in test_categories:
        test, _ = MockTest.objects.get_or_create(name=name, defaults={'description': desc})
        print(f"Syncing Battle: {name}...")
        
        try:
            res = requests.get(api_url).json()
            results = res.get('results', [])
            
            for r in results:
                # Merge correct and incorrect answers for our 4-option model
                opts = r['incorrect_answers'] + [r['correct_answer']]
                # Ensure we have exactly 4 options
                if len(opts) == 4:
                    MockTestQuestion.objects.create(
                        test=test,
                        question=r['question'],
                        option1=opts[0],
                        option2=opts[1],
                        option3=opts[2],
                        option4=opts[3],
                        answer=r['correct_answer']
                    )
            print(f"Successfully loaded {len(results)} real questions into {name}")
        except Exception as e:
            print(f"Uplink Error for {name}: {e}")

if __name__ == "__main__":
    sync_from_web()