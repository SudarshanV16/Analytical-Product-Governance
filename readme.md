## 🏗️ Architecture: Provider Pattern & Mocking
To ensure this governance hub is platform-agnostic, metadata ingestion is handled via an Object-Oriented Provider Pattern.
- `BaseBIExtractor` defines the contract.
- Local development is powered by `MockBIExtractor` utilizing the `Faker` library. It dynamically generates deterministic, relational metadata (Spaces, Apps, Users, Role Assignments) to simulate a multi-platform enterprise environment (e.g., Power BI and Qlik) without requiring live API keys.