
# Full Stack Application Project
a
## Project Overview

This project is a full-stack applicatiaaon built using a **Flask** backend and a **React** frontend. It demonstrates the integration of a powerful backend framework with a dynamic and interactive frontend, showcasing key features such as CRUD actions, relationships between models, client-side routing, and data validation. 

### Major Learning Goals
1. **Flask API Backend with React Frontend**:
   - The backend is built using Flask, handling data processing and API endpoint management, while React is used for the frontend, enabling a smooth and user-friendly interface.
   
2. **Database Models**:
   - Implement at least three models with the following relationships:
     - Two **one-to-many** relationships.
     - One **many-to-many** relationship with an additional user-submittable attribute (not just foreign keys).

3. **CRUD Actions**:
   - Full CRUD (Create, Read, Update, Delete) operations for at least one resource.
   - Create and read actions for all other resources.

4. **Client-Side Features**:
   - Use **React Router** for client-side routing with at least three different routes, allowing seamless navigation via a navigation bar or other UI elements.

5. **Forms and Validation**:
   - Use **Formik** for form handling with appropriate validation rules, including:
     - At least one **data type validation**.
     - At least one **string/number format validation**.

6. **Frontend-Backend Integration**:
   - Connect the frontend and backend using `fetch()` for data retrieval and submission.

## Project Features

1. **CRUD Operations**:
   - Manage resources such as users, posts, or products with full CRUD actions for at least one model.
   
2. **Relationship Management**:
   - Use of both one-to-many and many-to-many relationships to manage interconnected data.

3. **Routing and Navigation**:
   - Provide client-side routing with at least three routes (e.g., Home, Create, Details), ensuring easy navigation.

4. **Validation**:
   - Implement validation on all user inputs using Formik, ensuring data integrity.

## Project Prerequisites and Requirements
1. **Python 3.8+**
2. **Node.js and npm**
3. **VS Code** or another IDE for development

## Setting up the Project

#### 1. Clone this repository:
   ```bash
   git@github.com:Kenedy4/SecLink-Kenya.git
   ```
   ```
   Here is the live link to the system: []
   ```

#### 2. Navigate to the project directory:
   ```bash
   cd seclinkkenya
   ```

#### 3. Set up the backend virtual environment and install dependencies:
   ```bash
   pipenv install && pipenv shell
   ```

#### 4. Navigate to the frontend directory and install dependencies:
   ```bash
   cd client
   npm install
   ```

#### 5. Running the application:
   - Backend: 
     ```bash
     python server/app.py
     ```
   - Frontend:
     ```bash
     python client npm start
     ```

#### 6. Database Setup and Migration:
   - Initialize the database:
     ```bash
     flask db init
     flask db migrate -m "Initial migration"
     flask db upgrade
     ```

#### 7. Seeding the Database:
   ```bash
   python server/seed.py
   ```

## System Functionalities:
-- This is a school management system that allows teachers to create accounts and start managing clases, students as well as sharing important notifications with the parants. Similarly, it anables them to upload learning materails and update classs and students detals.
-- On the other hand, a parent can also create accounts with the system and they will be able to see the student information. Consequently, they can also download the learning materails.

## License

This project is licensed under the MIT License.
