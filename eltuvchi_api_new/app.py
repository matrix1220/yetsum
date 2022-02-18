import uvicorn
from main import application
#from config import debug
uvicorn.run(application, host='0.0.0.0', port=8081, log_level='debug')