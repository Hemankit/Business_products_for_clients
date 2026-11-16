# Business Products for Clients

This repository hosts a collection of AI-driven business automation products that are
delivered to multiple clients from a single, shared codebase. Each product is built on
the same architectural foundation, so adding a new product or onboarding a new client
means composing existing building blocks rather than writing new infrastructure.

## Repository Layout

```
core/          Shared domain-agnostic services used by every product
integrations/  Pluggable connectors to external systems (CRM, accounting, chat, etc.)
src/products/  One directory per product, each following the same internal shape
clients/       One directory per client, each following the same config shape
database/      Shared Postgres/pgvector schema used by retrieval-style products
scripts/       Standalone utility/debug scripts (auth flows, ingestion, ad-hoc tests)
docker-compose.yml  Local Postgres + pgvector service definition
requirements.txt    Shared dependency set for all products
.env.example        Template for the environment variables every product can read
```

## Core Layer (`core/`)

Every product depends on the same small set of framework services instead of talking
to clients or external systems directly:

- **`config.py` — `ClientConfig`**: Resolves a client name to its config directory
  under `clients/` and loads/validates the client's YAML files on demand (mappings,
  integrations, permissions, routing, operations, document-processing rules).
  `get_client_id()` returns the stable `client_id` from the client's `client.yaml`,
  which is the identity used for per-client integration connections.
- **`mapping.py` — `Mapper`**: Converts a validated, canonical Pydantic model into a
  client-specific field-name payload using the client's `mappings.yaml`.
- **`policies.py` — `PolicyChecker`**: Looks up whether a given action is allowed
  outright or requires human approval, based on the client's `permissions.yaml`.
- **`exceptions.py`**: A single set of typed exceptions (`ClientConfigError`,
  `MappingError`, `IntegrationError`, `ProviderError`, `LLMExtractionError`,
  `LLMGenerationError`, `EmbeddingError`, `VectorStoreError`, `IngestionError`,
  `DocumentUnderstandingError`) shared across all products and integrations.

Because these services only know about generic concepts (a "client", a "mapping", a
"policy", an "integration"), they never need to change when a new product or client is
added — only the YAML configuration and product-specific code do.

## Integration Layer (`integrations/`)

External systems are abstracted behind a common interface so that product workflows
never depend on a specific vendor API:

- **`base.py` — `BaseIntegration`**: Abstract contract with `create_record()` and a
  generic `execute_action()` dispatcher that every integration implements.
- **`registry.py` — `IntegrationRegistry`**: Reads a client's integration config
  (`provider: ...`) and instantiates the matching integration implementation.
- **`composio.py` — `ComposioIntegration`**: Executes actions through Composio,
  giving access to real third-party tools (CRM, email, chat, etc.) via a single API.
- **`mock.py` — `MockIntegration`**: A no-op integration used for local development,
  demos, and any client/product combination that isn't wired to a live system yet.

Products ask the registry for "the integration configured for this client/action" and
call `create_record()` / `execute_action()` without knowing or caring which concrete
provider is behind it.

### Payload Adapters (`integrations/adapters/`)

Canonical product data is converted into the exact payload a destination expects by a
payload adapter, so workflows never hard-code provider field names:

- **`base.py` — `BasePayloadAdapter`**: Contract with a single `build_payload(data)`.
- **`hubspot_create_contact.py` — `HubSpotCreateContactAdapter`**: Maps canonical
  `name` / `email` / `phone` / `company` to HubSpot contact properties (`firstname`,
  `lastname`, `email`, `phone`, `company`). Unsupported fields are dropped.
- **`configurable_mapping.py` — `ConfigurableMappingAdapter`**: Renames fields using a
  client's `mappings.yaml` section for the product.
- **`identity.py` — `IdentityPayloadAdapter`**: Passes data through unchanged. Used for
  `mock` integrations that have no mapping.
- **`registry.py` — `PayloadAdapterRegistry`**: Selects an adapter in this order:
  1. a provider-specific adapter registered for `(provider, toolkit_slug, action_slug)`,
  2. a `ConfigurableMappingAdapter` when the product has a `mappings.yaml` section,
  3. an `IdentityPayloadAdapter` for the `mock` provider,
  otherwise it raises `ValueError`.

Adapter unit tests live in `integrations/adapters/tests/`.

### Provider Setup

