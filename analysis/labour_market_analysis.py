import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print('PYTHON SCRIPT STARTED')

df1=pd.read_csv('(1) graduate employment survey modified.csv')
df2=pd.read_csv('(2) graduate employment survey modified .csv')
df3=pd.read_excel('LFR2023_SectionF.xlsx',sheet_name='F1', skiprows=5) #F1
df5=pd.read_excel('LFR2023_SectionF.xlsx',sheet_name='F2', skiprows=5) #F2
df4=pd.read_excel('mrsd_19_retrench_perm_by_ind_and_occ_grp.xlsx', sheet_name='2006-2025(SSIC2020)', skiprows=2)


# Noted that there are NAN (missing values) and also data with the literal 'na'. Convert all to NAN.
df2= df2.replace('na', np.nan)
# drop every column where theres NAN in all the rows (Chunk of unnamed rows)
df2 = df2.dropna(axis=1, how='all') 
df_merged = df1.merge(df2, on='Key', how='left') 



df_merged = df_merged.dropna(subset=['basic_monthly_mean']) 
# no specific reason to use basic_monthly_mean, as nan values are common across all df2 columns
salary_cols = df_merged.columns[5:]   

# Every column after index 5 is a integer val, hence we convert to float
df_merged[salary_cols] = df_merged[salary_cols].apply(pd.to_numeric, errors='coerce')
# There are values where the value is not a number, hence we drop these
df_merged = df_merged.dropna(subset=salary_cols, how='all')



df3.drop(df3.index[-2:], inplace=True) #remove source and nan at end

# Make first row into column head(years)

df3.columns = df3.iloc[0] 
df3 = df3.iloc[1:].reset_index(drop=True)

df3 = df3.copy()

new_cols = df3.columns.tolist()
new_cols[0] = 'employcat'
new_cols[1] = 'hours_worked'
df3.columns = new_cols

df3['employcat'] = df3['employcat'].ffill()
df3melt = df3.melt(
    id_vars=['employcat','hours_worked'],
    var_name='year',
    value_name='employees'
)

df3melt['employees'] = df3melt['employees'] * 1000
df3melt['employees'] = df3melt['employees'].astype(int)
df3melt['year'] = df3melt['year'].astype(int)




# Make all year into column headers
# Make all year into column headers
new_header = df4.loc[0].astype(str).tolist()
df4.columns = new_header

# remove unneccessary rows in head and tail
df4.drop(df4.index[0], inplace=True)
df4.drop(df4.index[-7:], inplace=True)

# remove quarterly data (irrelevant for us)
df4.drop(['1Q','2Q','3Q','4Q'], axis=1, errors='ignore', inplace=True)
df4 = df4.drop(columns=['2025'], errors='ignore')

# rename 2nd column to industry
df4 = df4.copy()
new_cols = df4.columns.tolist()
new_cols[1] = 'industry'
df4.columns = new_cols

# drop rows where all years are NA
df4.dropna(subset=df4.columns[2:], how='all', inplace=True)

# replace '-' with 0
df4 = df4.replace('-', 0)

# melt to long
# melt to long
df4 = df4.melt(
    id_vars=['industry'],
    var_name='year',
    value_name='employees'
)

df4['year'] = pd.to_numeric(df4['year'], errors='coerce')
df4 = df4.dropna(subset=['year'])
df4['year'] = df4['year'].astype(int)

df4['employees'] = pd.to_numeric(df4['employees'], errors='coerce')
df4 = df4.dropna(subset=['employees'])
df4['employees'] = df4['employees'].astype(int)



# DF_MERGED DATA MAPPING


df4sect = df4[(df4['industry'].str.isupper()) & (df4['industry'] != 'TOTAL') & (df4['industry'] != 'OTHERS*')] 
sectorlist = df4sect['industry'].unique()

# List of keywords relating to each sector
sectorkey = {
    'INFORMATION AND COMMUNICATIONS': [
        'comput', 'software', 'data', 'infocomm', 'digital', 'it', 'communication studies', 'systems'
    ],
    'FINANCIAL AND INSURANCE SERVICES': [
        'account', 'finance', 'banking', 'insurance', 'actuarial', 'economics'
    ],
    'REAL ESTATE SERVICES': [
        'real estate', 'property'
    ],
    'MANUFACTURING': [
        'engineering', 'manufacture', 'mechanical', 'electrical', 'aerospace', 'industrial', 'applied science'
    ],
    'COMMUNITY, SOCIAL AND PERSONAL SERVICES': [
        'medicine', 'nursing', 'health', 'pharmacy', 'social', 'psychology', 
        'sociology', 'education', 'sports', 'chinese', 'english', 'linguistic', 'arts', 'dental'
    ],
    'CONSTRUCTION': [
        'civil', 'construction', 'built environment'
    ],
    'TRANSPORTATION AND STORAGE': [
        'logistics', 'supply chain', 'maritime', 'aviation', 'transport'
    ],
    'SERVICES': [
        'business', 'management', 'administration', 'marketing', 'hr', 'human resource'
    ],
    'PROFESSIONAL SERVICES': [
        'law', 'legal', 'architecture', 'design', 'consulting', 'bio', 'chem', 'math', 'science', 'physics'
    ]
}


