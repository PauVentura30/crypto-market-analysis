"""
Test Script for Crypto Market Analysis Project
Run this to validate that everything is working correctly
"""

import sys
import os
sys.path.append('src')

def test_project():
    """Test all components of the project"""
    
    print("🚀 Testing Crypto Market Analysis Project")
    print("=" * 50)
    
    # Test 1: Import modules
    print("\n1️⃣ Testing module imports...")
    try:
        from data_collector import CryptoMarketCollector
        from analyzer import MarketAnalyzer
        from visualizer import MarketVisualizer
        print("✅ All modules imported successfully!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Data collection
    print("\n2️⃣ Testing data collection...")
    try:
        collector = CryptoMarketCollector()
        
        # Test with small dataset
        data = collector.get_combined_data(
            crypto_ids=['bitcoin', 'ethereum'],
            traditional_symbols=['SPY', 'QQQ'],
            days=30  # Small dataset for testing
        )
        
        if not data.empty:
            print(f"✅ Data collected successfully! Shape: {data.shape}")
            print(f"   Date range: {data.index.min()} to {data.index.max()}")
        else:
            print("❌ Data collection failed - empty dataset")
            return False
            
    except Exception as e:
        print(f"❌ Data collection error: {e}")
        return False
    
    # Test 3: Analysis
    print("\n3️⃣ Testing analysis...")
    try:
        analyzer = MarketAnalyzer(data)
        
        # Test performance metrics
        performance = analyzer.calculate_performance_metrics()
        print(f"✅ Performance analysis complete! Assets analyzed: {len(performance)}")
        
        # Test insights
        insights = analyzer.generate_insights()
        print(f"✅ Generated {len(insights)} market insights")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False
    
    # Test 4: Visualizations
    print("\n4️⃣ Testing visualizations...")
    try:
        visualizer = MarketVisualizer(data, analyzer)
        
        # Test plot generation
        price_plot = visualizer.plot_price_evolution()
        correlation_plot = visualizer.plot_correlation_heatmap()
        
        if price_plot and correlation_plot:
            print("✅ Visualizations generated successfully!")
        else:
            print("❌ Visualization generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return False
    
    # Test 5: Save functionality
    print("\n5️⃣ Testing save functionality...")
    try:
        # Save analysis
        analyzer.save_analysis("results/test_analysis.txt")
        
        # Save plots
        plots = {
            'test_price_evolution': price_plot,
            'test_correlation': correlation_plot
        }
        visualizer.save_plots(plots)
        
        print("✅ Save functionality working!")
        
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("\n📊 Project Summary:")
    print(f"   • Data collected: {data.shape[0]} days, {data.shape[1]} assets")
    print(f"   • Analysis complete: {len(performance)} assets analyzed")
    print(f"   • Insights generated: {len(insights)} key findings")
    print(f"   • Visualizations: Multiple charts created")
    print(f"   • Files saved: Analysis and charts exported")
    
    print("\n🚀 Ready to run the dashboard!")
    print("   Run: streamlit run dashboard/streamlit_app.py")
    
    return True

def show_sample_insights(insights):
    """Display sample insights from the analysis"""
    print("\n💡 Sample Insights:")
    print("-" * 20)
    for i, insight in enumerate(insights[:3], 1):
        print(f"{i}. {insight}")

if __name__ == "__main__":
    success = test_project()
    
    if success:
        print("\n✨ Your crypto market analysis project is ready!")
        print("   Perfect for your portfolio! 🎯")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")