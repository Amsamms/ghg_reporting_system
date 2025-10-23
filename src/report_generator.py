import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import os

class GHGReportGenerator:
    def __init__(self, excel_file_path):
        self.excel_file = excel_file_path
        self.data = self._load_excel_data()
        self.report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _load_excel_data(self):
        """Load data from all Excel sheets"""
        try:
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)
            return excel_data
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return None

    def get_custom_text(self):
        """Extract custom text from Custom Text sheet"""
        custom_text = {
            'company_introduction': '',
            'conclusion_text': '',
            'conclusion_title': 'Conclusion & Final Notes'  # Default title
        }

        try:
            if self.data and 'Custom Text' in self.data:
                df = self.data['Custom Text']
                # The sheet has format: [Field, Content] in columns
                for idx, row in df.iterrows():
                    if len(row) >= 2:
                        field = str(row.iloc[0]).strip()
                        content = str(row.iloc[1]).strip()

                        if 'Company Introduction' in field:
                            custom_text['company_introduction'] = content
                        elif 'Conclusion Title' in field:
                            custom_text['conclusion_title'] = content if content and content != 'nan' else 'Conclusion & Final Notes'
                        elif 'Conclusion' in field and 'Title' not in field:
                            custom_text['conclusion_text'] = content
        except Exception as e:
            print(f"Error loading custom text: {e}")

        return custom_text

    def _apply_threshold_to_sources(self, df, threshold_percent):
        """Apply threshold to sources and group remaining as 'Others'

        Args:
            df: DataFrame with 'Source' and 'Annual_Total' columns
            threshold_percent: Percentage threshold (0-100)

        Returns:
            tuple: (filtered_df, others_total)
        """
        if df.empty or 'Annual_Total' not in df.columns:
            return df, 0

        # Sort by Annual_Total descending
        df_sorted = df.sort_values('Annual_Total', ascending=False).copy()

        # Calculate total and cumulative percentage
        total = df_sorted['Annual_Total'].sum()
        if total == 0:
            return df_sorted, 0

        df_sorted['cumulative_pct'] = (df_sorted['Annual_Total'].cumsum() / total * 100)

        # Find sources up to threshold (closest to threshold without going under)
        if threshold_percent >= 100:
            # Show all sources
            return df_sorted, 0

        # Find the index where we exceed threshold
        exceeds_threshold = df_sorted['cumulative_pct'] >= threshold_percent
        if exceeds_threshold.any():
            # Include sources up to and including the one that exceeds threshold
            threshold_idx = exceeds_threshold.idxmax()
            idx_position = df_sorted.index.get_loc(threshold_idx)

            # Check which is closer to threshold: including or excluding this source
            if idx_position > 0:
                pct_with = df_sorted.loc[threshold_idx, 'cumulative_pct']
                pct_without = df_sorted.iloc[idx_position - 1]['cumulative_pct']

                if abs(pct_with - threshold_percent) <= abs(pct_without - threshold_percent):
                    # Including this source is closer to threshold
                    included_sources = df_sorted.iloc[:idx_position + 1]
                else:
                    # Excluding this source is closer to threshold
                    included_sources = df_sorted.iloc[:idx_position]
            else:
                # First source already exceeds threshold, include it
                included_sources = df_sorted.iloc[:1]

            others_total = df_sorted.iloc[len(included_sources):]['Annual_Total'].sum()
            return included_sources, others_total
        else:
            # All sources combined don't reach threshold, show all
            return df_sorted, 0

    def create_sankey_diagram(self, facility_filter=None, threshold_percent=80):
        """Create Sankey diagram for GHG emissions flow

        Args:
            facility_filter: Optional facility name to filter data
            threshold_percent: Percentage threshold for grouping sources (default: 80)
        """
        if not self.data:
            return None

        try:
            # Get summary stats which handles facility filtering
            summary = self.get_summary_statistics(facility_filter)

            # Get scope totals from dashboard or calculate
            scope1_df = self.data.get('Scope 1 Emissions', pd.DataFrame())
            scope2_df = self.data.get('Scope 2 Emissions', pd.DataFrame())
            scope3_df = self.data.get('Scope 3 Emissions', pd.DataFrame())

            # Calculate facility ratio if filtering
            facility_ratio = 1.0
            if facility_filter:
                facilities_df = self.data.get('Facility Breakdown', pd.DataFrame())
                if not facilities_df.empty and 'Facility' in facilities_df.columns:
                    facility_row = facilities_df[facilities_df['Facility'] == facility_filter]
                    if not facility_row.empty:
                        total_all_facilities = (facilities_df['Scope_1'].sum() +
                                                facilities_df['Scope_2'].sum() +
                                                facilities_df['Scope_3'].sum())
                        facility_emissions = (facility_row['Scope_1'].iloc[0] +
                                            facility_row['Scope_2'].iloc[0] +
                                            facility_row['Scope_3'].iloc[0])
                        facility_ratio = facility_emissions / total_all_facilities if total_all_facilities > 0 else 0

            # Check if any data exists
            if scope1_df.empty and scope2_df.empty and scope3_df.empty:
                return None

            # Calculate totals with facility filtering
            scope1_total = summary.get('scope1_total', 0)
            scope2_total = summary.get('scope2_total', 0)
            scope3_total = summary.get('scope3_total', 0)

            # Only proceed if we have some emissions data
            if scope1_total == 0 and scope2_total == 0 and scope3_total == 0:
                return None

            # Build node labels and track their indices
            labels = []
            node_indices = {}

            # Add emission sources first (left side)
            source_index = 0

            # Apply threshold to each scope
            top_scope1, scope1_others = self._apply_threshold_to_sources(scope1_df, threshold_percent)
            top_scope2, scope2_others = self._apply_threshold_to_sources(scope2_df, threshold_percent)
            top_scope3, scope3_others = self._apply_threshold_to_sources(scope3_df, threshold_percent)

            # Add scope 1 sources with threshold-based filtering
            for _, row in top_scope1.iterrows():
                if 'Source' in row and row['Annual_Total'] > 0:
                    # More readable labels - show full name if short, otherwise truncate smartly
                    source_text = str(row['Source'])
                    if len(source_text) > 20:
                        source_name = source_text[:20] + "..."
                    else:
                        source_name = source_text
                    labels.append(source_name)
                    node_indices[f"scope1_{row['Source']}"] = source_index
                    source_index += 1

            # Add "Others" for Scope 1 if needed
            if scope1_others > 0:
                labels.append("Others (S1)")
                node_indices["scope1_others"] = source_index
                source_index += 1

            # Add scope 2 sources with threshold-based filtering
            for _, row in top_scope2.iterrows():
                if 'Source' in row and row['Annual_Total'] > 0:
                    source_text = str(row['Source'])
                    if len(source_text) > 20:
                        source_name = source_text[:20] + "..."
                    else:
                        source_name = source_text
                    labels.append(source_name)
                    node_indices[f"scope2_{row['Source']}"] = source_index
                    source_index += 1

            # Add "Others" for Scope 2 if needed
            if scope2_others > 0:
                labels.append("Others (S2)")
                node_indices["scope2_others"] = source_index
                source_index += 1

            # Add scope 3 sources with threshold-based filtering
            for _, row in top_scope3.iterrows():
                if 'Source' in row and row['Annual_Total'] > 0:
                    source_text = str(row['Source'])
                    if len(source_text) > 20:
                        source_name = source_text[:20] + "..."
                    else:
                        source_name = source_text
                    labels.append(source_name)
                    node_indices[f"scope3_{row['Source']}"] = source_index
                    source_index += 1

            # Add "Others" for Scope 3 if needed
            if scope3_others > 0:
                labels.append("Others (S3)")
                node_indices["scope3_others"] = source_index
                source_index += 1

            # Add scope categories (middle)
            scope_start_index = len(labels)
            if scope1_total > 0:
                labels.append('Scope 1<br>(Direct)')
                node_indices['scope1'] = len(labels) - 1
            if scope2_total > 0:
                labels.append('Scope 2<br>(Energy)')
                node_indices['scope2'] = len(labels) - 1
            if scope3_total > 0:
                labels.append('Scope 3<br>(Indirect)')
                node_indices['scope3'] = len(labels) - 1

            # Add total (right side)
            labels.append('Total GHG<br>Emissions')
            total_index = len(labels) - 1

            # Create links (source -> scope -> total)
            source = []
            target = []
            value = []

            # Links from emission sources to scopes (apply facility ratio)
            for _, row in top_scope1.iterrows():
                if 'Source' in row and row['Annual_Total'] > 0 and 'scope1' in node_indices:
                    source_key = f"scope1_{row['Source']}"
                    if source_key in node_indices:
                        source.append(node_indices[source_key])
                        target.append(node_indices['scope1'])
                        value.append(row['Annual_Total'] * facility_ratio)

            # Add link for Scope 1 "Others" if exists
            if scope1_others > 0 and 'scope1_others' in node_indices and 'scope1' in node_indices:
                source.append(node_indices['scope1_others'])
                target.append(node_indices['scope1'])
                value.append(scope1_others * facility_ratio)

            for _, row in top_scope2.iterrows():
                if 'Source' in row and row['Annual_Total'] > 0 and 'scope2' in node_indices:
                    source_key = f"scope2_{row['Source']}"
                    if source_key in node_indices:
                        source.append(node_indices[source_key])
                        target.append(node_indices['scope2'])
                        value.append(row['Annual_Total'] * facility_ratio)

            # Add link for Scope 2 "Others" if exists
            if scope2_others > 0 and 'scope2_others' in node_indices and 'scope2' in node_indices:
                source.append(node_indices['scope2_others'])
                target.append(node_indices['scope2'])
                value.append(scope2_others * facility_ratio)

            for _, row in top_scope3.iterrows():
                if 'Source' in row and row['Annual_Total'] > 0 and 'scope3' in node_indices:
                    source_key = f"scope3_{row['Source']}"
                    if source_key in node_indices:
                        source.append(node_indices[source_key])
                        target.append(node_indices['scope3'])
                        value.append(row['Annual_Total'] * facility_ratio)

            # Add link for Scope 3 "Others" if exists
            if scope3_others > 0 and 'scope3_others' in node_indices and 'scope3' in node_indices:
                source.append(node_indices['scope3_others'])
                target.append(node_indices['scope3'])
                value.append(scope3_others * facility_ratio)

            # Links from scopes to total
            if scope1_total > 0 and 'scope1' in node_indices:
                source.append(node_indices['scope1'])
                target.append(total_index)
                value.append(scope1_total)

            if scope2_total > 0 and 'scope2' in node_indices:
                source.append(node_indices['scope2'])
                target.append(total_index)
                value.append(scope2_total)

            if scope3_total > 0 and 'scope3' in node_indices:
                source.append(node_indices['scope3'])
                target.append(total_index)
                value.append(scope3_total)

            # Only create diagram if we have links
            if not source or not target or not value:
                return None

            # Define colors for nodes
            node_colors = []
            for i, label in enumerate(labels):
                if label.startswith('S1:'):
                    node_colors.append('rgba(255, 183, 183, 0.8)')  # Light red for Scope 1 sources
                elif label.startswith('S2:'):
                    node_colors.append('rgba(183, 219, 255, 0.8)')  # Light blue for Scope 2 sources
                elif label.startswith('S3:'):
                    node_colors.append('rgba(219, 183, 255, 0.8)')  # Light purple for Scope 3 sources
                elif 'Scope 1' in label:
                    node_colors.append('rgba(231, 76, 60, 0.8)')   # Red for Scope 1
                elif 'Scope 2' in label:
                    node_colors.append('rgba(52, 152, 219, 0.8)')  # Blue for Scope 2
                elif 'Scope 3' in label:
                    node_colors.append('rgba(155, 89, 182, 0.8)')  # Purple for Scope 3
                else:  # Total
                    node_colors.append('rgba(46, 134, 193, 0.9)')  # Dark blue for total

            # Link colors based on scope
            link_colors = []
            for i, (s, t) in enumerate(zip(source, target)):
                if t == node_indices.get('scope1', -1) or s == node_indices.get('scope1', -1):
                    link_colors.append('rgba(231, 76, 60, 0.5)')
                elif t == node_indices.get('scope2', -1) or s == node_indices.get('scope2', -1):
                    link_colors.append('rgba(52, 152, 219, 0.5)')
                elif t == node_indices.get('scope3', -1) or s == node_indices.get('scope3', -1):
                    link_colors.append('rgba(155, 89, 182, 0.5)')
                else:
                    link_colors.append('rgba(149, 165, 166, 0.5)')

            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=20,
                    thickness=25,
                    line=dict(color="white", width=2),
                    label=labels,
                    color=node_colors,
                    x=[0.01] * (scope_start_index) + [0.5] * (total_index - scope_start_index) + [0.99],  # Position nodes
                    y=[i/(scope_start_index) if scope_start_index > 0 else 0 for i in range(scope_start_index)] +
                      [0.2, 0.5, 0.8][:total_index - scope_start_index] + [0.5]  # Spread sources vertically
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=link_colors
                ),
                textfont=dict(color="black", size=14, family="Arial")
            )])

            title = f"GHG Emissions Flow - {summary.get('facility_name', 'All Facilities')}"

            fig.update_layout(
                title_text=title,
                font=dict(size=14, family="Arial", color="black"),
                height=700,
                margin=dict(t=100, l=20, r=20, b=50),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            return fig
        except Exception as e:
            print(f"Error creating Sankey diagram: {e}")
            import traceback
            print(f"Detailed error: {traceback.format_exc()}")
            return None

    def create_scope_comparison_chart(self, facility_filter=None):
        """Create bar chart comparing the three scopes

        Args:
            facility_filter: Optional facility name to filter data
        """
        if not self.data:
            return None

        try:
            # Get summary stats which handles facility filtering
            summary = self.get_summary_statistics(facility_filter)

            scope1_total = summary.get('scope1_total', 0)
            scope2_total = summary.get('scope2_total', 0)
            scope3_total = summary.get('scope3_total', 0)

            scopes = ['Scope 1\n(Direct)', 'Scope 2\n(Energy)', 'Scope 3\n(Other Indirect)']
            values = [scope1_total, scope2_total, scope3_total]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

            fig = go.Figure(data=[
                go.Bar(x=scopes, y=values, marker_color=colors,
                       text=[f'{v:,.0f} tCO2e' for v in values],
                       textposition='auto')
            ])

            title = f'GHG Emissions by Scope - {summary.get("facility_name", "All Facilities")}'

            fig.update_layout(
                title=title,
                xaxis_title='Emission Scopes',
                yaxis_title='Emissions (tCO2e)',
                showlegend=False,
                height=500
            )

            return fig
        except Exception as e:
            print(f"Error creating scope comparison chart: {e}")
            return None

    def create_monthly_trend_chart(self, facility_filter=None):
        """Create monthly trend chart for all scopes

        Args:
            facility_filter: Optional facility name to filter data
        """
        if not self.data:
            return None

        try:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            fig = make_subplots(rows=1, cols=1)

            # Calculate monthly totals for each scope
            scope_dfs = {
                'Scope 1': self.data.get('Scope 1 Emissions', pd.DataFrame()),
                'Scope 2': self.data.get('Scope 2 Emissions', pd.DataFrame()),
                'Scope 3': self.data.get('Scope 3 Emissions', pd.DataFrame())
            }

            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

            # If facility filter, we need to proportion the data
            # Since scopes don't have per-facility breakdown, we proportion based on facility's share
            facility_ratio = 1.0
            if facility_filter:
                facilities_df = self.data.get('Facility Breakdown', pd.DataFrame())
                if not facilities_df.empty and 'Facility' in facilities_df.columns:
                    facility_row = facilities_df[facilities_df['Facility'] == facility_filter]
                    if not facility_row.empty:
                        # Calculate facility's proportion of total emissions
                        total_all_facilities = (facilities_df['Scope_1'].sum() +
                                                facilities_df['Scope_2'].sum() +
                                                facilities_df['Scope_3'].sum())
                        facility_emissions = (facility_row['Scope_1'].iloc[0] +
                                            facility_row['Scope_2'].iloc[0] +
                                            facility_row['Scope_3'].iloc[0])
                        facility_ratio = facility_emissions / total_all_facilities if total_all_facilities > 0 else 0

            for i, (scope_name, df) in enumerate(scope_dfs.items()):
                if not df.empty:
                    monthly_totals = []
                    for month in months:
                        if month in df.columns:
                            monthly_total = df[month].sum() * facility_ratio
                            monthly_totals.append(monthly_total)
                        else:
                            monthly_totals.append(0)

                    fig.add_trace(go.Scatter(
                        x=months,
                        y=monthly_totals,
                        mode='lines+markers',
                        name=scope_name,
                        line=dict(color=colors[i], width=3),
                        marker=dict(size=8)
                    ))

            summary = self.get_summary_statistics(facility_filter)
            title = f'Monthly GHG Emissions Trend by Scope - {summary.get("facility_name", "All Facilities")}'

            fig.update_layout(
                title=title,
                xaxis_title='Month',
                yaxis_title='Emissions (tCO2e)',
                height=500,
                hovermode='x unified'
            )

            return fig
        except Exception as e:
            print(f"Error creating monthly trend chart: {e}")
            return None

    def create_facility_breakdown_chart(self):
        """Create facility breakdown chart"""
        if not self.data:
            return None

        try:
            facilities_df = self.data.get('Facility Breakdown', pd.DataFrame())

            if facilities_df.empty or 'Facility' not in facilities_df.columns:
                return None

            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Total Emissions by Facility', 'Scope Breakdown by Facility',
                              'Energy Intensity by Facility', 'Production vs Emissions'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )

            # Total emissions by facility
            if all(col in facilities_df.columns for col in ['Scope_1', 'Scope_2', 'Scope_3']):
                facilities_df['Total_Emissions'] = facilities_df['Scope_1'] + facilities_df['Scope_2'] + facilities_df['Scope_3']

                fig.add_trace(go.Bar(
                    x=facilities_df['Facility'].tolist(),
                    y=facilities_df['Total_Emissions'].tolist(),
                    name='Total Emissions',
                    marker_color='#FF6B6B'
                ), row=1, col=1)

                # Stacked bar for scope breakdown
                fig.add_trace(go.Bar(
                    x=facilities_df['Facility'].tolist(),
                    y=facilities_df['Scope_1'].tolist(),
                    name='Scope 1',
                    marker_color='#FF6B6B'
                ), row=1, col=2)

                fig.add_trace(go.Bar(
                    x=facilities_df['Facility'].tolist(),
                    y=facilities_df['Scope_2'].tolist(),
                    name='Scope 2',
                    marker_color='#4ECDC4'
                ), row=1, col=2)

                fig.add_trace(go.Bar(
                    x=facilities_df['Facility'].tolist(),
                    y=facilities_df['Scope_3'].tolist(),
                    name='Scope 3',
                    marker_color='#45B7D1'
                ), row=1, col=2)

            # Energy intensity
            if 'Energy_Intensity' in facilities_df.columns:
                fig.add_trace(go.Bar(
                    x=facilities_df['Facility'].tolist(),
                    y=facilities_df['Energy_Intensity'].tolist(),
                    name='Energy Intensity',
                    marker_color='#96CEB4'
                ), row=2, col=1)

            # Production vs Emissions scatter
            if all(col in facilities_df.columns for col in ['Production', 'Total_Emissions']):
                fig.add_trace(go.Scatter(
                    x=facilities_df['Production'].tolist(),
                    y=facilities_df['Total_Emissions'].tolist(),
                    mode='markers',
                    name='Facilities',
                    marker=dict(size=12, color='#FFEAA7'),
                    text=facilities_df['Facility'].tolist()
                ), row=2, col=2)

            fig.update_layout(
                height=800,
                showlegend=False,
                title_text="Facility-wise GHG Analysis"
            )

            return fig
        except Exception as e:
            print(f"Error creating facility breakdown chart: {e}")
            return None

    def create_emission_by_source_chart(self):
        """Create emission by source analysis chart"""
        if not self.data:
            return None

        try:
            emission_df = self.data.get('Emission By Source', pd.DataFrame())

            if emission_df.empty:
                return None

            # Pie chart for emission distribution and bar chart for emissions
            if 'Source' in emission_df.columns and 'Annual_Total_tCO2e' in emission_df.columns:
                # Sort by emissions descending for better visualization
                emission_df_sorted = emission_df.sort_values('Annual_Total_tCO2e', ascending=False)

                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('Emission Distribution by Source', 'Emissions by Source (tCO₂e)'),
                    specs=[[{"type": "domain"}, {"type": "xy"}]]  # domain for pie, xy for bar
                )

                # Define proper colors for charts
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']

                # Pie chart with actual percentages calculated from data
                fig.add_trace(go.Pie(
                    labels=emission_df['Source'].tolist(),
                    values=emission_df['Annual_Total_tCO2e'].tolist(),
                    hole=0.3,
                    marker=dict(
                        colors=colors[:len(emission_df)],
                        line=dict(color='#FFFFFF', width=2)
                    ),
                    textinfo='label+percent',
                    textposition='outside',
                    showlegend=True
                ), row=1, col=1)

                # Bar chart for emissions in tCO₂e - using sorted data for better visualization
                # Assign colors to match pie chart
                source_colors = {source: colors[i % len(colors)] for i, source in enumerate(emission_df['Source'])}
                bar_colors = [source_colors[source] for source in emission_df_sorted['Source']]

                fig.add_trace(go.Bar(
                    x=emission_df_sorted['Source'].tolist(),
                    y=emission_df_sorted['Annual_Total_tCO2e'].tolist(),
                    orientation='v',  # Explicitly set vertical orientation
                    marker=dict(
                        color=bar_colors,
                        line=dict(color='#FFFFFF', width=1)
                    ),
                    text=[f'{val:,.0f}' for val in emission_df_sorted['Annual_Total_tCO2e']],
                    textposition='outside',
                    name='Emissions (tCO₂e)',
                    showlegend=False
                ), row=1, col=2)

                # Update axes labels
                fig.update_xaxes(title_text='Emission Source', row=1, col=2)
                fig.update_yaxes(title_text='Emissions (tCO₂e)', row=1, col=2)

                fig.update_layout(
                    height=500,
                    showlegend=True,
                    title_text="Emission By Source Analysis"
                )

                # Update pie chart formatting
                fig.update_traces(
                    selector=dict(type='pie'),
                    textfont_size=12,
                    marker=dict(line=dict(color='#FFFFFF', width=2))
                )

                return fig
        except Exception as e:
            print(f"Error creating emission by source chart: {e}")
            return None

    def generate_rule_based_recommendations(self):
        """Generate rule-based recommendations based on data thresholds"""
        if not self.data:
            return []

        recommendations = []

        try:
            # Analyze scope distribution
            scope1_df = self.data.get('Scope 1 Emissions', pd.DataFrame())
            scope2_df = self.data.get('Scope 2 Emissions', pd.DataFrame())
            scope3_df = self.data.get('Scope 3 Emissions', pd.DataFrame())

            if not scope1_df.empty and 'Annual_Total' in scope1_df.columns:
                scope1_total = scope1_df['Annual_Total'].sum()
                top_scope1_source = scope1_df.loc[scope1_df['Annual_Total'].idxmax(), 'Source'] if 'Source' in scope1_df.columns else 'Unknown'

                if scope1_total > 10000:  # High Scope 1 emissions
                    recommendations.append({
                        'priority': 'High',
                        'category': 'Scope 1 Reduction',
                        'recommendation': f'Focus on reducing {top_scope1_source} emissions through process optimization and equipment upgrades. Consider implementing carbon capture technology.',
                        'potential_impact': 'Up to 15% reduction in Scope 1 emissions'
                    })

            if not scope2_df.empty and 'Annual_Total' in scope2_df.columns:
                scope2_total = scope2_df['Annual_Total'].sum()
                if scope2_total > 5000:  # High Scope 2 emissions
                    recommendations.append({
                        'priority': 'Medium',
                        'category': 'Energy Transition',
                        'recommendation': 'Increase renewable energy procurement and implement energy efficiency measures. Consider on-site solar installations.',
                        'potential_impact': 'Up to 25% reduction in Scope 2 emissions'
                    })

            # Energy intensity analysis
            facilities_df = self.data.get('Facility Breakdown', pd.DataFrame())
            if not facilities_df.empty and 'Energy_Intensity' in facilities_df.columns:
                avg_intensity = facilities_df['Energy_Intensity'].mean()
                if avg_intensity > 5.0:  # High energy intensity
                    recommendations.append({
                        'priority': 'Medium',
                        'category': 'Energy Efficiency',
                        'recommendation': 'Implement comprehensive energy management system (ISO 50001) and conduct energy audits at high-intensity facilities.',
                        'potential_impact': 'Up to 10% improvement in energy intensity'
                    })

            # Targets analysis
            targets_df = self.data.get('Targets & Performance', pd.DataFrame())
            if not targets_df.empty and 'Status' in targets_df.columns:
                needs_improvement = targets_df[targets_df['Status'] == 'Needs Improvement']
                if not needs_improvement.empty:
                    recommendations.append({
                        'priority': 'High',
                        'category': 'Target Achievement',
                        'recommendation': 'Develop accelerated action plans for underperforming metrics. Increase investment in emission reduction technologies.',
                        'potential_impact': 'Meet 2025 targets'
                    })

            # General recommendations
            recommendations.extend([
                {
                    'priority': 'Medium',
                    'category': 'Technology Innovation',
                    'recommendation': 'Invest in emerging technologies such as hydrogen fuel, advanced biofuels, and carbon utilization for long-term emission reductions.',
                    'potential_impact': 'Up to 30% reduction by 2030'
                },
                {
                    'priority': 'Low',
                    'category': 'Reporting & Monitoring',
                    'recommendation': 'Implement real-time GHG monitoring systems and enhance data quality through automated data collection.',
                    'potential_impact': 'Improved data accuracy and faster response times'
                }
            ])

        except Exception as e:
            print(f"Error generating recommendations: {e}")

        return recommendations

    def generate_ai_recommendations(self):
        """Generate AI-powered recommendations using OpenAI GPT-5"""
        if not self.data:
            return []

        try:
            # Import openai here to avoid dependency if not used
            from openai import OpenAI

            # Check for API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("OpenAI API key not found. Falling back to rule-based recommendations.")
                return self.generate_rule_based_recommendations()

            # Prepare data summary
            summary = self.get_summary_statistics()

            # Get top emission sources
            scope1_df = self.data.get('Scope 1 Emissions', pd.DataFrame())
            scope2_df = self.data.get('Scope 2 Emissions', pd.DataFrame())
            scope3_df = self.data.get('Scope 3 Emissions', pd.DataFrame())
            emission_by_source = self.data.get('Emission By Source', pd.DataFrame())

            # Top 3 sources from each scope
            top_scope1 = []
            if not scope1_df.empty and 'Annual_Total' in scope1_df.columns and 'Source' in scope1_df.columns:
                top_scope1 = scope1_df.nlargest(3, 'Annual_Total')[['Source', 'Annual_Total']].to_dict('records')

            top_scope2 = []
            if not scope2_df.empty and 'Annual_Total' in scope2_df.columns and 'Source' in scope2_df.columns:
                top_scope2 = scope2_df.nlargest(3, 'Annual_Total')[['Source', 'Annual_Total']].to_dict('records')

            top_scope3 = []
            if not scope3_df.empty and 'Annual_Total' in scope3_df.columns and 'Source' in scope3_df.columns:
                top_scope3 = scope3_df.nlargest(3, 'Annual_Total')[['Source', 'Annual_Total']].to_dict('records')

            top_energy = []
            if not emission_by_source.empty and 'Annual_Total_tCO2e' in emission_by_source.columns and 'Source' in emission_by_source.columns:
                top_energy = emission_by_source.nlargest(3, 'Annual_Total_tCO2e')[['Source', 'Annual_Total_tCO2e']].to_dict('records')

            # Construct prompt for GPT-5
            prompt = f"""You are a GHG emissions expert analyzing a petroleum company's emissions data. Based on the data below, generate 5-6 strategic recommendations following the GHG Protocol Corporate Standard and petroleum industry best practices.

**Company Emissions Data:**
- Total Emissions: {summary.get('total_emissions', 0):,.0f} tCO₂e
- Scope 1 (Direct): {summary.get('scope1_total', 0):,.0f} tCO₂e ({summary.get('scope1_pct', 0):.1f}%)
- Scope 2 (Energy): {summary.get('scope2_total', 0):,.0f} tCO₂e ({summary.get('scope2_pct', 0):.1f}%)
- Scope 3 (Indirect): {summary.get('scope3_total', 0):,.0f} tCO₂e ({summary.get('scope3_pct', 0):.1f}%)
- Carbon Intensity: {summary.get('carbon_intensity', 0):.4f} tCO₂e/barrel
- Number of Facilities: {summary.get('total_facilities', 0)}

**Top Scope 1 Emission Sources:**
{json.dumps(top_scope1, indent=2) if top_scope1 else "No data available"}

**Top Scope 2 Emission Sources:**
{json.dumps(top_scope2, indent=2) if top_scope2 else "No data available"}

**Top Scope 3 Emission Sources:**
{json.dumps(top_scope3, indent=2) if top_scope3 else "No data available"}

**Top Energy-Related Emission Sources:**
{json.dumps(top_energy, indent=2) if top_energy else "No data available"}

**Instructions:**
1. Analyze the emission distribution and identify key reduction opportunities
2. Provide 5-6 specific, actionable recommendations tailored to THIS company's data
3. Assign priority based on impact potential and feasibility:
   - "High": Critical reductions, quick wins, largest emission sources
   - "Medium": Significant long-term impact, moderate complexity
   - "Low": Incremental improvements, monitoring enhancements
4. Include quantified potential impact where possible (be realistic based on the actual numbers)
5. Consider petroleum industry context (refining, flaring, fugitive emissions, etc.)
6. Focus on the LARGEST emission sources shown in the data

**Output Format - Return ONLY valid JSON matching this structure:**
{{
  "recommendations": [
    {{
      "priority": "High",
      "category": "Short descriptive category (e.g., 'Flare Gas Recovery', 'Energy Efficiency')",
      "recommendation": "Detailed recommendation text (2-3 sentences) that references SPECIFIC sources from the data above",
      "potential_impact": "Quantified impact based on actual data (e.g., 'Up to 20% reduction in Scope 1 emissions' or 'Estimated 5,000 tCO₂e annual reduction')"
    }}
  ]
}}"""

            # Call OpenAI API with GPT-5
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-5-mini",  # Using gpt-5-mini for cost-efficiency
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                reasoning_effort="minimal",  # User requested minimal reasoning
                verbosity="medium",  # Medium verbosity for balanced output
                max_completion_tokens=2000,  # Enough for 5-6 recommendations
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)
            recommendations = result.get('recommendations', [])

            # Validate recommendations structure
            validated_recs = []
            required_keys = ['priority', 'category', 'recommendation', 'potential_impact']

            for rec in recommendations:
                if all(k in rec for k in required_keys):
                    # Ensure priority is capitalized correctly
                    rec['priority'] = rec['priority'].capitalize()
                    validated_recs.append(rec)

            if validated_recs:
                print(f"✅ Generated {len(validated_recs)} AI-powered recommendations using GPT-5")
                return validated_recs
            else:
                print("❌ AI recommendations validation failed. Falling back to rule-based.")
                return self.generate_rule_based_recommendations()

        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            print("Falling back to rule-based recommendations.")
            return self.generate_rule_based_recommendations()

    def generate_recommendations(self, use_ai=False):
        """Generate recommendations - AI or rule-based

        Args:
            use_ai (bool): If True and OPENAI_API_KEY is set, use GPT-5. Otherwise use rule-based.

        Returns:
            list: List of recommendation dictionaries
        """
        if use_ai:
            return self.generate_ai_recommendations()
        else:
            return self.generate_rule_based_recommendations()

    def get_company_info(self):
        """Extract company information from Dashboard sheet"""
        if not self.data:
            return {'company_name': 'Unknown Company', 'reporting_year': '2025'}

        try:
            # First, try to get Dashboard data from already-loaded data (works for sample data)
            if 'Dashboard' in self.data:
                dashboard_df = self.data['Dashboard']

                if not dashboard_df.empty:
                    company_info = {}

                    # Dashboard sheet when read with header=0 has first row as columns
                    # So columns might be ['Company Name', 'PetrolCorp International']
                    # and first data row might be ['Reporting Year', 2024]

                    # Try to extract company name from column header (2nd column name)
                    if len(dashboard_df.columns) > 1:
                        company_name_candidate = dashboard_df.columns[1]
                        if pd.notna(company_name_candidate) and str(company_name_candidate) not in ['0', '1', 'Unnamed']:
                            company_info['company_name'] = str(company_name_candidate)

                    # Try to extract reporting year from first row second column
                    if not dashboard_df.empty and len(dashboard_df.columns) > 1:
                        year_candidate = dashboard_df.iloc[0, 1]
                        if pd.notna(year_candidate):
                            company_info['reporting_year'] = str(year_candidate)

                    # Set defaults if not found
                    if 'company_name' not in company_info:
                        company_info['company_name'] = 'Unknown Company'
                    if 'reporting_year' not in company_info:
                        company_info['reporting_year'] = '2025'

                    return company_info

            # Fallback: read from Excel file directly (for uploaded files)
            # Always read Dashboard sheet with header=None to avoid confusion
            dashboard_df_raw = pd.read_excel(self.excel_file, sheet_name='Dashboard', header=None)

            if dashboard_df_raw.empty:
                return {'company_name': 'Unknown Company', 'reporting_year': '2025'}

            company_info = {}

            # Dashboard sheet format: [Label, Value] in columns 0 and 1
            # Row 0: ['Company Name', actual_company_name]
            # Row 1: ['Reporting Year', actual_year]

            if len(dashboard_df_raw) > 0 and len(dashboard_df_raw.columns) > 1:
                company_info['company_name'] = str(dashboard_df_raw.iloc[0, 1]) if pd.notna(dashboard_df_raw.iloc[0, 1]) else 'Unknown Company'

            if len(dashboard_df_raw) > 1 and len(dashboard_df_raw.columns) > 1:
                company_info['reporting_year'] = str(dashboard_df_raw.iloc[1, 1]) if pd.notna(dashboard_df_raw.iloc[1, 1]) else '2025'

            # Set defaults if not found
            if 'company_name' not in company_info:
                company_info['company_name'] = 'Unknown Company'
            if 'reporting_year' not in company_info:
                company_info['reporting_year'] = '2025'

            return company_info
        except Exception as e:
            print(f"Error extracting company info: {e}")
            import traceback
            traceback.print_exc()
            return {'company_name': 'Unknown Company', 'reporting_year': '2025'}

    def get_summary_statistics(self, facility_filter=None):
        """Generate summary statistics for the report

        Args:
            facility_filter: Optional facility name to filter data for single facility
        """
        if not self.data:
            return {}

        try:
            scope1_df = self.data.get('Scope 1 Emissions', pd.DataFrame())
            scope2_df = self.data.get('Scope 2 Emissions', pd.DataFrame())
            scope3_df = self.data.get('Scope 3 Emissions', pd.DataFrame())
            facilities_df = self.data.get('Facility Breakdown', pd.DataFrame())

            # If facility filter is specified, get emissions for that facility only
            if facility_filter and not facilities_df.empty and 'Facility' in facilities_df.columns:
                facility_row = facilities_df[facilities_df['Facility'] == facility_filter]
                if not facility_row.empty:
                    scope1_total = facility_row['Scope_1'].iloc[0] if 'Scope_1' in facility_row.columns else 0
                    scope2_total = facility_row['Scope_2'].iloc[0] if 'Scope_2' in facility_row.columns else 0
                    scope3_total = facility_row['Scope_3'].iloc[0] if 'Scope_3' in facility_row.columns else 0
                    total_production = facility_row['Production'].iloc[0] if 'Production' in facility_row.columns else 1
                else:
                    scope1_total = scope2_total = scope3_total = total_production = 0
            else:
                # All facilities combined
                scope1_total = scope1_df['Annual_Total'].sum() if not scope1_df.empty and 'Annual_Total' in scope1_df.columns else 0
                scope2_total = scope2_df['Annual_Total'].sum() if not scope2_df.empty and 'Annual_Total' in scope2_df.columns else 0
                scope3_total = scope3_df['Annual_Total'].sum() if not scope3_df.empty and 'Annual_Total' in scope3_df.columns else 0
                total_production = facilities_df['Production'].sum() if not facilities_df.empty and 'Production' in facilities_df.columns else 1

            total_emissions = scope1_total + scope2_total + scope3_total

            # Calculate percentages
            scope_percentages = {
                'scope1_pct': (scope1_total / total_emissions * 100) if total_emissions > 0 else 0,
                'scope2_pct': (scope2_total / total_emissions * 100) if total_emissions > 0 else 0,
                'scope3_pct': (scope3_total / total_emissions * 100) if total_emissions > 0 else 0
            }

            # Production-based metrics
            carbon_intensity = total_emissions / total_production if total_production > 0 else 0

            # Get company info
            company_info = self.get_company_info()

            # Get facility names
            facility_names = []
            if not facilities_df.empty and 'Facility' in facilities_df.columns:
                facility_names = facilities_df['Facility'].tolist()

            return {
                'total_emissions': total_emissions,
                'scope1_total': scope1_total,
                'scope2_total': scope2_total,
                'scope3_total': scope3_total,
                'carbon_intensity': carbon_intensity,
                'total_facilities': 1 if facility_filter else (len(facilities_df) if not facilities_df.empty else 0),
                'report_date': self.report_date,
                'facility_name': facility_filter if facility_filter else 'All Facilities',
                'company_name': company_info.get('company_name', 'Unknown Company'),
                'reporting_year': company_info.get('reporting_year', '2025'),
                'facility_names': facility_names,
                **scope_percentages
            }
        except Exception as e:
            print(f"Error generating summary statistics: {e}")
            return {}