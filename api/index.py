from fastapi import FastAPI, HTTPException, Path

from subprocess import Popen, PIPE
from dotenv import load_dotenv
import os
# Import the patched version of generate_descriptor
from erc7730_patched import generate_descriptor
from erc7730.model.input.descriptor import InputERC7730Descriptor
import os
import traceback
from fastapi.encoders import jsonable_encoder

import json

from fastapi.responses import JSONResponse
from pydantic import BaseModel


def load_env():
    etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
    env = os.environ.copy()
    env["ETHERSCAN_API_KEY"] = etherscan_api_key
    # We're using in-memory cache instead of file-based cache
    # but keep this env var for compatibility with other parts of the code
    env["XDG_CACHE_HOME"] = '/tmp'
    load_dotenv()

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

class Message(BaseModel):
    message: str

class Props(BaseModel):
    abi: str | None = None
    address: str | None = None
    chain_id: int | None = None

@app.post("/api/py/generateERC7730", response_model=InputERC7730Descriptor, responses={400: {"model": Message}})
def run_erc7730(params: Props):
    """Generate the 'erc7730' based on an ABI."""
    try:
        load_env()
        result = None

        # we only manage ethereum mainnet
        chain_id = params.chain_id or 1
        
        if (params.abi):
            result = generate_descriptor(
                chain_id=chain_id,
                contract_address='0xdeadbeef00000000000000000000000000000000', # because it's mandatory mock address see with laurent
                abi=params.abi
            )
       
        if (params.address):
            result = generate_descriptor(
                chain_id=chain_id,
                contract_address=params.address
            )
            
        if result is None:
            return JSONResponse(status_code=404, content={"message": "No ABI or address provided"})
        
        return result

    except Exception as e:
        print('error', e)
        error_message = str(e)
        return JSONResponse(status_code=404, content={"message": error_message})