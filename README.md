# langchain-fodda

Official LangChain custom tool integration for the **Fodda Context Layer** — verified knowledge graphs, live supplemental market intelligence, and working Human Agents for autonomous AI reasoning models.

## Installation

```bash
pip install langchain-fodda
```

## Quickstart

```python
from langchain_fodda import FoddaContextRetriever

# Initialize tool (API key optional for unauthenticated discovery / x402 on-chain settlement)
fodda_tool = FoddaContextRetriever(api_key="sk_live_...")

# Query a knowledge graph
result = fodda_tool.run("psfk-retail")
print(result)
```

## Features

- **Autonomous 402 Paywall Handling**: Gracefully catches HTTP 402 challenges. If no credentials or wallet are configured, it automatically falls back to Fodda's verified markdown schema summaries (`free_readme`) so the LLM reasoning loop never crashes.
- **Base USDC Micro-Settlement**: Supports on-chain 5¢ Base USDC payments via `X-402-Payment`.
- **Enterprise Delegated Billing**: Supports zero-friction enterprise billing and delegated account budgets.

## License

MIT
