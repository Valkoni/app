# app.py
import json
import os
from abc import ABC, abstractmethod

# Импорт към shim-а (или реалния streamlit, ако е инсталиран)
import streamlit as st

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
}

city_info = {
    "София": {
        "hotel": ("Hotel Sofia Center", 70),
        "food": ("Традиционна българска кухня", 20),
        "sight": "Катедралата Александър Невски"
    },
    "Белград": {
        "hotel": ("Belgrade Inn", 65),
        "food": ("Сръбска скара", 22),
        "sight": "Калемегдан"
    },
    "Виена": {
        "hotel": ("Vienna City Hotel", 90),
        "food": ("Виенски шницел", 30),
        "sight": "Дворецът Шьонбрун"
    },
    "Мюнхен": {
        "hotel": ("Munich Central Hotel", 95),
        "food": ("Немска кухня", 28),
        "sight": "Мариенплац"
    }
}

DISTANCE_BETWEEN_CITIES = 300  # км (опростено)

# ================== OOP ==================


class Transport(ABC):
    def __init__(self, price_per_km):
        self.price_per_km = price_per_km

    @abstractmethod
    def name(self):
        pass

    def travel_cost(self, distance):
        return distance * self.price_per_km


class Car(Transport):
    def __init__(self):
        super().__init__(0.25)

    def name(self):
        return "🚗 Кола"


class Train(Transport):
    def __init__(self):
        super().__init__(0.18)

    def name(self):
        return "🚆 Влак"


class Plane(Transport):
    def __init__(self):
        super().__init__(0.45)

    def name(self):
        return "✈️ Самолет"


# ================== UI / Логика ==================

def calculate_trip(cities, days, transport):
    total_food_cost = 0
    total_hotel_cost = 0
    breakdown = []

    for city in cities:
        info = city_info.get(city, {})
        hotel_name, hotel_price = info.get("hotel", ("Няма данни", 0))
        food_name, food_price = info.get("food", ("Няма данни", 0))
        sight = info.get("sight", "Няма данни")

        city_food = food_price * days
        city_hotel = hotel_price * days

        total_food_cost += city_food
        total_hotel_cost += city_hotel

        breakdown.append({
            "city": city,
            "hotel": {"name": hotel_name, "per_night": hotel_price, "total": city_hotel},
            "food": {"name": food_name, "per_day": food_price, "total": city_food},
            "sight": sight
        })

    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)
    total_cost = transport_cost + total_food_cost + total_hotel_cost

    return {
        "breakdown": breakdown,
        "transport_cost": transport_cost,
        "food_cost": total_food_cost,
        "hotel_cost": total_hotel_cost,
        "total_distance": total_distance,
        "total_cost": total_cost
    }


def main():
    st.title("🌍 Интерактивен туристически планер (разширена версия)")

    # Възможност да добавиш нов маршрут (креативно разширение)
    st.markdown("### ✨ Управление на маршрути")
    if st.button("Добави примерен маршрут"):
        # добавяме примерен маршрут, ако го няма
        routes.setdefault("Балкани тур", ["Пловдив", "Скопие", "Тирана"])
        city_info.setdefault("Пловдив", {
            "hotel": ("Plovdiv Cozy", 60),
            "food": ("Родопска кухня", 18),
            "sight": "Старинен Пловдив"
        })
        city_info.setdefault("Скопие", {
            "hotel": ("Skopje Hotel", 55),
            "food": ("Македонска кухня", 17),
            "sight": "Камен мост"
        })
        city_info.setdefault("Тирана", {
            "hotel": ("Tirana Stay", 50),
            "food": ("Албанска кухня", 16),
            "sight": "Площад Скендербег"
        })
        st.success("Добавен маршрут 'Балкани тур' и примерни градове.")

    route_choice = st.selectbox("Избери маршрут:", list(routes.keys()))

    # Позволяваме потребителят да редактира списъка с градове (кратко)
    cities = routes[route_choice].copy()
    st.markdown("**Градове в маршрута:** " + ", ".join(cities))

    transport_choice = st.selectbox("Превозно средство:", ["Кола", "Влак", "Самолет"])

    days = st.slider("Брой дни за пътуването:", 1, 14, 4)

    budget = st.number_input("Твоят бюджет (лв):", 100, 20000, 1500)

    # Малко персонализация: избор на приоритет (евтино / комфорт / бързо)
    priority = st.selectbox("Приоритет при планиране:", ["Баланс", "Най-евтино", "Комфорт", "Бързо"])

    # Избор на транспорт (полиморфизъм)
    if transport_choice == "Кола":
        transport = Car()
    elif transport_choice == "Влак":
        transport = Train()
    else:
        transport = Plane()

    # Кнопка за планиране
    if st.button("Планирай пътуването 🧭"):
        result = calculate_trip(cities, days, transport)

        st.subheader("🗺️ Маршрут")
        st.write(" ➡️ ".join(cities))

        st.subheader("🏙️ Спирки и предложения")
        for item in result["breakdown"]:
            st.markdown(f"### 📍 {item['city']}")
            st.write(f"🏨 **Хотел:** {item['hotel']['name']} – {item['hotel']['per_night']} лв/нощ")
            st.write(f"🍽️ **Храна:** {item['food']['name']} – {item['food']['per_day']} лв/ден")
            st.write(f"🏛️ **Забележителност:** {item['sight']}")
            st.write(f"🔢 Разходи за този град: Хотел {item['hotel']['total']:.2f} лв; Храна {item['food']['total']:.2f} лв")

        st.subheader("💰 Разходи")
        st.write(f"{transport.name()} – транспорт: {result['transport_cost']:.2f} лв")
        st.write(f"🍽️ Храна: {result['food_cost']:.2f} лв")
        st.write(f"🏨 Хотели: {result['hotel_cost']:.2f} лв")
        st.write(f"📏 Общо разстояние: {result['total_distance']} км")

        st.markdown("---")
        st.write(f"## 💵 Общ бюджет: **{result['total_cost']:.2f} лв**")

        # Препоръки според приоритет
        if result['total_cost'] <= budget:
            st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨")
        else:
            st.error("❌ Бюджетът не достига. Помисли за по-евтин транспорт или по-малко дни.")
            if priority == "Най-евтино":
                st.write("- Съвет: избери Влак или намали броя дни.")
            elif priority == "Комфорт":
                st.write("- Съвет: запази избрания транспорт, но намали градовете.")
            elif priority == "Бързо":
                st.write("- Съвет: използвай Самолет за по-малко време в пътуване.")

        # Възможност за записване на плана в JSON (по желание на потребителя)
        if st.button("Запази плана като JSON"):
            plan = {
                "route": cities,
                "days": days,
                "transport": transport.name(),
                "breakdown": result["breakdown"],
                "costs": {
                    "transport": result["transport_cost"],
                    "food": result["food_cost"],
                    "hotel": result["hotel_cost"],
                    "total": result["total_cost"]
                }
            }
            filename = "trip_plan.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            st.success(f"Планът е записан в {os.path.abspath(filename)}")

    # Малък footer / помощ
    st.markdown("---")
    st.write("Съвет: Ако имаш инсталиран Streamlit, стартирай с `streamlit run app.py` за пълно интерактивно преживяване.")

if __name__ == "__main__":
    main()
