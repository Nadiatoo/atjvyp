#!/usr/bin/env python3
"""
拓扑分析原型 - 基于网络化概率思维和拓扑结构思想
"""

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE, MDS
from scipy.spatial.distance import pdist, squareform

class TopologyMarketAnalyzer:
    """市场拓扑分析器"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.manifold_coords = None
        self.topology_features = {}
        
    def build_correlation_network(self, price_data, threshold=0.7):
        """
        构建相关性网络
        price_data: DataFrame, 行是时间，列是股票/板块
        threshold: 相关性阈值
        """
        # 计算相关性矩阵
        corr_matrix = price_data.corr()
        
        # 构建网络
        self.graph = nx.Graph()
        
        # 添加节点
        for stock in price_data.columns:
            self.graph.add_node(stock, type='stock')
            
        # 添加边（基于相关性）
        for i, stock1 in enumerate(price_data.columns):
            for j, stock2 in enumerate(price_data.columns):
                if i < j:  # 避免重复
                    corr = abs(corr_matrix.iloc[i, j])
                    if corr > threshold:
                        self.graph.add_edge(stock1, stock2, 
                                          weight=corr,
                                          correlation=corr_matrix.iloc[i, j])
        
        return self.graph
    
    def analyze_topology_features(self):
        """分析拓扑特征"""
        features = {}
        
        # 1. 连通性分析
        if nx.is_connected(self.graph):
            features['connected'] = True
            features['diameter'] = nx.diameter(self.graph)
            features['avg_path_length'] = nx.average_shortest_path_length(self.graph)
        else:
            features['connected'] = False
            # 最大连通分量
            largest_cc = max(nx.connected_components(self.graph), key=len)
            features['largest_component_size'] = len(largest_cc)
            features['num_components'] = nx.number_connected_components(self.graph)
        
        # 2. 中心性分析
        features['degree_centrality'] = nx.degree_centrality(self.graph)
        features['betweenness_centrality'] = nx.betweenness_centrality(self.graph)
        features['closeness_centrality'] = nx.closeness_centrality(self.graph)
        
        # 3. 聚类分析
        features['clustering_coefficient'] = nx.average_clustering(self.graph)
        features['transitivity'] = nx.transitivity(self.graph)
        
        # 4. 社区检测
        from networkx.algorithms.community import greedy_modularity_communities
        communities = list(greedy_modularity_communities(self.graph))
        features['communities'] = communities
        features['num_communities'] = len(communities)
        
        # 5. 度分布
        degrees = [d for n, d in self.graph.degree()]
        features['degree_distribution'] = {
            'mean': np.mean(degrees),
            'std': np.std(degrees),
            'max': np.max(degrees),
            'min': np.min(degrees)
        }
        
        self.topology_features = features
        return features
    
    def manifold_learning(self, price_data, n_components=2):
        """
        流形学习：发现数据的内在低维结构
        """
        # 使用t-SNE进行流形学习
        tsne = TSNE(n_components=n_components, 
                   random_state=42,
                   perplexity=min(30, len(price_data.columns)-1))
        
        # 转置：每列（股票）是一个数据点
        data_for_tsne = price_data.T.values
        
        # 确保没有NaN
        data_for_tsne = np.nan_to_num(data_for_tsne)
        
        # 降维
        manifold_coords = tsne.fit_transform(data_for_tsne)
        self.manifold_coords = pd.DataFrame(
            manifold_coords,
            index=price_data.columns,
            columns=[f'component_{i}' for i in range(n_components)]
        )
        
        return self.manifold_coords
    
    def detect_singularities(self, price_data, window=20):
        """
        检测奇点：市场性质突变的地方
        """
        singularities = []
        
        # 计算滚动波动率
        volatility = price_data.rolling(window=window).std()
        
        # 检测波动率突变
        volatility_change = volatility.pct_change().abs()
        
        for stock in price_data.columns:
            # 找到波动率突变超过阈值的时间点
            threshold = volatility_change[stock].quantile(0.95)
            spike_points = volatility_change[stock][volatility_change[stock] > threshold]
            
            for date in spike_points.index:
                singularities.append({
                    'stock': stock,
                    'date': date,
                    'volatility_change': spike_points[date],
                    'type': 'volatility_spike'
                })
        
        # 计算相关性突变
        rolling_corr = price_data.rolling(window=window).corr(pairwise=True)
        
        return singularities
    
    def analyze_feedback_loops(self):
        """
        分析反馈循环
        """
        feedback_loops = []
        
        # 在有向图中寻找循环（这里简化处理）
        # 在实际应用中，需要构建有向图并分析循环
        
        # 简化的反馈分析：基于聚类系数和传递性
        if 'clustering_coefficient' in self.topology_features:
            clustering = self.topology_features['clustering_coefficient']
            transitivity = self.topology_features['transitivity']
            
            # 高聚类系数可能表示局部反馈循环
            if clustering > 0.5:
                feedback_loops.append({
                    'type': 'local_feedback',
                    'strength': clustering,
                    'description': '高聚类系数表明局部节点间存在强反馈'
                })
            
            # 高传递性可能表示全局反馈结构
            if transitivity > 0.3:
                feedback_loops.append({
                    'type': 'global_feedback',
                    'strength': transitivity,
                    'description': '高传递性表明存在全局反馈结构'
                })
        
        return feedback_loops
    
    def generate_insights(self):
        """生成拓扑分析洞察"""
        insights = []
        
        if not self.topology_features:
            self.analyze_topology_features()
        
        features = self.topology_features
        
        # 1. 市场结构洞察
        if features.get('connected', False):
            insights.append({
                'type': 'market_structure',
                'insight': '市场高度连通，信息传播迅速',
                'evidence': f"平均路径长度: {features['avg_path_length']:.2f}"
            })
        else:
            insights.append({
                'type': 'market_structure',
                'insight': '市场存在分割，不同板块相对独立',
                'evidence': f"连通分量数量: {features['num_components']}"
            })
        
        # 2. 中心节点识别
        degree_centrality = features.get('degree_centrality', {})
        if degree_centrality:
            top_central = sorted(degree_centrality.items(), 
                               key=lambda x: x[1], reverse=True)[:5]
            insights.append({
                'type': 'central_nodes',
                'insight': '识别出市场中的中心节点（影响力大的股票/板块）',
                'nodes': [{'name': n, 'centrality': c} for n, c in top_central]
            })
        
        # 3. 社区结构
        communities = features.get('communities', [])
        if communities:
            insights.append({
                'type': 'community_structure',
                'insight': f'市场自然分成了{len(communities)}个社区',
                'community_sizes': [len(c) for c in communities]
            })
        
        # 4. 度分布分析
        degree_dist = features.get('degree_distribution', {})
        if degree_dist.get('std', 0) > degree_dist.get('mean', 1) * 0.5:
            insights.append({
                'type': 'network_heterogeneity',
                'insight': '网络高度异质，少数节点连接众多',
                'evidence': f"度标准差({degree_dist['std']:.2f}) > 0.5 * 均值({degree_dist['mean']:.2f})"
            })
        
        return insights
    
    def visualize_topology(self, save_path=None):
        """可视化拓扑结构"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 网络图
        ax1 = axes[0, 0]
        pos = nx.spring_layout(self.graph, seed=42)
        nx.draw(self.graph, pos, ax=ax1, with_labels=True, 
               node_size=50, font_size=8, alpha=0.7)
        ax1.set_title('市场相关性网络')
        
        # 2. 度分布直方图
        ax2 = axes[0, 1]
        degrees = [d for n, d in self.graph.degree()]
        ax2.hist(degrees, bins=20, alpha=0.7)
        ax2.set_xlabel('度')
        ax2.set_ylabel('频率')
        ax2.set_title('度分布')
        
        # 3. 流形可视化（如果有）
        if self.manifold_coords is not None:
            ax3 = axes[1, 0]
            ax3.scatter(self.manifold_coords.iloc[:, 0], 
                       self.manifold_coords.iloc[:, 1],
                       alpha=0.6)
            for idx in self.manifold_coords.index:
                ax3.annotate(idx, 
                           (self.manifold_coords.loc[idx, 'component_0'],
                            self.manifold_coords.loc[idx, 'component_1']),
                           fontsize=8, alpha=0.7)
            ax3.set_title('流形学习可视化 (t-SNE)')
            ax3.set_xlabel('Component 1')
            ax3.set_ylabel('Component 2')
        
        # 4. 中心性对比
        ax4 = axes[1, 1]
        if self.topology_features:
            degree_centrality = list(self.topology_features.get('degree_centrality', {}).values())
            betweenness_centrality = list(self.topology_features.get('betweenness_centrality', {}).values())
            
            if degree_centrality and betweenness_centrality:
                ax4.scatter(degree_centrality, betweenness_centrality, alpha=0.6)
                ax4.set_xlabel('度中心性')
                ax4.set_ylabel('中介中心性')
                ax4.set_title('中心性对比')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"拓扑图已保存到: {save_path}")
        
        plt.show()

