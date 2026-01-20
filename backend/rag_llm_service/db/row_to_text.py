from datetime import date

def build_context_block(
    usage,
    stock,
    prediction,
    medicine,
    orders
):
    lines = []

    lines.append(f"Medicine: {usage['medicine_name']}")
    lines.append(f"Hospital: {usage['hospital_id']}")

    lines.append(
        f"Average available quantity: {round(usage['avg_quantity_available'], 2)} units"
    )

    if stock:
        days_to_expiry = (stock["medicine_expiry"] - date.today()).days
        lines.append(f"Current stock: {stock['medicine_quantity']} units")
        lines.append(f"Days to expiry: {days_to_expiry}")

    if prediction:
        daily_usage = prediction["x1_amc"] / 30
        lines.append(f"Average daily usage: {round(daily_usage, 2)} units/day")
        lines.append(f"Lead time: {prediction['lead_time']} days")
        lines.append(f"Safety stock: {prediction['safety_stock']} units")
        lines.append(f"Reorder point: {prediction['reorder_stock']} units")

    lines.append(f"ABC category: {medicine['abc_category']}")
    lines.append(f"VED category: {medicine['ved_category']}")
    lines.append(
        f"Cold storage required: {'Yes' if medicine['cold_storage'] else 'No'}"
    )
    lines.append(f"Unit cost: ₹{medicine['medicine_price']}")
    lines.append(f"Pack size: {medicine['pack_size']}")

    if medicine.get("salt_composition"):
        lines.append(f"Salt composition: {medicine['salt_composition']}")

    if orders:
        lines.append("Recent orders:")
        for o in orders:
            lines.append(
                f"- Status: {o['order_status']}, "
                f"Predicted: {o['medicine_quantity_predicted']}, "
                f"Received: {o['recieved_quantity']}"
            )

    return "\n".join(lines)
