"""
Sylly App - Main Entry Point
Syllabus extraction and calendar sync application
"""

from database import FirebaseDB
from datetime import datetime, date


def main():
    """Example usage of the Firebase database"""
    
    # Initialize database
    db = FirebaseDB("firebase-key.json")
    
    # Example: Create a user
    user_id = "user123"
    db.create_user(
        user_id=user_id,
        email="student@example.com",
        name="John Doe"
    )
    print(f"Created user: {user_id}")
    
    # Example: Upload a syllabus
    syllabus_id = "syllabus456"
    db.create_syllabus(
        user_id=user_id,
        syllabus_id=syllabus_id,
        filename="CS101_Syllabus.pdf",
        file_type="pdf",
        file_size=1024000,
        storage_path="uploads/user123/syllabus456.pdf"
    )
    print(f"Created syllabus: {syllabus_id}")
    
    # Example: Mark syllabus as processed with extracted text
    db.set_syllabus_extracted_text(
        syllabus_id=syllabus_id,
        extracted_text="CS 101 Introduction to Computer Science..."
    )
    
    # Example: Create extracted events
    events = [
        {
            "title": "Midterm Exam",
            "event_type": "exam",
            "start_date": datetime(2025, 3, 15, 14, 0),
            "start_time": "14:00",
            "end_time": "16:00",
            "location": "Room 101"
        },
        {
            "title": "Assignment 1 Due",
            "event_type": "deadline",
            "start_date": datetime(2025, 2, 10, 15, 0),
            "start_time": "23:59"
        },
        {
            "title": "Final Project Due",
            "event_type": "deadline",
            "start_date": datetime(2025, 5, 1, 23, 59),
            "start_time": "23:59"
        }
    ]
    
    event_ids = db.batch_create_events(
        syllabus_id=syllabus_id,
        events_list=events,
        user_id=user_id
    )
    print(f"Created {len(event_ids)} events")
    
    # Example: Get pending events for review
    pending_events = db.get_pending_events(user_id)
    print(f"\nFound {len(pending_events)} pending events:")
    for event in pending_events:
        print(f"  - {event['title']} ({event['event_type']}) on {event['start_date']}")
    
    # Example: Approve an event
    if pending_events:
        first_event_id = pending_events[0]['id']
        db.approve_event(first_event_id)
        print(f"\nApproved event: {first_event_id}")
    
    # Example: Get all user syllabi
    user_syllabi = db.get_user_syllabi(user_id)
    print(f"\nUser has {len(user_syllabi)} syllabi uploaded")


if __name__ == "__main__":
    main()

