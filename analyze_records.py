import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置seaborn样式
sns.set_theme(style="darkgrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

def load_csv_files(records_dir='records'):
    """加载所有CSV文件并解析文件名中的参数"""
    data_frames = []
    
    for file_path in Path(records_dir).glob('*.csv'):
        try:
            # 解析文件名中的参数
            filename = file_path.stem
            params = filename.split('_')
            base_asset = params[2].replace('0', '')  # USDC0 -> USDC
            usdt_amount = float(params[3].replace('USDT', ''))
            buy_price = float(params[4].replace('buy', ''))
            spread = float(params[5].replace('spread', ''))
            
            # 读取CSV文件
            df = pd.read_csv(file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 添加参数列
            df['base_asset'] = base_asset
            df['initial_usdt'] = usdt_amount
            df['buy_price'] = buy_price
            df['spread'] = spread
            
            data_frames.append(df)
            logger.info(f"Successfully loaded {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
    
    return pd.concat(data_frames, ignore_index=True)

def plot_total_amount_comparison(df, output_dir):
    """绘制不同买入价格和基础资产的总资产价值变化"""
    plt.figure(figsize=(15, 8))
    
    # 使用seaborn的颜色调色板，为每个base_asset选择一个基础颜色
    base_palette = sns.color_palette("husl", n_colors=len(df['base_asset'].unique()))
    
    # 获取排序后的买入价格列表
    buy_prices = sorted(df['buy_price'].unique())
    
    # 为每个base_asset创建一个颜色渐变
    for i, base_asset in enumerate(sorted(df['base_asset'].unique())):
        base_color = base_palette[i]
        # 创建颜色渐变
        colors = sns.light_palette(base_color, n_colors=len(buy_prices) + 2)[1:-1]  # 去掉最浅和最深的颜色
        
        for j, buy_price in enumerate(buy_prices):
            data = df[(df['base_asset'] == base_asset) & (df['buy_price'] == buy_price)]
            if not data.empty:
                sns.lineplot(
                    data=data,
                    x='timestamp',
                    y='totalAmount',
                    label=f'{base_asset}/USDT (buy={buy_price})',
                    marker='o',
                    color=colors[j]
                )
    
    plt.title('Total Amount Comparison', fontsize=14, pad=20)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Total Amount (USDT)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存图片，增加DPI使图片更清晰
    plt.savefig(f'{output_dir}/total_amount.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_trading_frequency(df, output_dir):
    """绘制交易频率分析"""
    plt.figure(figsize=(15, 6))
    
    # 使用seaborn的颜色调色板
    palette = sns.color_palette("Set2", n_colors=len(df['base_asset'].unique()))
    
    for i, base_asset in enumerate(sorted(df['base_asset'].unique())):
        asset_data = df[df['base_asset'] == base_asset]
        trades_per_hour = asset_data.groupby(asset_data['timestamp'].dt.hour).size()
        
        # 使用seaborn的scatterplot和lineplot组合
        sns.scatterplot(
            x=trades_per_hour.index,
            y=trades_per_hour.values,
            label=f'{base_asset}/USDT',
            color=palette[i],
            s=100
        )
        sns.lineplot(
            x=trades_per_hour.index,
            y=trades_per_hour.values,
            color=palette[i],
            alpha=0.5
        )
    
    plt.title('Trading Frequency by Hour', fontsize=14, pad=20)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Number of Trades', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存图片，增加DPI使图片更清晰
    plt.savefig(f'{output_dir}/trading_frequency.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_profit_comparison(df, output_dir):
    """绘制不同策略的收益率对比"""
    plt.figure(figsize=(12, 6))
    
    profits = []
    labels = []
    colors = []
    
    # 使用seaborn的颜色调色板，为每个base_asset选择一个基础颜色
    base_palette = sns.color_palette("husl", n_colors=len(df['base_asset'].unique()))
    
    # 获取排序后的买入价格列表
    buy_prices = sorted(df['buy_price'].unique())
    
    # 为每个base_asset创建一个颜色渐变
    for i, base_asset in enumerate(sorted(df['base_asset'].unique())):
        base_color = base_palette[i]
        # 创建颜色渐变
        color_palette = sns.light_palette(base_color, n_colors=len(buy_prices) + 2)[1:-1]  # 去掉最浅和最深的颜色
        
        for j, buy_price in enumerate(buy_prices):
            data = df[(df['base_asset'] == base_asset) & (df['buy_price'] == buy_price)]
            if not data.empty:
                initial_amount = data['initial_usdt'].iloc[0]
                final_amount = data['totalAmount'].iloc[-1]
                profit_pct = (final_amount - initial_amount) / initial_amount * 100
                
                profits.append(profit_pct)
                labels.append(f'{base_asset}/USDT\nbuy={buy_price}')
                colors.append(color_palette[j])
    
    # 使用seaborn的barplot
    sns.barplot(x=labels, y=profits, palette=colors)
    
    plt.title('Profit Comparison (%)', fontsize=14, pad=20)
    plt.xlabel('Strategy', fontsize=12)
    plt.ylabel('Profit (%)', fontsize=12)
    plt.xticks(rotation=45)
    
    # 添加数值标签
    for i, v in enumerate(profits):
        plt.text(i, v, f'{v:.2f}%', ha='center', va='bottom')
    
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    # 保存图片，增加DPI使图片更清晰
    plt.savefig(f'{output_dir}/profit_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """主函数"""
    logger.info("Starting analysis...")
    output_dir = 'analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    df = load_csv_files()
    
    # 生成分析图表
    plot_total_amount_comparison(df, output_dir=output_dir)
    plot_trading_frequency(df, output_dir=output_dir)
    plot_profit_comparison(df, output_dir=output_dir)
    
    logger.info(f"Analysis completed. Check the generated PNG files in {output_dir} directory for results.")

if __name__ == "__main__":
    main() 