import pandas as pd
import matplotlib.pyplot as plt

def plot_performance():
    try:
        df = pd.read_csv("backtest_report.csv")
    except FileNotFoundError:
        print("❌ Error: Run 'make run-mock' first to generate the CSV.")
        return
    if df.empty:
        print("❌ Error: backtest_report.csv is empty.")
        return

    # Create the figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot the Price Line
    color = 'tab:blue'
    ax1.set_xlabel('Cycle')
    ax1.set_ylabel('Consensus Price ($)', color=color)
    ax1.plot(df['Cycle'], df['Price'], color=color, marker='o', linewidth=2, label='ETH Price')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Highlight the Crash and Recovery (Optional annotations based on our mock data)
    min_price_cycle = df.loc[df['Price'].idxmin(), 'Cycle']
    max_price_cycle = df.loc[df['Price'].idxmax(), 'Cycle']
    
    ax1.annotate('BUY TRIGGER\n(Dip Detected)', 
                 xy=(min_price_cycle, df['Price'].min()), 
                 xytext=(min_price_cycle, df['Price'].min() - 150),
                 arrowprops=dict(facecolor='green', shrink=0.05),
                 color='green', fontweight='bold', ha='center')

    ax1.annotate('SELL TRIGGER\n(Peak Detected)', 
                 xy=(max_price_cycle, df['Price'].max()), 
                 xytext=(max_price_cycle, df['Price'].max() + 100),
                 arrowprops=dict(facecolor='red', shrink=0.05),
                 color='red', fontweight='bold', ha='center')

    # Title and styling
    plt.title('MiniChain Vault: Automated Backtest Performance', fontsize=14, fontweight='bold')
    fig.tight_layout()

    # Save it as an image
    plt.savefig('backtest_chart.png', dpi=300)
    print("✅ Success! Chart saved as 'backtest_chart.png'")

if __name__ == "__main__":
    plot_performance()