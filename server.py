from mcp.server import MCPServer
import httpx
from typing import Any
from typing import Literal
from mcp.types import Resource, TextContent
mcp = MCPServer("ecommerce_suite_mcp_server")

base_url="https://ecommercesuite-experienceapi-proxy-md40ok.5sc6y6-3.usa-e2.cloudhub.io/exp-proxy"

jwtToken = None

# globalInstructions = """While requesting a tool that needs JWT token, if you encounter an issue in which login is required,
# help the user to login using the login tool, dont ask the user to login from somewhere else.
# Always verify data obtained from user before calling any tool"""

# @mcp.tool()
# async def globalInstructions() -> str:
#     """Use this tool to understand the global instructions that are applied for every tool"""
#     return globalInstructions
    

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
            jwtToken = f"Bearer {response.json()["jwt"]}"
        return response.json()

@mcp.tool()
async def getStoresForAdmin(verificationStatus: str) -> dict[str, Any]:
    """Use this tool when an user asks for stores list by verification status.
    Verification status can be verified, unverified, rejected.
    Requires JWT token
    If authentication fails because the JWT is missing or expired, use the login tool and retry."""

    param={"verificationStatus": verificationStatus}

    header = {"authorization": jwtToken}

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
    Doesn't require jwt token
    If authentication fails because the JWT is missing or expired, use the login tool and retry."""

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
        if response.status_code == 200:
            jwtToken = f"Bearer {response.json()["jwt"]}"
        return{
            "statusCode": response.status_code,
            "body": response.json()
        }

@mcp.tool()
async def createNewStore(storeName: str, gstin: str, accountNumber: str, accountHolderName: str) -> dict[str, Any]:
    """Use this tool when the user asks to create or add a new store.
    Requires JWT token
    If authentication fails because the JWT is missing or expired, use the login tool and retry."""

    payload={
        "storeName": storeName,
        "gstin": gstin,
        "accountNumber": accountNumber,
        "accountHolderName": accountHolderName
    }

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header = {
        "authorization": jwtToken
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

@mcp.tool()
async def storeVerificationStatusUpdate(storeId: str, status: str)-> dict[str, Any]:
    """Use this tool when an admin asks to verify a store, or change/update verification status of a store.
    Requires JWT token
    If authentication fails because the JWT is missing or expired, use the login tool and retry."""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header = {
        "authorization": jwtToken
    }
    payload = {
        "status": status
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{base_url}/stores/{storeId}/verification",
            headers = header,
            json = payload
        )

    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

@mcp.tool()
async def addNewProductToStore(productName: str, brand: str, category: Literal["Clothing","Electronics","Furniture","Stationary"], stock: int, details: str, price: float, storeId: str, subCategory: str = "")-> dict[str, Any]:
    """Use this tool when a seller asks to add a product to his store.
    Subcategories are:
    -Clothing(Men's Shirt, Men's Jeans, Women's Saree, Women's Kurti)
    -Electronics(Smartphone, Laptop, Headphones, Earbuds),
    -Furniture(Sofa, Bed Frame, Tea Table, Chair)
    -Stationary(Notebook, Pen, Pencil, highlighter)
    Tell the store owner that subcategory can be left empty.
    Verify details with store owner before adding the product.
    If store owner doesn't remember the storeId use getStoresListForSeller tool, to get the list of stores owned by the store Owner.
    requires JWT Token
    If authentication fails because the JWT is missing or expired, use the login tool and retry."""

    payload={
        "productName": productName,
        "brand": brand,
        "category": category,
        "stock": stock,
        "details": details,
        "price": price,
        "subCategory": subCategory
    }

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/stores/{storeId}/products",
            headers= header,
            json = payload
        )

    return{
        "statusCode" : response.status_code,
        "body" : response.json()
    }

@mcp.tool()
async def getProductsByFilters(brand: str = "", category: str="", subCategory: str="", maxPrice: float | None = None, minPrice: float | None = None, inStock: Literal["inStock", "outOfStock"] | None = None, minRatings: float | None = None, storeName: str = "")-> dict[str, Any]:
    """Use this tool get get products using filters, or when user wants to browse products from website
    Subcategories are:
        -Clothing(Men's Shirt, Men's Jeans, Women's Saree, Women's Kurti)
        -Electronics(Smartphone, Laptop, Headphones, Earbuds),
        -Furniture(Sofa, Bed Frame, Tea Table, Chair)
        -Stationary(Notebook, Pen, Pencil, highlighter)
    minRatings must be a float value between 0.0 to 5.0
    Don't show product ID to user"""


    params={}

    if brand:
        params["brand"] = brand

    if category:
        params["category"] = category

    if subCategory:
        params["subCategory"] = subCategory

    if minPrice is not None:
        params["minPrice"] = minPrice

    if maxPrice is not None:
        params["maxPrice"] = maxPrice

    if inStock == "inStock":
        params["inStock"] = True
    elif inStock == "outOfStock":
        params["inStock"] = False

    if minRatings is not None:
        params["minRatings"] = minRatings

    if storeName:
        params["storeName"] = storeName

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/products",
            params=params
        )

    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

