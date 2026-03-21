// lib/widgets/checkpoint_timeline_widget.dart
import 'package:flutter/material.dart';
import '../models/job_model.dart';

class CheckpointTimelineWidget extends StatelessWidget {
  final List<Checkpoint> checkpoints;
  final Function(String) onRollback;
  
  const CheckpointTimelineWidget({
    super.key,
    required this.checkpoints,
    required this.onRollback,
  });
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.timeline, size: 20),
                SizedBox(width: 8),
                Text(
                  'Checkpoint Timeline',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Spacer(),
                Icon(Icons.info_outline, size: 16),
              ],
            ),
            const SizedBox(height: 16),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (int i = 0; i < checkpoints.length; i++)
                    _buildCheckpointItem(context, checkpoints[i], i == checkpoints.length - 1),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                children: [
                  Icon(Icons.lightbulb, size: 16, color: Colors.blue),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '💡 Tip: Click any checkpoint to rollback and retry from that stage',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildCheckpointItem(BuildContext context, Checkpoint checkpoint, bool isLast) {
    return Row(
      children: [
        Column(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: checkpoint.isRestorable ? Colors.blue : Colors.grey.shade300,
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: Icon(
                  _getStageIcon(checkpoint.stage),
                  size: 20,
                  color: checkpoint.isRestorable ? Colors.white : Colors.grey,
                ),
                onPressed: checkpoint.isRestorable
                    ? () => _showRollbackDialog(context, checkpoint.id)
                    : null,
              ),
            ),
            Text(
              _formatTime(checkpoint.timestamp),
              style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
            ),
          ],
        ),
        if (!isLast)
          Container(
            width: 60,
            height: 2,
            color: Colors.grey.shade300,
          ),
      ],
    );
  }
  
  IconData _getStageIcon(String stage) {
    switch (stage.toLowerCase()) {
      case 'specs':
        return Icons.description;
      case 'frontend':
        return Icons.code;
      case 'backend':
        return Icons.storage;
      case 'infrastructure':
        return Icons.cloud;
      case 'qa':
        return Icons.check_circle;
      case 'final':
        return Icons.check;
      default:
        return Icons.fiber_manual_record;
    }
  }
  
  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}:${time.second.toString().padLeft(2, '0')}';
  }
  
  void _showRollbackDialog(BuildContext context, String checkpointId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rollback to Checkpoint'),
        content: const Text(
          'Are you sure you want to rollback to this checkpoint? '
          'All progress after this point will be lost.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              onRollback(checkpointId);
            },
            child: const Text('Rollback'),
          ),
        ],
      ),
    );
  }
}
