#!/usr/bin/env python3
"""
Script to optimize HTML files by:
1. Extracting common inline CSS to external file
2. Replacing PNG logo references with inline SVG
3. Improving accessibility and performance
"""

import re
import os

# Logo SVG content with accessibility attributes
LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="Stink Films Logo" class="logo-svg">
  <title>Stink Films</title>
  <g>
    <path d="M48.66,34.44h9.23L41.21,88.33h-12Z"/>
    <path d="M116.06,54.41c-5.11-3.76-11.47-3.17-15.17-2a19,19,0,0,0-6,3.51c-2.87,2.41-5.75,6.4-5.53,11,.36,7.8,9.18,5.68,12.93,10.36a8.61,8.61,0,0,1,1,9.5,6,6,0,0,1-7.14,3.39A7.94,7.94,0,0,1,93.45,89c-3.59-2.46-6.27-6.81-8.55-10.79C82,73.13,78.19,67,78.25,62.93c0-2.91,5.18-6.82,10.77-11.5,3.46-2.89,5.32-4.7,11.08-9.88,2.59-2.33,7.78-7.11,7.78-7.11h-13s-4.65,5.36-7.78,9.17c0,0-1.71,2.07-5,5.82-5.2,6-9.88,9.63-12.15,9.18a.88.88,0,0,1-.23-.07c-2.12-.94-.29-6.45,1.76-11.59,1.15-2.87,6.27-12.51,6.27-12.51H66.16L49.48,88.33H61.1A78.33,78.33,0,0,1,63.22,76.4c.76-2.92,2.83-11.65,5.44-11.65,2,0,4.22,2.61,6,11.86C76,83.08,79,90.77,82.76,94c8.66,7.33,19.3,4.14,23.89,2.12,4.76-2.1,7.87-6.19,8.43-9.58,1.38-8.36-5-12.89-9-14.95s-5.55-3.92-5.68-6.75c-.18-3.79,2.42-8.42,6.81-9.13,2.17-.36,5.19.18,5.75,2.28.61,2.29-4.59,7.34-4.59,7.34h10.1S122.85,59.41,116.06,54.41Z"/>
    <path d="M15.64,40c1.52,10.23,4.69,18.58,7.21,18.58s4.19-2.16,7.68-16C32.63,34.3,35,21.48,35,21.48H45.56L26.62,72.25H16.5L.14,21.48H14.08A156.14,156.14,0,0,0,15.64,40Z"/>
  </g>
