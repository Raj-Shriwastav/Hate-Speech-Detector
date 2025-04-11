import os
import pandas as pd
from comment_analyzer import CommentAnalyzer
import json
from dotenv import load_dotenv

def print_separator():
    print("\n" + "="*50 + "\n")

def test_data_loading():
    """Test loading data from both CSV and JSON files"""
    print("\n=== Testing Data Loading ===")
    analyzer = CommentAnalyzer()
    csv_df = json_df = None
    
    # Test CSV loading
    try:
        csv_df = analyzer.load_data("comments_dataset.csv")
        print(f"✅ CSV loading successful: {len(csv_df)} rows loaded")
        print("\nSample from CSV:")
        print(json.dumps(csv_df.head(1).to_dict('records')[0], indent=2))
    except Exception as e:
        print(f"❌ CSV loading failed: {str(e)}")
    
    # Test JSON loading
    try:
        json_df = analyzer.load_data("comments_dataset.json")
        print(f"\n✅ JSON loading successful: {len(json_df)} rows loaded")
        print("\nSample from JSON:")
        print(json.dumps(json_df.head(1).to_dict('records')[0], indent=2))
    except Exception as e:
        print(f"❌ JSON loading failed: {str(e)}")
    
    return csv_df, json_df

def test_comment_analysis(analyzer, df):
    """Test comment analysis functionality"""
    print_separator()
    print("=== Testing Comment Analysis ===")
    
    if df is None:
        print("❌ Cannot proceed with analysis: No data available")
        return None
    
    # Test with a sample of comments
    sample_df = df.head(5)
    print(f"Testing with {len(sample_df)} sample comments...")
    
    try:
        results_df = analyzer.process_comments(sample_df)
        print(f"\n✅ Comment analysis successful: {len(results_df)} comments analyzed")
        
        # Check if offensive comments were detected
        offensive_count = results_df[results_df['is_offensive'] == True].shape[0]
        print(f"Found {offensive_count} offensive comments out of {len(results_df)}")
        
        # Display sample results
        print("\nSample analysis results:")
        for _, row in results_df.iterrows():
            print(f"\nComment: '{row['comment_text'][:100]}...'")
            print(f"Is offensive: {row['is_offensive']}")
            print(f"Offense type: {row['offense_type']}")
            print(f"Explanation: {row['explanation']}")
            print("-" * 40)
    except Exception as e:
        print(f"❌ Comment analysis failed: {str(e)}")
        return None
    
    return results_df

def test_report_generation(analyzer, df):
    """Test report generation functionality"""
    print_separator()
    print("=== Testing Report Generation ===")
    
    if df is None:
        print("❌ Cannot proceed with report generation: No analyzed data available")
        return
    
    try:
        report = analyzer.generate_report(df)
        print("✅ Report generation successful")
        print(f"\nTotal comments: {report['total_comments']}")
        print(f"Offensive comments: {report['offensive_comments']}")
        print("\nOffense types breakdown:")
        for offense_type, count in report['offense_types'].items():
            print(f"- {offense_type}: {count}")
        
        print("\nTop 3 most severe offensive comments:")
        for i, comment in enumerate(report['top_offensive'][:3], 1):
            print(f"\n{i}. User: {comment['username']}")
            print(f"   Comment: '{comment['comment_text'][:100]}...'")
            print(f"   Type: {comment['offense_type']}")
            print(f"   Explanation: {comment['explanation']}")
    except Exception as e:
        print(f"❌ Report generation failed: {str(e)}")

def test_visualization(analyzer, df):
    """Test visualization functionality"""
    print_separator()
    print("=== Testing Visualization ===")
    
    if df is None:
        print("❌ Cannot proceed with visualization: No analyzed data available")
        return
    
    try:
        fig = analyzer.create_visualization(df)
        if fig is not None:
            print("✅ Visualization creation successful")
            print("Note: The visualization object is ready for display in Streamlit")
        else:
            print("⚠️ Visualization creation returned None")
    except Exception as e:
        print(f"❌ Visualization failed: {str(e)}")

def test_export_functionality(analyzer, df):
    """Test export functionality"""
    print_separator()
    print("=== Testing Export Functionality ===")
    
    if df is None:
        print("❌ Cannot proceed with export: No analyzed data available")
        return
    
    try:
        # Test CSV export
        csv_path = "test_export.csv"
        analyzer.export_results(df, csv_path)
        print(f"✅ CSV export successful: {csv_path}")
        
        # Test JSON export
        json_path = "test_export.json"
        analyzer.export_results(df, json_path)
        print(f"✅ JSON export successful: {json_path}")
        
        # Verify exported files
        csv_df = pd.read_csv(csv_path)
        print(f"\nCSV export verification: {len(csv_df)} rows")
        
        with open(json_path, "r") as f:
            json_data = json.load(f)
        print(f"JSON export verification: {len(json_data)} records")
        
        print("\nExport files created successfully:")
        print(f"1. {csv_path}")
        print(f"2. {json_path}")
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")

def main():
    print("🚀 Starting Project Tests")
    print("Make sure you have set up your GOOGLE_API_KEY in the .env file")
    print_separator()
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        print("Please add your API key to the .env file and try again")
        return
    
    # Test data loading
    csv_df, json_df = test_data_loading()
    
    # Use CSV data for further tests
    analyzer = CommentAnalyzer()
    
    # Test comment analysis
    results_df = test_comment_analysis(analyzer, csv_df)
    
    # Test report generation
    test_report_generation(analyzer, results_df)
    
    # Test visualization
    test_visualization(analyzer, results_df)
    
    # Test export functionality
    test_export_functionality(analyzer, results_df)
    
    print_separator()
    print("🏁 All Tests Completed")
    print("Check the output above for any errors or warnings")

if __name__ == "__main__":
    main() 