import matplotlib.pyplot as plt
import numpy as np

# Data
methods = ['Vector Search', 'Keyword Search', 'Hybrid (RRF)']
hit_rate = [65, 52, 88]  # Percent
mrr = [0.62, 0.48, 0.84]

plt.style.use('seaborn-v0_8-muted')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

bars1 = ax1.bar(methods, hit_rate, color=['#A8DADC', '#457B9D', '#E63946'])
ax1.set_title('Порівняння Hit Rate @5 (%)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Відсоток успішного пошуку')
ax1.set_ylim(0, 100)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}%', ha='center', fontweight='bold')

bars2 = ax2.bar(methods, mrr, color=['#A8DADC', '#457B9D', '#E63946'])
ax2.set_title('Порівняння MRR (Якість ранжування)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Середній зворотний ранг')
ax2.set_ylim(0, 1.0)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f'{yval:.2f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('search_benchmark_results.png', dpi=300)
plt.show()