# HuggingFace Pricing Configuration

## Overview

HuggingFace API calls (specifically for GPT-OSS-120B model via Groq) are tracked and billed using configurable pricing. The pricing can be set via environment variables in your `.env` file.

## Environment Variables

### `HUGGINGFACE_INPUT_TOKEN_COST`
- **Description**: Cost per input token for HuggingFace API calls
- **Format**: Float (decimal number)
- **Default**: `0.000001` ($1 per 1M input tokens)
- **Example**: `HUGGINGFACE_INPUT_TOKEN_COST=0.000001`

### `HUGGINGFACE_OUTPUT_TOKEN_COST`
- **Description**: Cost per output token for HuggingFace API calls
- **Format**: Float (decimal number)
- **Default**: `0.000003` ($3 per 1M output tokens)
- **Example**: `HUGGINGFACE_OUTPUT_TOKEN_COST=0.000003`

## Configuration

### Step 1: Add to .env File

Add the following lines to your `.env` file:

```bash
# HuggingFace Pricing (for GPT-OSS-120B via Groq)
# Pricing is per token (e.g., 0.000001 = $1 per 1M tokens)
HUGGINGFACE_INPUT_TOKEN_COST=0.000001
HUGGINGFACE_OUTPUT_TOKEN_COST=0.000003
```

### Step 2: Initialize/Update Pricing

The pricing is automatically initialized when the database is set up. To update pricing after changing environment variables:

1. **Option 1**: Restart the backend server (pricing will be updated on next initialization)
2. **Option 2**: Run the database setup script to update pricing:
   ```bash
   python backend/scripts/create_subscription_tables.py
   ```

### Step 3: Verify Pricing

Check that pricing is correctly configured by:
1. Checking the database `api_provider_pricing` table
2. Making a test API call and checking the cost in usage logs
3. Viewing the billing dashboard to see cost calculations

## Pricing Calculation

The cost calculation works as follows:

1. **Database Lookup**: The system first tries to find pricing in the database for the specific model
2. **Model Matching**: It tries multiple model name variations:
   - Exact model name (e.g., "openai/gpt-oss-120b:groq")
   - Short model name (e.g., "gpt-oss-120b")
   - Default model name ("default")
3. **Environment Variable Fallback**: If no pricing is found in the database, it uses environment variables for HuggingFace/Mistral provider
4. **Default Estimates**: As a last resort, it uses default estimates ($1 per 1M tokens for both input and output)

## Cost Calculation Formula

```
cost_input = tokens_input * HUGGINGFACE_INPUT_TOKEN_COST
cost_output = tokens_output * HUGGINGFACE_OUTPUT_TOKEN_COST
cost_total = cost_input + cost_output
```

## Example

For a HuggingFace API call with:
- Input tokens: 1000
- Output tokens: 500
- HUGGINGFACE_INPUT_TOKEN_COST: 0.000001 ($1 per 1M tokens)
- HUGGINGFACE_OUTPUT_TOKEN_COST: 0.000003 ($3 per 1M tokens)

Calculation:
```
cost_input = 1000 * 0.000001 = 0.001 ($0.001)
cost_output = 500 * 0.000003 = 0.0015 ($0.0015)
cost_total = 0.001 + 0.0015 = 0.0025 ($0.0025)
```

## Testing

To test the pricing configuration:

1. Set environment variables in `.env`
2. Restart the backend server
3. Make a HuggingFace API call
4. Check the usage logs in the billing dashboard
5. Verify the cost is calculated correctly

## Notes

- Pricing is stored in the `api_provider_pricing` table
- Pricing is updated automatically when `initialize_default_pricing()` is called
- Environment variables take precedence over database values if pricing is not found in DB
- The pricing applies to all HuggingFace models that map to the MISTRAL provider enum
- Default pricing is based on Groq's estimated pricing for GPT-OSS-120B model

