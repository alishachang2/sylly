"""
Firebase Database Module for Sylly App
Handles user data, syllabi metadata, and extracted events
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Optional, Dict, List, Any
import os


class FirebaseDB:
    """Firebase Firestore database manager"""
    
    def __init__(self, key_path: str = "firebase-key.json"):
        """
        Initialize Firebase Admin SDK
        
        Args:
            key_path: Path to Firebase service account key file
        """
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    # ========== USER OPERATIONS ==========
    
    def create_user(self, user_id: str, email: str, name: Optional[str] = None, 
                   google_calendar_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user document
        
        Args:
            user_id: Unique user identifier
            email: User email address
            name: User's display name
            google_calendar_id: Google Calendar ID if connected
        
        Returns:
            User document data
        """
        user_data = {
            "email": email,
            "name": name,
            "google_calendar_id": google_calendar_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.db.collection("users").document(user_id).set(user_data)
        return user_data
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user document by ID"""
        doc = self.db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user document"""
        updates["updated_at"] = datetime.now()
        self.db.collection("users").document(user_id).update(updates)
        return True
    
    def set_google_calendar_id(self, user_id: str, calendar_id: str) -> bool:
        """Set Google Calendar ID for user"""
        return self.update_user(user_id, {"google_calendar_id": calendar_id})
    
    # ========== SYLLABI OPERATIONS ==========
    
    def create_syllabus(self, user_id: str, syllabus_id: str, filename: str,
                       file_type: str, file_size: int, 
                       storage_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new syllabus document
        
        Args:
            user_id: ID of user who uploaded the syllabus
            syllabus_id: Unique syllabus identifier
            filename: Original filename
            file_type: File type (pdf, docx, image)
            file_size: File size in bytes
            storage_path: Path to file in storage (if stored)
        
        Returns:
            Syllabus document data
        """
        syllabus_data = {
            "user_id": user_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "storage_path": storage_path,
            "status": "uploaded",  # uploaded, processing, processed, error
            "extracted_text": None,
            "processing_error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.db.collection("syllabi").document(syllabus_id).set(syllabus_data)
        return syllabus_data
    
    def get_syllabus(self, syllabus_id: str) -> Optional[Dict[str, Any]]:
        """Get syllabus document by ID"""
        doc = self.db.collection("syllabi").document(syllabus_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_user_syllabi(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all syllabi for a user"""
        syllabi = self.db.collection("syllabi").where("user_id", "==", user_id).get()
        return [{"id": doc.id, **doc.to_dict()} for doc in syllabi]
    
    def update_syllabus(self, syllabus_id: str, updates: Dict[str, Any]) -> bool:
        """Update syllabus document"""
        updates["updated_at"] = datetime.now()
        self.db.collection("syllabi").document(syllabus_id).update(updates)
        return True
    
    def set_syllabus_extracted_text(self, syllabus_id: str, extracted_text: str) -> bool:
        """Update syllabus with extracted text"""
        return self.update_syllabus(syllabus_id, {
            "extracted_text": extracted_text,
            "status": "processed"
        })
    
    def set_syllabus_processing_status(self, syllabus_id: str, status: str, 
                                       error: Optional[str] = None) -> bool:
        """Update syllabus processing status"""
        updates = {"status": status}
        if error:
            updates["processing_error"] = error
        return self.update_syllabus(syllabus_id, updates)
    
    # ========== EXTRACTED EVENTS OPERATIONS ==========
    
    def create_extracted_event(self, syllabus_id: str, event_data: Dict[str, Any],
                              user_id: Optional[str] = None) -> str:
        """
        Create an extracted event document
        
        Args:
            syllabus_id: ID of syllabus this event was extracted from
            event_data: Event details (title, date, time, type, etc.)
            user_id: ID of user who owns this event
        
        Returns:
            Event document ID
        """
        event_doc = {
            "syllabus_id": syllabus_id,
            "user_id": user_id,
            "title": event_data.get("title", ""),
            "description": event_data.get("description", ""),
            "event_type": event_data.get("event_type", "deadline"),  # deadline, exam, class, assignment
            "start_date": event_data.get("start_date"),
            "end_date": event_data.get("end_date"),
            "start_time": event_data.get("start_time"),
            "end_time": event_data.get("end_time"),
            "location": event_data.get("location", ""),
            "review_status": "pending",  # pending, approved, rejected
            "calendar_synced": False,
            "google_calendar_event_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Add any additional fields from event_data
        for key, value in event_data.items():
            if key not in event_doc:
                event_doc[key] = value
        
        doc_ref = self.db.collection("extracted_events").document()
        doc_ref.set(event_doc)
        return doc_ref.id
    
    def get_extracted_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get extracted event document by ID"""
        doc = self.db.collection("extracted_events").document(event_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_syllabus_events(self, syllabus_id: str) -> List[Dict[str, Any]]:
        """Get all events extracted from a syllabus"""
        events = self.db.collection("extracted_events").where("syllabus_id", "==", syllabus_id).get()
        return [{"id": doc.id, **doc.to_dict()} for doc in events]
    
    def get_user_events(self, user_id: str, review_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all events for a user
        
        Args:
            user_id: User ID
            review_status: Filter by review status (pending, approved, rejected)
        """
        query = self.db.collection("extracted_events").where("user_id", "==", user_id)
        
        if review_status:
            query = query.where("review_status", "==", review_status)
        
        events = query.get()
        return [{"id": doc.id, **doc.to_dict()} for doc in events]
    
    def get_pending_events(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all pending events for a user to review"""
        return self.get_user_events(user_id, review_status="pending")
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update extracted event document"""
        updates["updated_at"] = datetime.now()
        doc_ref = self.db.collection("extracted_events").document(event_id)
        doc_ref.update(updates)
        return True
    
    def approve_event(self, event_id: str) -> bool:
        """Mark event as approved for calendar sync"""
        return self.update_event(event_id, {"review_status": "approved"})
    
    def reject_event(self, event_id: str) -> bool:
        """Mark event as rejected"""
        return self.update_event(event_id, {"review_status": "rejected"})
    
    def mark_event_synced(self, event_id: str, google_calendar_event_id: str) -> bool:
        """Mark event as synced to Google Calendar"""
        return self.update_event(event_id, {
            "calendar_synced": True,
            "google_calendar_event_id": google_calendar_event_id
        })
    
    def batch_create_events(self, syllabus_id: str, events_list: List[Dict[str, Any]],
                           user_id: Optional[str] = None) -> List[str]:
        """
        Create multiple events in a batch operation
        
        Args:
            syllabus_id: ID of syllabus
            events_list: List of event data dictionaries
            user_id: User ID
        
        Returns:
            List of created event IDs
        """
        batch = self.db.batch()
        event_ids = []
        
        for event_data in events_list:
            event_doc = {
                "syllabus_id": syllabus_id,
                "user_id": user_id,
                "title": event_data.get("title", ""),
                "description": event_data.get("description", ""),
                "event_type": event_data.get("event_type", "deadline"),
                "start_date": event_data.get("start_date"),
                "end_date": event_data.get("end_date"),
                "start_time": event_data.get("start_time"),
                "end_time": event_data.get("end_time"),
                "location": event_data.get("location", ""),
                "review_status": "pending",
                "calendar_synced": False,
                "google_calendar_event_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Add additional fields
            for key, value in event_data.items():
                if key not in event_doc:
                    event_doc[key] = value
            
            doc_ref = self.db.collection("extracted_events").document()
            batch.set(doc_ref, event_doc)
            event_ids.append(doc_ref.id)
        
        batch.commit()
        return event_ids
    
    # ========== UTILITY METHODS ==========
    
    def delete_syllabus(self, syllabus_id: str, delete_events: bool = True) -> bool:
        """
        Delete a syllabus and optionally its associated events
        
        Args:
            syllabus_id: Syllabus ID to delete
            delete_events: If True, also delete associated events
        """
        batch = self.db.batch()
        
        if delete_events:
            # Delete associated events
            events = self.get_syllabus_events(syllabus_id)
            for event in events:
                event_doc = self.db.collection("extracted_events").document(event["id"])
                batch.delete(event_doc)
        
        # Delete syllabus
        batch.delete(self.db.collection("syllabi").document(syllabus_id))
        batch.commit()
        return True

