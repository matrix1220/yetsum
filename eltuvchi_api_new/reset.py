import os
import os.path



from dbscheme import Base
from config import engine, sessionmaker
#engine.reflect()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = sessionmaker()


session.add_all([matrix_1220s, shahzods])
session.commit()

session.close()