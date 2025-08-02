# Appointment API Documentation

## 📌 Endpoints Overview

| Endpoint           | GET                   | POST               | PATCH              | DELETE                    |
| ------------------ | --------------------- | ------------------ | ------------------ | ------------------------- |
| `/appointment`     | Get all appointments  | Create appointment | -                  | -                         |
| `/appointment/:id` | Get appointment by ID | -                  | Update appointment | Cancel/Delete appointment |

---

## 📌 `/appointment`

### ✅ Roles & Access

| Method | Who Can Access | Description              |
| ------ | -------------- | ------------------------ |
| POST   | User, Walk-in  | Create a new appointment |
| GET    | Admin, User    | Get all appointments     |

### 📝 POST `/appointment` – Request Body

| Field             | Type    | Required | Description                         |
| ----------------- | ------- | -------- | ----------------------------------- |
| `service_id`      | string  | ✅       | ID of the service booked            |
| `aesthetician_id` | string  | ✅       | ID of the aesthetician              |
| `voucher_code`    | string  | ❌       | Voucher code if applicable          |
| `payment_method`  | string  | ✅       | `cash`, `e_wallet`, `bank_transfer` |
| `is_walk_in`      | boolean | ✅       | Whether the customer is walk-in     |

### 📤 Example Request

```json
{
  "service_id": "123",
  "aesthetician_id": "456",
  "voucher_code": "DISCOUNT10",
  "payment_method": "e_wallet",
  "is_walk_in": true
}
```
