import logging
import sys
import structlog

def setup_structlog():
    """Setup structlog for logging"""
    logging.basicConfig(
        format="%(message)s",  # structlog remplace ce format
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),             
            structlog.stdlib.add_log_level,                           
            structlog.processors.StackInfoRenderer(),                
            structlog.processors.format_exc_info,                    
            structlog.processors.JSONRenderer()                       
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