# 示例使用
def example_usage():
    """示例：如何使用拓扑分析器"""
    print("=== 拓扑分析原型示例 ===")
    
    # 1. 创建分析器
    analyzer = TopologyMarketAnalyzer()
    
    # 2. 模拟数据（实际应用中从tushare获取）
    np.random.seed(42)
    dates = pd.date_range('2026-01-01', '2026-03-18', freq='D')
    stocks = ['科技股', '能源股', '金融股', '消费股', '医药股', '工业股']
    
    # 生成相关的时间序列
    base_trend = np.cumsum(np.random.randn(len(dates)) * 0.01)
    price_data = pd.DataFrame(index=dates)
    
    for i, stock in enumerate(stocks):
        # 每只股票有自己独特的趋势，但都与基础趋势相关
        noise = np.random.randn(len(dates)) * 0.02
        correlation = 0.3 + i * 0.1  # 不同的相关性强度
        price_data[stock] = base_trend * correlation + noise + i * 0.1
    
    # 3. 构建相关性网络
    print("构建相关性网络...")
    graph = analyzer.build_correlation_network(price_data, threshold=0.5)
    print(f"网络节点数: {graph.number_of_nodes()}")
    print(f"网络边数: {graph.number_of_edges()}")
    
    # 4. 分析拓扑特征
    print("\n分析拓扑特征...")
    features = analyzer.analyze_topology_features()
    print(f"平均聚类系数: {features['clustering_coefficient']:.3f}")
    print(f"连通分量数量: {features.get('num_components', 'N/A')}")
    
    # 5. 流形学习
    print("\n进行流形学习...")
    manifold = analyzer.manifold_learning(price_data)
    print("流形坐标:")
    print(manifold.head())
    
    # 6. 检测奇点
    print("\n检测奇点...")
    singularities = analyzer.detect_singularities(price_data)
    print(f"检测到 {len(singularities)} 个奇点")
    
    # 7. 分析反馈循环
    print("\n分析反馈循环...")
    feedback_loops = analyzer.analyze_feedback_loops()
    for loop in feedback_loops:
        print(f"反馈循环类型: {loop['type']}, 强度: {loop['strength']:.3f}")
    
    # 8. 生成洞察
    print("\n生成拓扑洞察...")
    insights = analyzer.generate_insights()
    for insight in insights[:3]:  # 显示前3个洞察
        print(f"- {insight['insight']}")
    
    # 9. 可视化
    print("\n生成拓扑可视化...")
    analyzer.visualize_topology(save_path='/tmp/topology_analysis.png')
    
    print("\n=== 示例完成 ===")

if __name__ == "__main__":
    example_usage()