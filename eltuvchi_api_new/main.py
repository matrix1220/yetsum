
from starlette.applications import Starlette

import courier
import priviliged

routes = [*courier.routes, *priviliged.routes]



application = Starlette(
	routes=routes,
)

