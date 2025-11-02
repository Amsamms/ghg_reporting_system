"""
AI-powered and rule-based recommendation engine for GHG emission reduction.
Generates strategic recommendations based on emission data analysis.
"""

import os
import json
from typing import Dict, Any, List, Optional


def generate_recommendations(
    summary: Dict[str, Any],
    by_scope: Dict[int, Dict],
    by_subcategory: Dict[str, Dict],
    by_facility: Dict[str, Dict],
    use_ai: bool = False,
) -> List[Dict[str, str]]:
    """
    Generate strategic recommendations for emission reduction.

    Args:
        summary: Summary statistics dictionary
        by_scope: Emissions by scope
        by_subcategory: Emissions by subcategory
        by_facility: Emissions by facility
        use_ai: If True, use AI-powered recommendations (requires OpenAI API key)

    Returns:
        List of recommendation dictionaries with priority, category, recommendation, and impact
    """

    if use_ai:
        try:
            return generate_ai_recommendations(summary, by_scope, by_subcategory, by_facility)
        except Exception as e:
            print(f"AI recommendations failed: {e}. Falling back to rule-based.")
            return generate_rule_based_recommendations(summary, by_scope, by_subcategory, by_facility)
    else:
        return generate_rule_based_recommendations(summary, by_scope, by_subcategory, by_facility)


