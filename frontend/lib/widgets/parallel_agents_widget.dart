// lib/widgets/parallel_agents_widget.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/job_provider.dart';

class ParallelAgentsWidget extends StatelessWidget {
  const ParallelAgentsWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final job = Provider.of<JobProvider>(context).currentJob;
    final agents = job?.agents ?? {};
    
    final agentList = [
      {'name': 'Frontend', 'icon': Icons.code, 'color': const Color(0xFF6366F1)},
      {'name': 'Backend', 'icon': Icons.storage, 'color': const Color(0xFF10B981)},
      {'name': 'Infrastructure', 'icon': Icons.cloud, 'color': const Color(0xFFF59E0B)},
      {'name': 'QA', 'icon': Icons.check_circle, 'color': const Color(0xFF8B5CF6)},
    ];
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.speed, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Parallel Agent Execution',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.flash_on, size: 14, color: Colors.green),
                      SizedBox(width: 4),
                      Text(
                        '4x Faster',
                        style: TextStyle(fontSize: 12, color: Colors.green),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Text(
                    '⚡ Total Speed: 4x faster than sequential execution',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ),
                Text(
                  'Active: ${agents.values.where((a) => a.status == 'running').length}/4',
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                ),
              ],
            ),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.5,
              children: agentList.map((agent) {
                final agentStatus = agents[agent['name']?.toLowerCase()];
                final progress = agentStatus?.progress ?? 0;
                final status = agentStatus?.status ?? 'pending';
                
                return Container(
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: status == 'running'
                          ? agent['color']
                          : Colors.grey.withOpacity(0.3),
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: agent['color'].withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Icon(
                                agent['icon'],
                                size: 20,
                                color: agent['color'],
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                agent['name']!,
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                            ),
                            if (status == 'running')
                              const SizedBox(
                                height: 12,
                                width: 12,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        LinearProgressIndicator(
                          value: progress / 100,
                          backgroundColor: Colors.grey.shade200,
                          valueColor: AlwaysStoppedAnimation<Color>(agent['color']),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${progress}%',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _getStatusText(status),
                          style: TextStyle(
                            fontSize: 10,
                            color: status == 'running' ? agent['color'] : Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
  
  String _getStatusText(String status) {
    switch (status) {
      case 'running':
        return '🔄 Generating...';
      case 'completed':
        return '✅ Completed';
      case 'failed':
        return '❌ Failed';
      default:
        return '⏳ Pending';
    }
  }
}
