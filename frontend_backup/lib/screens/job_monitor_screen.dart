// lib/screens/job_monitor_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_highlight/flutter_highlight.dart';
import 'package:flutter_highlight/themes/vs2015.dart';
import '../providers/job_provider.dart';
import '../models/job_model.dart';
import '../widgets/parallel_agents_widget.dart';
import '../widgets/checkpoint_timeline_widget.dart';
import '../widgets/live_logs_widget.dart';
import '../widgets/code_preview_widget.dart';
import '../widgets/quality_report_widget.dart';

class JobMonitorScreen extends StatefulWidget {
  const JobMonitorScreen({super.key});

  @override
  State<JobMonitorScreen> createState() => _JobMonitorScreenState();
}

class _JobMonitorScreenState extends State<JobMonitorScreen> {
  late String _jobId;
  
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)?.settings.arguments as Map?;
    _jobId = args?['jobId'] as String? ?? '';
    
    if (_jobId.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Provider.of<JobProvider>(context, listen: false).getJobStatus(_jobId);
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);
    final job = jobProvider.currentJob;
    
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(job?.id ?? 'Job Monitor'),
        actions: [
          if (job?.isRunning == true)
            IconButton(
              icon: const Icon(Icons.stop),
              onPressed: () => jobProvider.cancelJob(_jobId),
              tooltip: 'Cancel',
            ),
          if (job?.isFailed == true)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => jobProvider.retryJob(_jobId),
              tooltip: 'Retry',
            ),
          if (job?.isCompleted == true)
            IconButton(
              icon: const Icon(Icons.download),
              onPressed: () {},
              tooltip: 'Download',
            ),
        ],
      ),
      body: job == null
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Progress Header
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              _buildStatusIcon(job.status),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'JOB STATUS: ${job.status.toUpperCase()}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    Text(
                                      job.currentStage ?? 'Processing...',
                                      style: TextStyle(
                                        color: Colors.grey.shade600,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    '${job.progress}%',
                                    style: const TextStyle(
                                      fontSize: 24,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Text(
                                    'Elapsed: ${_formatDuration(job.createdAt)}',
                                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          LinearProgressIndicator(
                            value: job.progress / 100,
                            backgroundColor: Colors.grey.shade200,
                            valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF6366F1)),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Current Stage: ${job.currentStage ?? 'Initializing'}',
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                              ),
                              if (job.cost != null)
                                Text(
                                  'Cost: \$${job.cost!.total.toStringAsFixed(4)}',
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                                ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Parallel Agents Dashboard
                  const ParallelAgentsWidget(),
                  const SizedBox(height: 16),
                  
                  // Checkpoint Timeline
                  if (job.checkpoints != null && job.checkpoints!.isNotEmpty)
                    CheckpointTimelineWidget(
                      checkpoints: job.checkpoints!,
                      onRollback: (checkpointId) async {
                        await jobProvider.rollbackToCheckpoint(_jobId, checkpointId);
                      },
                    ),
                  const SizedBox(height: 16),
                  
                  // Live Logs
                  LiveLogsWidget(logs: job.logs ?? []),
                  const SizedBox(height: 16),
                  
                  // Code Preview
                  CodePreviewWidget(artifacts: job.artifacts),
                  const SizedBox(height: 16),
                  
                  // QA Report
                  if (job.quality != null)
                    QualityReportWidget(quality: job.quality!),
                  const SizedBox(height: 16),
                  
                  // Action Buttons
                  Row(
                    children: [
                      if (job.needsIntervention)
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => _showFeedbackDialog(context, jobProvider),
                            icon: const Icon(Icons.feedback),
                            label: const Text('Provide Feedback'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.orange,
                            ),
                          ),
                        ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => jobProvider.cancelJob(_jobId),
                          icon: const Icon(Icons.cancel),
                          label: const Text('Cancel'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.red,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }
  
  Widget _buildStatusIcon(String status) {
    IconData icon;
    Color color;
    
    switch (status) {
      case 'completed':
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case 'failed':
        icon = Icons.error;
        color = Colors.red;
        break;
      case 'needs_intervention':
        icon = Icons.warning;
        color = Colors.orange;
        break;
      default:
        icon = Icons.sync;
        color = Colors.blue;
    }
    
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, color: color, size: 24),
    );
  }
  
  String _formatDuration(DateTime startTime) {
    final duration = DateTime.now().difference(startTime);
    if (duration.inSeconds < 60) {
      return '${duration.inSeconds}s';
    } else if (duration.inMinutes < 60) {
      return '${duration.inMinutes}m ${duration.inSeconds % 60}s';
    } else {
      return '${duration.inHours}h ${duration.inMinutes % 60}m';
    }
  }
  
  void _showFeedbackDialog(BuildContext context, JobProvider provider) {
    final controller = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Human Intervention Required'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'The AI is stuck on the following issues:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            if (provider.currentJob?.quality?.issues != null)
              ...provider.currentJob!.quality!.issues.map((issue) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: issue.severityColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(child: Text(issue.title)),
                      ],
                    ),
                  )),
            const SizedBox(height: 16),
            const Text('Provide feedback to help the AI:'),
            const SizedBox(height: 8),
            TextField(
              controller: controller,
              maxLines: 5,
              decoration: const InputDecoration(
                hintText: 'e.g., Use SQLAlchemy ORM instead of raw SQL...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              await provider.provideFeedback(_jobId, controller.text);
              if (context.mounted) Navigator.pop(context);
            },
            child: const Text('Submit Feedback & Retry'),
          ),
        ],
      ),
    );
  }
}