def map(degree):
    degree = degree.lower()
    for sector, keywords in sectorkey.items():
        for kw in keywords:
            if kw in degree:
                return sector

    return 'OTHERS'

df_merged['Sector'] = df_merged['degree'].apply(map)

df_merged=df_merged.drop(columns=['school']) 
# not safe to use school, as it still has na values. we drop it because it is irrelevant to us


# ===== FIX DF5 HEADERS (EXACT SAME AS DF3) =====

df5.drop(df5.index[-5:], inplace=True)  # remove source and nan at end

# Make first row into column head (years)
df5.columns = df5.iloc[0]
df5 = df5.iloc[1:].reset_index(drop=True)

df5 = df5.copy()
new_cols = df5.columns.tolist()
new_cols[0] = 'employcat'
new_cols[1] = 'hours_worked'
df5.columns = new_cols

df5['employcat'] = df5['employcat'].ffill()

# Melt -> industry becomes column
df5 = df5.melt(
    id_vars=['employcat','hours_worked'],
    var_name='industry',
    value_name='employees'
)

# remove Others
df5 = df5[df5['industry'] != 'Others']

df5['employees'] = pd.to_numeric(df5['employees'], errors='coerce')
df5 = df5.dropna(subset=['employees'])
df5['employees'] = df5['employees'].astype(int)


# ==============================
# SINGLE DASHBOARD (6 SUBPLOTS)
# ==============================
fig, axes = plt.subplots(3, 2, figsize=(24,16))

# Define df_plot at the start
df_plot = df_merged.dropna(subset=['employment_rate_overall', 'Sector'])

# Graph1: Total retrenchment over time
ax1 = axes[0, 0]

ret_total = df4[df4['industry']=='TOTAL']
ax1.plot(ret_total['year'], ret_total['employees'])

# Shade COVID-19 period , alpha is transparency
ax1.axvspan(2019, 2021, alpha=0.6, label='COVID-19 period')

# Labels and title
ax1.set_title('Total Retrenchments in Singapore Over Time')
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Retrenchments')
ax1.set_xticks(ret_total['year'])
ax1.set_xticklabels(ret_total['year'], rotation=45)
ax1.legend()




# Interpretation: As seen in the graph, the retrenchment rate fluctuates, for example based on social situations like covid 19. Even though there is an overall increasing trend, individual sectors may affect the retrenchment rates.



# Graph 2:
ax2 = axes[0, 1]
# Graph2: Retrenchment Split by sectors

df4sect = df4[(df4['industry'].str.isupper()) & (df4['industry'] != 'TOTAL')] 
# Get all sectors (since sectors is uppercase)

top5sects = (df4sect.groupby('industry')['employees'].sum().sort_values(ascending=False).head(5).index)

# get df, where years are between 2018 and 2014, and industry only includes top 5 sectors with highest retrenchment
df4sect = df4sect[df4sect['industry'].isin(top5sects)]
df4sect = df4sect[df4sect['year'].between(2018, 2024)]



stack_data = (
    df4sect
    .groupby(['year', 'industry'])['employees']
    .sum()
    .unstack()
    .sort_index()
)


stack_data.plot(kind='bar',ax=ax2)

ax2.set_title('Retrenchments by Sector Over Time')
ax2.set_xlabel('Year')
ax2.set_ylabel('Number of Retrenchments')
ax2.tick_params(axis='x', rotation=45)
ax2.legend(title='Sector', fontsize=8)




# graph 3: Employment rate by sector

ax3 = axes[1,0]

# Create the Boxplot
sns.boxplot(
    data=df_plot, 
    x='employment_rate_overall', 
    y='Sector',
    ax=ax3
)

ax3.axvline(90, color='r', linestyle='-', alpha=0.3)
ax3.set_title('Employment rate of graduates by  Sector')
ax3.set_xlabel('Employment Rate (%)')

