import matplotlib.pyplot as plt
import numpy as np

# Set up the figure with multiple subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Social Media Demographics: YouTube, Reddit, and Bluesky', fontsize=16, fontweight='bold', y=0.98)

# Adjust spacing between subplots
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. Gender Distribution
platforms = ['YouTube', 'Reddit', 'Bluesky']
male_percentages = [54, 65, 62]
female_percentages = [46, 35, 38]

x = np.arange(len(platforms))
width = 0.35

bars1 = ax1.bar(x - width/2, male_percentages, width, label='Male', color='#4ECDC4')
bars2 = ax1.bar(x + width/2, female_percentages, width, label='Female', color='#FF6B6B')

ax1.set_xlabel('Platform')
ax1.set_ylabel('Percentage (%)')
ax1.set_title('Gender Distribution')
ax1.set_xticks(x)
ax1.set_xticklabels(platforms)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add percentage labels
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{height}%', ha='center', va='bottom')

for bar in bars2:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{height}%', ha='center', va='bottom')

# 2. Age Distribution (Primary age groups where data available)
age_platforms = ['Reddit', 'Bluesky']
age_18_29 = [45, 26]  # Reddit: 45%, Bluesky: 18-24 age group
age_30_plus = [55, 74]  # Remaining percentages

x_age = np.arange(len(age_platforms))
bars3 = ax2.bar(x_age - width/2, age_18_29, width, label='18-29 years', color='#96CEB4')
bars4 = ax2.bar(x_age + width/2, age_30_plus, width, label='30+ years', color='#FFEAA7')

ax2.set_xlabel('Platform')
ax2.set_ylabel('Percentage (%)')
ax2.set_title('Age Distribution (Available Data)')
ax2.set_xticks(x_age)
ax2.set_xticklabels(age_platforms)
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# Add percentage labels
for bar in bars3:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{height}%', ha='center', va='bottom')

for bar in bars4:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{height}%', ha='center', va='bottom')

# 3. Education Level (Reddit only - most complete data)
education_categories = ['College Degree+', 'Other Education']
education_percentages = [46, 54]

colors = ['#DDA0DD', '#87CEEB']
wedges, texts, autotexts = ax3.pie(education_percentages, labels=education_categories, 
                                  colors=colors, autopct='%1.0f%%', startangle=90)
ax3.set_title('Education Level (Reddit Users)')

# 4. Income Level (Reddit only - most complete data)
income_categories = ['75%-200%+ of Median', 'Other Income Levels']
income_percentages = [56, 44]

colors2 = ['#98FB98', '#F0E68C']
wedges2, texts2, autotexts2 = ax4.pie(income_percentages, labels=income_categories, 
                                     colors=colors2, autopct='%1.0f%%', startangle=90)
ax4.set_title('Income Level (Reddit Users)')

plt.tight_layout()

# Save the chart locally
plt.savefig('social_media_demographics.png', dpi=300, bbox_inches='tight')

plt.show()

# Print summary statistics
print("\n" + "="*50)
print("SOCIAL MEDIA DEMOGRAPHICS SUMMARY")
print("="*50)
print("\nGENDER DISTRIBUTION:")
for i, platform in enumerate(platforms):
    print(f"{platform}: {male_percentages[i]}% male, {female_percentages[i]}% female")

print(f"\nAGE INSIGHTS:")
print(f"• Reddit: 45% are 18-29 years old, 40% are 30-49 years old")
print(f"• Bluesky: 62% of users are under 34 (Gen Z and Millennials)")
print(f"• YouTube: Attracts users across all age groups")

print(f"\nEDUCATION & INCOME (Reddit):")
print(f"• 46% have college degree or higher")
print(f"• 56% have income 75%-200%+ of median")

print(f"\nKEY OBSERVATIONS:")
print(f"• All three platforms are male-dominated")
print(f"• Reddit and Bluesky skew younger and more educated")
print(f"• YouTube has the most balanced demographics")
print("="*50)
