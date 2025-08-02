# MY Aesthetics Brow Studio API Documentation

## 📌 Endpoints Overview

| Endpoint                | GET                              | POST                | PATCH                | DELETE                       |
| ----------------------- | -------------------------------- | ------------------- | -------------------- | ---------------------------- |
| `/auth`                 | Get the current user credentials | -                   | -                    | -                            |
| `/auth/all-admin`       | Get the credentials of admin     | -                   | -                    | -                            |
| `/auth/signin`          | -                                | Get access token    | -                    | -                            |
| `/auth/update-password` | -                                | -                   | Update the password  | -                            |
| `/auth/signup`          | -                                | Create account      | -                    | -                            |
| `/auth/delete-admin`    | -                                | -                   | -                    | Delete the admin credentials |
| `/auth/signout`         | -                                | Remove access token | -                    | Delete appointment           |
| `/user`                 | Get the current customer info    | -                   | Update customer info | -                            |
| `/admin`                | Get the current admin info       | -                   | Update admin info    | -                            |
| `/admin/all`            | Get all admin info               | -                   | -                    | -                            |
| `/service`              | Get all service info             | Create service      | Update service       | Delete service               |
| `/aesthetician`         | Get all aesthetician info        | Create aesthetician | Update aesthetician  | Delete aesthetician          |
| `/branch`               | Get all branch info              | Create branch       | Update branch        | Delete branch                |
| `/voucher`              | Get all voucher info             | Create voucher      | Update voucher       | Delete voucher               |
| `/appointment`          | -                                | Create appointment  | Update appointment   | Delete appointment           |
| `/appointment/all`      | Get all appointments             | -                   | -                    | -                            |

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
