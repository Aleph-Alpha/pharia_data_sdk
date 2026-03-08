<div align="center">

# 📚 Examples

### Ready-to-run code samples for the Pharia SDK

</div>

---

## 🎯 Available Examples

### 🔰 Basic Usage
**File:** `basic_usage.py`

Get started with common operations:
- List stages, repositories, and connectors
- Fetch specific resources by ID
- List files in a stage

```bash
cd pharia/examples
python basic_usage.py
```

---

### 🚀 Creating Stages
**File:** `create_stages.py`

Comprehensive guide to creating stages with different embedding types:

| Type | Use Case |
|------|----------|
| **Simple** | No embedding, just data storage |
| **Instruct** | Custom instruction-based embeddings |
| **Semantic** | Asymmetric/symmetric semantic search |
| **VLLM** | VLLM-based embedding models |

Each example creates a stage and automatically cleans it up.

```bash
cd pharia/examples
python create_stages.py
```

---

### 🔍 Search Stores
**File:** `search_stores_usage.py`

Full search store lifecycle including the Filter DSL:
- Create search stores (semantic, instruct)
- Add documents and search with metadata filters
- Use `Filter`, `And`, `Or`, `Not`, and `ModalityCondition` for Pythonic queries

```bash
cd pharia/examples
python search_stores_usage.py
```

---

### 🛡️ Type-Safe Usage
**File:** `typed_usage.py`

Learn how to use TypedDict annotations for:
- Better IDE autocomplete
- Type checking with mypy
- Safer, more maintainable code

```bash
cd pharia/examples
python typed_usage.py
```

---

## ⚙️ Configuration

Set your credentials via environment variables:

```bash
export PHARIA_DATA_API_BASE_URL="https://<base-url>"
export PHARIA_API_KEY="your-api-key-here"
```

The client will automatically read these values. No code changes needed!

---

## ⚡ Quick Tips

- ✅ Most examples are **read-only** and safe to run
- ✅ `create_stages.py` creates resources but **auto-cleans** them
- ✅ All examples use the **staging environment** by default
- ✅ Install the SDK first: `uv sync` from `pharia/` directory

---

<div align="center">

**Learn by doing** • [Back to main README](../README.md)

</div>