# Graph 4: median gross monthly salary by sector
ax4 = axes[1, 1]
top_sectors = df_merged.groupby('Sector')['gross_monthly_median'].median().sort_values(ascending=False).head(10)
top_sectors.plot(kind='barh', ax=ax4)
ax4.set_title('Top Sectors by Median Gross Monthly Salary')
ax4.set_xlabel('Median Monthly Salary (SGD)')

# Graph 5: Salary vs. Full-Time Employment Rate
ax5 = axes[2, 0]
sns.scatterplot(data=df_merged, x='employment_rate_ft_perm', y='gross_monthly_median', alpha=0.7, ax=ax5)
ax5.set_title('Salary vs. Full-Time Employment Rate')
ax5.set_xlabel('Full-Time Employment Rate (%)')
ax5.set_ylabel('Median Monthly Gross Salary (SGD)')
ax5.grid(True, linestyle='--', alpha=0.6)

# Graph 6: Workers working more than 48 hours
ax6 = axes[2, 1]
workers = df5[(df5['hours_worked']=='More Than 48 Hours') & (df5['employcat']=='Total') & (df5['industry'] != 'Total')]
count = workers['employees']
labels = workers['industry']
ax6.pie(count, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
ax6.set_title('Number of Workers Working More Than 48 Hours in Different Sectors')

fig.tight_layout()

plt.savefig("dashboard.png", dpi=200, bbox_inches="tight")

# ==============================
# PRINTED ANALYSIS (FOR UIPATH)
# ==============================
Analysis1 = 'As seen in the graph, the retrenchment rate fluctuates, for example based on social situations like COVID-19. Even though there is an overall increasing trend, individual sectors may affect the retrenchment rates.'
Analysis2 = 'The general trend (in the last 5 years 2018–2024) is that Services and Manufacturing sectors consist of the majority retrenchment rate. There is higher risk for people working in Services and Manufacturing sectors.'

Analysis3 = '''
Median employment rate is highest for graduates from Financial and Insurance services, while lowest for graduates from Manufacturing (excluding other degrees)
    - This tells us that graduates from Financial and Insurance services have the highest average chance of getting employment, while graduates from manufacturing has the lowest average chance of getting employment
The distribution of employment rate is highest for graduates from professional services, while lowest for real estate services graduates.
    - Despite the relatively high median employment rate, graduates from professional services do not always get employed.
    - Graduates from real estate services have generally a high chance of getting employment.'''

Analysis4 = '''
- Information and Communications offers the highest median monthly salary while Real Estate Services records the lowest.
- However, the overall variation across sectors is relatively small, indicating that median wages are fairly consistent across industries.'''

Analysis5 = 'Most jobs with high employment rates are also paid well. There are still outliers, but this is the general trend (this can be affected by sectors and job roles).'

Analysis6 = '''
- Professionals usually are more prone to working overtime, while craftsmen and related trade workers, as well as labour related jobs require less overtime work
- Overtime work is usually demanded by jobs in higher levels'''

Final_Conclusion = '''
 While retrenchment and workload patterns vary by sector, the strongest predictor of salary is job security rather than working hours. While deciding a job area to work on,choose sectors with low retrenchment rates and high graduate employment for better salary. 
The sectors with highest retrenchment rates are: 
    - Services 
    - Manufacturing
    - Wholesale & Retail Trade
    - Financial & Insurance Services
    - Professional Services

Best sectors to be in are: 
    1. Financial & Insurance Services
    Highest graduate employment rate (>95%)
    High median salary (~$3,500+)
    Average retrenchment rates
    
    2. Professional Services
    High graduate employment rate (>90%)
    High median salary (~$3,500)
    Lower retrenchment risk
    - However these have high overtime


    3. Information & Communications
    Highest salary levels (~$3,600)
    Growing sector
    Moderate employment rates
    Higher retrenchment
    - However these have high overtime

'''

result = f"""
Research question :

How does retrenchment and workload patterns relate to salary outcomes in Singapore over time?
Authors: Ephraim Toji & Han Qian

Analyse Charts:

Graph 1 (Total Retrenchments Over Time): {Analysis1}

Graph 2 (Retrenchments by Sector Over Time): {Analysis2}

Graph 3 (Employment Rate by Sector - Boxplot): {Analysis3}

Graph 4 (Top Sectors by Median Salary): {Analysis4}

Graph 5 (Salary vs Full-Time Employment Rate): {Analysis5}

Graph 6 (Workers >48 Hours by Sector): {Analysis6}

Final Conclusion:
{Final_Conclusion}
"""

print(result)
input("Press Enter to close...")

with open("result.txt", 'w') as f:
    f.write(result)

print('PYTHON RAN SUCCESSFULLY')
