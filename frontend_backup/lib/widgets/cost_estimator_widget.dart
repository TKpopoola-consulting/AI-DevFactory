// lib/widgets/cost_estimator_widget.dart
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../utils/constants.dart';

class CostEstimatorWidget extends StatelessWidget {
  final Map<String, dynamic> config;
  final List<String> requirements;
  
  const CostEstimatorWidget({
    super.key,
    required this.config,
    required this.requirements,
  });
  
  @override
  Widget build(BuildContext context) {
    final estimatedTokens = _estimateTokens();
    final estimatedCompute = _estimateCompute();
    final estimatedStorage = _estimateStorage();
    
    final aiCost = estimatedTokens / 1000 * AppConstants.aiTokenPrice;
    final computeCost = estimatedCompute / 3600 * AppConstants.computePricePerHour;
    final storageCost = estimatedStorage * AppConstants.storagePricePerGB;
    final totalCost = aiCost + computeCost + storageCost;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.attach_money, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Cost Estimator',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.compare_arrows, size: 16),
                  label: const Text('Compare Providers'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildCostCard(
                    context,
                    'AI Tokens',
                    '${(estimatedTokens / 1000).toStringAsFixed(1)}K',
                    '\$${aiCost.toStringAsFixed(3)}',
                    Colors.purple,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildCostCard(
                    context,
                    'Compute',
                    '${(estimatedCompute / 60).toStringAsFixed(0)} min',
                    '\$${computeCost.toStringAsFixed(3)}',
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildCostCard(
                    context,
                    'Storage',
                    '${estimatedStorage.toStringAsFixed(0)} MB',
                    '\$${storageCost.toStringAsFixed(4)}',
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Estimated Total',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '\$${totalCost.toStringAsFixed(4)}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF6366F1),
                      ),
                    ),
                    Text(
                      'Range: \$${(totalCost * 0.8).toStringAsFixed(4)} - \$${(totalCost * 1.2).toStringAsFixed(4)}',
                      style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 120,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: totalCost * 1.2,
                  barGroups: [
                    BarChartGroupData(
                      x: 0,
                      barRods: [
                        BarChartRodData(
                          toY: aiCost,
                          color: Colors.purple,
                          width: 20,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    ),
                    BarChartGroupData(
                      x: 1,
                      barRods: [
                        BarChartRodData(
                          toY: computeCost,
                          color: Colors.blue,
                          width: 20,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    ),
                    BarChartGroupData(
                      x: 2,
                      barRods: [
                        BarChartRodData(
                          toY: storageCost,
                          color: Colors.green,
                          width: 20,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    ),
                  ],
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          const titles = ['AI', 'Compute', 'Storage'];
                          return Text(
                            titles[value.toInt()],
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            '\$${value.toStringAsFixed(2)}',
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              '💰 Set budget alert: ',
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {},
                    child: const Text('Set Alert at \$0.50'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {},
                    child: const Text('Set Alert at \$1.00'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildCostCard(
    BuildContext context,
    String title,
    String value,
    String cost,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            cost,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
  
  int _estimateTokens() {
    // Rough estimation based on prompt length and requirements
    int baseTokens = 1000;
    int promptTokens = (_getPromptText().length / 4).ceil();
    int requirementTokens = requirements.length * 100;
    int configTokens = 500;
    
    return baseTokens + promptTokens + requirementTokens + configTokens;
  }
  
  int _estimateCompute() {
    // Estimate compute time in seconds
    int baseCompute = 60;
    int requirementCompute = requirements.length * 10;
    int complexityCompute = _getComplexityFactor() * 30;
    
    return baseCompute + requirementCompute + complexityCompute;
  }
  
  double _estimateStorage() {
    // Estimate storage in MB
    double baseStorage = 5.0;
    double fileCountEstimate = (requirements.length * 3) + 10;
    return baseStorage + (fileCountEstimate * 0.2);
  }
  
  String _getPromptText() {
    return 'Build a complete e-commerce platform'; // Placeholder
  }
  
  int _getComplexityFactor() {
    return requirements.length ~/ 5;
  }
}
