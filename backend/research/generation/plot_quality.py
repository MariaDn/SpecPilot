import matplotlib.pyplot as plt
import numpy as np

metrics = ['Структура', 'Фактологія', 'Стиль', 'Загальний бал']
baseline_scores = [0, 0, 5, 5]
enhanced_scores = [40, 40, 10, 90]

x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, baseline_scores, width, label='Baseline (Zero-shot)', color='#e74c3c', alpha=0.8)
rects2 = ax.bar(x + width/2, enhanced_scores, width, label='Enhanced (Ours)', color='#1d3557', alpha=0.9)

ax.set_ylabel('Бали (Score)')
ax.set_title('Оцінка якості та комплаєнсу (ДСТУ 3008)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 125) 
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.3)

def autolabel(rects):
  for rect in rects:
    height = rect.get_height()
    ax.annotate(f'{height}',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), 
                textcoords="offset points",
                ha='center', va='bottom', fontweight='bold')

autolabel(rects1)
autolabel(rects2)

plt.tight_layout()
plt.savefig('research/results/quality_comparison_ua.png', dpi=300)
print("Графік якісного порівняння збережено")