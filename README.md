Django backend assignment APIs related to a product listing system.

### API endpoints:
Authentication and AES encryption is implemented.

 #### User Authentication & Account

| Method | Endpoint                          | Description                          |
|--------|-----------------------------------|--------------------------------------|
| POST   | `/register/`                      | Register a new user                  |
| GET    | `/activate/<uid>/<token>/`        | Activate user via email link         |
| POST   | `/login/`                         | Log in and get JWT tokens            |
| POST   | `/logout/`                        | Log out and blacklist refresh token  |


⸻

 #### Categories

| Method | Endpoint              | Description               |
|--------|-----------------------|---------------------------|
| GET    | `/categories/`        | List all categories       |
| POST   | `/categories/`        | Create a new category     |
| GET    | `/categories/{id}/`   | Get category by ID        |
| PUT    | `/categories/{id}/`   | Update category by ID     |
| PATCH  | `/categories/{id}/`   | Partially update category |
| DELETE | `/categories/{id}/`   | Delete category by ID     |


⸻

 #### Products

| Method | Endpoint                          | Description                                 |
|--------|-----------------------------------|---------------------------------------------|
| GET    | `/products/`                      | List products (filtered by role)            |
| POST   | `/products/`                      | Create new product (with video upload)      |
| GET    | `/products/{id}/`                 | Retrieve product by ID                      |
| PUT    | `/products/{id}/`                 | Update product by ID                        |
| PATCH  | `/products/{id}/`                 | Partially update product by ID              |
| DELETE | `/products/{id}/`                 | Delete product by ID                        |
| POST   | `/products/{id}/approve/`         | Approve a product                           |
| POST   | `/products/{id}/reject/`          | Reject a product                            |
| GET    | `/products/history/`              | Get current user’s product upload history   |


⸻

 #### Orders

| Method | Endpoint              | Description                                      |
|--------|-----------------------|--------------------------------------------------|
| GET    | `/orders/`            | List orders (all or user-specific based on role)|
| POST   | `/orders/`            | Create a new order (EndUser only)               |
| GET    | `/orders/{id}/`       | Retrieve order by ID                            |
| PUT    | `/orders/{id}/`       | Update order by ID                              |
| PATCH  | `/orders/{id}/`       | Partially update order                          |
| DELETE | `/orders/{id}/`       | Delete order by ID                              |


##  TODO/Still lacks

-  **Integrated testing with frontend**  
  Some APIs return incorrect data when triggered from the frontend. Need thorough testing and fixes.

-  **Dockerize the system using Docker Compose**  
  services should include:
    - Django server  
    - Celery worker  
    - Redis server  

-  **Add more detailed documentation**  
  Including API examples, expected responses, and error codes.

-  **video upload progress bar**  

---
  
**Note:** For frontend part, I've taken assistance from AI.