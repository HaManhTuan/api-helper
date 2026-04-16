from sqlalchemy import Column, String, Text

from app.models.base_model import BaseModel


class CommercialAuditLog(BaseModel):
    """
    Audit log for commercial configuration changes (catalog, pricing, commission).
    """

    actor_user_id = Column(String, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # e.g. service_offering, price_book_entry, commission_rule
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # create/update/deactivate/delete

    before = Column(Text, nullable=True)
    after = Column(Text, nullable=True)