@mcp.tool()
async def getProductsByProductId(productId: str)-> dict[str, Any]:
    """Use this tool for accessing product details by productId"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/products/{productId}"
        )
    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

@mcp.tool()
async def getProductListByStoreId(storeId: str)-> dict[str, Any]:
    """Use this tool to list products from a store by store ID"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/stores/{storeId}/products"
        )
    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

# @mcp.tool()
# async def deleteProudctByProductId(productId: str)-> dict[str, Any]:
#     """Use this tool when a store owner asks to delete a product data from his store.
#     This is a destructive operation so re-confirm with store owner.
#     before responding to user recheck for the existance of the product using getProductByProductId tool"""

#     header = {
#         "authorization": f"Bearer {jwtToken}"
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.delete(
#             f"{base_url}/products/{productId}",
#             headers=header
#         )
    
#     return{
#         "statusCode": response.status_code,
#         "body": response.json()
#     }

@mcp.tool()
async def restockProduct(productId: str, quantity: int)-> dict[str, Any]:
    """Use this tool when a store owner asks to restock a product.
    If store owner don't know the productId use getStoresListForSeller tool to get the list of stores owned by the seller, using the store Id from the response of getStoresListForSeller tool get the list of products from that store.
    If authentication fails because the JWT is missing or expired, use the login tool and retry."""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    header = {
        "authorization": jwtToken
    }
    payload = {
        "quantity": quantity
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.patch(
            f"{base_url}/products/{productId}/restock",
            headers = header,
            json = payload
        )
    
    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

@mcp.tool()
async def updateProductData(productId: str, subCategory: str="", price: float | None = None, category: str="", details: str="",
                            brand: str="", productName: str="")-> dict[str, Any]:
    """Use this tool when a seller asks to update data for this product.
    If store owner don't know the productId use getStoresListForSeller tool to get the list of stores owned by the seller, using the store Id from the response of getStoresListForSeller tool get the list of products from that store.
    requires JWT token.
    If authentication fails because JWT is missing or expired, use login tool and retry"""

    payload={}

    if subCategory:
        payload["subCategory"] = subCategory
    if price is not None:
        payload["price"] = price
    if category:
        payload["category"] = category
    if details:
        payload["details"] = details
    if brand:
        payload["brand"] = brand
    if productName:
        payload["productName"] = productName

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    header={
        "authorization": jwtToken
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.patch(
            f"{base_url}/products/{productId}",
            json=payload,
            headers=header
        )

    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

@mcp.tool()
async def addProductToCart(productId: str, quantity: int)-> dict[str, Any]:
    """Use this tool when a buyer asks to add a product to his cart.
    If product already exist in the cart, then the quantity will be updated(e.g. if quantity was 1 before hitting this tool, and it is 2 this time then the final quantity will be 2 and not 3)
    Requires jwt token.
    If there is any authentication error beacuse of invalid/missing jwt token then use login tool and retry again."""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    header={
        "authorization": jwtToken
    }

    payload={
        "productId": productId,
        "quantity": quantity
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/carts",
            headers= header,
            json=payload
        )

    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

@mcp.tool()
async def getCart()-> dict[str, Any]:
    """Use this tool to show products in a cart of a buyer.
    Requires jwt token.
    If there are any authentication error due to invalid/missing jwt token use login tool and retry again."""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient() as client:
        response= await client.get(
            f"{base_url}/carts",
            headers=header
        )

    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

@mcp.tool()
async def updateCartItemQuantity(cartItemId: str, quantity: int)-> dict[str, Any]:
    """Use this tool when buyer asks to update quantity of a proudct that is already is his/her cart.
    cartItemId is the unique id for the item in buyers cart.
    This tool updates the quantity(e.g. if quantity was 1 before hitting this tool, and it is 2 this time then the final quantity will be 2 and not 3)
    Requires JWT token.
    If there are any authentication errors due to invalid/missing jwt token then use login tool and retry again."""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    payload={
        "quantity":quantity
    }

    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{base_url}/carts/{cartItemId}/quantity",
            headers=header,
            json = payload
        )

    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

@mcp.tool()
async def deleteWholeCart()-> dict[str, Any]:
    """Use this tool when buyer asks to delete all the items from his/her cart or empty his/her cart
    Requires jwt token.
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{base_url}/carts",
            headers=header
        )

    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

@mcp.tool()
async def deleteSingleItemFromCart(cartItemId: str)-> dict[str, Any]:
    """Use this tool when buyer asks to delete a single item from his cart using the cartItemId
    For cartItemId use getCart tool to get the list of items in cart.
    Requires jwt token.
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{base_url}/carts/{cartItemId}",
            headers=header
        )

    return{
        "statusCode": response.status_code,
        "body": response.json()
    }

@mcp.tool()
async def placeOrder(pincode: str, productId: str="", quantity: int | None = None)-> dict[str, Any]:
    """Use this tool when buyer asks to place order.
    Pincode is always required.
    productId and quantity are optional, but must be provided together.
    Either provide both productId and quantity or provide neither.
    If payment fails then try again.
    Requires JWT token.
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    payload={
        "deliveryPincode": pincode
    }

    header={
        "authorization":jwtToken
    }

    if productId and quantity is not None:
        if quantity <= 0:
            return{
                    "error": "Quantity should be greater than 0"
                }
        payload["product"] = {
        "productId": productId,
        "quantity": quantity
    }
    elif productId or quantity is not None:
        return{
            "error": "productId and quantity must be provided together"
        }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{base_url}/orders",
            json=payload,
            headers=header
        )

    return{
            "statusCode": response.status_code,
            "body": response.json()
        }

@mcp.tool()
async def getOrdersForSeller()-> dict[str, Any]:
    """Use this tool when a seller wants to see the orders that he/she has received
    Requires JWT token
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{base_url}/orders/seller",
            headers=header
        )
    return{
            "statusCode": response.status_code,
            "body": response.json()
        }

