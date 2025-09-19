import streamlit as st
import streamlit.components.v1 as components

# Set wide layout
st.set_page_config(layout="wide", page_title="Portfolio Report")

# Load HTML file
try:
    with open('portfolio_report.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Header with download button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📊 Portfolio Report")
    
    st.divider()
    
    # Enhanced HTML with print functionality
    enhanced_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                background: white !important;
                color: black !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                line-height: 1.5;
            }}
            
            * {{
                color: black !important;
                background: transparent !important;
            }}
            
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                background: white !important;
            }}
            
            th, td {{
                border: 1px solid #333 !important;
                padding: 12px 8px;
                text-align: left;
                color: black !important;
                background: white !important;
            }}
            
            th {{
                background: #f8f9fa !important;
                font-weight: bold;
                color: black !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #333 !important;
                margin: 20px 0 10px 0;
            }}
            
            .print-btn {{
                position: fixed;
                top: 10px;
                right: 10px;
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                z-index: 1000;
            }}
            
            .print-btn:hover {{
                background: #0056b3;
            }}
            
            @media print {{
                .print-btn {{ display: none; }}
                body {{ 
                    background: white !important;
                    color: black !important;
                }}
                * {{
                    color: black !important;
                    background: white !important;
                }}
            }}
        </style>
    </head>
    <body>
        <button class="print-btn" onclick="window.print()">📄 Print/Save as PDF</button>
        {html_content}
        
        <script>
            // Ensure all elements are visible
            document.addEventListener('DOMContentLoaded', function() {{
                const elements = document.querySelectorAll('*');
                elements.forEach(el => {{
                    if (el.style.color === 'transparent' || el.style.display === 'none') {{
                        el.style.color = 'black';
                        el.style.display = 'block';
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    # Display the HTML
    components.html(enhanced_html, height=1500, scrolling=True)
    
    # Instructions
    st.info("💡 **To save as PDF:** Click the 'Print/Save as PDF' button in the report, then choose 'Save as PDF' in your browser's print dialog.")

except FileNotFoundError:
    st.error("❌ File 'portfolio_report.html' not found in the current directory!")
    st.info("Make sure 'portfolio_report.html' is in the same folder as your Python script.")

except Exception as e:
    st.error(f"❌ Error loading file: {str(e)}")