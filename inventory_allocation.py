
import pandas as pd


def reallocate_demand(df, capacity, shift_months):
    adjusted_demand = df["Demand"].astype(float).copy()
    allocation_records = []

    for current_month in range(len(df)):

        excess = max(0, adjusted_demand[current_month] - capacity)

        if excess == 0:
            continue

        target_month = current_month - shift_months

        while excess > 0 and target_month >= 0:

            available = capacity - adjusted_demand[target_month]

            if available > 0:
                qty = min(excess, available)

                adjusted_demand[current_month] -= qty
                adjusted_demand[target_month] += qty

                excess -= qty

                allocation_records.append({
                    "From Month": df.loc[current_month, "Month"],
                    "To Month": df.loc[target_month, "Month"],
                    "Allocated Quantity": qty
                })

            target_month -= shift_months

    summary_df = pd.DataFrame({
        "Month": df["Month"],
        "Original Demand": df["Demand"],
        "Adjusted Demand": adjusted_demand,
        "Capacity": capacity,
        "Difference (Surplus/Shortfall)": capacity - adjusted_demand
    })

    allocation_df = pd.DataFrame(allocation_records)

    return summary_df, allocation_df


def main():

    capacity = 180
    shift_months = 1

    df = pd.read_csv("demand_data.csv")

    summary, allocations = reallocate_demand(
        df,
        capacity,
        shift_months
    )

    print("\nDEMAND SUMMARY")
    print(summary.to_string(index=False))

    print("\nALLOCATION MAPPING")

    if allocations.empty:
        print("No reallocations required.")
    else:
        print(allocations.to_string(index=False))

    with pd.ExcelWriter(
        "inventory_output.xlsx",
        engine="openpyxl"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Demand Summary",
            index=False
        )

        allocations.to_excel(
            writer,
            sheet_name="Allocation Mapping",
            index=False
        )

    print("\nResults exported to inventory_output.xlsx")


if __name__ == "__main__":
    main()