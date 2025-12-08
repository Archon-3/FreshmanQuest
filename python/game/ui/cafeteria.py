from ..popup import Popup


def build_popup(h):
    s = h['state']
    p = Popup("Cafeteria")
    p.add_line("Grab a meal and recharge.")

    def get_coupon():
        if not s.flags['mealCoupon']:
            s.flags['mealCoupon'] = True
            h['addItem']('Meal Coupon')
            h['toast']('Meal coupon collected')
            h['rebuild']()

    def eat():
        if not s.flags['ateMeal'] and s.flags['mealCoupon']:
            s.flags['ateMeal'] = True
            h['setEnergy'](100)
            h['addXP'](5)
            h['completeQuest']('eatMeal')
            h['toast']('Meal eaten (+5 XP, energy 100)')
            h['rebuild']()

    p.add_button(
        "Get Meal Coupon",
        get_coupon,
        primary=False,
        disabled=s.flags['mealCoupon']
    )
    p.add_button(
        "Eat Meal (+5 XP, Energy 100)",
        eat,
        primary=True,
        disabled=s.flags['ateMeal'] or not s.flags['mealCoupon']
    )
    return p
