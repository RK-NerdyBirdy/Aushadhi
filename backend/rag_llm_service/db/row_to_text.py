from datetime import date

def build_context_block(*, usage, stock, prediction, medicine, orders):
    lines = []

    if usage:
        lines.append(f"Hospital ID: {usage['hospital_id']}")
        lines.append(f"Medicine: {usage['medicine_name']}")
        lines.append(f"Historical usage period: {usage['total_days']} days")
        lines.append(f"Average daily usage: {round(usage['avg_daily_usage'], 2)} units/day")
        lines.append(f"Peak daily usage: {usage['peak_daily_usage']} units")
        lines.append(f"Total usage in period: {usage['total_usage']} units")

   
    if stock:
        if isinstance(stock, list) and isinstance(stock[0], dict):
            total_stock = sum(s.get("medicine_quantity", 0) for s in stock)
            earliest_expiry = min(
                (s.get("medicine_expiry") for s in stock if s.get("medicine_expiry")),
                default="unknown"
            )
            lines.append(
                f"Current stock: {total_stock} units "
                f"(earliest expiry: {earliest_expiry})"
            )
        else:
            lines.append(f"Stock data present but malformed: {stock}")

    if prediction:
        lines.append(
            f"Lead time: {prediction['lead_time']} days, "
            f"Safety stock: {prediction['safety_stock']} units, "
            f"Reorder point: {prediction['reorder_stock']} units"
        )

    if medicine:
        lines.append(
            f"Price per unit: ₹{medicine['medicine_price']}, "
            f"Cold storage required: {medicine['cold_storage']}, "
            f"ABC: {medicine['abc_category']}, "
            f"VED: {medicine['ved_category']}"
        )

    if orders:
        lines.append("Recent orders:")
        for o in orders:
            lines.append(
                f"- Status: {o['order_status']}, "
                f"Predicted: {o['medicine_quantity_predicted']}, "
                f"Received: {o['recieved_quantity']}, "
                f"Expected: {o['expected_delivery_date']}, "
                f"Actual: {o['actual_delivery_date']}"
            )

    return "\n".join(lines)
