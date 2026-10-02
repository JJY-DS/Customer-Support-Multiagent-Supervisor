# 🛒 ShopSmart Customer Support Multi-Agent System

> An intelligent, multi-agent customer support pipeline powered by LangGraph, GPT-5-mini, and RAG — featuring supervisor routing, specialist sub-agents, PII redaction, and human-in-the-loop escalation.

---

## 📐 Architecture Overview

```
User Query
    │
    ▼
┌─────────────────────┐
│   Supervisor Agent  │  ← Structured output classification
│   (gpt-5-mini)      │    Routes to the right specialist
└─────────┬───────────┘
          │
    ┌─────┴──────┬──────────────┬───────────────┐
    ▼            ▼              ▼                ▼
┌────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────────┐
│ Order  │ │ Returns │ │ Billing  │ │    Product      │
│ Agent  │ │  Agent  │ │  Agent   │ │     Agent       │
└────────┘ └─────────┘ └──────────┘ └─────────────────┘
    │            │              │                │
    └────────────┴──────────────┴────────────────┘
                          │
                    ┌─────▼──────┐
                    │  Formatter │  ← Final response shaping
                    └─────┬──────┘
                          │
               ┌──────────▼──────────┐
               │  Escalation Handler │  ← HITL interrupt + resume
               └─────────────────────┘
```

---

## 🧩 System Components

### Graph Nodes (8 total)
| Node | Role |
|---|---|
| `supervisor` | Classifies intent and routes queries |
| `order_handler` | Handles order status, tracking, cancellations |
| `returns_handler` | Manages return requests and refund eligibility |
| `billing_handler` | Resolves billing disputes and payment questions |
| `product_handler` | Answers product specs, availability, and FAQs |
| `escalation` | Triggers human-in-the-loop when confidence is low |
| `formatter` | Shapes final response for the end user |
| *(entry node)* | Entry point / state initializer |

### Specialist Sub-Agents (4)
- **Order Agent** — Checks order status, delivery tracking, and cancellations
- **Returns Agent** — Validates return windows and initiates refunds
- **Billing Agent** — Resolves payment issues and disputes
- **Product Agent** — Looks up specs, FAQs, and availability

---

## 🛠️ Tools & Infrastructure

| # | Tool | Description |
|---|---|---|
| 1 | `get_order_status` | Fetches order info by order ID |
| 2 | `initiate_return` | Starts return workflow |
| 3 | `check_return_eligibility` | Validates return window |
| 4 | `get_billing_info` | Retrieves billing records |
| 5 | `dispute_charge` | Flags a charge for review |
| 6 | `search_products` | Semantic product search via FAISS |
| 7 | `get_product_faq` | Retrieves RAG-indexed FAQ chunks |
| 8 | `lookup_policy` | FAISS + semantic search over policy docs |
| 9 | `redact_pii` | Regex + DB-driven PII scrubbing |
| 10 | `escalate_to_human` | Triggers HITL interrupt |

---

## 🔍 RAG Pipeline

- **Embedding Model:** `text-embedding-3-small`
- **Vector Store:** FAISS (local, in-memory)
- **Chunks Indexed:** 9 policy/FAQ chunks
- **Policy Domains Covered:** Return, Shipping, Billing, Escalation
- **Policy Size:** 2,974 characters

Deterministic Quick-Answer mode bypasses the LLM entirely for high-confidence policy lookups — reducing latency and cost.

---

## 🤖 LLM Configuration

| Role | Model | Settings |
|---|---|---|
| Primary (Supervisor + Specialists) | `gpt-5-mini` | Reasoning mode, no temperature |
| Secondary (Formatting + Fallback) | `gpt-4.1-mini` | `temperature=0.3` |

The supervisor uses **structured output classification** to deterministically route queries — no free-text parsing, no prompt injection surface.

---

## 🧠 Patterns Implemented

| Pattern | Description |
|---|---|
| ✅ **Supervisor Routing** | Structured output classification for intent detection |
| ✅ **Specialist Sub-Agents** | `create_agent` with domain-scoped tools per handler |
| ✅ **Deterministic Quick-Answer** | Skips LLM for simple policy lookups |
| ✅ **RAG Policy Lookup** | FAISS + semantic search over curated policy chunks |
| ✅ **PII Redaction** | Regex + database-driven before any LLM call |
| ✅ **HITL Escalation** | Interrupt + command resume for human handoff |
| ✅ **Thread Memory** | `InMemorySaver` for within-session context |
| ✅ **Cross-Session Store** | `InMemoryStore` for persistent user state |

---

## 📦 Data

| Entity | Count | Details |
|---|---|---|
| Customers | 10 | Bronze / Silver / Platinum tiers |
| Orders | 100 | Delivered, In-Transit, Processing, Cancelled |
| Products | 20 | With specs and FAQ entries |
| Support Tickets | 100 | 6 categories, 4 priority levels |
| Policies | 2,974 chars | Return, Shipping, Billing, Escalation |

---

## 🚀 Getting Started

### Prerequisites
```bash
python >= 3.11
langgraph
langchain-openai
faiss-cpu
```

### Installation
```bash
git clone https://github.com/your-org/shopsmart-multi-agent.git
cd shopsmart-multi-agent
pip install -r requirements.txt
```

### Environment Variables
```env
OPENAI_API_KEY=your_openai_key
```

### Run
```bash
python main.py
```

---

## 🔄 Query Flow

1. User submits a support query
2. **PII is redacted** before any LLM sees the input
3. **Supervisor** classifies intent using structured output
4. If policy-answerable → **Deterministic Quick-Answer** (no LLM)
5. Otherwise → routed to the appropriate **Specialist Sub-Agent**
6. Agent invokes relevant tools, queries RAG if needed
7. **Formatter** shapes the final user-facing response
8. If confidence is low → **Escalation** interrupts for human review

---

## 🏗️ Project Structure

```
shopsmart-multi-agent/
├── agents/
│   ├── supervisor.py        # Routing + classification
│   ├── order_agent.py
│   ├── returns_agent.py
│   ├── billing_agent.py
│   └── product_agent.py
├── tools/
│   ├── order_tools.py
│   ├── returns_tools.py
│   ├── billing_tools.py
│   ├── product_tools.py
│   ├── policy_lookup.py     # FAISS + RAG
│   └── pii_redactor.py
├── graph/
│   ├── builder.py           # LangGraph state graph
│   ├── nodes.py
│   └── edges.py
├── data/
│   ├── customers.json
│   ├── orders.json
│   ├── products.json
│   ├── tickets.json
│   └── policies.txt
├── memory/
│   ├── thread_store.py      # InMemorySaver
│   └── cross_session.py     # InMemoryStore
├── main.py
├── requirements.txt
└── README.md
```

---

## 🛡️ Safety & Compliance

- **PII Redaction** runs before every LLM call using regex patterns + a configurable deny-list database
- **Structured output routing** eliminates prompt injection risk at the supervisor layer
- **HITL escalation** ensures a human reviews edge cases before response delivery

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
