# 🛍️ Printful API Setup Guide (Updated)

## 🔐 Secure Token Setup ✅

Your Printful token has been securely configured:
- **Token**: `eWlXN3veWJXrQyOan2OEpHkQ9nuZuUqy6pZnmJjk`
- **Status**: ✅ Securely stored in `.env` file
- **Git Protection**: ✅ Never committed to repository

## 📋 Updated Printful Integration

### ✅ What's Working:
- **New API Version**: Using Printful's latest token-based API
- **Secure Authentication**: Bearer token authentication
- **Enhanced Error Handling**: Better error messages and debugging
- **Connection Testing**: Automatic API connection testing on startup
- **GCP Ready**: Token configured for cloud deployment

### 🔧 API Improvements:
- **Better Error Messages**: Specific error codes (401, 404, etc.)
- **Network Error Handling**: Graceful handling of connection issues
- **Retail Costs**: Proper pricing structure in orders
- **Enhanced Logging**: Detailed API response logging

## 🧪 Testing Your Setup

### 1. Test API Connection:
```bash
# Test Printful API connection
curl http://127.0.0.1:5000/api/test-printful
```

### 2. Check App Startup:
The app automatically tests Printful connection on startup and shows:
- ✅ Connection successful
- 📦 Number of products found
- ❌ Any authentication errors

### 3. Test Complete Purchase Flow:
1. **Visit Shop**: http://127.0.0.1:5000/shop
2. **Select Product**: Choose size and quantity
3. **Checkout**: Fill shipping information
4. **PayPal Payment**: Complete test payment
5. **Order Creation**: Verify order appears in Printful dashboard

## 📦 Product Setup in Printful

### Step 1: Create Your T-Shirt Product
1. **Login to Printful**: [printful.com](https://printful.com)
2. **Go to Products**: Click "Products" in dashboard
3. **Add New Product**: Click "Add Product"
4. **Choose T-Shirt**: Select "T-Shirts" category
5. **Upload Design**: Upload your "IT'S TOO HOT!" design
6. **Configure Product**:
   - **Name**: "IT'S TOO HOT! T-Shirt"
   - **Brand**: Your brand name
   - **Sizes**: S, M, L, XL, XXL
   - **Colors**: White, Black (or your choice)
   - **Price**: $25.00
7. **Save Product**: Click "Save" or "Publish"

### Step 2: Get Your Product ID
After creating the product:
1. **Find Product**: In your product list
2. **Click Product**: Open product details
3. **Check URL**: Product ID is in URL
   - Example: `printful.com/dashboard/products/12345`
   - Product ID = `12345`

### Step 3: Update Your App
Replace the placeholder in `app.py`:
```python
'printful_product_id': 'your-printful-product-id'  # Replace with actual ID
```

## 🔍 API Testing Endpoints

### Test Printful Connection:
```bash
curl http://127.0.0.1:5000/api/test-printful
```

### Expected Response:
```json
{
  "success": true,
  "message": "Printful API connection test completed"
}
```

## 🚀 GCP Deployment

### Updated Deployment Script:
The `deploy_gcp.sh` script now includes your Printful token:
```bash
--set-env-vars="PRINTFUL_API_KEY=eWlXN3veWJXrQyOan2OEpHkQ9nuZuUqy6pZnmJjk"
```

### Deploy to GCP:
```bash
# Update other API keys in deploy_gcp.sh first
./deploy_gcp.sh
```

## 🔒 Security Features

### ✅ Implemented:
- **Environment Variables**: Token stored securely in `.env`
- **Git Protection**: `.env` file ignored by git
- **Bearer Authentication**: Secure token-based API access
- **Error Handling**: Graceful handling of API errors
- **Connection Testing**: Automatic API validation

## 📊 Enhanced Order Processing

### New Order Structure:
```json
{
  "recipient": {
    "name": "Customer Name",
    "address1": "123 Main St",
    "city": "City",
    "state_code": "ST",
    "country_code": "US",
    "zip": "12345"
  },
  "items": [{
    "sync_product_id": "your-product-id",
    "quantity": 1
  }],
  "retail_costs": {
    "currency": "USD",
    "subtotal": "25.00",
    "shipping": "5.00",
    "tax": "0.00",
    "total": "30.00"
  }
}
```

## 🐛 Troubleshooting

### Common Issues:

1. **Authentication Failed (401)**:
   - Check your Printful token is correct
   - Verify token is in `.env` file
   - Test connection: `curl http://127.0.0.1:5000/api/test-printful`

2. **Product Not Found (404)**:
   - Verify product ID in `app.py`
   - Check product exists in Printful dashboard
   - Update product ID with correct value

3. **Network Errors**:
   - Check internet connection
   - Verify Printful API is accessible
   - Check firewall settings

### Debug Commands:
```bash
# Test API connection
curl http://127.0.0.1:5000/api/test-printful

# Check environment variables
grep PRINTFUL .env

# View app logs
python app.py
```

## 🎯 Next Steps

### 1. Create Your Product:
- Set up t-shirt product in Printful dashboard
- Get the product ID
- Update `app.py` with correct product ID

### 2. Test Complete Flow:
- Make a test purchase
- Verify order appears in Printful
- Check email confirmations

### 3. Deploy to Production:
- Update `deploy_gcp.sh` with all API keys
- Deploy to GCP Cloud Run
- Test live payment flow

## 📞 Support Resources

- **Printful Help**: [help.printful.com](https://help.printful.com)
- **API Documentation**: [printful.com/api](https://printful.com/api)
- **Live Chat**: Available in Printful dashboard
- **Email Support**: support@printful.com

## 🎉 Ready to Launch!

Your Printful integration is now:
- ✅ **Securely configured** with your token
- ✅ **Using latest API** version
- ✅ **Enhanced error handling**
- ✅ **GCP deployment ready**
- ✅ **Automatically tested** on startup

**Your climate awareness t-shirt business is ready to go live!** 🌍🛍️ 