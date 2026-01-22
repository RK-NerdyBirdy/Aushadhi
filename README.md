<div align="center">
  <br />
  <h1>Aushadhi</h1>
  <p>AI-Powered Pharmaceutical Inventory Management and Demand Forecasting</p>
</div>

---

## Overview

**Aushadhi** (Sanskrit: औषधि) is a comprehensive, open-source platform designed to modernize pharmaceutical supply chain management. It provides a robust inventory system with AI-powered demand forecasting to help pharmacies and warehouses optimize stock levels, reduce waste, and ensure the timely availability of medicines.

The system is built with a decoupled frontend and backend architecture, making it scalable, flexible, and easy to maintain. The frontend provides an intuitive dashboard for managing inventory, orders, and reports, while the backend handles business logic, data processing, and integration with a powerful RAG-based LLM service for intelligent forecasting.

---

## Key Features

- **Real-Time Inventory Tracking:** Manage medicines, stock levels, and batches across multiple locations (pharmacies and warehouses).
- **Order Management:** Create, process, and track purchase orders and stock transfers.
- **AI-Powered Demand Forecasting:** Utilizes a Retrieval-Augmented Generation (RAG) pipeline with a Large Language Model (LLM) to predict future medicine demand based on historical data.
- **Intelligent Alerts:** Automated notifications for low stock, expiring medicines, and unusual usage patterns.
- **Comprehensive Dashboards:** Rich data visualizations and reports for data-driven decision-making.
- **User & Organization Management:** Role-based access control for different user types (e.g., pharmacists, warehouse managers, administrators).
- **RESTful API:** A well-documented API for seamless integration with other systems.

---

## Tech Stack

### Frontend (Next.js)
- **Framework:** [Next.js](https://nextjs.org/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **UI Components:** [Shadcn/UI](https://ui.shadcn.com/)
- **Data Fetching:** [Axios](https://axios-http.com/)

### Backend (FastAPI)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Language:** [Python](https://www.python.org/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) with [Alembic](https://alembic.sqlalchemy.org/) for migrations
- **Authentication:** JWT (JSON Web Tokens)

### AI/ML Service (Python)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **LLM Engine:** [Groq](https://groq.com/)
- **Methodology:** Retrieval-Augmented Generation (RAG) for context-aware forecasting.
- **Data Retrieval:** Context built from historical usage, stock, and order data.

### Database
- **Primary:** [PostgreSQL](https://www.postgresql.org/) (assumed, compatible with SQLAlchemy)
- **Vector Store:** (Implied for RAG) A vector database like ChromaDB or FAISS could be used.

---

## Architecture

Aushadhi is designed with a service-oriented architecture:

1.  **Frontend (`/frontend`)**: A Next.js application that serves as the user-facing interface. It includes dashboards, forms, and data visualizations for interacting with the system. It communicates with the Backend API via REST endpoints.

2.  **Backend API (`/backend`)**: A FastAPI application that serves as the core of the system. It handles all business logic, including user authentication, CRUD operations for inventory and orders, and serves data to the frontend.

3.  **RAG/LLM Service (`/backend/rag_llm_service`)**: A specialized FastAPI service dedicated to AI-powered forecasting. It uses a RAG pipeline to build context from historical data stored in the database and queries a Groq-powered LLM to generate demand predictions.

---

## Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing purposes.

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [Python](https://www.python.org/) (v3.9 or later) & `pip`
- [PostgreSQL](https://www.postgresql.org/download/) server running

### Backend Setup

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `backend/` directory and populate it with database credentials and other settings. Refer to `backend/app/core/config.py`.

5.  **Run database migrations:**
    ```sh
    alembic upgrade head
    ```

6.  **Run the backend server:**
    ```sh
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Configure Environment Variables:**
    Create a `.env.local` file in the `frontend/` directory to specify the backend API URL (e.g., `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`).

4.  **Run the development server:**
    ```sh
    npm run dev
    ```
    The application will be available at `http://localhost:3000`.

---

## Project Structure

```
aushadhi/
├── backend/
│   ├── alembic/         # Database migrations
│   ├── app/             # Core FastAPI application
│   │   ├── api/         # API endpoints and dependencies
│   │   ├── crud/        # CRUD operations
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic services
│   ├── rag_llm_service/ # AI-powered forecasting service
│   └── requirements.txt
│
└── frontend/
    ├── app/             # Next.js pages and layouts
    ├── components/      # React components
    ├── hooks/           # Custom React hooks
    ├── apis/            # API communication layer
    └── package.json
```

---

## Contributors

This project was developed by the following individuals:

- **Saksham Dubey** - Frontend and Blockchain development [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SakD2006) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/saksy999/)
- **Maneet Gupta** - Backend and Agentic AI Integration [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/RK-NerdyBirdy) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maneet-gupta/)
- **Aakashdeep Singh** - Agentic AI Development & Pipelining [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/AakashdeepSinghDummy) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/AakashdeepSinghDummy)
- **Utkarsh Malaiya** - Development of ML Models and Forecaster [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/utkrshm) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/utkarsh-malaiya/)

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.