def generate_ai_recommendations(
    summary: Dict[str, Any],
    by_scope: Dict[int, Dict],
    by_subcategory: Dict[str, Dict],
    by_facility: Dict[str, Dict],
) -> List[Dict[str, str]]:
    """
    Generate AI-powered recommendations using OpenAI GPT-5.

    Requires OPENAI_API_KEY environment variable.
    """

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI library required. Install with: pip install openai")

    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    # Prepare top emission sources
    top_subcategories = sorted(
        [
            {
                'subcategory': subcat,
                'emissions_tco2e': data.get('_total_co2e_kg', 0) / 1000
            }
            for subcat, data in by_subcategory.items()
        ],
        key=lambda x: x['emissions_tco2e'],
        reverse=True
    )[:5]

    top_facilities = sorted(
        [
            {
                'facility': fac,
                'emissions_tco2e': data.get('_total_co2e_kg', 0) / 1000
            }
            for fac, data in by_facility.items()
        ],
        key=lambda x: x['emissions_tco2e'],
        reverse=True
    )[:3]

    # Construct prompt
    prompt = f"""You are a GHG emissions expert analyzing a petroleum company's emissions data. Based on the data below, generate 5-6 strategic recommendations following the GHG Protocol Corporate Standard and petroleum industry best practices.

**Company Emissions Data:**
- Total Emissions: {summary['total_co2e_tonnes']:,.0f} tCO₂e
- Scope 1 (Direct): {by_scope.get(1, {}).get('_total_co2e_kg', 0) / 1000:,.0f} tCO₂e ({summary['scope_1_pct']:.1f}%)
- Scope 2 (Energy): {by_scope.get(2, {}).get('_total_co2e_kg', 0) / 1000:,.0f} tCO₂e ({summary['scope_2_pct']:.1f}%)
- Scope 3 (Indirect): {by_scope.get(3, {}).get('_total_co2e_kg', 0) / 1000:,.0f} tCO₂e ({summary['scope_3_pct']:.1f}%)

**Top Emission Subcategories:**
{json.dumps(top_subcategories, indent=2)}

**Top Emitting Facilities:**
{json.dumps(top_facilities, indent=2)}

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

    # Call OpenAI API
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

    return recommendations


def generate_rule_based_recommendations(
    summary: Dict[str, Any],
    by_scope: Dict[int, Dict],
    by_subcategory: Dict[str, Dict],
    by_facility: Dict[str, Dict],
) -> List[Dict[str, str]]:
    """
    Generate rule-based recommendations using emission data analysis.
    Fallback when AI is not available.
    """

    recommendations = []

    total_emissions = summary['total_co2e_tonnes']
    scope1_pct = summary['scope_1_pct']
    scope2_pct = summary['scope_2_pct']
    scope3_pct = summary['scope_3_pct']

    # Rule 1: High Scope 1 emissions
    if scope1_pct > 60:
        scope1_tonnes = by_scope.get(1, {}).get('_total_co2e_kg', 0) / 1000
        recommendations.append({
            'priority': 'High',
            'category': 'Scope 1 Direct Emissions',
            'recommendation': f'Scope 1 emissions represent {scope1_pct:.1f}% ({scope1_tonnes:,.0f} tCO₂e) of your total footprint. Priority actions: 1) Conduct detailed combustion efficiency audit, 2) Implement flare gas recovery systems, 3) Upgrade fugitive emission monitoring and repair programs (LDAR), 4) Consider fuel switching to lower-carbon alternatives where feasible.',
            'potential_impact': f'Estimated reduction potential: 15-25% of Scope 1 emissions ({scope1_tonnes * 0.15:,.0f} - {scope1_tonnes * 0.25:,.0f} tCO₂e annually)'
        })

    # Rule 2: High Scope 2 emissions
    if scope2_pct > 30:
        scope2_tonnes = by_scope.get(2, {}).get('_total_co2e_kg', 0) / 1000
        recommendations.append({
            'priority': 'High',
            'category': 'Renewable Energy Transition',
            'recommendation': f'Scope 2 emissions account for {scope2_pct:.1f}% ({scope2_tonnes:,.0f} tCO₂e). Implement renewable energy procurement strategy: 1) Evaluate on-site solar PV potential, 2) Negotiate renewable energy PPAs, 3) Purchase renewable energy certificates (RECs) for residual consumption, 4) Conduct energy efficiency improvements (lighting, HVAC, motors).',
            'potential_impact': f'Potential to achieve 50-100% Scope 2 reduction through renewable energy ({scope2_tonnes * 0.5:,.0f} - {scope2_tonnes:,.0f} tCO₂e)'
        })

    # Rule 3: Check for flaring
    flaring_found = any('flaring' in subcat.lower() or 'flare' in subcat.lower() for subcat in by_subcategory.keys())
    if flaring_found:
        flaring_emissions = sum(
            data.get('_total_co2e_kg', 0) / 1000
            for subcat, data in by_subcategory.items()
            if 'flaring' in subcat.lower() or 'flare' in subcat.lower()
        )
        if flaring_emissions > 0:
            recommendations.append({
                'priority': 'High',
                'category': 'Flare Gas Recovery',
                'recommendation': f'Flaring activities contribute {flaring_emissions:,.0f} tCO₂e. Implement flare minimization program: 1) Install vapor recovery units (VRUs), 2) Optimize process operations to minimize upsets, 3) Route excess gas to fuel system where possible, 4) Upgrade flare monitoring systems, 5) Consider gas-to-power opportunities.',
                'potential_impact': f'Flare reduction potential: 40-70% ({flaring_emissions * 0.4:,.0f} - {flaring_emissions * 0.7:,.0f} tCO₂e annually)'
            })

    # Rule 4: Check for fugitive emissions
    fugitive_found = any('fugitive' in subcat.lower() or 'leak' in subcat.lower() for subcat in by_subcategory.keys())
    if fugitive_found:
        fugitive_emissions = sum(
            data.get('_total_co2e_kg', 0) / 1000
            for subcat, data in by_subcategory.items()
            if 'fugitive' in subcat.lower() or 'leak' in subcat.lower()
        )
        if fugitive_emissions > 0:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Fugitive Emission Control',
                'recommendation': f'Fugitive emissions total {fugitive_emissions:,.0f} tCO₂e. Strengthen leak detection and repair (LDAR) program: 1) Implement optical gas imaging (OGI) surveys, 2) Increase inspection frequency, 3) Replace high-leak components with low-emission designs, 4) Install continuous monitoring at critical points.',
                'potential_impact': f'LDAR program improvements: 25-40% reduction ({fugitive_emissions * 0.25:,.0f} - {fugitive_emissions * 0.4:,.0f} tCO₂e)'
            })

    # Rule 5: Check for transportation
    transport_found = any('transport' in subcat.lower() or 'travel' in subcat.lower() or 'commut' in subcat.lower() for subcat in by_subcategory.keys())
    if transport_found:
        transport_emissions = sum(
            data.get('_total_co2e_kg', 0) / 1000
            for subcat, data in by_subcategory.items()
            if 'transport' in subcat.lower() or 'travel' in subcat.lower() or 'commut' in subcat.lower()
        )
        if transport_emissions > total_emissions * 0.1:  # >10% of total
            recommendations.append({
                'priority': 'Medium',
                'category': 'Transportation Optimization',
                'recommendation': f'Transportation-related emissions total {transport_emissions:,.0f} tCO₂e ({transport_emissions / total_emissions * 100:.1f}% of total). Strategies: 1) Optimize logistics and routing, 2) Transition fleet to hybrid/electric vehicles, 3) Encourage employee carpooling and remote work, 4) Consolidate shipments to improve load factors.',
                'potential_impact': f'Transportation optimization: 15-30% reduction ({transport_emissions * 0.15:,.0f} - {transport_emissions * 0.3:,.0f} tCO₂e)'
            })

    # Rule 6: Energy efficiency (general)
    recommendations.append({
        'priority': 'Medium',
        'category': 'Energy Efficiency',
        'recommendation': 'Implement comprehensive energy management system per ISO 50001: 1) Conduct energy audits at all facilities, 2) Install sub-metering for real-time monitoring, 3) Optimize boiler/heater operations, 4) Implement waste heat recovery, 5) Upgrade to high-efficiency motors and drives, 6) Establish energy performance KPIs.',
        'potential_impact': f'Energy efficiency programs typically yield 10-15% reduction ({total_emissions * 0.1:,.0f} - {total_emissions * 0.15:,.0f} tCO₂e)'
    })

    # Rule 7: Data quality and monitoring
    recommendations.append({
        'priority': 'Low',
        'category': 'Data Quality & Monitoring',
        'recommendation': 'Enhance GHG data management infrastructure: 1) Deploy continuous emissions monitoring systems (CEMS) at major sources, 2) Implement automated data collection and validation, 3) Conduct third-party verification, 4) Establish monthly tracking dashboards, 5) Align with TCFD reporting framework.',
        'potential_impact': 'Improved data quality enables better decision-making and ensures accurate tracking of reduction progress'
    })

    # Rule 8: If facilities have large variations
    if len(by_facility) > 1:
        facility_emissions = sorted(
            [(fac, data.get('_total_co2e_kg', 0) / 1000) for fac, data in by_facility.items()],
            key=lambda x: x[1],
            reverse=True
        )
        top_facility = facility_emissions[0]
        if top_facility[1] > total_emissions * 0.4:  # One facility >40% of total
            recommendations.append({
                'priority': 'High',
                'category': 'Facility-Specific Action',
                'recommendation': f'Facility "{top_facility[0]}" accounts for {top_facility[1]:,.0f} tCO₂e ({top_facility[1] / total_emissions * 100:.1f}% of total). Prioritize site-specific decarbonization plan: 1) Detailed facility audit, 2) Technology feasibility studies (CCS, electrification, hydrogen), 3) Capital investment plan, 4) Stakeholder engagement with local community.',
                'potential_impact': f'Focus on top facility can drive 30-50% of total organizational reduction target'
            })

    # Ensure we have 5-6 recommendations (trim if too many)
    return recommendations[:6]
