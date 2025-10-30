<div align="center">

# 🚀 Quick Start Guide

### Get up and running with Pharia SDK in 2 minutes

</div>

---

## Step 1: Install

```bash
uv add git+https://github.com/Aleph-Alpha/pharia_data_sdk.git
```

## Step 2: Configure

Set your environment variables:

```bash
export PHARIA_DATA_API_BASE_URL="https://<base-url>/api/v1"
export PHARIA_API_KEY="your-api-key-here"
```

> 💡 **Tip:** Add these to your `~/.zshrc` or `~/.bashrc` to make them permanent.

## Step 3: Run an Example

```bash
cd examples
python basic_usage.py
```

## Step 4: Write Your First Script

```python
import asyncio
from pharia_sdk import Client

async def main():
    # Client automatically reads environment variables
    client = Client()

    # List all stages
    stages = await client.stages.list(page=0, size=10)
    print(f"✅ Found {stages['total']} stages!")

    for stage in stages['stages']:
        print(f"  - {stage['name']}")

if __name__ == "__main__":
    asyncio.run(main())
```

Save as `my_script.py` and run:
```bash
python my_script.py
```

---

## What's Next?

- 📚 Check out [examples/](./examples/) for more advanced usage
- 📖 Read the [full README](./README.md) for detailed documentation
- 🛡️ Explore [models.py](./pharia_sdk/models.py) for all available types

---

<div align="center">

**You're all set!** 🎉

[Back to README](./README.md)

</div>
