# E-Commerce Integration Suite — MCP Server

## Overview

The **MCP Server** (`ecommerce_suite_mcp_server`) is the AI integration layer of the E-Commerce Integration Suite. It exposes the Experience API's capabilities as MCP (Model Context Protocol) tools, allowing an AI agent such as Claude to interact with the e-commerce platform using natural language.

**Key responsibilities:**
- Exposing e-commerce operations as MCP tools consumable by an AI agent
- Handling JWT token management for authenticated tool calls
- Translating AI agent requests into HTTP calls to the Experience API
- Returning structured responses back to the AI agent

> This server acts as the bridge between the AI agent and the Experience API. It does not implement any business logic — all operations are delegated to the Experience API.

---

## Architecture

The MCP Server sits at the top of the API-led connectivity model, above the Experience API.

```
    AI Agent (via MCP Server)
              ↓
    MCP Server (This Layer)
              ↓
    Experience API Proxy (CloudHub)
              ↓
    Experience API
              ↓
      Process API Layer
              ↓
    System APIs (Database API, Mock Payment API)
              ↓
    Data Layer (MySQL Database on Aiven Cloud)
```

**Role of MCP Server:**
- Receives natural language instructions from an AI agent
- Maps user intent to the appropriate MCP tool
- Calls the Experience API with the correct HTTP method, headers, and payload
- Returns the API response to the AI agent for interpretation and presentation

