Service Layer Guidelines

Overview
- The API has adopted a bulk-at-root convention for all create operations. This impacts service design and how routers call services.

Rules
- Do not add or reintroduce per-item create methods in services for standard resources.
- Provide create methods that accept bulk wrappers (1..N), e.g. create_vehicles, create_pipelines.
- Routers should accept the bulk wrapper at POST /{resource} and call the create service method.
- Scenes currently remain single-create; follow existing pattern for that router/service only.

Why
- One canonical create semantics (1..N) simplifies routers and client code.
- Reduces duplicate logic and lowers maintenance surface (single vs bulk).

References
- Routers: api/app/routers/* (POST / endpoints use bulk wrappers)
- Clients: Portal services wrap single-item creates and fetch by ID when needed.
