"""
Training Progress Callback for QLib Web Interface
Captures training metrics and updates task progress
"""
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class TrainingProgressTracker:
    """
    Track training progress and metrics during QLib training

    This class stores training metrics and can calculate progress percentages
    based on the total number of expected iterations.
    """

    def __init__(self, total_epochs:预估int = 100):
        """
        Initialize the progress tracker

        Args:
            total_epochs: Expected number of training epochs/iterations
        """
        self.total_epochs = total_epochs
        self.metrics_history: Dict[str, List[float]] = defaultdict(list)
        self.current_step = 0
        self.best_score = None
        self.best_epoch = 0

    def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """
        Log training metrics

        Args:
            metrics: Dictionary of metric names to values
            step: Current step/epoch number
        """
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1

        # Store metrics
        for name, value in metrics.items():
            self.metrics_history[name].append(value)

            # Track best score for certain metrics
            if name in ['train_score', 'valid_score', 'IC', 'Rank IC']:
                if self.best_score is None or value > self.best_score:
                    self.best_score = value
                    self.best_epoch = self.current_step

        logger.debug(f"Step {self.current_step}: {metrics}")

    def get_progress_percentage(self) -> float:
        """
        Calculate current progress as a percentage

        Returns:
            Progress percentage (0-100)
        """
        if self.total_epochs <= 0:
            return 50.0  # Default to 50% if we don't know total

        progress = min(100.0, (self.current_step / self.total_epochs) * 100)
        return progress

    def get_metrics_history(self) -> Dict[str, List[float]]:
        """
        Get all recorded metrics history

        Returns:
            Dictionary of metric names to their value history
        """
        return dict(self.metrics_history)

    def get_current_metrics(self) -> Dict[str, float]:
        """
        Get the latest metrics

        Returns:
            Dictionary of latest metric values
        """
        current = {}
        for name, values in self.metrics_history.items():
            if values:
                current[name] = values[-1]
        return current

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of training progress

        Returns:
            Summary dictionary with key statistics
        """
        summary = {
            'current_step': self.current_step,
            'total_epochs': self.total_epochs,
            'progress': self.get_progress_percentage(),
            'best_score': self.best_score,
            'best_epoch': self.best_epoch,
            'metrics_count': len(self.metrics_history)
        }
        return summary


class TrainingProgressCallback:
    """
    Callback class that integrates with QLib's R.log_metrics

    This class can be used to capture metrics logged during QLib training
    and update a web task object with progress information.
    """

    def __init__(self, task=None, total_epochs= 100):
        """
        Initialize the callback

        Args:
            task: Web task object to update with progress
            total_epochs: Expected number of training epochs
        """
        self.task = task
        self.tracker = TrainingProgressTracker(total_epochs)

    def log(self, metrics: Dict[str, float], step: int = None):
        """
        Log metrics and update task progress

        Args:
            metrics: Dictionary of metric names to values
            step: Current step/epoch number
        """
        self.tracker.log_metrics(metrics, step)

        if self.task:
            progress = self.tracker.get_progress_percentage()
            current_metrics = self.tracker.get_current_metrics()

            # Create a meaningful message
            message_parts = []
            if 'train_loss' in current_metrics:
                message_parts.append(f"Loss: {current_metrics['train_loss']:.4f}")
            if 'valid_score' in current_metrics:
                message_parts.append(f"Score: {current_metrics['valid_score']:.4f}")

            if message_parts:
                message = f"Epoch {self.tracker.current_step} - {', '.join(message_parts)}"
            else:
                message = f"Epoch {self.tracker.current_step}"

            self.task.update_progress(progress, message)

    def get_metrics_history(self) -> Dict[str, List[float]]:
        """
        Get the complete metrics history

        Returns:
            Dictionary of metric names to value lists
        """
        return self.tracker.get_metrics_history()

    def get_final_results(self) -> Dict[str, Any]:
        """
        Get final training results formatted for web display

        Returns:
            Dictionary with training history and summary
        """
        history = self.get_metrics_history()

        # Normalize metric names for frontend
        normalized_history = {}
        for key, values in history.items():
            # Map various metric names to standard names
            if 'train' in key and 'loss' in key:
                normalized_history.setdefault('train_loss', []).extend(values)
            elif 'valid' in key and 'loss' in key:
                normalized_history.setdefault('valid_loss', []).extend(values)
            elif 'train' in key and 'score' in key:
                normalized_history.setdefault('train_score', []).extend(values)
            elif 'valid' in key and 'score' in key:
                normalized_history.setdefault('valid_score', []).extend(values)
            else:
                # Keep original name for other metrics
                normalized_history[key] = values

        return {
            'training_history': normalized_history,
            'summary': self.tracker.get_summary(),
            'current_metrics': self.tracker.get_current_metrics()
        }


def parse_lightgbm_metrics(evals_result: Dict[str, Any]) -> Dict[str, List[float]]:
    """
    Parse LightGBM evaluation results into a standardized format

    Args:
        evals_result: Raw evaluation results from LightGBM callbacks

    Returns:
        Dictionary with parsed metrics history
    """
    metrics = {'epochs': [], 'train_loss': [], 'valid_loss': [], 'train_score': [], 'valid_score': []}

    if not evals_result:
        return metrics

    # Determine max number of steps
    max_steps = 0
    for dataset_metrics in evals_result.values():
        for metric_values in dataset_metrics.values():
            if isinstance(metric_values, (list, tuple)):
                max_steps = max(max_steps, len(metric_values))

    # Extract metrics
    for epoch in range(max_steps):
        metrics['epochs'].append(epoch + 1)

        for dataset_name, dataset_metrics in evals_result.items():
            if not isinstance(dataset_metrics, dict):
                continue

            for metric_name, metric_values in dataset_metrics.items():
                if not isinstance(metric_values, (list, tuple)) or epoch >= len(metric_values):
                    continue

                value = metric_values[epoch]

                # Map LightGBM metric names to standard names
                key = f"{metric_name}_{dataset_name}".replace('@', '_')

                if 'l1' in metric_name.lower() or 'l2' in metric_name.lower():
                    # Loss metric
                    if 'train' in dataset_name.lower():
                        metrics['train_loss'].append(value)
                    else:
                        metrics['valid_loss'].append(value)
                elif 'score' in metric_name.lower() or 'ic' in metric_name.lower():
                    # Score metric
                    if 'train' in dataset_name.lower():
                        metrics['train_score'].append(value)
                    else:
                        metrics['valid_score'].append(value)

    # Fill missing values with last known value
    for key in ['train_loss', 'valid_loss', 'train_score', 'valid_score']:
        while len(metrics[key]) < len(metrics['epochs']):
            if metrics[key]:
                metrics[key].append(metrics[key][-1])
            else:
                metrics[key].append(0.0)

    return metrics
