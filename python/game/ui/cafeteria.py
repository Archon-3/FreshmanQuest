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
            h['addStress'](-5)  # Eating reduces stress
            h['addReputation'](2)  # Socializing at cafeteria
            h['completeQuest']('eatMeal')
            h['toast']('Meal eaten (+5 XP, Energy 100, -5 Stress, +2 Reputation)')
            h['rebuild']()
        elif s.flags['mealCoupon'] and s.energy < 80:
            # Can eat again if energy is low (but no quest completion)
            h['setEnergy'](min(100, s.energy + 30))
            h['addStress'](-3)
            h['addReputation'](1)
            h['toast']('Meal eaten (Energy +30, -3 Stress, +1 Reputation)')

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
