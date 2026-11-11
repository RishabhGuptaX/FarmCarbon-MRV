"""Interface shared by demo and Earth Engine satellite providers."""
from abc import ABC, abstractmethod

class SatelliteProvider(ABC):
    mode = "unknown"
    @abstractmethod
    def get_observations(self, farm, start_date, end_date, cloud_threshold):
        raise NotImplementedError
