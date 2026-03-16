import os, django, sys, requests, random, html

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_tracker.settings')
django.setup()

from dashboard.models import MockTest, MockTestQuestion


def sync_from_web():

    api_url = "https://opentdb.com/api.php?amount=35&category=18&type=multiple"

    test_categories = [
        ("Python Masterclass", "Core logic and syntax"),
        ("Database Architect", "SQL and Normalization"),
        ("Web Foundations", "HTML/CSS and Networking")
    ]

    for name, desc in test_categories:

        test, _ = MockTest.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )

        print(f"Syncing Battle: {name}...")

        try:

            res = requests.get(api_url).json()
            results = res.get('results', [])

            for r in results:

                opts = r['incorrect_answers'] + [r['correct_answer']]
                random.shuffle(opts)

                question_text = html.unescape(r['question'])

                if not MockTestQuestion.objects.filter(test=test, question=question_text).exists():

                    MockTestQuestion.objects.create(
                        test=test,
                        question=question_text,
                        option1=html.unescape(opts[0]),
                        option2=html.unescape(opts[1]),
                        option3=html.unescape(opts[2]),
                        option4=html.unescape(opts[3]),
                        answer=html.unescape(r['correct_answer'])
                    )

            print(f"Loaded {len(results)} real questions into {name}")

        except Exception as e:

            print(f"Uplink Error for {name}: {e}")


if __name__ == "__main__":
    sync_from_web()