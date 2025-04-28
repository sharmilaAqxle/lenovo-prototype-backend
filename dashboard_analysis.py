import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
from scipy import stats

# Set style for better visualizations
plt.style.use('seaborn-v0_8')  # Updated style name
sns.set_theme()  # Use seaborn's default theme

class LenovoDashboardAnalysis:
    def __init__(self):
        self.base_path = Path("dataset")
        self.semrush_data = {}
        self.google_trends_data = {}
        self.sales_data = {}
        try:
            self.load_data()
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

    def load_data(self):
        """Load all datasets from their respective folders"""
        try:
            # Load SEMrush data
            semrush_path = self.base_path / "Semrush dataset"
            if not semrush_path.exists():
                raise FileNotFoundError(f"SEMrush dataset directory not found at {semrush_path}")
            
            self.semrush_data['lenovo'] = pd.read_excel(semrush_path / "Organic_Search_Lenovo.xlsx")
            self.semrush_data['hp'] = pd.read_excel(semrush_path / "Organic_Search_HP.xlsx")
            self.semrush_data['dell'] = pd.read_excel(semrush_path / "Organic_Search_Dell.xlsx")

            # Load Google Trends data
            trends_path = self.base_path / "Google trends dataset"
            if not trends_path.exists():
                raise FileNotFoundError(f"Google trends dataset directory not found at {trends_path}")
            
            self.google_trends_data['comparison'] = pd.read_excel(trends_path / "Comparison.xlsx")
            self.google_trends_data['web'] = pd.read_excel(trends_path / "Web_Data.xlsx")
            self.google_trends_data['youtube'] = pd.read_excel(trends_path / "Yt Search.xlsx")

            # Load Sales data
            sales_path = self.base_path / "Sales datasets"
            if not sales_path.exists():
                raise FileNotFoundError(f"Sales datasets directory not found at {sales_path}")
            
            self.sales_data['brands'] = pd.read_excel(sales_path / "HP_Dell_Lenovo.xlsx")
            self.sales_data['spend'] = pd.read_excel(sales_path / "Laptop_brands_daily_spend_new.xlsx")
            
            print("All datasets loaded successfully!")
        except Exception as e:
            print(f"Error in load_data: {str(e)}")
            raise

    def analyze_keyword_gaps(self):
        """
        Question 1: Identify keywords where competitors (Dell/HP) dominate but Lenovo underperforms
        This analysis combines:
        1. Google Trends data to identify high-search-volume keywords
        2. SEMrush organic search data to compare performance
        
        Returns:
            DataFrame with analysis of keyword gaps
        """
        # Get Google Trends data for search volume
        web_trends = self.google_trends_data['web']
        youtube_trends = self.google_trends_data['youtube']
        
        # Clean column names and prepare data
        web_trends.columns = web_trends.iloc[0]  # Use first row as headers
        web_trends = web_trends.iloc[1:]  # Remove the header row from data
        
        # Extract relevant metrics
        lenovo_metrics = {
            'organic_traffic': self.semrush_data['lenovo']['Traffic'],
            'organic_keywords': self.semrush_data['lenovo']['Number of Keywords'],
            'commercial_intent': self.semrush_data['lenovo']['Positions with commercial intents in top 20']
        }
        
        hp_metrics = {
            'organic_traffic': self.semrush_data['hp']['Traffic'],
            'organic_keywords': self.semrush_data['hp']['Number of Keywords'],
            'commercial_intent': self.semrush_data['hp']['Positions with commercial intents in top 20']
        }
        
        dell_metrics = {
            'organic_traffic': self.semrush_data['dell']['Traffic'],
            'organic_keywords': self.semrush_data['dell']['Number of Keywords'],
            'commercial_intent': self.semrush_data['dell']['Positions with commercial intents in top 20']
        }
        
        # Calculate performance gaps
        results = []
        
        # Analyze web search trends
        for col in web_trends.columns:
            if 'Lenovo' in str(col):
                lenovo_search = web_trends[col].mean()
                
                # Find corresponding competitor columns
                dell_cols = [c for c in web_trends.columns if 'Dell' in str(c)]
                hp_cols = [c for c in web_trends.columns if 'HP' in str(c)]
                
                # Calculate average competitor performance
                dell_search = web_trends[dell_cols].mean().mean()
                hp_search = web_trends[hp_cols].mean().mean()
                
                # Calculate gap score
                search_volume = lenovo_search
                competitor_avg = (dell_search + hp_search) / 2
                gap_score = competitor_avg - lenovo_search
                
                if gap_score > 0:  # Only include where competitors outperform
                    results.append({
                        'keyword': col.replace(': (United States)', ''),
                        'search_volume': search_volume,
                        'lenovo_performance': lenovo_search,
                        'competitor_avg': competitor_avg,
                        'gap_score': gap_score,
                        'source': 'Web Search'
                    })
        
        # Convert to DataFrame and sort by gap score
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('gap_score', ascending=False)
        
        # Add organic traffic and keyword metrics
        df_results['lenovo_organic_traffic'] = lenovo_metrics['organic_traffic'].mean()
        df_results['competitor_organic_traffic'] = (hp_metrics['organic_traffic'].mean() + 
                                                  dell_metrics['organic_traffic'].mean()) / 2
        
        # Calculate opportunity score
        df_results['opportunity_score'] = (
            df_results['gap_score'] * 
            df_results['search_volume'] * 
            (df_results['competitor_organic_traffic'] / df_results['lenovo_organic_traffic'])
        )
        
        return df_results.sort_values('opportunity_score', ascending=False).head(10)

    def analyze_ad_spend_efficiency(self):
        """
        Question 2: Compare ad spend efficiency across competitors in critical markets
        This analysis:
        1. Analyzes ad spend across different channels (Desktop, Mobile, Social Media)
        2. Compares spend with organic visibility and traffic
        3. Calculates efficiency ratios for different markets
        
        Returns:
            DataFrame with ad spend efficiency metrics
        """
        # Get ad spend data
        spend_data = self.sales_data['spend'].copy()
        
        # Normalize spend data
        for col in spend_data.columns:
            if col != 'date':
                # Convert to numeric, replacing non-numeric values with 0
                spend_data[col] = pd.to_numeric(spend_data[col], errors='coerce').fillna(0)
                # Cap extreme values at 99th percentile
                cap_value = spend_data[col].quantile(0.99)
                spend_data[col] = spend_data[col].clip(upper=cap_value)
        
        # Get organic performance data
        lenovo_organic = self.semrush_data['lenovo']
        hp_organic = self.semrush_data['hp']
        dell_organic = self.semrush_data['dell']
        
        # Calculate total spend by channel
        channel_spend = {
            'Desktop': ['Desktop Display', 'Desktop Video'],
            'Mobile': ['Mobile Display', 'Mobile Video'],
            'Social': ['Facebook', 'Instagram', 'LinkedIn', 'TikTok', 'X'],
            'Video': ['YouTube', 'OTT'],
            'Other': ['Snapchat']
        }
        
        # Calculate efficiency metrics
        results = []
        
        # Analyze by channel
        for channel, columns in channel_spend.items():
            # Calculate total spend for each brand
            valid_columns = [col for col in columns if col in spend_data.columns]
            if valid_columns:
                lenovo_spend = spend_data[valid_columns].sum().sum()
                hp_spend = spend_data[valid_columns].sum().sum()  # Assuming same structure
                dell_spend = spend_data[valid_columns].sum().sum()  # Assuming same structure
                
                # Get organic metrics
                lenovo_traffic = lenovo_organic['Traffic'].mean()
                hp_traffic = hp_organic['Traffic'].mean()
                dell_traffic = dell_organic['Traffic'].mean()
                
                # Calculate efficiency ratios with zero handling
                lenovo_efficiency = lenovo_traffic / (lenovo_spend + 1)  # Add 1 to avoid division by zero
                hp_efficiency = hp_traffic / (hp_spend + 1)
                dell_efficiency = dell_traffic / (dell_spend + 1)
                
                # Calculate relative efficiency with zero handling
                competitor_avg_efficiency = (hp_efficiency + dell_efficiency) / 2
                relative_efficiency = lenovo_efficiency / (competitor_avg_efficiency + 1) if competitor_avg_efficiency > 0 else 0
                
                results.append({
                    'channel': channel,
                    'lenovo_spend': lenovo_spend,
                    'competitor_avg_spend': (hp_spend + dell_spend) / 2,
                    'lenovo_traffic': lenovo_traffic,
                    'competitor_avg_traffic': (hp_traffic + dell_traffic) / 2,
                    'lenovo_efficiency': lenovo_efficiency,
                    'competitor_avg_efficiency': competitor_avg_efficiency,
                    'relative_efficiency': relative_efficiency
                })
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Calculate overall efficiency score
        df_results['efficiency_score'] = (
            df_results['relative_efficiency'] * 
            (df_results['lenovo_traffic'] / (df_results['competitor_avg_traffic'] + 1))
        )
        
        return df_results.sort_values('efficiency_score', ascending=False)

    def analyze_youtube_trends(self):
        """
        Question 3: Identify untapped YouTube search trends where Lenovo's content is underrepresented
        This analysis:
        1. Analyzes YouTube search trends for different product categories
        2. Compares Lenovo's content presence with competitors
        3. Identifies content gaps and opportunities
        
        Returns:
            DataFrame with YouTube trend analysis and content gaps
        """
        # Get YouTube search data
        youtube_data = self.google_trends_data['youtube']
        
        # Clean and prepare data
        youtube_data.columns = youtube_data.iloc[0]
        youtube_data = youtube_data.iloc[1:]
        
        # Define product categories and their search terms
        product_categories = {
            'Laptops': ['laptop', 'notebook', 'ultrabook'],
            'Business': ['business laptop', 'work laptop', 'office laptop'],
            'Gaming': ['gaming laptop', 'gaming pc'],
            'Convertible': ['2 in 1 laptop', 'convertible laptop'],
            'Chromebook': ['chromebook', 'chrome os laptop'],
            'Workstation': ['workstation laptop', 'mobile workstation'],
            'Budget': ['budget laptop', 'cheap laptop', 'affordable laptop']
        }
        
        # Get SEMrush data for content analysis
        lenovo_content = self.semrush_data['lenovo']
        hp_content = self.semrush_data['hp']
        dell_content = self.semrush_data['dell']
        
        results = []
        
        # Analyze each product category
        for category, search_terms in product_categories.items():
            # Get YouTube search trends
            lenovo_cols = [col for col in youtube_data.columns if 'Lenovo' in str(col)]
            hp_cols = [col for col in youtube_data.columns if 'HP' in str(col)]
            dell_cols = [col for col in youtube_data.columns if 'Dell' in str(col)]
            
            # Calculate average search interest
            lenovo_search = youtube_data[lenovo_cols].mean().mean()
            hp_search = youtube_data[hp_cols].mean().mean()
            dell_search = youtube_data[dell_cols].mean().mean()
            
            # Analyze content presence
            def count_content(df, terms):
                count = 0
                for term in terms:
                    count += len(df[df['URL'].str.contains(term, case=False, na=False)])
                return count
            
            lenovo_content_count = count_content(lenovo_content, search_terms)
            hp_content_count = count_content(hp_content, search_terms)
            dell_content_count = count_content(dell_content, search_terms)
            
            # Calculate content gap
            avg_competitor_content = (hp_content_count + dell_content_count) / 2
            content_gap = avg_competitor_content - lenovo_content_count
            
            # Calculate opportunity score
            search_volume = (lenovo_search + hp_search + dell_search) / 3
            opportunity_score = (search_volume * content_gap) / (avg_competitor_content + 1)
            
            results.append({
                'category': category,
                'search_terms': ', '.join(search_terms),
                'lenovo_search_interest': lenovo_search,
                'competitor_avg_search_interest': (hp_search + dell_search) / 2,
                'lenovo_content_count': lenovo_content_count,
                'competitor_avg_content_count': avg_competitor_content,
                'content_gap': content_gap,
                'opportunity_score': opportunity_score
            })
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Sort by opportunity score
        return df_results.sort_values('opportunity_score', ascending=False)

    def analyze_competitor_impact(self):
        """
        Question 4: Analyze correlation between competitor ad spend and Lenovo's visibility
        This analysis:
        1. Tracks daily ad spend patterns of competitors
        2. Monitors Lenovo's organic visibility changes
        3. Identifies correlations and potential impacts
        4. Analyzes time-lagged effects
        
        Returns:
            DataFrame with correlation analysis and impact metrics
        """
        # Get ad spend data with proper date handling
        spend_data = self.sales_data['spend'].copy()
        if 'date' in spend_data.columns:
            spend_data['date'] = pd.to_datetime(spend_data['date'])
        
        # Get organic visibility data
        lenovo_organic = self.semrush_data['lenovo'].copy()
        
        # Create a date range based on spend data dates or use default range
        if 'date' in spend_data.columns and not spend_data['date'].isna().all():
            date_range = pd.date_range(
                start=spend_data['date'].min(),
                end=spend_data['date'].max(),
                freq='D'
            )
        else:
            # Use a default 12-month range
            date_range = pd.date_range(
                start='2023-01-01',
                periods=min(len(lenovo_organic), 365),
                freq='D'
            )
        
        # Normalize spend data
        for col in spend_data.columns:
            if col != 'date':
                # Convert to numeric, replacing non-numeric values with 0
                spend_data[col] = pd.to_numeric(spend_data[col], errors='coerce').fillna(0)
                # Cap extreme values at 99th percentile
                cap_value = spend_data[col].quantile(0.99)
                spend_data[col] = spend_data[col].clip(upper=cap_value)
        
        # Add dates to organic data (matching length)
        date_index = date_range[:min(len(lenovo_organic), len(date_range))]
        lenovo_organic = lenovo_organic.iloc[:len(date_index)].copy()
        lenovo_organic['date'] = date_index
        
        # Prepare time series data
        def prepare_time_series(df, metric_col):
            if isinstance(metric_col, pd.Series):
                # Handle pre-computed series
                return metric_col.reindex(date_index).fillna(method='ffill')
            elif 'date' in df.columns:
                # Handle dataframe with date column
                df = df.set_index('date')
                return df[metric_col].reindex(date_index).fillna(method='ffill')
            else:
                # Create new series with date range
                values = df[metric_col].values[:len(date_index)]
                return pd.Series(values, index=date_index)
        
        # Calculate total daily spend by channel type
        channel_groups = {
            'Display': ['Desktop Display', 'Mobile Display'],
            'Video': ['Desktop Video', 'Mobile Video', 'YouTube', 'OTT'],
            'Social': ['Facebook', 'Instagram', 'LinkedIn', 'TikTok', 'X', 'Snapchat']
        }
        
        # Prepare competitor spend time series
        competitor_spend = {}
        for channel, columns in channel_groups.items():
            valid_columns = [col for col in columns if col in spend_data.columns]
            if valid_columns:
                channel_spend = spend_data[valid_columns].sum(axis=1)
                competitor_spend[channel] = prepare_time_series(spend_data, channel_spend)
        
        # Prepare Lenovo visibility metrics
        lenovo_metrics = {
            'organic_traffic': prepare_time_series(lenovo_organic, 'Traffic'),
            'keyword_positions': prepare_time_series(lenovo_organic, 'Positions with commercial intents in top 20'),
            'visibility_score': prepare_time_series(lenovo_organic, 'Traffic (%)')
        }
        
        results = []
        
        # Analyze correlations with different time lags
        time_lags = [0, 1, 3, 7, 14]  # days
        
        for channel, spend_series in competitor_spend.items():
            for metric_name, metric_series in lenovo_metrics.items():
                for lag in time_lags:
                    # Ensure both series are properly aligned
                    common_index = spend_series.index.intersection(metric_series.index)
                    if len(common_index) > 0:
                        aligned_spend = spend_series[common_index]
                        aligned_metric = metric_series[common_index]
                        
                        # Calculate correlation with lag
                        if lag > 0:
                            # Shift Lenovo metrics forward to simulate lag
                            shifted_metric = aligned_metric.shift(-lag)
                            valid_index = ~shifted_metric.isna()
                            if valid_index.any():
                                correlation = aligned_spend[valid_index].corr(shifted_metric[valid_index])
                            else:
                                correlation = 0
                        else:
                            correlation = aligned_spend.corr(aligned_metric)
                        
                        # Handle NaN correlations
                        correlation = 0 if pd.isna(correlation) else correlation
                        
                        # Calculate impact score
                        impact_score = abs(correlation) * metric_series.mean()
                        
                        results.append({
                            'channel': channel,
                            'metric': metric_name,
                            'time_lag': lag,
                            'correlation': correlation,
                            'impact_score': impact_score,
                            'avg_spend': aligned_spend.mean(),
                            'metric_value': aligned_metric.mean()
                        })
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results) if results else pd.DataFrame(columns=[
            'channel', 'metric', 'time_lag', 'correlation', 'impact_score',
            'avg_spend', 'metric_value'
        ])
        
        # Calculate overall impact
        if not df_results.empty and df_results['avg_spend'].max() > 0:
            df_results['overall_impact'] = (
                df_results['impact_score'] * 
                (df_results['avg_spend'] / df_results['avg_spend'].max())
            )
        else:
            df_results['overall_impact'] = 0
        
        return df_results.sort_values('overall_impact', ascending=False)

    def analyze_opportunity_keywords(self):
        """
        Question 5: Identify low-CPC, high-opportunity keywords
        This analysis:
        1. Analyzes keyword metrics across all brands
        2. Identifies keywords with low CPC but high search volume
        3. Considers competitor presence and traffic potential
        4. Calculates opportunity scores based on multiple factors
        
        Returns:
            DataFrame with opportunity keyword analysis
        """
        # Get keyword data from all brands
        lenovo_keywords = self.semrush_data['lenovo']
        hp_keywords = self.semrush_data['hp']
        dell_keywords = self.semrush_data['dell']
        
        # Extract keywords from URLs
        def extract_keywords(url):
            # Remove common elements
            url = url.lower().replace('https://', '').replace('www.', '')
            # Split by slashes and take relevant parts
            parts = url.split('/')
            # Join relevant parts and split by common separators
            keywords = ' '.join(parts[2:]).replace('-', ' ').replace('_', ' ')
            return keywords
        
        # Process each brand's data
        def process_brand_data(df, brand_name):
            df = df.copy()
            # Extract keywords from URLs
            df['keywords'] = df['URL'].apply(extract_keywords)
            # Add brand and metrics
            df['brand'] = brand_name
            df['search_volume'] = df['Traffic']
            df['positions'] = df['Positions with commercial intents in top 20']
            return df
        
        # Combine all keyword data
        all_keywords = pd.concat([
            process_brand_data(lenovo_keywords, 'Lenovo'),
            process_brand_data(hp_keywords, 'HP'),
            process_brand_data(dell_keywords, 'Dell')
        ])
        
        # Calculate opportunity metrics
        results = []
        for keyword_group in all_keywords['keywords'].unique():
            keyword_data = all_keywords[all_keywords['keywords'] == keyword_group]
            
            # Get metrics for each brand
            lenovo_data = keyword_data[keyword_data['brand'] == 'Lenovo']
            hp_data = keyword_data[keyword_data['brand'] == 'HP']
            dell_data = keyword_data[keyword_data['brand'] == 'Dell']
            
            # Calculate base metrics
            search_volume = keyword_data['search_volume'].max()
            positions = keyword_data['positions'].mean()
            
            # Calculate brand-specific metrics
            lenovo_traffic = lenovo_data['Traffic'].mean() if not lenovo_data.empty else 0
            hp_traffic = hp_data['Traffic'].mean() if not hp_data.empty else 0
            dell_traffic = dell_data['Traffic'].mean() if not dell_data.empty else 0
            
            # Calculate competitive metrics
            competitor_presence = len(keyword_data[keyword_data['brand'].isin(['HP', 'Dell'])])
            competitor_traffic = (hp_traffic + dell_traffic) / 2
            traffic_gap = max(0, competitor_traffic - lenovo_traffic)
            
            # Calculate opportunity score components
            position_score = 1 / (positions + 1)  # Better positions = higher score
            volume_score = search_volume / (all_keywords['search_volume'].max() + 1)
            traffic_gap_score = traffic_gap / (competitor_traffic + 1)
            competition_score = 1 / (competitor_presence + 1)
            
            # Calculate overall opportunity score
            opportunity_score = (
                position_score * 0.3 +  # Weight for position
                volume_score * 0.3 +  # Weight for search volume
                traffic_gap_score * 0.2 +  # Weight for traffic gap
                competition_score * 0.2  # Weight for competition
            )
            
            results.append({
                'keyword': keyword_group,
                'search_volume': search_volume,
                'positions': positions,
                'lenovo_traffic': lenovo_traffic,
                'competitor_avg_traffic': competitor_traffic,
                'traffic_gap': traffic_gap,
                'competitor_presence': competitor_presence,
                'position_score': position_score,
                'volume_score': volume_score,
                'traffic_gap_score': traffic_gap_score,
                'competition_score': competition_score,
                'opportunity_score': opportunity_score
            })
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Filter out irrelevant keywords
        df_results = df_results[
            ~df_results['keyword'].str.contains('|'.join([
                'www', 'http', 'https', 'com', 'html', 'php',
                'index', 'page', 'site', 'web', 'home'
            ]), case=False, na=False)
        ]
        
        # Sort by opportunity score
        return df_results.sort_values('opportunity_score', ascending=False).head(20)

    def plot_keyword_gaps(self, df):
        """Return data for keyword gaps visualization"""
        chart_data = {
            'title': 'Keyword Performance Gap Analysis',
            'subtitle': 'Comparing Lenovo vs Competitor Performance in Key Search Terms',
            'insights': [
                f"Top opportunity: {df.iloc[0]['keyword']} with {df.iloc[0]['opportunity_score']:.0f} score",
                f"Average performance gap: {df['gap_score'].mean():.1f} points",
                f"Total opportunities identified: {len(df)} keywords"
            ],
            'data': {
                'keywords': df['keyword'].tolist(),
                'lenovo_performance': df['lenovo_performance'].tolist(),
                'competitor_avg': df['competitor_avg'].tolist(),
                'opportunity_scores': df['opportunity_score'].tolist()
            }
        }
        return chart_data

    def plot_ad_spend_efficiency(self, df):
        """Return data for ad spend efficiency visualization"""
        chart_data = {
            'title': 'Ad Spend Efficiency Analysis',
            'subtitle': 'Comparing Channel Performance and Investment Returns',
            'insights': [
                f"Most efficient channel: {df.loc[df['efficiency_score'].idxmax(), 'channel']}",
                f"Average relative efficiency: {df['relative_efficiency'].mean():.2f}x",
                f"Total channels analyzed: {len(df)}"
            ],
            'data': {
                'channels': df['channel'].tolist(),
                'lenovo_spend': df['lenovo_spend'].tolist(),
                'competitor_avg_spend': df['competitor_avg_spend'].tolist(),
                'lenovo_traffic': df['lenovo_traffic'].tolist(),
                'competitor_avg_traffic': df['competitor_avg_traffic'].tolist(),
                'relative_efficiency': df['relative_efficiency'].tolist(),
                'efficiency_score': df['efficiency_score'].tolist()
            }
        }
        return chart_data

    def plot_youtube_trends(self, df):
        """Return data for YouTube trends visualization"""
        chart_data = {
            'title': 'YouTube Content Gap Analysis',
            'subtitle': 'Identifying Content Opportunities Across Product Categories',
            'insights': [
                f"Largest content gap: {df.loc[df['content_gap'].idxmax(), 'category']} category",
                f"Average search interest: {df['lenovo_search_interest'].mean():.1f}",
                f"Total categories analyzed: {len(df)}"
            ],
            'data': {
                'categories': df['category'].tolist(),
                'lenovo_search_interest': df['lenovo_search_interest'].tolist(),
                'competitor_avg_search_interest': df['competitor_avg_search_interest'].tolist(),
                'lenovo_content_count': df['lenovo_content_count'].tolist(),
                'competitor_avg_content_count': df['competitor_avg_content_count'].tolist(),
                'content_gap': df['content_gap'].tolist(),
                'opportunity_score': df['opportunity_score'].tolist()
            }
        }
        return chart_data

    def plot_competitor_impact(self, df):
        """Return data for competitor impact visualization"""
        chart_data = {
            'title': 'Competitor Impact Analysis',
            'subtitle': 'Correlation Between Competitor Ad Spend and Lenovo Visibility',
            'insights': [
                f"Strongest impact channel: {df.loc[df['overall_impact'].idxmax(), 'channel']}",
                f"Average correlation: {df['correlation'].mean():.2f}",
                f"Time lags analyzed: {df['time_lag'].nunique()} days"
            ],
            'data': {
                'channels': df['channel'].unique().tolist(),
                'time_lags': df['time_lag'].unique().tolist(),
                'correlations': df.pivot(index='channel', columns='time_lag', values='correlation').to_dict(),
                'impact_scores': df.pivot(index='channel', columns='time_lag', values='impact_score').to_dict(),
                'overall_impact': df.groupby('channel')['overall_impact'].mean().to_dict()
            }
        }
        return chart_data

    def plot_opportunity_keywords(self, df):
        """Return data for opportunity keywords visualization"""
        chart_data = {
            'title': 'Keyword Opportunity Analysis',
            'subtitle': 'Identifying High-Potential Keywords with Low Competition',
            'insights': [
                f"Top opportunity: {df.iloc[0]['keyword']} with {df.iloc[0]['opportunity_score']:.0f} score",
                f"Average search volume: {df['search_volume'].mean():.0f}",
                f"Total keywords analyzed: {len(df)}"
            ],
            'data': {
                'keywords': df['keyword'].tolist(),
                'search_volume': df['search_volume'].tolist(),
                'positions': df['positions'].tolist(),
                'lenovo_traffic': df['lenovo_traffic'].tolist(),
                'competitor_avg_traffic': df['competitor_avg_traffic'].tolist(),
                'traffic_gap': df['traffic_gap'].tolist(),
                'competitor_presence': df['competitor_presence'].tolist(),
                'opportunity_score': df['opportunity_score'].tolist()
            }
        }
        return chart_data

if __name__ == "__main__":
    analyzer = LenovoDashboardAnalysis()
    
    # Example usage:
    keyword_gaps = analyzer.analyze_keyword_gaps()
    print(analyzer.plot_keyword_gaps(keyword_gaps))
    
    ad_efficiency = analyzer.analyze_ad_spend_efficiency()
    print(analyzer.plot_ad_spend_efficiency(ad_efficiency))
    
    youtube_trends = analyzer.analyze_youtube_trends()
    print(analyzer.plot_youtube_trends(youtube_trends))
    
    competitor_impact = analyzer.analyze_competitor_impact()
    print(analyzer.plot_competitor_impact(competitor_impact))
    
    opportunity_keywords = analyzer.analyze_opportunity_keywords()
    print(analyzer.plot_opportunity_keywords(opportunity_keywords)) 