@mcp.tool()
async def getOrdersForBuyer()-> dict[str, Any]:
    """Use this tool when a buyer wants to see all the orders that he has placed.
    Requires JWT token
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }

    header={
        "authorization": jwtToken
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{base_url}/orders/buyer",
            headers=header
        )
    return{
            "statusCode": response.status_code,
            "body": response.json()
        }

@mcp.tool()
async def orderCancellation(orderId: str)-> dict[str, Any]:
    """Use this tool when a buyer asks to cancel order that he/she has already placed.
    If buyer doesn't remember orderId, use the getOrdersForBuyer tool to get the list of all the orders for that buyer, and then access the orderId from the output of getOrdersForBuyer tool.
    Requires jwt token.
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    header={
        "authorization":jwtToken
    }

    async with httpx.AsyncClient() as client:
        response= await client.patch(
            f"{base_url}/orders/{orderId}/cancellation",
            headers=header
        )

    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

@mcp.tool()
async def getOrdersByOrderId(orderId: str)-> dict[str, Any]:
    """Use this tool when a buyer asks to access a specific order. Use orderId to access that order.
    If buyer doesn't remember orderId, use the getOrdersForBuyer tool to get the list of all the orders for that buyer, and then access the orderId from the output of getOrdersForBuyer tool.
    Requires JWT token.
    If there is any authentication error due to invalid/missing jwt token use login tool and retry again"""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
    
    header={
        "authorization":jwtToken
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/orders/{orderId}",
            headers=header
        )

    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

@mcp.tool()
async def getStoresListForSeller()-> dict[str, Any]:
    """Use this tool when a seller asks to list all the stores that he own.
    Requires JWT token.
    If there is any authentication errors due to invalid/missing jwt use login tool and retry again."""

    if(jwtToken == None):
        return{
            "error":"Missing JWT Token. Please Login."
        }
        
    header={
        "authorization":jwtToken
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/stores/seller",
            headers=header
        )
    return{
        "statusCode":response.status_code,
        "body":response.json()
    }

if __name__ == "__main__":
    mcp.run()