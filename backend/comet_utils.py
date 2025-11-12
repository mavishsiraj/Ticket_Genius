import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyTracker:
    """Dummy tracker that does nothing - used when Comet ML is not available"""
    def __getattr__(self, name):
        def method(*args, **kwargs):
            logger.debug(f"DummyTracker: {name} called with args: {args}, kwargs: {kwargs}")
            return None
        return method

# Try to initialize Comet ML, fall back to dummy tracker if it fails
try:
    from comet_ml import Experiment
    
    class CometTracker:
        """Wrapper around Comet ML Experiment for better error handling"""
        def __init__(self):
            load_dotenv()
            self.api_key = os.getenv("COMET_API_KEY")
            self.workspace = os.getenv("COMET_WORKSPACE", "default")
            self.experiment = None
            
            if not self.api_key or self.api_key.startswith("pplx-"):
                raise ValueError("Invalid or missing Comet ML API key")
            
            self._init_experiment()
        
        def _init_experiment(self):
            """Initialize the Comet ML experiment"""
            try:
                self.experiment = Experiment(
                    api_key=self.api_key,
                    project_name="ticket-genius",
                    workspace=self.workspace,
                    auto_metric_logging=True,
                    auto_param_logging=True,
                    log_code=True
                )
                logger.info("Comet ML experiment initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Comet ML: {str(e)}")
                self.experiment = None
        
        def log_metrics(self, metrics: Dict[str, Any], step: Optional[int] = None):
            """Log metrics to Comet ML"""
            if not self.experiment:
                return
            try:
                for key, value in metrics.items():
                    self.experiment.log_metric(key, value, step=step)
            except Exception as e:
                logger.error(f"Failed to log metrics: {str(e)}")
        
        def log_params(self, params: Dict[str, Any]):
            """Log parameters to Comet ML"""
            if not self.experiment:
                return
            try:
                self.experiment.log_parameters(params)
            except Exception as e:
                logger.error(f"Failed to log parameters: {str(e)}")
        
        def log_ticket(self, ticket_data: Dict[str, Any], metrics: Optional[Dict[str, Any]] = None):
            """Log ticket processing data"""
            if not self.experiment:
                return
                
            try:
                # Log ticket data as parameters
                self.log_params({
                    f"ticket_{k}": v for k, v in ticket_data.items()
                })
                
                # Log any additional metrics
                if metrics:
                    self.log_metrics(metrics)
            except Exception as e:
                logger.error(f"Failed to log ticket data: {str(e)}")
        
        def end_experiment(self):
            """End the current experiment"""
            if self.experiment:
                try:
                    self.experiment.end()
                    self.experiment = None
                except Exception as e:
                    logger.error(f"Failed to end experiment: {str(e)}")
    
    # Initialize the global tracker
    try:
        comet_tracker = CometTracker()
    except Exception as e:
        logger.warning(f"Falling back to dummy tracker: {str(e)}")
        comet_tracker = DummyTracker()

except ImportError:
    logger.warning("Comet ML not installed. Using dummy tracker.")
    comet_tracker = DummyTracker()
except Exception as e:
    logger.error(f"Error initializing Comet ML: {str(e)}. Using dummy tracker.")
    comet_tracker = DummyTracker()