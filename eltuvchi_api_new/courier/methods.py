from dbscheme import Courier, Order, Cooperator, Offer, Districts
from dbscheme import Regions, OrderHistory, Product
from dbscheme import OrderView, ProductStore
from config import bot, statuses


from sqlalchemy import and_, or_
from sqlalchemy.sql import func

import time, decimal, datetime
