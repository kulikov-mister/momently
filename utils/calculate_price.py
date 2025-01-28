async def calculate_price(distance):
    # Простое сопоставление расстояния со стоимостью
    price_list = {1: 140, 2: 160, 3: 170, 4: 180, 5: 190, 6: 200, 7: 210, 8: 220, 9: 230, 10: 240}

    for i in reversed(sorted(price_list.keys())):
        if distance >= i:
            return price_list[i]
    return None  # В случае, если расстояние меньше 1 км
