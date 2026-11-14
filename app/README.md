
# FastAPI CRUD Operations

**FastAPI CRUD operations** are the four basic actions used to manage data in a web application using Python's FastAPI framework.

### CRUD Stands For:

- **C — Create:** Add new data.
- **R — Read:** Retrieve existing data.
- **U — Update:** Modify existing data.
- **D — Delete:** Remove existing data.

## 1. CRUD Operations in FastAPI Project

| Operation | HTTP Method | Endpoint | Purpose |
|-----------|-------------|----------|---------|
| Create | `POST` | `/posts` | Create a new post |
| Read | `GET` | `/posts` | Retrieve all posts |
| Read | `GET` | `/posts/{id}` | Retrieve a particular post |
| Update | `PUT` | `/posts/{id}` | Update an existing post |
| Delete | `DELETE` | `/posts/{id}` | Delete a post |

## 2. Real-World Example

Imagine you're creating an Instagram-like application.

| User Action | CRUD | HTTP Method |
|-------------|------|-------------|
| Upload a new post | Create | `POST` |
| View someone's posts | Read | `GET` |
| Edit a post caption | Update | `PUT/PATCH` |
| Remove a post | Delete | `DELETE` |