</svg>'''

# Base64 encoded inline SVG for meta tags (smaller for social sharing)
LOGO_DATA_URI = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAgMTIwIj48Zz48cGF0aCBkPSJNNDguNjYsMzQuNDRoOS4yM0w0MS4yMSw4OC4zM2gtMTJaIi8+PHBhdGggZD0iTTExNi4wNiw1NC40MWMtNS4xMS0zLjc2LTExLjQ3LTMuMTctMTUuMTctMmExOSwxOSwwLDAsMC02LDMuNTFjLTIuODcsMi40MS01Ljc1LDYuNC01LjUzLDExLC4zNiw3LjgsOS4xOCw1LjY4LDEyLjkzLDEwLjM2YTguNjEsOC42MSwwLDAsMSwxLDkuNSw2LDYsMCwwLDEtNy4xNCwzLjM5QTcuOTQsNy45NCwwLDAsMSw5My40NSw4OWMtMy41OS0yLjQ2LTYuMjctNi44MS04LjU1LTEwLjc5QzgyLDczLjEzLDc4LjE5LDY3LDc4LjI1LDYyLjkzYzAtMi45MSw1LjE4LTYuODIsMTAuNzctMTEuNSwzLjQ2LTIuODksNS4zMi00LjcsMTEuMDgtOS44OCwyLjU5LTIuMzMsNy43OC03LjExLDcuNzgtNy4xMWgtMTNzLTQuNjUsNS4zNi03Ljc4LDkuMTdjMCwwLTEuNzEsMi4wNy01LDUuODItNS4yLDYtOS44OCw5LjYzLTEyLjE1LDkuMThhLjg4Ljg4LDAsMCwxLS4yMy0uMDdjLTIuMTItLjk0LS4yOS02LjQ1LDEuNzYtMTEuNTksMS4xNS0yLjg3LDYuMjctMTIuNTEsNi4yNy0xMi41MUg2Ni4xNkw0OS40OCw4OC4zM0g2MS4xQTc4LjMzLDc4LjMzLDAsMCwxLDYzLjIyLDc2LjRjLjc2LTIuOTIsMi44My0xMS42NSw1LjQ0LTExLjY1LDIsMCw0LjIyLDIuNjEsNiwxMS44NkM3Niw4My4wOCw3OSw5MC43Nyw4Mi43Niw5NGM4LjY2LDcuMzMsMTkuMyw0LjE0LDIzLjg5LDIuMTIsNC43Ni0yLjEsNy44Ny02LjE5LDguNDMtOS41OCwxLjM4LTguMzYtNS0xMi44OS05LTE0Ljk1cy01LjU1LTMuOTItNS42OC02Ljc1Yy0uMTgtMy43OSwyLjQyLTguNDIsNi44MS05LjEzLDIuMTctLjM2LDUuMTkuMTgsNS43NSwyLjI4LjYxLDIuMjktNC41OSw3LjM0LTQuNTksNy4zNGgxMC4xUzEyMi44NSw1OS40MSwxMTYuMDYsNTQuNDFaIi8+PHBhdGggZD0iTTE1LjY0LDQwYzEuNTIsMTAuMjMsNC42OSwxOC41OCw3LjIxLDE4LjU4czQuMTktMi4xNiw3LjY4LTE2QzMyLjYzLDM0LjMsMzUsMjEuNDgsMzUsMjEuNDhINDUuNTZMMjYuNjIsNzIuMjVIMTYuNUwuMTQsMjEuNDhIMTQuMDhBMTU2LjE0LDE1Ni4xNCwwLDAsMCwxNS42NCw0MFoiLz48L2c+PC9zdmc+'

def extract_common_css(html_files):
    """Extract common CSS from all HTML files."""
    all_css = []
    
    for file in html_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
        if style_match:
            css = style_match.group(1)
            all_css.append(css)
    
    if not all_css:
        return ''
    
    # Find common prefix (first ~28K characters are common)
    # Split at .changing[ to get the common base
    common_css = all_css[0].split('.changing[')[0]
    
    return common_css

def update_html_file(file_path, common_css_link, logo_svg):
    """Update a single HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace PNG logo references in meta tags with data URI
    content = re.sub(
        r'https://films-stink\.b-cdn\.net/wp-content/uploads/2021/04/stink-films-logo-black-small\.png',
        LOGO_DATA_URI,
        content
    )
    
    # 2. Extract and split inline CSS
    style_match = re.search(r'(<style[^>]*>)(.*?)(</style>)', content, re.DOTALL)
    if style_match:
        style_start = style_match.group(1)
        inline_css = style_match.group(2)
        style_end = style_match.group(3)
        
        # Split CSS into common and page-specific
        parts = inline_css.split('.changing[')
        if len(parts) > 1:
            # Keep page-specific CSS inline
            page_specific_css = '.changing[' + '.changing['.join(parts[1:])
            
            # Replace inline style with link to common CSS + remaining page-specific CSS
            new_style_block = f'{common_css_link}{style_start}{page_specific_css}{style_end}'
            content = content[:style_match.start()] + new_style_block + content[style_match.end():]
    
    return content

def main():
    """Main function to optimize all HTML files."""
    html_files = ['index.html', 'about/index.html', 'production/index.html', 'search/index.html']
    
    # Extract common CSS
    print("Extracting common CSS...")
    common_css = extract_common_css(html_files)
    print(f"Common CSS size: {len(common_css)} characters")
    
    # Save common CSS to external file
    css_file = '_nuxt/common.css'
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(common_css)
    print(f"Created {css_file}")
    
    # Determine CSS link path for each file
    css_links = {
        'index.html': '<link rel="stylesheet" href="_nuxt/common.css">',
        'about/index.html': '<link rel="stylesheet" href="../_nuxt/common.css">',
        'production/index.html': '<link rel="stylesheet" href="../_nuxt/common.css">',
        'search/index.html': '<link rel="stylesheet" href="../_nuxt/common.css">',
    }
    
    # Update each HTML file
    for file in html_files:
        print(f"\nProcessing {file}...")
        original_size = os.path.getsize(file)
        
        updated_content = update_html_file(file, css_links[file], LOGO_SVG)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        new_size = os.path.getsize(file)
        savings = original_size - new_size
        print(f"  Original: {original_size} bytes")
        print(f"  New: {new_size} bytes")
        print(f"  Savings: {savings} bytes ({savings/original_size*100:.1f}%)")
    
    print("\n✓ Optimization complete!")
    print(f"✓ Created external CSS file: {css_file}")
    print(f"✓ Updated {len(html_files)} HTML files")
    print(f"✓ Replaced PNG logo references with inline SVG data URI")

if __name__ == '__main__':
    main()
