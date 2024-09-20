import pandas as pd
import streamlit as st
import plotly.express as px

#st.set_page_config(layout="wide")

color_map = {'Netflix': '#1f77b4', 'Tinder': '#ff7f0e', 'Clash of Clans': '#2ca02c', 
             'Brawl Stars': '#d62728', 'Clash Royale': '#9467bd', 'myCANAL': '#8c564b', 
             'Candy Crush Saga': '#e377c2', 'Homescapes': '#7f7f7f'}

# Application title
st.title('Impact of Lockdown on Mobile App Monetization')

# Load data
df = pd.read_csv('files/enriched_transactions.csv')

# Convert 'year_month' column to datetime
df['year_month'] = pd.to_datetime(df['year_month'], format='%Y-%m')

# Define periods
pre_lockdown_end = pd.Timestamp('2020-03-15')
during_lockdown_end = pd.Timestamp('2020-05-31')

# Calculate metrics for each period
df_pre = df[df['year_month'] < pre_lockdown_end]
df_during = df[(df['year_month'] >= pre_lockdown_end) & (df['year_month'] <= during_lockdown_end)]
df_post = df[df['year_month'] > during_lockdown_end]

def calculate_metrics(df):
    return df.groupby('year_month').agg({
        'order_total_paid': ['sum', 'mean', 'count']
    }).reset_index()

metrics_pre = calculate_metrics(df_pre)
metrics_during = calculate_metrics(df_during)
metrics_post = calculate_metrics(df_post)

# Prepare data for charts
metrics_pre.columns = ['year_month', 'total_pre', 'average_pre', 'frequency_pre']
metrics_during.columns = ['year_month', 'total_during', 'average_during', 'frequency_during']
metrics_post.columns = ['year_month', 'total_post', 'average_post', 'frequency_post']

# Merge data
metrics = pd.merge(pd.merge(metrics_pre, metrics_during, on='year_month', how='outer'),
                   metrics_post, on='year_month', how='outer')

# Add columns for period changes
metrics['period'] = 'Before Lockdown'
metrics.loc[metrics['year_month'] >= pre_lockdown_end, 'period'] = 'During Lockdown'
metrics.loc[metrics['year_month'] > during_lockdown_end, 'period'] = 'After Lockdown'

# Display charts over time
st.header('What is the market like?')

# Total In-App Purchases
st.subheader('Total In-App Purchases')
st.line_chart(metrics.set_index('year_month')[['total_pre', 'total_during', 'total_post']])

# Average Purchase Value
st.subheader('Average Purchase Value')
st.line_chart(metrics.set_index('year_month')[['average_pre', 'average_during', 'average_post']])

# Purchase Frequency
st.subheader('Purchase Frequency')
st.line_chart(metrics.set_index('year_month')[['frequency_pre', 'frequency_during', 'frequency_post']])

# Conclusion
st.subheader('Conclusion')
st.write("""**Moderate impact on total purchases**: The lockdown temporarily reduced purchases, contrary to the idea that users might have spent more online. However, the recovery after the lockdown shows a return of activity.
        \n**Reduction in purchase value**: The lockdown saw a notable decrease in purchase value, likely related to consumer caution during a period of economic uncertainty.
        \n**Increase in frequency after the lockdown**: Although frequency did not spike during the lockdown, it slightly increased afterward, perhaps as people regained some stability.""")

# Revenue by app
st.header('Analysis per app')

def plot_pie_chart(data, title):
    revenue_per_app = data.groupby('app_title')['order_total_paid'].sum().reset_index()
    fig = px.pie(revenue_per_app, values='order_total_paid', names='app_title',
                 color='app_title', color_discrete_map=color_map, title=title)
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0),  # Reduce margins to avoid empty space
                      height=400,  # Adjust height for optimal rendering
                      width=400)  # Adjust width for optimal rendering
    return fig

# Display "During Lockdown" pie chart
fig_during = plot_pie_chart(df_during, 'Revenue Distribution (During Lockdown)')
st.plotly_chart(fig_during, use_container_width=True)

# Display "Before" and "After" Lockdown charts side by side
col1, col2 = st.columns(2)  # Two columns
with col1:
    fig_pre = plot_pie_chart(df_pre, 'Revenue Distribution (Before Lockdown)')
    st.plotly_chart(fig_pre, use_container_width=True)