For the complete system architecture, deployment topology, and integration details, refer to the [main project repository](https://github.com/Anurag180259/ecommerce_suite).

---

## Prerequisites

- **Python**: 3.10 or later
- **uv**: Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **VS Code**: With the MCP extension or Claude Desktop configured to use this server
- **Experience API**: Must be deployed and accessible at the configured base URL

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Anurag180259/ecommerce_suite_mcp_server.git
cd ecommerce_suite_mcp_server
```

### 2. Install uv

Open the VS Code embedded terminal and run:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify the installation:
```bash
uv --version
```

### 3. Installing the dependencies

```bash
uv sync
```

This reads the [`pyproject.toml`](./pyproject.toml) and installs all required dependencies into a virtual environment managed by uv.

### 4. Configure the Base URL

Open `server.py` and update the `base_url` variable to point to your deployed Experience API:

```python
base_url = "YOUR_EXPERIENCE_API_BASE_URL"
```

### 5. Run the MCP Server

```bash
uv run server.py
```

The MCP server will start and be ready to accept connections from an AI agent.

---

## MCP Tools

The MCP server exposes the following tools to the AI agent. Each tool maps to one or more Experience API endpoints.

### Quick Reference

| Tool | Auth Required | Description |
|---|---|---|
| `login` | No | Log in a user and store the JWT token |
| `newUserRegistration` | No | Register a new buyer or seller |
| `getStoresForAdmin` | Yes | Get stores filtered by verification status |
| `createNewStore` | Yes | Create a new store |
| `storeVerificationStatusUpdate` | Yes | Update store verification status |
| `getStoresListForSeller` | Yes | Get all stores owned by the authenticated seller |
| `addNewProductToStore` | Yes | Add a new product to a store |
| `getProductsByFilters` | No | Browse products using optional filters |
| `getProductsByProductId` | No | Get product details by product ID |
| `getProductListByStoreId` | No | Get all products in a store |
| `restockProduct` | Yes | Restock a product |
| `updateProductData` | Yes | Update product details |
| `addProductToCart` | Yes | Add a product to the buyer's cart |
| `getCart` | Yes | Get all items in the buyer's cart |
| `updateCartItemQuantity` | Yes | Update quantity of a cart item |
| `deleteSingleItemFromCart` | Yes | Remove a single item from the cart |
| `deleteWholeCart` | Yes | Clear the entire cart |
| `placeOrder` | Yes | Place an order |
| `getOrdersForBuyer` | Yes | Get all orders for the authenticated buyer |
| `getOrdersForSeller` | Yes | Get all orders for the authenticated seller |
| `getOrdersByOrderId` | Yes | Get a specific order by order ID |
| `orderCancellation` | Yes | Cancel an order |

---

### Authentication Tools

#### `login`
Logs in a user with email and password. On success, stores the JWT token in memory for use by all subsequent authenticated tool calls.

**Parameters:**
- `email` — User's email address
- `password` — User's password

**Returns:** Login response from the Experience API including the JWT token and user ID.

---

#### `newUserRegistration`
Registers a new user. On success, stores the JWT token in memory.

**Parameters:**
- `firstname` — User's first name
- `lastname` — User's last name
- `email` — User's email address
- `password` — User's password
- `role` — `seller` or `buyer` (ask the user about their intent — whether they want to sell or buy — rather than asking for the value directly)
- `city` — User's city
- `phoneno` — User's phone number

---

### Store Management Tools

#### `getStoresForAdmin`
Gets all stores filtered by verification status. Requires the authenticated user to be an admin.

**Parameters:**
- `verificationStatus` — `verified`, `unverified`, or `rejected`

---

#### `createNewStore`
Creates a new store for the authenticated seller.

**Parameters:**
- `storeName` — Store name
- `gstin` — GSTIN number
- `accountNumber` — Bank account number
- `accountHolderName` — Account holder name

---

#### `storeVerificationStatusUpdate`
Updates the verification status of a store. Requires the authenticated user to be an admin.

**Parameters:**
- `storeId` — Store ID
- `status` — `verified`, `unverified`, or `rejected`

---

#### `getStoresListForSeller`
Gets all stores owned by the authenticated seller. Useful when the seller does not remember their store ID.

---

### Product Management Tools

#### `addNewProductToStore`
Adds a new product to a store. Requires the authenticated user to be a seller.

**Parameters:**
- `productName` — Product name
- `brand` — Brand name
- `category` — One of: `Clothing`, `Electronics`, `Furniture`, `Stationary`
- `stock` — Initial stock quantity
- `details` — Product description (max 255 characters)
- `price` — Product price
- `storeId` — Store ID to add the product to
- `subCategory` — Optional. Supported subcategories:
  - Clothing: `Men's Shirt`, `Men's Jeans`, `Women's Saree`, `Women's Kurti`
  - Electronics: `Smartphone`, `Laptop`, `Headphones`, `Earbuds`
  - Furniture: `Sofa`, `Bed Frame`, `Tea Table`, `Chair`
  - Stationary: `Notebook`, `Pen`, `Pencil`, `Highlighter`

---

#### `getProductsByFilters`
Browses products using optional filters. No authentication required.

**Parameters (all optional):**
- `brand`
- `category`
- `subCategory`
- `maxPrice`
- `minPrice`
- `inStock` — `inStock` or `outOfStock`
- `minRatings` — Float between `0.0` and `5.0`
- `storeName`

> Product IDs are not shown to the user.

---

#### `getProductsByProductId`
Gets full product details by product ID.

**Parameters:**
- `productId` — Product ID

---

#### `getProductListByStoreId`
Gets all products in a store by store ID.

**Parameters:**
- `storeId` — Store ID

---

#### `restockProduct`
Restocks a product by adding to its existing stock.

**Parameters:**
- `productId` — Product ID
- `quantity` — Quantity to add to existing stock

> If the seller does not remember the product ID, the tool description guides the AI agent to use `getStoresListForSeller` followed by `getProductListByStoreId` to locate it.

---

#### `updateProductData`
Updates one or more product fields. All fields are optional — only supplied fields are updated.

**Parameters (all optional except `productId`):**
- `productId` — Product ID (required)
- `productName`
- `brand`
- `price`
- `category`
- `subCategory`
- `details`

---

### Cart Management Tools

#### `addProductToCart`
Adds a product to the buyer's cart. If the product already exists in the cart, the quantity is updated to the supplied value rather than added to it.

**Parameters:**
- `productId` — Product ID
- `quantity` — Desired quantity

---

#### `getCart`
Gets all items currently in the buyer's cart.

---

#### `updateCartItemQuantity`
Updates the quantity of a specific cart item. Sets the quantity to the supplied value rather than adding to it.

**Parameters:**
- `cartItemId` — Cart item ID
- `quantity` — New quantity to set

---

#### `deleteSingleItemFromCart`
Removes a single item from the buyer's cart.

**Parameters:**
- `cartItemId` — Cart item ID

> If the buyer does not remember the cart item ID, the AI agent uses `getCart` to retrieve it.

---

#### `deleteWholeCart`
Clears all items from the buyer's cart.

---

### Order Management Tools

#### `placeOrder`
Places an order. Pincode is always required. `productId` and `quantity` are optional but must be provided together — if omitted, the order is placed for all items in the buyer's cart.

**Parameters:**
- `pincode` — 6-digit delivery pincode (supported: `100001`, `100002`, `100003`)
- `productId` — Optional. Product ID for a direct order
- `quantity` — Optional. Must be provided with `productId`

> If payment fails, the tool description instructs the AI agent to retry automatically.

---

#### `getOrdersForBuyer`
Gets all orders placed by the authenticated buyer.

---

#### `getOrdersForSeller`
Gets all orders received by the authenticated seller across all their stores.

---

#### `getOrdersByOrderId`
Gets details of a specific order by order ID.

**Parameters:**
- `orderId` — Order ID

> If the buyer does not remember the order ID, the AI agent uses `getOrdersForBuyer` to retrieve it.

---

#### `orderCancellation`
Cancels an order placed by the authenticated buyer.

**Parameters:**
- `orderId` — Order ID

> If the buyer does not remember the order ID, the AI agent uses `getOrdersForBuyer` to retrieve it.

---

## JWT Token Management

The MCP server stores the JWT token as a global in-memory variable (`jwtToken`). It is set automatically when `login` or `newUserRegistration` is called successfully.

**Important limitations:**
- The token is stored in memory only — it is lost when the MCP server restarts
- The token expires after 1 hour — after expiry, `login` must be called again to obtain a fresh token
- All authenticated tools check for the token before making a request and return an error if it is missing, prompting the AI agent to call `login` and retry

---

## Error Handling

Each tool returns a structured response containing the HTTP status code and response body:

```json
{
  "statusCode": 200,
  "body": { ... }
}
```

For authentication errors, tools return:
```json
{
  "error": "Missing JWT Token. Please Login."
}
```

The AI agent uses the status code and body to determine the outcome and take appropriate action — for example, retrying after login on authentication errors.

---

## Logging

The MCP server uses the standard MCP logging mechanism. Tool calls and API responses are handled by the `MCPServer` runtime.

---

## Troubleshooting

### JWT Token Missing or Expired
- **Error:** `"Missing JWT Token. Please Login."`
- **Solution:** Call the `login` tool to obtain a fresh token. Tokens expire after 1 hour and are lost on server restart.

### Experience API Unreachable
- **Error:** Connection error or timeout
- **Solution:** Ensure the Experience API is deployed and the `base_url` in `server.py` points to the correct URL

### Wrong Role Error
- **Error:** `403 Forbidden` from the Experience API
- **Solution:** Ensure the logged-in user has the correct role for the operation — admin for store verification, seller for store and product management, buyer for cart and orders

### Order Delivery Pincode Not Supported
- **Error:** `422 Unprocessable Entity` with reason `notDeliverable`
- **Solution:** Use one of the supported delivery pincodes: `100001`, `100002`, or `100003`

### Payment Failed
- **Error:** `422 Unprocessable Entity` with reason `paymentFailed`
- **Solution:** Retry the `placeOrder` tool — the Mock Payment API uses round-robin and will return a different outcome on the next call

---

## Related Documentation

- **`pyproject.toml`**: [link to pyproject.toml](./pyproject.toml)
- **Main Project Repository:** [ecommerce_suite](https://github.com/Anurag180259/ecommerce_suite) — Contains overall architecture, deployment guide, and project scope

---

## Support

For issues, questions, or contributions, please refer to the main project repository.

---

**Last Updated:** September 2026
**Version:** 1.0
**Maintained by:** Anurag Ninave
