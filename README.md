# MY Aesthetics Brow Studio API Documentation

## 📌 Endpoints Overview

| Endpoint                | GET                              | POST                | PATCH               | DELETE                       |
| ----------------------- | -------------------------------- | ------------------- | ------------------- | ---------------------------- |
| `/auth`                 | Get the current user credentials | -                   | -                   | -                            |
| `/auth/all-admin`       | Get the credentials of admin     | -                   | -                   | -                            |
| `/auth/signin`          | -                                | Get access token    | -                   | -                            |
| `/auth/update-password` | -                                | -                   | Update the password | -                            |
| `/auth/signup`          | -                                | Create account      | -                   | -                            |
| `/auth/delete-admin`    | -                                | -                   | -                   | Delete the admin credentials |
| `/auth/signout`         | -                                | Remove access token | -                   | Delete appointment           |
| `/user/`                | Get the user info                | -                   | Update user info    | -                            |
| `/appointment`          | -                                | Create appointment  | Update appointment  | Delete appointment           |
| `/appointment/all`      | Get all appointments             | -                   | -                   | -                            |

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
