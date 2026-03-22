from ecom_shop_shared_lib.models import OutboxMixin

from db.session import Base


class Outbox(Base, OutboxMixin):
    __tablename__ = "outbox"
