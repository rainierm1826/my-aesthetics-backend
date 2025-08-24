from .base_crud_controller import BaseCRUDController
from ..models.voucher_model import Voucher

class VoucherController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Voucher,
            id_field="voucher_code",
            searchable_fields=["voucher_code"],
            required_fields=["quantity", "discount_amount","minimum_spend",  "valid_from", "valid_until", "discount_type"],
            updatable_fields=["quantity", "discount_amount","minimum_spend",  "valid_from", "valid_until", "discount_type"],
        )