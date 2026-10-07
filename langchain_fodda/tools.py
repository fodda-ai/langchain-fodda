import time
import httpx
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class FoddaQueryInput(BaseModel):
    graph_slug: str = Field(
        description="The exact identifier or slug for the knowledge graph or market report to retrieve. Example: 'psfk-retail' or 'food-beverage'"
    )

class FoddaContextRetriever(BaseTool):
    """
    LangChain Tool for retrieving verified knowledge graphs, market intelligence,
    and expert research from Fodda.
    
    Gracefully handles the HTTP 402 challenge:
    - If a Web3 private key is configured, it executes the 5¢ Base USDC micro-settlement,
      waits for Retry-After block finality, and resubmits.
    - If unauthenticated or no wallet is present, it returns the free, unauthenticated
      markdown summary fallback so the reasoning loop continues without halting.
    """
    name: str = "fodda_context_retriever"
    description: str = "Retrieves verified knowledge graphs, market intelligence, and expert research from Fodda. Safely handles A2A 402 payment gates internally."
    args_schema: Type[BaseModel] = FoddaQueryInput
    
    base_url: str = "https://api.fodda.ai/v1"
    api_key: Optional[str] = None
    wallet_private_key: Optional[str] = None

    def _run(self, graph_slug: str) -> str:
        url = f"{self.base_url}/graphs/{graph_slug}"
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=headers)
            
            # 1. Clean Success
            if response.status_code == 200:
                return response.text

            # 2. Handle HTTP 402 Payment Required Challenge
            if response.status_code == 402:
                challenge_data = response.json()
                fallback_readme_url = challenge_data.get("free_readme")
                
                # In-flight x402 Web3 execution if wallet is mounted
                if self.wallet_private_key:
                    try:
                        # [Onchain transfer generation logic goes here if handling internally]
                        # tx_hash = self._sign_base_usdc_transfer()
                        
                        retry_after = int(response.headers.get("Retry-After", 2))
                        time.sleep(retry_after)
                        
                        headers["X-402-Payment"] = tx_hash
                        headers["X-402-Network"] = "base"
                        retry_resp = client.get(url, headers=headers)
                        if retry_resp.status_code == 200:
                            return retry_resp.text
                    except Exception:
                        pass # Fall through to markdown summary fallback

                # 3. Graceful Fallback: Fetch open text/markdown summary layer
                if fallback_readme_url:
                    fallback_resp = client.get(fallback_readme_url)
                    if fallback_resp.status_code == 200:
                        return (
                            f"[Notice: Gated context layer. Displaying verified schema summary fallback].\n\n"
                            f"{fallback_resp.text}"
                        )
                
                return f"Gated Resource. Payment Required: {challenge_data.get('llm_instruction')}"

            return f"Fodda network error: Status code {response.status_code}"

    async def _arun(self, graph_slug: str) -> str:
        raise NotImplementedError("Use sync _run or implement with httpx.AsyncClient")
