from abc import ABC, abstractmethod


class EventsHandler(ABC):
    """Interface for class that is able to handle specified GUI events."""

    @abstractmethod
    def load_model_handle(self, data_path):
        """Get data source from user (e.g. directory path, file path, URL, ...)"""
        pass

    @abstractmethod
    def change_slice_handle(self, n, plain):
        """Handle request to change displayed slice to n-th in specified plain."""
        pass

    @abstractmethod
    def histogram_mode_handle(self, mode):
        """Change histogram displaying mode (e.g. show/display)"""
        pass

    @abstractmethod
    def histogram_changed_handle(self, histogram, plain):
        """Handle info about histogram windowing parameters changing in specified plain."""
        pass

    @abstractmethod
    def roi_mode_handle(self, mode):
        """Change roi displaying mode (e.g. show/display)"""
        pass

    @abstractmethod
    def roi_changed_handle(self, roi, plain):
        """Handle info about region-of-interest changing in specified plain."""
        pass

    @abstractmethod
    def quit_app_handle(self):
        """Exit app."""
        pass
