# MY Aesthetics Brow Studio API Documentation

## 📌 Endpoints Overview

| Endpoint                | GET                                    | POST                | PATCH                | DELETE                       |
| ----------------------- | -------------------------------------- | ------------------- | -------------------- | ---------------------------- |
| `/auth`                 | Get the current user credentials       | -                   | -                    | -                            |
| `/auth/all-admin`       | Get the credentials of admin           | -                   | -                    | -                            |
| `/auth/signin`          | -                                      | Get access token    | -                    | -                            |
| `/auth/update-password` | -                                      | -                   | Update the password  | -                            |
| `/auth/signup`          | -                                      | Create account      | -                    | -                            |
| `/auth/delete-admin`    | -                                      | -                   | -                    | Delete the admin credentials |
| `/auth/signout`         | -                                      | Remove access token | -                    | Delete appointment           |
| `/user`                 | Get the current customer info          | -                   | Update customer info | -                            |
| `/admin`                | Get the current admin info             | -                   | Update admin info    | -                            |
| `/admin/all`            | Get all admin info                     | -                   | -                    | -                            |
| `/service`              | Get all service info                   | Create service      | Update service       | Delete service               |
| `/aesthetician`         | Get all aesthetician info              | Create aesthetician | Update aesthetician  | Delete aesthetician          |
| `/branch`               | Get all branch info                    | Create branch       | Update branch        | Delete branch                |
| `/voucher`              | Get all voucher info                   | Create voucher      | Update voucher       | Delete voucher               |
| `/appointment`          | Get the current customer's appointment | Create appointment  | Update appointment   | Delete appointment           |
| `/appointment/all`      | Get all appointments                   | -                   | -                    | -                            |

---

## 📌 `/voucher`

### ✅ Roles & Access

| Method | Who Can Access         | Description     |
| ------ | ---------------------- | --------------- |
| POST   | Admin, Owner           | Create voucher  |
| GET    | Customer, Admin, Owner | Get all voucher |
| PATCH  | Admin, Owner           | Update voucher  |
| DELETE | Admin, Owner           | Delete voucher  |

### 📝 POST `/voucher` – Request Body

| Field             | Type | Required | Description             |
| ----------------- | ---- | -------- | ----------------------- |
| `discount_amount` | int  | ✅       | Discount amount in peso |
| `quantity`        | int  | ✅       | Number of voucher       |
| `expires_at`      | date | ✅       | Expires at              |

### 📤 Example Request

```json
{
  "discount_amount": 100,
  "quantity": 5,
  "expires_at": "2025-08-02T12:30:00Z"
}
```

### 📝 PATCH `/voucher` – Request Body

| Field          | Type   | Required | Description  |
| -------------- | ------ | -------- | ------------ |
| `voucher_code` | string | ✅       | Voucher code |

### 📤 Example Request

```json
{
  "voucher_code": "aesthetic-OP12"
}
```

### 📝 DELETE `/voucher` – Request Body

| Field          | Type   | Required | Description  |
| -------------- | ------ | -------- | ------------ |
| `voucher_code` | string | ✅       | Voucher code |

### 📤 Example Request

```json
{
  "voucher_code": "aesthetic-OP12"
}
```

---

## 📌 `/appointment`

### ✅ Roles & Access

| Method | Who Can Access         | Description                          |
| ------ | ---------------------- | ------------------------------------ |
| POST   | Customer, Admin, Owner | Create appointment (self or walk-in) |
| GET    | Customer               | Get current or past appointment      |
| PATCH  | Customer, Admin, Owner | Update appointment status            |
| DELETE | Admin, Owner           | Delete appointment                   |

## 📌 `/appointment/all`

### ✅ Roles & Access

| Method | Who Can Access | Description         |
| ------ | -------------- | ------------------- |
| GET    | Admin, Owner   | Get all appointment |

### 📝 POST `/appointment` – Request Body for Walk-In

| Field            | Type    | Required | Description                          |
| ---------------- | ------- | -------- | ------------------------------------ |
| `first_name`     | string  | ✅       | Walk in customer's first name        |
| `last_name`      | string  | ✅       | Walk in customer's last name         |
| `middle_initial` | string  | ✅       | Walk in customer's middle initial    |
| `sex`            | string  | ✅       | `male`, `female`, `other`            |
| `phone_number`   | string  | ✅       | Phone number of the walk in customer |
| `branch_id`      | string  | ✅       | ID of the branch                     |
| `voucher_code`   | string  | ❌       | Voucher code if applicable           |
| `payment_method` | string  | ✅       | `cash`, `e_wallet`, `bank_transfer`  |
| `is_walk_in`     | boolean | ✅       | Whether the customer is walk-in      |

### 📤 Example Request

```json
{
  "is_walk_in": true,
  "first_name": "Hello",
  "last_name": "World",
  "middle_initial": "M",
  "sex": "female",
  "phone_number": "0932123312",
  "voucher_code": "aesthetics-KL06",
  "payment_method": "cash",
  "branch_id": "5a29ff27-881e-45cd-900b-e3e6d9aa0785",
  "service_id": "e12b7e97-8c22-486d-96d1-f6351549c5af",
  "aesthetician_id": "c042385c-61ba-4e3d-9b72-fc771146e985"
}
```

### 📝 POST `/appointment` – Request Body for Online Customer

| Field             | Type    | Required | Description                         |
| ----------------- | ------- | -------- | ----------------------------------- |
| `service_id`      | string  | ✅       | ID of the service booked            |
| `aesthetician_id` | string  | ✅       | ID of the aesthetician              |
| `branch_id`       | string  | ✅       | ID of the branch                    |
| `voucher_code`    | string  | ❌       | Voucher code if applicable          |
| `payment_method`  | string  | ✅       | `cash`, `e_wallet`, `bank_transfer` |
| `is_walk_in`      | boolean | ✅       | Whether the customer is walk-in     |

### 📤 Example Request

```json
{
  "voucher_code": "aesthetics-KL06",
  "payment_method": "cash",
  "branch_id": "5a29ff27-881e-45cd-900b-e3e6d9aa0785",
  "service_id": "e12b7e97-8c22-486d-96d1-f6351549c5af",
  "aesthetician_id": "c042385c-61ba-4e3d-9b72-fc771146e985"
}
```
