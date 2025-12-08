(function(){
  window.UI = window.UI || {};
  window.UI.cafeteria = function(container, state, {addXP, addItem, completeQuest, setEnergy}){
    const root = document.createElement('div');
    root.className = 'ui-grid';

    const services = document.createElement('div');
    services.className = 'ui-card';
    const t1 = document.createElement('div'); t1.className = 'ui-title'; t1.textContent = 'Meal Services';
    const row1 = document.createElement('div'); row1.className = 'hstack';
    const couponBtn = document.createElement('button'); couponBtn.className = 'btn'; couponBtn.textContent = state.flags.mealCoupon ? 'Meal Coupon Collected' : 'Get Meal Coupon';
    couponBtn.disabled = !!state.flags.mealCoupon;
    couponBtn.addEventListener('click', function(){ if(state.flags.mealCoupon) return; state.flags.mealCoupon = true; addItem('Meal Coupon'); couponBtn.textContent = 'Meal Coupon Collected'; couponBtn.disabled = true; });
    row1.appendChild(couponBtn);
    services.appendChild(t1); services.appendChild(row1);

    const dining = document.createElement('div');
    dining.className = 'ui-card';
    const t2 = document.createElement('div'); t2.className = 'ui-title'; t2.textContent = 'Dining';
    const row2 = document.createElement('div'); row2.className = 'hstack';
    const eatBtn = document.createElement('button'); eatBtn.className = 'btn primary'; eatBtn.textContent = state.flags.ateMeal ? 'Meal Eaten' : 'Eat Meal (+5 XP, Energy 100)';
    eatBtn.disabled = !!state.flags.ateMeal || !state.flags.mealCoupon;
    eatBtn.addEventListener('click', function(){ if (state.flags.ateMeal || !state.flags.mealCoupon) return; state.flags.ateMeal = true; setEnergy(100); addXP(5); completeQuest('eatMeal'); eatBtn.textContent = 'Meal Eaten'; eatBtn.disabled = true; });
    row2.appendChild(eatBtn);
    dining.appendChild(t2); dining.appendChild(row2);

    root.appendChild(services);
    root.appendChild(dining);
    container.appendChild(root);
  };
})();
