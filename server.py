from mcp.server import MCPServer
import httpx
from typing import Any
mcp = MCPServer("ecommerce_suite_mcp_server",
                instructions="""While requesting a tool that needs JWT token, if value of variable "jwtToken" is none use login tool for jwtToken.""")

base_url="https://ecommercesuite-experienceapi-proxy-md40ok.5sc6y6-3.usa-e2.cloudhub.io/exp-proxy"

jwtToken = None

@mcp.tool()
async def login(email: str, password: str) -> dict[str, Any]:
    global jwtToken
    """Use this tool for logging in a user"""

    payload={
        "email": email,
        "password": password
    }
    async with httpx.AsyncClient() as Client:
        response = await Client.post(
            f"{base_url}/auth/login", json=payload
        )
        if response.status_code == 200:
            jwtToken = response.json()["jwt"]
        return response.json()

@mcp.tool()
async def getStoresForAdmin(verificationStatus: str) -> dict[str, Any]:
    """Use this tool when an user asks for stores list by verification status.
    Verification status can be verified, unverified, rejected.
    Requires JWT token"""

    param={"verificationStatus": verificationStatus}

    header = {"authorization": f"Bearer {jwtToken}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/stores/admin",
            params=param,
            headers=header
        )
        return{
            "statusCode": response.status_code,
            "body": response.json()
        }

@mcp.tool()
async def newUserRegistration(firstname: str, lastname: str, email: str, password: str, role: str, city: str, phoneno: str)-> dict[str, Any]:
    """use this tool for registering new user.
    Role can only contain "seller" and "buyer".
    For role ask about the purpose i.e. if user wants to sell products or buy products, instead of directly asking for the value.
    Verify values with the user before calling the tool.
    Doesn't require jwt token"""

    payload={
        "firstName": firstname,
        "lastName": lastname,
        "password": password,
        "role": role,
        "city": city,
        "email": email,
        "phoneNo": phoneno
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/auth/register",
            json=payload
        )
        return{
            "statusCode": response.status_code,
            "body": response.json()
        }

@mcp.tool()
async def createNewStore(storeName: str, gstin: str, accountNumber: str, accountHolderName: str) -> dict[str, Any]:
    """Use this tool when the user asks to create or add a new store.
    Requires JWT token"""

    payload={
        "storeName": storeName,
        "gstin": gstin,
        "accountNumber": accountNumber,
        "accountHolderName": accountHolderName
    }

    header = {
        "authorization": f"Bearer {jwtToken}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/stores",
            json = payload,
            headers = header
        )
    return{
        "statusCode": response.status_code,
        "body": response.json()
    }
    
if __name__ == "__main__":
    mcp.run()