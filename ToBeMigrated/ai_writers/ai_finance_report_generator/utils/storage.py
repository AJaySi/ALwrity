"""
Storage Module for AI Finance Report Generator

This module handles the persistence of user preferences and recent reports using JSON files.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class StorageManager:
    """Manages storage operations for user preferences and recent reports."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the storage manager.
        
        Args:
            base_dir (Optional[str]): Base directory for storage files
        """
        if base_dir is None:
            # Use user's home directory by default
            self.base_dir = Path.home() / ".ai_finance"
        else:
            self.base_dir = Path(base_dir)
            
        # Create storage directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Define file paths
        self.prefs_file = self.base_dir / "preferences.json"
        self.reports_file = self.base_dir / "recent_reports.json"
        
        # Initialize files if they don't exist
        self._initialize_storage()
    
    def _initialize_storage(self) -> None:
        """Initialize storage files if they don't exist."""
        if not self.prefs_file.exists():
            self._save_preferences({})
            
        if not self.reports_file.exists():
            self._save_reports([])
    
    def _save_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Save user preferences to file.
        
        Args:
            preferences (Dict[str, Any]): User preferences to save
        """
        with open(self.prefs_file, 'w') as f:
            json.dump(preferences, f, indent=4)
    
    def _load_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences from file.
        
        Returns:
            Dict[str, Any]: User preferences
        """
        try:
            with open(self.prefs_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_reports(self, reports: List[Dict[str, Any]]) -> None:
        """
        Save recent reports to file.
        
        Args:
            reports (List[Dict[str, Any]]): Recent reports to save
        """
        with open(self.reports_file, 'w') as f:
            json.dump(reports, f, indent=4)
    
    def _load_reports(self) -> List[Dict[str, Any]]:
        """
        Load recent reports from file.
        
        Returns:
            List[Dict[str, Any]]: Recent reports
        """
        try:
            with open(self.reports_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Save user preferences.
        
        Args:
            preferences (Dict[str, Any]): User preferences to save
        """
        self._save_preferences(preferences)
    
    def load_user_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences.
        
        Returns:
            Dict[str, Any]: User preferences
        """
        return self._load_preferences()
    
    def save_recent_reports(self, reports: List[Dict[str, Any]]) -> None:
        """
        Save recent reports.
        
        Args:
            reports (List[Dict[str, Any]]): Recent reports to save
        """
        # Convert datetime objects to ISO format strings
        serialized_reports = []
        for report in reports:
            serialized_report = report.copy()
            if isinstance(report.get('timestamp'), datetime):
                serialized_report['timestamp'] = report['timestamp'].isoformat()
            serialized_reports.append(serialized_report)
        
        self._save_reports(serialized_reports)
    
    def load_recent_reports(self) -> List[Dict[str, Any]]:
        """
        Load recent reports.
        
        Returns:
            List[Dict[str, Any]]: Recent reports with datetime objects
        """
        reports = self._load_reports()
        
        # Convert ISO format strings back to datetime objects
        for report in reports:
            if isinstance(report.get('timestamp'), str):
                report['timestamp'] = datetime.fromisoformat(report['timestamp'])
        
        return reports
    
    def clear_storage(self) -> None:
        """Clear all stored data."""
        self._save_preferences({})
        self._save_reports([])
    
    def backup_storage(self, backup_dir: Optional[str] = None) -> None:
        """
        Create a backup of the storage files.
        
        Args:
            backup_dir (Optional[str]): Directory to store backup files
        """
        if backup_dir is None:
            backup_dir = self.base_dir / "backups"
        else:
            backup_dir = Path(backup_dir)
            
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup preferences
        if self.prefs_file.exists():
            backup_prefs = backup_dir / f"preferences_{timestamp}.json"
            with open(self.prefs_file, 'r') as src, open(backup_prefs, 'w') as dst:
                dst.write(src.read())
        
        # Backup reports
        if self.reports_file.exists():
            backup_reports = backup_dir / f"recent_reports_{timestamp}.json"
            with open(self.reports_file, 'r') as src, open(backup_reports, 'w') as dst:
                dst.write(src.read())
    
    def restore_from_backup(self, backup_file: str) -> None:
        """
        Restore storage from a backup file.
        
        Args:
            backup_file (str): Path to the backup file
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Determine which type of backup file it is
        if "preferences" in backup_path.name:
            with open(backup_path, 'r') as src, open(self.prefs_file, 'w') as dst:
                dst.write(src.read())
        elif "recent_reports" in backup_path.name:
            with open(backup_path, 'r') as src, open(self.reports_file, 'w') as dst:
                dst.write(src.read())
        else:
            raise ValueError(f"Unknown backup file type: {backup_file}")

def get_storage_manager(base_dir: Optional[str] = None) -> StorageManager:
    """
    Get a storage manager instance.
    
    Args:
        base_dir (Optional[str]): Base directory for storage files
        
    Returns:
        StorageManager: Storage manager instance
    """
    return StorageManager(base_dir) 