with col2:
    fig_post = plot_pie_chart(df_post, 'Revenue Distribution (After Lockdown)')
    st.plotly_chart(fig_post, use_container_width=True)

# Conclusion
st.subheader('**Conclusion:**')
st.write("""The analysis of revenues before, during, and after the lockdown **reveals clear trends**:
\n**Before the Lockdown**: Netflix led the revenue with various subscriptions, while Tinder and games like Clash of Clans also made significant contributions.
\n**During the Lockdown**: Disney+ saw a dramatic increase in revenue, reflecting strong demand for streaming. Netflix performed well and myCANAL also experienced a rise.
\n**After the Lockdown**: Disney+ and Tinder continued to generate high revenues. Netflix remained strong, and games like Clash of Clans and Brawl Stars gained popularity, marking a return to interactive entertainment.
\n\nIn summary, the lockdown period favored streaming services, while the post-lockdown phase saw a broader diversification of revenues towards games and online entertainment services.""")

def plot_bar_chart(data, title):
    fig = px.bar(data, x='product_name', y='order_total_paid', 
                 title=title, text='order_total_paid')
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=600,  # Increase the chart height for better visibility
        margin=dict(b=200),  # Increase bottom margin to accommodate labels
    )
    
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')  # Display values outside bars

    return fig

# Top 10 transactions by period
def top_10_transactions_grouped(df, period_name):
    df_transactions = df.groupby(['app_title', 'product_name'])['order_total_paid'].sum().reset_index()
    sorted_transactions = df_transactions.sort_values('order_total_paid', ascending=False).head(10)
    return sorted_transactions

# Top 10 transactions before the lockdown
top_10_pre = top_10_transactions_grouped(df_pre, 'Before Lockdown')
st.subheader('Top 10 Transactions Before Lockdown')
st.bar_chart(top_10_pre, x='product_name', y='order_total_paid')

# Top 10 transactions during the lockdown
top_10_during = top_10_transactions_grouped(df_during, 'During Lockdown')
st.subheader('Top 10 Transactions During Lockdown')
st.bar_chart(top_10_during, x='product_name', y='order_total_paid')

# Top 10 transactions after the lockdown
top_10_post = top_10_transactions_grouped(df_post, 'After Lockdown')
st.subheader('Top 10 Transactions After Lockdown')
st.bar_chart(top_10_post, x='product_name', y='order_total_paid')

st.subheader('**Conclusion:**')
st.write("""The analysis of transactions before, during, and after the lockdown **reveals clear trends**:
\n**Before the Lockdown**: Netflix led the revenue with various subscriptions, while Tinder and games like Clash of Clans also made significant contributions.
\n**During the Lockdown**: Disney+ saw a dramatic increase in revenue, reflecting strong demand for streaming. Netflix performed well and myCANAL also experienced a rise.
\n**After the Lockdown**: Disney+ and Tinder continued to generate high revenues. Netflix remained strong, and games like Clash of Clans and Brawl Stars gained popularity, marking a return to interactive entertainment.
\n\nIn summary, the lockdown period favored streaming services, while the post-lockdown phase saw a broader diversification of revenues towards games and online entertainment services.""")

st.header('Summary of Key Insights')
st.write("""
**Temporary Shift in Behavior**: The lockdown period created a temporary shift in consumer behavior, prioritizing streaming services due to increased time at home and a need for passive entertainment.
\n**Economic Impact on Spending Patterns**: Users exhibited economic caution during the lockdown, reflected in lower average transaction values. This cautious spending was mitigated post-lockdown as economic conditions stabilized.
\n**Diversification Post-Lockdown:** The return of interactive apps to the top of the revenue charts highlights a post-lockdown normalization, where consumers balanced their engagement between passive and interactive digital content.
\n**Market Resilience**: The mobile app market showed remarkable resilience and adaptability, with revenues rebounding and diversifying post-lockdown, demonstrating its capacity to meet evolving consumer demands.
\nIn conclusion, while the lockdown initially constrained spending and skewed usage patterns towards streaming, the overall market proved robust, bouncing back with diversified revenue streams and strong consumer engagement across different app categories.
""")