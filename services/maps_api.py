import requests
from typing import List, Dict, Optional
from models.models import TennisCourt
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MapsService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the maps service with an optional API key."""
        self.api_key = api_key or current_app.config.get('MAPS_API_KEY')

    def get_nearby_tennis_courts(self, latitude: float, longitude: float, radius_km: float = 10) -> List[Dict]:
        """
        Find tennis courts near a given location.
        
        Args:
            latitude (float): User's latitude
            longitude (float): User's longitude
            radius_km (float): Search radius in kilometers
            
        Returns:
            List[Dict]: List of tennis courts with their details
        """
        try:
            # For demonstration, we'll return courts from our database
            # In a real implementation, this would make an API call to a mapping service
            
            # TODO: Implement actual distance calculation and filtering
            courts = TennisCourt.query.all()
            
            nearby_courts = []
            for court in courts:
                # Simple distance calculation (this should be replaced with proper geolocation)
                distance = self._calculate_distance(
                    latitude, longitude,
                    court.latitude, court.longitude
                )
                
                if distance <= radius_km:
                    nearby_courts.append({
                        'id': court.id,
                        'name': court.name,
                        'address': court.address,
                        'latitude': court.latitude,
                        'longitude': court.longitude,
                        'price_per_hour': court.price_per_hour,
                        'distance': round(distance, 2)
                    })
            
            return sorted(nearby_courts, key=lambda x: x['distance'])
            
        except Exception as e:
            logger.error(f"Error finding nearby tennis courts: {str(e)}")
            return []

    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Convert an address to coordinates (latitude, longitude).
        
        Args:
            address (str): The address to geocode
            
        Returns:
            Optional[Dict[str, float]]: Dictionary with 'lat' and 'lng' if successful
        """
        try:
            # TODO: Implement actual geocoding using a service like Google Maps
            # For now, return None to indicate geocoding is not implemented
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            return None

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points using the Haversine formula.
        
        Args:
            lat1 (float): Latitude of first point
            lon1 (float): Longitude of first point
            lat2 (float): Latitude of second point
            lon2 (float): Longitude of second point
            
        Returns:
            float: Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert coordinates to radians
        lat1, lon1 = radians(lat1), radians(lon1)
        lat2, lon2 = radians(lat2), radians(lon2)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth's radius in kilometers
        R = 6371
        
        return R * c

def get_maps_service() -> MapsService:
    """Factory function to create a MapsService instance."""
    return MapsService()