`composio.py` reads `COMPOSIO_API_KEY` from the environment when it is imported, and it
does not call `load_dotenv()` itself. Entry points must load `.env` before importing
`integrations.registry` (the product `llm.py` modules do this on import, so import the
product's LLM step first, or export the variable in the shell).

To run a client against live HubSpot, set the integration in the client's
`integrations.yaml`:

```yaml
crm:
  provider: composio
  toolkit_slug: hubspot
  action_slug: HUBSPOT_CREATE_CONTACT
```

Set `provider: mock` to run the same workflow without calling any external system.

The Composio user a connection belongs to is the client's `client_id`, defined in
`clients/<client_name>/client.yaml` (not in `integrations.yaml`):

```yaml
client_id: demo_company
```

`ComposioIntegration` checks for an active connection before executing and raises an
`IntegrationError` if the client has not connected the toolkit.

#### Connecting a client's account

Generate a Connect Link for a client and authenticate through it:

```
PYTHONPATH=. python -u scripts/connect_composio_toolkit.py <client_name> [toolkit_slug]
```

`toolkit_slug` defaults to `hubspot`. The script prints the link, waits up to 10
minutes for the authentication to finish, then prints the connected account id. After
that, any workflow run with the same client uses that connection. Linked accounts live
in Composio, so remove test connections from the Composio dashboard when done.

### Running Workflows

Product modules import each other as `src.products.<product>...`, so run entry points
from the repository root with the root on the import path (`PYTHONPATH=.`). The
repository ships an empty `src/__init__.py` so this `src` package takes precedence over
any unrelated `src` package installed in site-packages.

## Product Structure (`src/products/<product>/`)

Every product lives in its own folder under `src/products/` and follows the same
internal shape, regardless of what the product actually does:

- **`schemas.py` / `schema.py`**: Pydantic models defining the canonical, product-specific
  data shape (the structured output the LLM step must produce and the structured input
  later pipeline stages consume).
- **`prompts.py` / `prompt.py`**: Prompt templates used to instruct the LLM for this
  product's extraction/generation step.
- **`llm.py`**: Wraps the LLM call (via `instructor`/`litellm`) that turns raw input
  (text, documents, questions) into one of the schemas above.
- **`workflow_*.py`**: The orchestration entry point for the product. It wires together
  `ClientConfig`, the product's LLM step, any product-specific business logic, the
  `IntegrationRegistry`, and `PolicyChecker` into a single callable pipeline, and
  exposes a `run_*_workflow(...)` function as its public interface.
- Optional supporting modules follow the same naming convention when a product needs
  them: `validator.py` (business-rule validation), `router.py`/`resolver.py`
  (canonical request → destination/integration decision), or, for retrieval-oriented
  products, `embeddings.py`, `ingestion.py`, `vector_store.py`, and `retriever.py`.

### Common Workflow Pipeline

Although each product's business logic differs, every `workflow_*.py` follows the same
general sequence:

1. Load the requesting client's configuration via `ClientConfig`.
2. Call the product's `llm.py` step to turn raw input into a canonical, schema-validated
   object.
3. (Optional) Run product-specific validation/routing/resolution logic against the
   client's configuration.
4. Convert the canonical object into the destination payload via
   `PayloadAdapterRegistry` (provider-specific adapter, the client's `mappings.yaml`, or
   pass-through for `mock`).
5. Resolve the destination integration for the action via `IntegrationRegistry`.
6. Check whether the action is allowed or requires approval via `PolicyChecker`.
7. Execute the integration action (or stop and return early if approval/validation is
   pending), returning a structured result describing every stage of the pipeline.

Early stops return only the stages completed so far: failed validation
(`review_required` / `incomplete`) returns before any payload, policy check, or
integration call, and `approval_required` returns the payload and policy decision
without an `integration_result`.

## Client Structure (`clients/<client_name>/`)

Every client is represented purely as configuration — no client-specific code — using
a consistent set of optional YAML files that `ClientConfig` knows how to load:

- **`client.yaml`**: The client's stable `client_id`, used as the Composio user id for
  that client's connected accounts.
- **`mappings.yaml`**: Canonical field name → client-specific field name, keyed by
  product.
- **`integrations.yaml`**: Which integration provider (`mock`, `composio`, etc.) and
  connection details back each named integration (e.g. `crm`, `accounting`, `support`,
  `operations`) for that client.
- **`permissions.yaml`**: Which `integration.action` combinations are auto-allowed
  versus requiring human approval.
- **`routing.yaml`**: Category → integration/destination rules for request-routing
  products.
- **`operations.yaml`**: Supported operations, their target integration/action, and
  their required parameters.
- **`document_processing.yaml`**: Per document-type validation/extraction rules.

A client only needs to define the files relevant to the products it uses; `ClientConfig`
raises a typed error if a required file or key is missing.

## Shared Data Layer (`database/`, `docker-compose.yml`)

Retrieval-oriented products share a single Postgres schema (`database/init.sql`) built
on the `pgvector` extension, with rows scoped per-client via a `client_id` column and
per-document chunking/metadata columns. `docker-compose.yml` spins up this Postgres
instance locally for development.

## Configuration & Dependencies

- **`.env.example`** documents every environment variable the shared layers and
  products can read (LLM provider keys, integration/API keys, vector store connection
  string, human-in-the-loop channels, orchestration/broker settings, and observability
  keys), loaded via `python-dotenv`.
- **`requirements.txt`** lists the dependency set shared by all products, grouped by
  concern: integration layer, LLM + structured extraction, retrieval, human-in-the-loop,
  orchestration, and observability/testing.
- **`scripts/`** holds standalone, non-product scripts (connector auth flows such as
  `connect_composio_toolkit.py`, ingestion smoke tests, retrieval smoke tests) used during development rather than in production
  pipelines.
