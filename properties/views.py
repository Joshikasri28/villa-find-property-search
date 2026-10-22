
import re
from decimal import Decimal
from django.shortcuts import render
from .models import Property


def property_search(request):
    query = request.GET.get("q", "").strip()
    properties = Property.objects.all()
    parsed = {}

    def convert_budget(amount, unit=None):
        amount = Decimal(amount.replace(",", ""))
        unit = (unit or "").lower()

        if unit.startswith("crore") or unit == "cr":
            return amount * Decimal("10000000")

        if unit.startswith("lakh") or unit.startswith("lac") or unit == "l":
            return amount * Decimal("100000")

        return amount

    if query:
        text = query.lower()

        bhk = re.search(r"\b(\d+)\s*[- ]?bhk\b", text)

        if bhk:
            parsed["bhk"] = int(bhk.group(1))
            properties = properties.filter(bhk=parsed["bhk"])

        types = ["apartment", "villa", "flat", "house", "plot"]

        for item in types:
            if re.search(rf"\b{item}s?\b", text):
                value = "apartment" if item == "flat" else item
                parsed["property_type"] = value
                properties = properties.filter(
                    property_type__iexact=value
                )
                break

        budget_range = re.search(
            r"\bbetween\s+(?:₹|rs\.?\s*|inr\s*)?"
            r"([\d,.]+)\s*(crores?|cr|lakhs?|lacs?|l)?"
            r"\s*(?:and|to|-)\s*"
            r"(?:₹|rs\.?\s*|inr\s*)?"
            r"([\d,.]+)\s*(crores?|cr|lakhs?|lacs?|l)?\b",
            text,
        )

        if budget_range:
            first_amount = budget_range.group(1)
            first_unit = budget_range.group(2)
            second_amount = budget_range.group(3)
            second_unit = budget_range.group(4)

            if first_unit:
                min_budget = convert_budget(first_amount, first_unit)
            elif second_unit:
                min_budget = convert_budget(first_amount, second_unit)
            else:
                min_budget = convert_budget(first_amount)

            max_budget = convert_budget(
                second_amount,
                second_unit or first_unit
            )

            if min_budget > max_budget:
                min_budget, max_budget = max_budget, min_budget

            parsed["min_budget"] = min_budget
            parsed["max_budget"] = max_budget

            properties = properties.filter(
                price__gte=min_budget,
                price__lte=max_budget,
            )

        else:
            budget = re.search(
                r"\b(?:under|below|within|less than|maximum|max|"
                r"budget of|up to|upto)\s+"
                r"(?:₹|rs\.?\s*|inr\s*)?"
                r"([\d,.]+)\s*(crores?|cr|lakhs?|lacs?|l)?\b",
                text,
            )

            if budget:
                max_budget = convert_budget(
                    budget.group(1),
                    budget.group(2)
                )

                parsed["max_budget"] = max_budget

                properties = properties.filter(
                    price__lte=max_budget
                )

        if "garden" in text:
            parsed["garden"] = True
            properties = properties.filter(garden=True)

        parking = re.search(
            r"\b(\d+)\s*(?:car\s*)?parking"
            r"(?:\s+spaces?)?\b",
            text,
        )

        if parking:
            parsed["parking_spaces"] = int(parking.group(1))

            properties = properties.filter(
                parking_spaces__gte=parsed["parking_spaces"]
            )

        locations = Property.objects.values_list(
            "location",
            flat=True
        ).distinct()

        for location in locations:
            if location and location.lower() in text:
                parsed["location"] = location

                properties = properties.filter(
                    location__iexact=location
                )
                break

    return render(
        request,
        "properties/search.html",
        {
            "query": query,
            "parsed": parsed,
            "properties": properties,
        },
    )
