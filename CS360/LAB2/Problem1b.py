import matplotlib.pyplot as plt
from Problem1a import df

plt.rcParams.update({'figure.figsize':(10,8), 'figure.dpi':100})
plt.scatter(df['YearsExperience'], df['Salary'], color='blue', alpha=0.7)
plt.title('Salary vs Years of Experience')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
import os
img_path = os.path.join(os.path.dirname(__file__), 'salary_vs_experience.png')
plt.savefig(img_path, dpi=300, bbox_inches='tight')
plt.show()
