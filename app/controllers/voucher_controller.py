from .base_crud_controller import BaseCRUDController
from ..models.voucher_model import Voucher

class VoucherController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Voucher,
            id_field="voucher_code",
            required_fields=["quantity", "discount_amount", "expires_at"],
            updatable_fields=["quantity", "discount_amount", "expires_at"],
        )