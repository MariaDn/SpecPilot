import matplotlib.pyplot as plt
import numpy as np

systems = ['Baseline (Zero-shot)', 'Розроблений АІ-асистент']
stability_scores = [67.5, 85.0]
variance = [10.6, 3.5]

plt.figure(figsize=(10, 6))

bars = plt.bar(systems, stability_scores, color=['#e74c3c', '#1d3557'], alpha=0.8, width=0.5)

plt.errorbar(systems, stability_scores, yerr=variance, fmt='none', ecolor='black', capsize=8, elinewidth=2)

for bar in bars:
  height = bar.get_height()
  plt.text(bar.get_x() + bar.get_width()/2., height + 2,
          f'{height}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

plt.ylabel('Показник стабільності (%)', fontsize=12)
plt.title('Порівняння стабільності генерації: Baseline vs АІ-асистент', fontsize=14, fontweight='bold')
plt.ylim(0, 110)
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('research/results/stability_comparison_ua.png', dpi=300)
print("Графік стабільності збережено")