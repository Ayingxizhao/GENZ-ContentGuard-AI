from local_model import LocalGenZDetector
import time

def test_model():
    """Test the trained model with various content types"""
    
    print("🔄 Loading local model...")
    detector = LocalGenZDetector()
    
    if not detector.model_loaded:
        print("❌ Model failed to load!")
        return
    
    print("✅ Model loaded successfully!")
    print("\n" + "="*60)
    print("🧪 TESTING MODEL WITH VARIOUS CONTENT TYPES")
    print("="*60)
    
    # Test cases - different types of content
    test_cases = [
        # Safe content examples
        {
            "title": "Feeling down today",
            "content": "I'm having a rough day and could use some advice. Anyone else feel this way?",
            "expected": "safe"
        },
        {
            "title": "Movie recommendations",
            "content": "What are your favorite movies? I love watching films and need new suggestions!",
            "expected": "safe"
        },
        
        # Clearly malicious content examples
        {
            "title": "Hate speech",
            "content": "I hate all [racial slur] people, they should die and burn in hell forever",
            "expected": "malicious"
        },
        {
            "title": "Suicide encouragement",
            "content": "kill yourself you worthless piece of shit, nobody will miss you",
            "expected": "malicious"
        },
        {
            "title": "Violent threats",
            "content": "I'm going to find you and beat you to death with a baseball bat",
            "expected": "malicious"
        },
        
        # GenZ specific language (potentially problematic)
        {
            "title": "GenZ slang",
            "content": "This is so cringe, kys and touch grass you absolute loser",
            "expected": "malicious"
        },
        {
            "title": "Online harassment",
            "content": "You're so ugly, delete your account and never post again",
            "expected": "malicious"
        },
        
        # Ambiguous cases
        {
            "title": "Strong opinion",
            "content": "I really dislike this person, they're the worst and I can't stand them",
            "expected": "safe"  # Strong dislike but not necessarily malicious
        },
        {
            "title": "Dark humor",
            "content": "Lol this is so bad it makes me want to die (jk though)",
            "expected": "safe"  # Dark humor, not serious
        }
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['title']}")
        print(f"Content: {test_case['content'][:80]}...")
        print(f"Expected: {test_case['expected']}")
        
        # Get prediction
        start_time = time.time()
        result = detector.predict(test_case['title'], test_case['content'])
        prediction_time = time.time() - start_time
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            continue
            
        print(f"Predicted: {result['prediction']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Time: {prediction_time:.3f}s")
        
        # Check if prediction matches expectation
        if result['prediction'] == test_case['expected']:
            print("✅ CORRECT!")
            correct_predictions += 1
        else:
            print("❌ WRONG!")
            
        print("-" * 40)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Total tests: {total_tests}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Accuracy: {(correct_predictions/total_tests)*100:.1f}%")
    
    if correct_predictions/total_tests >= 0.8:
        print("🎉 Model is performing well!")
    elif correct_predictions/total_tests >= 0.6:
        print("⚠️  Model needs improvement")
    else:
        print("🚨 Model needs significant improvement")

if __name__ == "__main__":
    test_model()
