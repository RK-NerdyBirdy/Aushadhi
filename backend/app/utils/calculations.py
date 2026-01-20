import math
from datetime import datetime, timedelta


def calculate_daily_demand(amc: float) -> float:
    """Calculate average daily demand from annual monthly consumption"""
    return amc / 30


def calculate_daily_demand_std(amc: float, cv: float) -> float:
    """Calculate standard deviation of daily demand"""
    avg_daily = amc / 30
    return avg_daily * cv


def calculate_safety_stock(
    daily_demand_std: float,
    lead_time_days: int,
    service_level: float = 0.95
) -> int:
    """
    Calculate safety stock using Z-score method
    Z-score for 95% service level = 1.645
    """
    z_score = 1.645 if service_level == 0.95 else 1.28
    safety_stock = z_score * daily_demand_std * math.sqrt(lead_time_days)
    return int(safety_stock)


def calculate_reorder_point(
    amc: float,
    lead_time_days: int,
    safety_stock: int
) -> int:
    """
    Calculate reorder point (s)
    s = (Average daily demand × Lead time) + Safety stock
    """
    avg_daily_demand = amc / 30
    reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
    return int(reorder_point)


def calculate_eoq(
    annual_demand: float,
    unit_price: float,
    ordering_cost: float = 100,
    holding_cost_rate: float = 0.15
) -> float:
    """
    Calculate Economic Order Quantity
    EOQ = sqrt((2 × D × S) / (H × P))
    where D = annual demand, S = ordering cost, H = holding cost rate, P = unit price
    """
    numerator = 2 * annual_demand * ordering_cost
    denominator = (unit_price * holding_cost_rate) + 0.01  # Avoid division by zero
    eoq = math.sqrt(numerator / denominator)
    return eoq


def calculate_max_stock(reorder_point: int, eoq: float) -> int:
    """
    Calculate maximum stock (S)
    S = Reorder point + EOQ
    """
    max_stock = reorder_point + eoq
    return int(max_stock)


def calculate_daily_holding_cost(
    unit_price: float,
    holding_cost_rate: float = 0.15
) -> float:
    """Calculate daily holding cost"""
    return (unit_price * holding_cost_rate) / 365


def calculate_delivery_date(expected_delivery_days: int) -> datetime:
    """Calculate expected delivery date"""
    return (datetime.utcnow() + timedelta(days=expected_delivery_days)).date()
